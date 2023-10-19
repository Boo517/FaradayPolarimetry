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
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import phaseCorrelation

#%%
"""
DEBUG
"""
# set true to use cropped subselection of a single image 
# instead of 2 separate images
subselection = False   

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

# choose 2 images to perform phase correlation on
file1 = getfile('Select Image 1')
folder = '/'.join(file1.split('/')[:-1]) + '/'
# load images
im1 = Image.open(file1)
if not subselection:
    im2 = Image.open(getfile('Select Image 2'))
    
# convert to grayscale numpy arrays
# im1 = np.array(ImageOps.grayscale(im1))
# if not subselection:
#     im2 = np.array(ImageOps.grayscale(im2))

im1 = np.array(im1)
if not subselection:
    im2 = np.array(im2)

# take cropped subselections of to simulate translation
if subselection:
    # NOTE: translations should be smaller than margins for this to work 
    dx_set = 150
    dy_set = -150
    #spacing from each edge for crop, so negative translations work
    margins = [200, 200, 200, 200]    
    im = im1    # copy of im1, as i1 is cropped and im2 should be
    # a subselection of the og im1, not the cropped version
    im1 = im[margins[0]:-margins[1], margins[2]:-margins[3]]   # crop
    # translated crop
    im2 = im[margins[0]+dx_set:-margins[1]+dx_set, 
              margins[2]+dy_set:-margins[3]+dy_set]
    # flip image to simulate effect of beamsplitter, so the next line
    im2 = np.flip(im2, 1)

#%%
"""
PHASE CORRELATION
"""
# TODO: try zero-padding the images to see if it has an effect

# flip one image horizontally bc they're mirrored from the beamsplitter
# (comment out if using cropped subselection)
im2 = np.flip(im2, 1)
(dx, dy) = phaseCorrelation.phaseCorrelate(im1, im2)
print("Displacement: ({}, {})".format(dx, dy))
(im1_crop, im2_crop) = phaseCorrelation.cropAlign(im1, im2, dx, dy)
    
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
ax3.imshow(im1_crop)
ax3.set_title("Cropped Image 1")

ax4.imshow(im2_crop)
ax4.set_title("Cropped Image 2")



