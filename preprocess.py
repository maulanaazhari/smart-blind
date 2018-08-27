import cv2
import numpy as np
#import matplotlib.pyplot as plt
#import pytesseract
from PIL import Image
from scipy.ndimage import filters,interpolation,morphology,measurements
from scipy import stats

def pil2array(im,alpha=0):
    if im.mode=="L":
        a = np.fromstring(im.tobytes(),'B')
        a.shape = im.size[1],im.size[0]
        return a
    if im.mode=="RGB":
        a = np.fromstring(im.tobytes(),'B')
        a.shape = im.size[1],im.size[0],3
        return a
    if im.mode=="RGBA":
        a = np.fromstring(im.tobytes(),'B')
        a.shape = im.size[1],im.size[0],4
        if not alpha: a = a[:,:,:3]
        return a
    return pil2array(im.convert("L"))

def array2pil(a):
    if a.dtype==np.dtype("B"):
        if a.ndim==2:
            return Image.frombytes("L",(a.shape[1],a.shape[0]),a.tostring())
        elif a.ndim==3:
            return Image.frombytes("RGB",(a.shape[1],a.shape[0]),a.tostring())
        else:
            raise OcropusException("bad image rank")
    elif a.dtype==np.dtype('float32'):
        return Image.fromstring("F",(a.shape[1],a.shape[0]),a.tostring())

def isfloatarray(a):
    return a.dtype in [np.dtype('f'),np.dtype('float32'),np.dtype('float64')]

def normalize_raw_image(raw):
    image = raw-np.amin(raw)
    if np.amax(image)==np.amin(image):
        print_info("# image is empty: %s" % (fname))
        return None
    image = image / np.amax(image)
    return image

def estimate_local_whitelevel(image, zoom=0.5, perc=80, range=20, debug=0):
    m = interpolation.zoom(image,zoom)
    m = filters.percentile_filter(m,perc,size=(range,2))
    m = filters.percentile_filter(m,perc,size=(2,range))
    m = interpolation.zoom(m,1.0/zoom)
    w,h = np.minimum(np.array(image.shape),np.array(m.shape))
    flat = np.clip(image[:w,:h]-m[:w,:h]+1,0,1)
    return flat

def estimate_thresholds(flat, bignore=0.1, escale=1.0, lo=5, hi=90, debug=0):
    d0,d1 = flat.shape
    o0,o1 = int(bignore*d0),int(bignore*d1)
    est = flat[o0:d0-o0,o1:d1-o1]
    if escale>0:
        e = escale
        v = est-filters.gaussian_filter(est,e*20.0)
        v = filters.gaussian_filter(v**2,e*20.0)**0.5
        v = (v>0.3*np.amax(v))
        v = morphology.binary_dilation(v,structure=np.ones((int(e*50),1)))
        v = morphology.binary_dilation(v,structure=np.ones((1,int(e*50))))
    lo = stats.scoreatpercentile(est.ravel(),lo)
    hi = stats.scoreatpercentile(est.ravel(),hi)
    return lo, hi

def start(pil):
	#pil = Image.open(pil_image)
	a = pil2array(pil)
	if a.dtype==np.dtype('uint8'):
    		a = a/255.0
	if a.dtype==np.dtype('int8'):
    		a = a/127.0
	elif a.dtype==np.dtype('uint16'):
    		a = a/65536.0
	elif a.dtype==np.dtype('int16'):
    		a = a/32767.0
	elif isfloatarray(a):
    		pass
	if a.ndim==3:
    		a = np.mean(a,2)
	raw = a

	image = normalize_raw_image(raw)

	extreme = (np.sum(image<0.05)+np.sum(image>0.95))*1.0/np.prod(image.shape)

	if extreme > 0.95:
    		flat = image
	else:
    		flat = estimate_local_whitelevel(image)

	#flat, angle = estimate_skew(flat)
	#print(angle)

	lo, hi = estimate_thresholds(flat)

	flat = flat - lo
	flat = flat / (hi-lo)
	flat = np.clip(flat,0,1)

	image = flat

	if isfloatarray(image):
    		image = np.array(255*np.clip(image,0.0,1.0),'B')

	im = array2pil(image)
	im.save('/home/pi/preprocess.jpg')
	return im
