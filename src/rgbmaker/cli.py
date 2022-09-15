from rgbmaker.fetch import query
import argparse
parser = argparse.ArgumentParser('rgbmaker',description="""A python package which communicates to different 
astronomical services and fetches fits and numerical data.
""", formatter_class=argparse.RawDescriptionHelpFormatter)
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
    annot=args.annot or 'True'
    annot = str(annot).lower()=='true'
    q = query(name=name,position=position,radius=radius,imagesopt=imagesopt,archives=archives,kind=kind,spidx_file=spidx_file,
    px=pixels,annot=annot)
    print(q)


if __name__ == "__main__":
    cli()