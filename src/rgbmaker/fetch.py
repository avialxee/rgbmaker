from rgbmaker import RGBMaker as rgbmaker
from rgbmaker.imgplt import pl_RGB, to_pixel, pl_RGBC, overlayc, overlayo, sqrt
from rgbmaker.tgss_spidx import find_spidx

from matplotlib import pyplot as plt
from regions import PixCoord, EllipsePixelRegion
from astropy.coordinates import Angle, SkyCoord
from astropy import units as ut
from matplotlib.collections import PatchCollection

import matplotlib.patches as mpatches
import numpy as np
import io
import urllib
import base64
from time import perf_counter
from os import path, makedirs

import sys

def query(name="", position="", radius=float(0.12), archives=1, 
                    imagesopt=2, kind='base64', spidx_file=None, px=480, annot=True):
    """
    Usage
    ------
    >>>> from radathome.fetch import query
    >>>> 

    Form Fields:
    ------------
         
        name (Optional) (default=Anonymous) (string)
        -------------------------------------------

            Your name will be displayed on the image enabling mentors, professors, 
            fellow students to be able to recognize your work. Credit is important!

        position (Required)
        -------------------

            The object name or the coordinates of the object in the FK5 (J2000) system. 
            Ex: "14 09 48.86 -03 02 32.6", M87, NGC1243, without quotes.

        radius (Required) (default = 0.12) (float)
        ------------------------------------------

            The size of the image in degrees, this size will be used for the 
            [field of view](https://en.wikipedia.org/wiki/Field_of_view) in the resultant image. 
            For reference, in the night sky, the moon is about 0.52 degrees across.

        imagesopt (default=2)(string)(values=1,2,3)
        -------------------------------------------

            This dropdown gives you a choice of the composite images you want to create. 

            IOU ROR Optical (option = 1)
            ---------------------------
            
                _This option returns four images._

                1. There are two [ROR](#what-is-iou-ror-and-rgb) 
                    (Radio (TGSS ADR1) - Optical (DSS2Red) - Radio (NVSS)) images. 
                    One with TGSS Contours and another with NVSS Contours. 
                One with TGSS Contours and another with NVSS Contours. 
                    One with TGSS Contours and another with NVSS Contours. 
                
                2. The third image is an [IOU](#what-is-iou-ror-and-rgb) 
                    _(Infrared (WISE 22) - Optical (DSS2 Red) - Ultraviolet (Galex Near UV))_ 
                _(Infrared (WISE 22) - Optical (DSS2 Red) - Ultraviolet (Galex Near UV))_ 
                    _(Infrared (WISE 22) - Optical (DSS2 Red) - Ultraviolet (Galex Near UV))_ 
                    with TGSS Contours.

                3. The final RGB image is an optical image with 
                    _(DSS2IR - DSS2Red - DSS2Blue)_ 
                _(DSS2IR - DSS2Red - DSS2Blue)_ 
                    _(DSS2IR - DSS2Red - DSS2Blue)_ 
                    with TGGSS Contours.
            
            Composite Contours on DSS2R  (option = 2)
            -----------------------------------------
            
                _This option returns two images._

                1. The first is a [ROR](#what-is-iou-ror-and-rgb) Image with TGSS contours. 
                    The various symbol seen on the image is the [catalog](https://en.wikipedia.org/wiki/Astronomical_catalog) 
                The various symbol seen on the image is the [catalog](https://en.wikipedia.org/wiki/Astronomical_catalog) 
                    The various symbol seen on the image is the [catalog](https://en.wikipedia.org/wiki/Astronomical_catalog) 
                    data of the respective survey.

                2. The second image is a composite image with DSS2Red background and contours of various 
                    radio surveys like TGSS, NVSS, and VLA First (if available).

            
        archives (default=1)(string)
        ----------------------------

            This dropdown currently offers access to the NVAS image archive. Selecting this option will 
            return the top 5 results from NVAS (if exists). These can be downloaded as .imfits files (open with DS9) 
            by using save as an option when right-clicked.
    """
    fetch_q = rgbmaker(name=name, position=position,
                  radius=radius, archives=archives, imagesopt=imagesopt)
    name = fetch_q.name
    start = perf_counter()
    fetch_q.px = px
    val = fetch_q.submit_query()
    
    level_contour=4

    if fetch_q.server_down:
        fetch_q.status, fetch_q.info = 'warning', 'SkyView is down!'
        return fetch_q.throw_output()

    else:
        fetch_q.otext.append({'Target center': fetch_q.c.to_string('hmsdms')})
        if fetch_q.imagesopt == 1 and fetch_q.c:
            # --- using variables for readability -#--#
            tgss, dss2r, nvss, w22, gnuv, dss2i, dss2b = val['tgss']['data'], val[
                'dss2r']['data'], val['nvss']['data'], val['w22']['data'], val[
                    'gnuv']['data'], val['dss2ir']['data'], val['dss2b']['data']

            # --- creating images ----------#--#
            img1, lvlc1 = overlayc(tgss, dss2r, nvss, nvss, level_contour, 0.0015)
            img2, lvlc2 = overlayc(tgss, dss2r, nvss, tgss, level_contour, 0.015)
            img3 = overlayo(w22,dss2r,gnuv, kind='IOU')
            img4 = overlayo(dss2i,dss2r,dss2b, kind='Optical')
            if lvlc1 is not None:
                fetch_q.otext.append({'TGSS contour ': (str(np.round(lvlc1, 3)))})
            if lvlc2 is not None:
                fetch_q.otext.append({'NVSS contour ': (str(np.round(lvlc2, 4)))})

            # -------- plotting first plot -------------#--#
            plt.ioff()
            fig = plt.figure(figsize=(20, 20))

            pl_RGBC(1, 2, 1, fetch_q.wcs, val['nvss']['data'], lvlc1, img1, fig, name,annot=annot)
            pl_RGBC(1, 2, 2, fetch_q.wcs, val['tgss']['data'], lvlc2, img2, fig, name,annot=annot)
            plt.subplots_adjust(wspace=0.01, hspace=0.01)

            #-------- Saving first plot ------#--#
            string = save_fig(plt, fig, kind)
            
            fetch_q.uri.append(
                {'img1': 'data:image/png;base64,' + urllib.parse.quote(string)})

            #-------- plotting second plot -----#--#
            plt.ioff()
            fig1 = plt.figure(figsize=(20, 20))
            pl_RGBC(1, 2, 1, fetch_q.wcs, val['tgss']['data'], lvlc2, img3, fig1, name, pkind='iou',annot=annot)
            pl_RGBC(1, 2, 2, fetch_q.wcs,
                val['tgss']['data'], lvlc2, img4, fig1, name, pkind='iou',annot=annot)
            plt.subplots_adjust(wspace=0.01, hspace=0.01)

            #-------- Saving second plot ------#--#
            string1 = save_fig(plt, fig1, kind)
            
            fetch_q.uri.append(
                {'img2': 'data:image/png;base64,' + urllib.parse.quote(string1)})

            #-------- Output for success -----#--#
            time_taken = perf_counter()-start
            fetch_q.info = 'completed in ' + str(np.round(time_taken, 3))+". "
            fetch_q.status = "success"
            
        elif fetch_q.imagesopt == 2 and fetch_q.c:
            
            tgss, dss2r, nvss, first = val['tgss']['data'], val[
                'dss2r']['data'], val['nvss']['data'], val['first']['data']

            # --- plots initialization ------#--#
            #img1, lvlc1 = overlayc(tgss, dss2r, nvss, tgss, level_contour, 0.015)
            if tgss.max() > 0.015:
                lvlct = np.arange(0.015, tgss.max(), ((tgss.max() - 0.015)/level_contour))
                fetch_q.otext.append({'TGSS contour ': (str(np.round(lvlct.tolist(), 3)))})
            else:
                lvlct = None
            if first.max() > 0.0005:
                lvlcf = np.arange(0.0005, first.max(),
                                    ((first.max() - 0.0005)/level_contour))
                fetch_q.otext.append({'FIRST contour ': (str(np.round(lvlcf, 4)))})
            else:
                lvlcf = None
            if nvss.max() > 0.0015:
                lvlcn = np.arange(0.0015, nvss.max(), ((nvss.max() - 0.0015)/level_contour))
                fetch_q.otext.append({'NVSS contour ': (str(np.round(lvlcn.tolist(), 4)))})
            else:
                lvlcn = None

            #--- plotting --------------------#--#
            plt.ioff()
            fig = plt.figure(figsize=(20, 20))
            title = ' TGSS(GMRT)-NVSS(VLA)-DSS2R(DSS)'
            dss2r = sqrt(dss2r, scale_min=np.percentile(
                np.unique(dss2r), 1.), scale_max=np.percentile(np.unique(dss2r), 100.))

            #--- RGBC plot -------------------#--#
            ax1 = fig.add_subplot(1,2,1, projection=fetch_q.wcs) 
            pl_RGB(ax1, dss2r, title, name, annot)
            
            #--- vizier access ---------------#--
            # TODO : return table in output
            tgss_viz, nvss_viz = fetch_q.vz_query()
            if tgss_viz is not None:
                tmaj, tmin, tPA, tcen, s_tgss, es_tgss = tgss_viz
            if nvss_viz is not None:
                nmaj, nmin, nPA, ncen, s_nvss, es_nvss = nvss_viz
            try:
                try:
                    patch1 = []
                    for i in range(len(tcen[0])):
                        x, y = tcen[0][i], tcen[1][i]
                        ce = PixCoord(x, y)
                        a = to_pixel(tmaj[i], fetch_q.r, px)
                        b = to_pixel(tmin[i], fetch_q.r, px)
                        theta =Angle(tPA[i], 'deg') + 90*ut.deg

                        reg = EllipsePixelRegion(center=ce, width=a, height=b, angle=theta)
                        ellipse = reg.as_artist(facecolor='none', edgecolor='magenta', lw=2)
                        patch1.append(ellipse)
                        #kwar = dict(arrowprops=dict(arrowstyle="->", ec=".5",
                        #                              relpos=(0.5, 0.5)),
                        #              bbox=dict(boxstyle="round", ec="none", fc="w"))
                        ax1.annotate(i+1, xy=(x,y),
                                    xytext=(0, 0), textcoords="offset points", color="magenta")
                                    #ha="right", va="top")#, **kwar)
                        fetch_q.otext.append({f'S_TGSS-{i+1}': f'{s_tgss.tolist()[i]} {str(s_tgss.unit)}'})
                        fetch_q.otext.append({f'S_TGSS_e-{i+1}': f'{np.round(es_tgss.tolist()[i],3)} {str(es_tgss.unit)}'})
                    tgss_catalog = PatchCollection(
                    patch1, edgecolor='magenta', facecolor='None')
                    
                    ax1.add_collection(tgss_catalog)
                
                finally:
                    patch2 = []
                    for i in range(len(ncen[0])):
                        x, y = ncen[0][i], ncen[1][i]
                        ce = PixCoord(x, y)
                        a = to_pixel(nmaj[i], fetch_q.r, px)
                        b = to_pixel(nmin[i], fetch_q.r, px)
                        if nPA[i] != 0 and nPA[i] != '--':
                            theta = Angle(nPA[i], 'deg') + 90*ut.deg
                        else:
                            theta = 0*ut.deg + 90*ut.deg

                        reg = EllipsePixelRegion(
                            center=ce, width=a, height=b, angle=theta)
                        ellipse = reg.as_artist(
                            facecolor='none', edgecolor='cyan', lw=2)
                        patch2.append(ellipse)
                        ax1.annotate(i+1, xy=(x, y),
                                    xytext=(0, 0), textcoords="offset points", color="cyan",
                                        ha="right", va="top")#, **kwar)
                        
                        fetch_q.otext.append({f'S_NVSS-{i+1}': f'{s_nvss.tolist()[i]} {str(s_nvss.unit)}'})
                        fetch_q.otext.append({f'S_NVSS_e-{i+1}': f'{np.round(es_nvss.tolist()[i],3)} {str(es_nvss.unit)}'})
                    nvss_catalog = PatchCollection(
                        patch2, edgecolor='cyan', facecolor='None')
                    ax1.add_collection(nvss_catalog)                
            except:
                fetch_q.info = "catalog data missing"
            finally:
                #ax1.legend(framealpha=0.0, labelcolor='white')
                if spidx_file is not None:
                    kwargs = dict(arrowprops=dict(arrowstyle="->", ec=".5",
                                    relpos=(0.5, 0.5)),
                    bbox=dict(boxstyle="round", ec="none", fc="w"))
                    xi, yi, spidx = find_spidx(spidx_file, fetch_q.c, fetch_q.r)
                    for ien in range(len(xi)):
                        #print(ien)
                        Xi, Yi = fetch_q.wcs.world_to_pixel(SkyCoord(xi[ien]*ut.deg, yi[ien]*ut.deg)) 
                        #print(Xi,Yi, spidx)
                        ax1.annotate(f'{spidx[ien]}', xy=(Xi, Yi),
                                        xytext=(1, -40), textcoords="offset points",
                                        ha="right", va="top", **kwargs)

                #-------- single survey plot ---------#--#
                dss2r = sqrt(dss2r, scale_min=np.percentile(
                    np.unique(dss2r), 1.), scale_max=np.percentile(np.unique(dss2r), 100.))
                ax2 = fig.add_subplot(1, 2, 2, projection=fetch_q.wcs)
                pl_RGB(ax2, dss2r, title='TGSS(GMRT)-NVSS(VLA)-FIRST(VLA)-DSS2R(DSS)', name=name, annot=annot)
                
                ax2.contour(nvss, lvlcn, colors='cyan')
                ax2.contour(tgss, lvlct, colors='magenta')
                ax2.contour(first, lvlcf, colors='yellow')

                leg1 = mpatches.Patch(color='cyan', label='NVSS')
                leg2 = mpatches.Patch(color='magenta', label='TGSS')
                leg3 = mpatches.Patch(color='yellow', label='FIRST')
                leg4 = mpatches.Patch(color='white', label='DSS2R')
                
                ax2.legend(handles=[leg1, leg2, leg3, leg4],
                        labelcolor='linecolor', framealpha=0.0,)
                ax2.autoscale(False)
                plt.subplots_adjust(wspace=0.01, hspace=0.01)

                #-------- Saving final plot ------#--#
                string1 = save_fig(plt, fig, kind)
                

                #-------- Output for success -----#--#
                fetch_q.uri.append(
                    {'img1': 'data:image/png;base64,' + urllib.parse.quote(string1)})
                time_taken = perf_counter()-start
                fetch_q.info = 'completed in ' + str(np.round(time_taken, 3))+". "
                fetch_q.status = "success"

        return fetch_q.throw_output()

