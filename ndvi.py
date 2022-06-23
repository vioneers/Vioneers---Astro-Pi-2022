import cv2
import numpy as np
from pathlib import Path
from fastiecm import fastiecm

baseFolder = Path(__file__).parent.resolve()

def mask(image):
    # Create a mask
    shape = image.shape
    y = int(shape[0]/2)-50
    x = int(shape[1]/2)-20
    r = 1300
    mask = np.zeros(image.shape, dtype=np.uint8)
    mask = cv2.circle(mask, (x, y), r, (255, 255, 255), -1)
    image[image<0] = 0
    image[image>255] = 255
    image = image.astype(np.uint8)
    image = cv2.bitwise_and(image, mask)
    return image

def display(image, image_name):
    image = np.array(image, dtype=float)/float(255) #convert to an array
    shape = image.shape
    height = int(shape[0]/2)
    width = int(shape[1]/2)
    image = cv2.resize(image, (width, height))
    cv2.namedWindow(image_name) # create window
    cv2.imshow(image_name, image) # display image
    cv2.waitKey(0) # wait for key press
    cv2.destroyAllWindows()

def contrast_stretch(im):
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)

    out_min = 0.0
    out_max = 255.0

    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min
    
    return out

def calc_ndvi(image):
    b, g, r = cv2.split(image)
    b = b*b*b*b*b*b
    r = r*r*r*r*r*r
    bottom = (r.astype(float) + b.astype(float))
    bottom[bottom==0] = 0.01
    ndvi = (b.astype(float) - r) / bottom + 0.2
    ndvi = contrast_stretch(ndvi)
    return ndvi

def color_maping1(image):
    image[image<0] = 0
    image[image>255] = 255
    color_mapped_prep = image.astype(np.uint8)
    #color_mapped_image = cv2.applyColorMap(color_mapped_prep, fastiecm)
    color_mapped_image = cv2.applyColorMap(color_mapped_prep, cv2.COLORMAP_TURBO)
    #color_mapped_image = cv2.applyColorMap(color_mapped_prep, cv2.COLORMAP_INFERNO)
    return color_mapped_image

def color_maping2(image):
    image[image<0] = 0
    image[image>255] = 255
    color_mapped_prep = image.astype(np.uint8)
    #color_mapped_image = cv2.applyColorMap(color_mapped_prep, fastiecm)
    #color_mapped_image = cv2.applyColorMap(color_mapped_prep, cv2.COLORMAP_JET)
    color_mapped_image = cv2.applyColorMap(color_mapped_prep, cv2.COLORMAP_INFERNO)
    return color_mapped_image

def process(nr):
    image = cv2.imread(f'{baseFolder}/vioneers-20220619T082250Z-001/vioneers/photo{nr:03d}.jpg') # load image
    #image = mask(image)
    image = contrast_stretch(image)
    image = calc_ndvi(image)
    image = mask(image)
    cv2.imwrite(f'{baseFolder}/ndvi/value/ndvi{nr:03d}.png', image)
    cm1 = color_maping1(image)
    cv2.imwrite(f'{baseFolder}/ndvi/color1/ndvi{nr:03d}_color1.png', cm1)
    cm2 = color_maping2(image)
    cv2.imwrite(f'{baseFolder}/ndvi/color2/ndvi{nr:03d}_color2.png', cm2)
    #display(image, 'ndvi')

for i in range(1, 346):
    process(i)
    print(i)
