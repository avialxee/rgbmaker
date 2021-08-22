#-- author: @avialxee ---#--#
import requests
from astropy import coordinates, units as ut
from astropy.wcs import WCS
from astroquery.skyview import SkyView as skv

import numpy as np
from time import perf_counter

from warnings import simplefilter
from astroquery.nvas import Nvas
from astroquery.vizier import Vizier

class RGBMaker:

    def __init__(self, name="", position="", radius=float(0.12), archives=1, imagesopt=2, px=480):
        """
        creating instance for variables to be used throughout the process.
        """

        #--- input variables -----#-#

        self.name = str(name)
        self.position = str(position)
        self.radius = float(radius)
        self.archives = int(archives)
        self.imagesopt = int(imagesopt)

        #--- helper & output variables -----#-#

        self.i = 0
        self.uri = []
        self.info = ""
        self.imglt = []
        self.wcs = None
        self.status = "info"
        self.otext = []
        self.px = px
        self.name, self.c, self.r = self._inp_sanitize()
        self.server_down = False

    def throw_output(self):
        """
        returns output showing status of output. 
        
        TODO 
        ----
        1. Http Status-code-like json output. 200, 202, 404 etc
        2. Show vizier table. ex. otext['vizier]
        """
        return self.status, self.uri, self.info, self.otext

    def submit_query(self):
        """
        takes input of name, position, radius, choice of image and arhives 
        to fetch FITS from Skyview and NVAS.        
        """
        ## ------------- Settings ---------------------
        np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
        #VerifyWarning by astropy for NVSS in imagesopt=2 
        simplefilter('ignore', category=UserWarning)
        _input_svys, _input_sampler = self._sanitize_rgb()
        self.name, self.c, self.r = self._inp_sanitize()
        if self.c is not None :
            self._getNVAS(self.archives)
            try:
                hdu_d_list, error = self.getdd(_input_svys, _input_sampler)
            except:
                if self.c :
                    if self.imagesopt == 1 or self.imagesopt == 2 or self.imagesopt == 3:
                        self.status, self.info = 'info', 'error fetching data from skyview'
                    else:
                        self.status, self.info = 'info', 'No images to return'
                return self.throw_output()
            return self._arr_rgb(_input_svys, hdu_d_list)
        else :
            self.status, self.info = 'warning', 'Please check Coordinates'
            return self.throw_output()
        
        #return hdu_d_list #DEBUG

    def _arr_rgb(self, input_svys, hdu_d_list):
        """
        @input 
            of svy names, data returned for surveys 
        @returns: 
            list containing data, range that can be used to plot in matplotlib.
        """
        _svys_res = None
        if hdu_d_list is not None:
            for result in hdu_d_list:
                if not self.wcs:
                    self.wcs = WCS(result[1])
            _key_svy_dict = list(self.svy_dict('*').keys())
            _val_svy_dict = list(self.svy_dict('*').values())
            _svys_res = {}
            _start = perf_counter()
            if self.wcs:
                for i in range(len(input_svys)):
                    _ind_rgb_dict = _val_svy_dict.index(input_svys[i])
                    _svy_sname = _key_svy_dict[_ind_rgb_dict]
                    _svys_res[_svy_sname] = {'data': hdu_d_list[i][0],
                                            'range': 'value ranges from {:0.4f} to {:0.4f}'.format(hdu_d_list[i][0].min(), hdu_d_list[i][0].max())
                                            }
                    if _svy_sname == 'tgss' or _svy_sname == 'nvss' or _svy_sname=='first':
                        self.otext.append(
                            {input_svys[i]  :  _svys_res[_svy_sname]['range']})
                
            else:
                self.info = "No images found."
                _time_taken = perf_counter()-_start
                self.info += ' Time taken:' + str(np.round(_time_taken, 3))+". "
                self.status = "warning"
                return self.throw_output()        
            return _svys_res
        else:
            self.info = "No data fetched from skyview."
            return self.throw_output()

    def _sanitize_rgb(self):
        """
        returns RGB surveys as array dtype=<U13 and sampler as list to be used by getdd().
        """
        _rgbs = []
        _sampler = [None]
        if (self.c is not None) and (self.imagesopt == 1 or self.imagesopt == 2 or self.imagesopt == 3):
            if int(self.imagesopt) == 1 :
                _rgb1 = self.rgb_dict('ror')
                _rgb2 = self.rgb_dict('iou')
                _rgb3 = self.rgb_dict('optical')
                _rgbs = list(set(_rgb1['rgb']) | set(
                    _rgb2['rgb']) | set(_rgb3['rgb']))

            elif int(self.imagesopt) == 2 :
                _rgb1 = self.rgb_dict('single')
                _rgb2 = self.rgb_dict('ror')
                _rgbs = list(set(_rgb1['rgb']) | set(_rgb2['rgb']))

            elif int(self.imagesopt) == 3 :
                _rgb1 = self.rgb_dict('allwise')
                _rgbs = list(set(_rgb1['rgb']))

            _sampler = np.array([None]*len(_rgbs))
            indices = np.where(np.array(_rgbs) == 'NVSS')
            
            if len(indices[0]):
                _sampler[indices] = 'Lanczos3'
        return _rgbs, _sampler

    def getdd(self, input_svys, sampler):
        """
        takes input svys and fetches fits from skyview using astroquery.
        returns [list([hdulist[0].data, hdulist[0].header]), error]
        """
        _imglt = []
        _imgls, _error = self._run_imgl(
            self.c, self.r, input_svys, sampler)
        for i in range(len(_imgls)):
            if _imgls[i] == 0:
                _imglt.insert(
                    i, [np.zeros((int(self.px), int(self.px))), None])
            else:
                _imglt.append([_imgls[i][0][0].data, _imgls[i][0][0].header])
        return _imglt, _error

    def _getNVAS(self, archives):
        archives = self.archives
        if archives and int(archives) == 2 and self.c:
            text=""     
            try :
                nvas_urls = Nvas.get_image_list(self.c,radius=2*ut.arcsec)
                text += " " + str(len(nvas_urls)) + \
                    " Image(s) found in NVAS: "
                i = 1
                for nvas in nvas_urls :
                    if i<=5 :
                        text += " <a href='" + str(nvas) + "' target='_blank' rel='noreferrer noopener'>[" + str(i) + "]</a>"
                        i+=1
                self.otext.append({'NVAS': text})
            except :
                self.otext.append({'NVAS' : 'NVAS server error'})

    def _run_imgl(self, c, r, _in_svys, sam):
        """
        Takes coordinate, radius and surveys to be fetched from 
        skyview and sends to _get_imgl_pool.
        returns a list of hdul and errors requested by getdd.
        """
        result = [0]*len(_in_svys)
        _error = None
        _sam = sam
        try:
            #print(_in_svys)
            try:
                for ind in range(len(_in_svys)):
                    imglt = self._get_imgl_pool(
                        [c, _in_svys[ind], r, result, ind,  _sam[ind]])
            except:
                _error = "problem with survey: " + str(_in_svys)
        except Exception as e:
            _error = e
        return imglt, _error

    def _get_imgl_pool(self, cals):
        """
        Requests Fits from Skyview one by one. Written for multithread pooling.
        returns a list of hdul requested by _run_imgl
        """
        c, svy, r, queue, ind, _sam = cals
        if _sam == 'None':
            _sam = None
        try:
            imglr = skv.get_images(position=c, survey=svy, pixels=str(
                self.px), radius=r, scaling="Linear", sampler=_sam, cache='True')
            queue[ind] = imglr
        except requests.exceptions.ConnectionError as e:
            self.server_down = True
            self.info = e
        except Exception as e:
            # --- if file not found/doesn't exist. Program will continue.
            print("{} not found ".format(svy))
            pass
        return queue

    def _inp_sanitize(self):
        """
        sanitizing inputs: name, radius, position
        """

        #------------ name --#
        name = str(self.name)
        if len(name) <= 2:
            name = "Anonymous"
        if len(name) > 27:
            name = name[:28]

        #---------- radius --#
        if float(str(self.radius)) > 2.0:
            self.radius = 2.0
        r = float(str(self.radius))*ut.degree

        #----- coordinates --#
        c = None
        try:
            if not ('' or None) :
                c = coordinates.SkyCoord.from_name(self.position, frame='fk5')
                self.info = "success"
                self.status = "success"
                return name, c, r
        except:
            self.info = " Please check coordinates"
            self.status = "warning"
            #print(self.throw_output())
            return name, c, r

    @classmethod
    def rgb_dict(cls, combination):
        """
        dictionary for creating RGB images and single survey images using svy_dict().
        """
        _sampling_b, _r, _g, _b = [None]*4
        if "iou" in combination:
            _r = cls.svy_dict('w22')
            _g = cls.svy_dict('dss2r')
            _b = cls.svy_dict('gnuv')
        elif "ror" in combination:
            _r = cls.svy_dict('tgss')
            _g = cls.svy_dict('dss2r')
            _b = cls.svy_dict('nvss')
            _sampling_b = 'Lanczos3'
        elif "optical" in combination:
            _r = cls.svy_dict('dss2ir')
            _g = cls.svy_dict('dss2r')
            _b = cls.svy_dict('dss2b')
        elif "single" in combination:
            _g = cls.svy_dict('dss2r')
            _r = cls.svy_dict('first')
            return {'rgb': [_r,_g], 'sampler': [None]}
        elif "allwise" in combination:
            _r = cls.svy_dict('w22')
            _g = cls.svy_dict('w4_6')
            _b = cls.svy_dict('w3_4')
            return {'rgb': [_r,_g, _b], 'sampler': [None, None, None]}

        return {'rgb': [_r, _g, _b], 'sampler': [None, None, _sampling_b]}
    
    def vz_query(self):
        """
        query from vizier for NVSS and TGSS.
        @returns:
            MajorAxis (unitless) (Vizier : arcsec), 
            MinorAxis (unitless) (Vizier : arcsec),
            PA  (unitless) (Vizier : deg), 
            pixel based position (single arguement)
        """
        _tgss_viz, _nvss_viz = [None]*2
        if self.imagesopt == 2:
            try:
                try: 
                    _tviz = Vizier(columns=self.vzc_dict('tgss')).query_region(
                        self.c, self.r, catalog=self.vzb_dict('tgss'))
                    _tra = _tviz[0]['RAJ2000']  # *ut.deg
                    _tdec = _tviz[0]['DEJ2000']  # *ut.deg
                    _tMaj = _tviz[0]['Maj']
                    _tMin = _tviz[0]['Min']
                    _s_tgss = _tviz[0]['Stotal']
                    _es_tgss = _tviz[0]['e_Stotal']
                    if "PA" in _tviz[0].columns:
                        _tPA = _tviz[0]["PA"]
                    else:
                        _tPA = 0
                    _center_tgss = coordinates.SkyCoord(ra=_tra, dec=_tdec)
                    _center_tgss_px = self.wcs.world_to_pixel(_center_tgss)
                    _tgss_viz = [_tMaj, _tMin, _tPA, _center_tgss_px, _s_tgss, _es_tgss]
                finally:
                    _nviz = Vizier(columns=self.vzc_dict('nvss')).query_region(
                        self.c,self.r, catalog=self.vzb_dict('nvss'))
                    _nra = coordinates.Angle(_nviz[0]['RAJ2000'], unit=ut.hour)  # .deg
                    _ndec = coordinates.Angle(_nviz[0]['DEJ2000'], unit=ut.deg)  # .deg
                    #_nrad = coordinates.Angle(_nviz[0]['RAJ2000'], unit=ut.hour).deg
                    #_ndecd = coordinates.Angle(_nviz[0]['DEJ2000'], unit=ut.deg).deg for scatter plots
                    _nMaj = _nviz[0]["MajAxis"]
                    _nMin = _nviz[0]["MinAxis"]
                    _s_nvss = _nviz[0]['S1.4']
                    _es_nvss = _nviz[0]['e_S1.4']
                    if "PA" in _nviz[0].columns:
                        _nPA = _nviz[0]["PA"]
                    else:
                        _nPA = 0
                    _center_nvss = coordinates.SkyCoord(ra=_nra, dec=_ndec)
                    _center_nvss_px = self.wcs.world_to_pixel(_center_nvss)
                    _nvss_viz = [_nMaj, _nMin, _nPA, _center_nvss_px, _s_nvss, _es_nvss]
            except:
                self.info = " no data in catalog"

        return _tgss_viz, _nvss_viz

    @classmethod
    def svy_dict(cls, svy=None):
        """
        dictionary for surveys to be used to fetch FITS from skyview using astroquery.
        """
        cls.svys = Surveys()
        _dict = cls.svys.__dict__
        if svy in _dict:
            return _dict[svy]
        if svy is None :
            return cls.svys
        elif svy == '*':
            return _dict
        elif svy == 'v':
            return _dict.values()
        elif svy == 'k':
            return _dict.keys()
        else:
            return "'{}' is not a valid survey. please choose one from {} or use any of '*' 'v' 'k' ".format(svy, _dict.keys())

    @staticmethod
    def vzc_dict(svy):
        """
        vizier column dictionary
        dictionary for NVSS, TGSS column using vizier
        TODO: add column for errors too
        """
        columns = {'tgss': ['RAJ2000', 'DEJ2000', 'Maj', 'Min', 'PA', 'Stotal', 'e_Stotal'],
                   'nvss': ['RAJ2000', 'DEJ2000', 'MajAxis', 'MinAxis', 'PA', '+NVSS', ' S1.4', 'e_S1.4']
                   }
        if svy in columns:
            return columns[svy]
        elif svy == '*':
            return columns
        elif svy == 'v':
            return columns.values()
        elif svy == 'k':
            return columns.keys()
        else:
            return "'{}' is not a valid survey. please choose one from {} or use any of '*' 'v' 'k' ".format(svy, columns.keys())

    @staticmethod
    def vzb_dict(svy):
        """
        vizier base dictionary
        dictionary for NVSS, TGSS catalog using vizier
        """
        base = {'tgss': 'J/A+A/598/A78/table3',
                'nvss': 'VIII/65/nvss'
                }
        if svy in base:
            return base[svy]
        elif svy == '*':
            return base
        elif svy == 'v':
            return base.values()
        elif svy == 'k':
            return base.keys()
        else:
            return "'{}' is not a valid survey. please choose one from {} or use any of '*' 'v' 'k' ".format(svy, base.keys())

class Surveys(RGBMaker):
    
    def __init__(self) -> None:

        self.__dict__ = {'tgss': 'TGSS ADR1',
                'nvss': 'NVSS',
                'first': 'VLA FIRST (1.4 GHz)',
                'dss2r': 'DSS2 Red',
                'dss2ir': 'DSS2 IR',
                'dss2b': 'DSS2 Blue',
                'w22': 'WISE 22',
                'w12': 'WISE 12',
                'w4_6': 'WISE 4.6',
                'w3_4': 'WISE 3.4',
                'gnuv': 'GALEX Near UV'}