def save_fig(plt, fig, kind='base64', output='output.jpg'):
    
    if kind == 'base64':
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight',
                    transparent=True, pad_inches=0)
        buf.seek(0)
        string = base64.b64encode(buf.read())
        plt.close()
        return string
    elif kind == 'plot':
        plt.show()
        return 'plotted'
    else :
        if not path.exists('output'):
            makedirs('output')
        newPath = 'output/'+output
        opt = newPath
        if path.exists(newPath):
            numb = 1
            while path.exists(newPath):
                newPath = "{0}_{2}{1}".format(
                    *path.splitext(opt) + (numb,))
                try :
                    if path.exists(newPath):
                        numb += 1 
                except:
                    pass               
        fig.savefig(newPath, format=kind, bbox_inches='tight',
                    pad_inches=0)
        print("saved {}".format(newPath))
        plt.close()
        return newPath


def help_o():
    return(
        'use without identifier: (name="", position="", radius=float(0.12), imagesopt=2) -> tuple[str, list, str, list]')

def cli():
    if sys.argv[1] == '-h':
        print(help(query))
        sys.exit()
    else:
        try:
            imagesopt = 2
            if len(sys.argv) > 4:
                if sys.argv[4] == 'ror-iou' or 1 or 'roriou' or 'iou' or 'ror':
                    imagesopt = 1
            q = query(name=str(sys.argv[1]), position=str(
                sys.argv[2]), radius=sys.argv[3], imagesopt=imagesopt, kind='jpg')
            print(str(q))
        except Exception as e:
            print('error occured : {}'.format(e))
            try:
                print(
                    'query(name={}, position={}, radius={}, archives={}, imagesopt={})'.format(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
            except:
                print(help_o())


if __name__ == "__main__":
    cli()
