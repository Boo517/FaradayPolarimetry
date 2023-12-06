# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 13:13:30 2023

@author: P3 Lab Office
"""

#%%
"""
PACKAGE IMPORTS
"""
import numpy as np
import tkinter as Tkinter, tkinter.filedialog as tkFileDialog
from PIL import Image#, ImageOps
import matplotlib.pyplot as plt
import phaseCorrelation

#%%
"""
DEBUG
"""
# if true, flip im2 to account for beamsplitter mirroring
flip = True

# set true to use cropped subselection of a single image 
# instead of 2 separate images
subselection = False
if subselection:
    flip = True     # subselection automatically preflips

# set true to use cropped subselections for alignment instead of full images
align_images = False

# save aligned images if true
save = True

phasecorr_margin = 10
phasecorr_plotting = True

#%%
"""
FILE IMPORTS
"""
# this function opens a file select dialog through Tkinter and returns 
# the path to the selected file
def getfile(message):
    root = Tkinter.Tk()
    root.after(100, root.focus_force)
    root.after(200,root.withdraw)    
    filepath = tkFileDialog.askopenfilename(parent=root,title=message)    
    return filepath 

# choose images to perform phase correlation on
file1 = getfile('Select Image 1')
folder = '/'.join(file1.split('/')[:-1]) + '/'
# load images
im1 = np.array(Image.open(file1))
if not subselection:
    im2 = np.array(Image.open(getfile('Select Image 2')))
else:
    # take cropped subselections of im1 to simulate translation
    # NOTE: translations should be smaller than margins for this to work 
    dx_set = 1
    dy_set = 1
    #spacing from each edge for crop, so negative translations work
    margins = [200, 200, 200, 200]    
    im = im1    # copy of im1, as i1 is cropped and im2 should be
    # a subselection of the og im1, not the cropped version
    im1 = im[margins[0]:-margins[1], margins[2]:-margins[3]]   # crop
    # translated crop
    im2 = im[margins[0]+dy_set:-margins[1]+dy_set, 
              margins[2]+dx_set:-margins[3]+dx_set]
    # flip image to simulate effect of beamsplitter
    im2 = np.flip(im2, 1)
    
# convert to grayscale numpy arrays
# not doing this right now, as importing cr2 w PIL reduces to 8-bit, instead
# just importing 16-bit linear tiffs using imagej dcrawreader
# im1 = np.array(ImageOps.grayscale(im1))
# if not subselection:
#     im2 = np.array(ImageOps.grayscale(im2))

#%%
"""
PHASE CORRELATION
"""
# flip one image horizontally bc they're mirrored from the beamsplitter
# no need to comment out if using cropped subselection bc pre-flips
if flip:
    im2 = np.flip(im2, 1)
# use phase correlation to get displacement of images, using alignment images,
# if align_images is True or otherwise just using im1 and im2
if not align_images:
    (dx, dy) = phaseCorrelation.phaseCorrelate(im1, im2, 
                       margin=phasecorr_margin, plotting=phasecorr_plotting)
else:
    (dx, dy) = phaseCorrelation.phaseCorrelate(
        np.array(Image.open(getfile('Select Align1'))),
        np.array(Image.open(getfile('Select Align2'))),
        margin=phasecorr_margin, plotting=phasecorr_plotting)
print("Displacement: ({}, {})".format(dx, dy))
(im1_aligned, im2_aligned) = phaseCorrelation.cropAlign(im1, im2, dx, dy)
    
#%%
"""
SHOW IMAGES
"""
fig1, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
# plot raw images
ax1.imshow(im1)
ax1.set_title("Image 1")

ax2.imshow(im2)
ax2.set_title("Image 2")

# plot cropped images
ax3.imshow(im1_aligned)
ax3.set_title("Cropped Image 1")

ax4.imshow(im2_aligned)
ax4.set_title("Cropped Image 2")

#%%
"""
SAVE IMAGES
"""
if save:
    Image.fromarray(im1_aligned).save(folder+"im1_aligned"+".tif")
    Image.fromarray(im2_aligned).save(folder+"im2_aligned"+".tif")



