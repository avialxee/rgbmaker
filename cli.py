import sys
from radathome.fetch import rgbmaker, query
fetch_q = []
def help_o():
    return(
        'use without identifier: (name="", position="", radius=float(0.12), archives=1, imagesopt=2) -> tuple[str, list, str, list]')

if sys.argv[1] == 'help':
    print(help(query))
else :
    try:
        imagesopt=2
        if len(sys.argv) > 4:
            if sys.argv[4] == 'ror-iou' or 1 or 'roriou' or 'iou' or 'ror':
                imagesopt = 1
        q = query(name=str(sys.argv[1]), position=str(
            sys.argv[2]), radius=sys.argv[3], imagesopt=imagesopt, kind='jpg')
        print(str(q))
    except Exception as e:
        print('error occured : {}'.format(e))
        try :
            print(
                'query(name={}, position={}, radius={}, archives={}, imagesopt={})'.format(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[5]))
            
        except:
            print(help_o())
