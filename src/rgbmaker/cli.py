from rgbmaker.fetch import query
from rgbmaker.imgplt import pl_powerlawsi
import argparse

def cli_ASCII():
        ascii_rgbmaker="""
            _                     _             
           | |                   | |            
  _ __ __ _| |__  _ __ ___   __ _| | _____ _ __ 
 | '__/ _` | '_ \| '_ ` _ \ / _` | |/ / _ \ '__|
 | | | (_| | |_) | | | | | | (_| |   <  __/ |   
 |_|  \__, |_.__/|_| |_| |_|\__,_|_|\_\___|_|   
       __/ |                                    
      |___/                                     

A python package which communicates to different 
astronomical services and fetches fits and numerical data
        """
        return ascii_rgbmaker


parser = argparse.ArgumentParser('rgbmaker',description=cli_ASCII(), formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-p', '--position', type=str, help="""(Required)
        The object name or the coordinates of the object in the FK5 (J2000) system. 
        Ex: "14 09 48.86 -03 02 32.6", M87, NGC1243, without quotes.""")
parser.add_argument('-r', '--radius', type=str, help="""(Required) (default = 0.12) (float)
        The size of the image in degrees, this size will be used for the 
        field of view in the resultant image.
        For reference, in the night sky, the moon is about 0.52 degrees across.""")
parser.add_argument('-i', '--imagesopt', type=str, help="""(default=2)(string)(values=1,2,3)
        IOU ROR Optical (option = 1)
        Composite Contours on DSS2R  (option = 2)""")
parser.add_argument('-n', '--name', type=str, help="""(Optional) (default=Anonymous) (string)  
        Your name will be displayed on the image enabling mentors, professors, 
        fellow students to be able to recognize your work. Credit is important!""")
parser.add_argument('-a', '--archives', type=str, help="""(default=1)(string)
        This option currently offers access to the NVAS image archive. Selecting this option will 
        return the top 5 results from NVAS (if exists). These can be downloaded as .imfits files""")
parser.add_argument('-k', '--kind', type=str, help="""(default='base64')
        choose from base64, plot, png, jpg to show base64 of resultant image, plot on output, save png/jpg files""")
parser.add_argument('-s', '--spidx_file', type=str, help="""(Default=None)
        enter path to spidx.fits file that contains spectral index data.""")
parser.add_argument('-px', '--pixels', type=str, help="""(default=480)
        change pixel value for the final resulatant image.""")
parser.add_argument('-A', '--annot', type=str, help="""(default=True)
        remove any annotation by setting this to False.""")
parser.add_argument('-S', '--flux_list', type=str, help="""(Optional)(list)(Default=None)
        Takes input as list for spectral index calculation.""")
parser.add_argument('-S_e', '--flux_error', type=str, help="""(Optional)(list)(Default=[0,0])
        Takes input as list for spectral index calculation.""")
parser.add_argument('-freq', '--freq_list', type=str, help="""(Optional) (Default=None)
        Takes input as list for spectral index calculation.""")
args=parser.parse_args()

def cli():
    
    position=args.position or ""
    radius=args.radius or float(0.12)
    imagesopt=args.imagesopt or 2
    name=args.name or ""
    archives=args.archives or 1
    kind=args.kind or "png"
    spidx_file=args.spidx_file
    pixels=args.pixels or 480
    annot = str(args.annot or 'True').lower()=='true'
    S=args.flux_list 
    S_e=args.flux_error or "0,0"
    freq=args.freq_list or "150,1420"
    if S:
        S=list(map(float, S.split(',')))
        S_e=list(map(float, S_e.split(',')))
        freq=list(map(float, freq.split(',')))
        sindex = pl_powerlawsi(S,S_e,freq, kind='png', label="output")
    if position:
        q = query(name=name,position=position,radius=radius,imagesopt=imagesopt,archives=archives,kind=kind,spidx_file=spidx_file,
        px=pixels,annot=annot)
        print(q)


if __name__ == "__main__":
    cli()
