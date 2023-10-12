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
im2 = Image.open(getfile('Select Image 2'))
# convert to grayscale numpy arrays
im1 = np.array(ImageOps.grayscale(im1))
im2 = np.array(ImageOps.grayscale(im2))

# # take cropped subselections of to simulate translation
# file = getfile('Select Image 1')
# folder = '/'.join(file.split('/')[:-1]) + '/'
# im = Image.open(file)
# im = np.array(ImageOps.grayscale(im))

# dx_set = 300
# dy_set = -200
# margins = [400, 400, 300, 300]    #spacing from each edge for crop
# im1 = im[margins[0]:-margins[1], margins[2]:-margins[3]]   # crop
# # translated crop
# im2 = im[margins[0]+dx_set:-margins[1]+dx_set, 
         # margins[2]+dy_set:-margins[3]+dy_set]   

#%%
"""
PHASE CORRELATION
"""
# TODO: try zero-padding the images to see if it has an effect

# flip one image horizontally bc they're mirrored from the beamsplitter
im2 = np.flip(im2, 1)
# right now, cropping from a single image, so no flip needed

# get cross-power spectrum of two images
# operations from wikipedia page on phase correlation
G1 = np.fft.fft2(im1)
G2 = np.fft.fft2(im2)
R = G1*np.conjugate(G2)/(np.absolute(G1)*np.absolute(G2))
r = np.fft.ifft2(R)
r = np.real(r)  # remove imaginary component

# get max, whose coordinates should be the displacement
# NOTE: first array index is row#, which corresponds to y instead of x,
# so first index of max location is dy, not dx, same for shape/lengths
(dy, dx) = np.unravel_index(np.argmax(r), r.shape)
# account for negative displacements, which are weird (see notes 10-4-23)
# essentially, negative displacements give a maximum at (dx+Lx, dy+Ly)
# instead of (dx, dy), which is detected by seeing if the given displacements
# are > half of image length (b/c displacement shouldn't be this big) 
# NOTE: this then means that this algorithm won't work for displacements
# greater than half the image length
(Ly, Lx) = r.shape
dx = dx-Lx if dx > Lx//2 else dx
dy = dy-Ly if dy > Ly//2 else dy

print("Displacement: ("+str(dx)+", "+str(dy)+")")
print("Image size: ("+str(Lx)+", "+str(Ly)+")")

# plot phase correlation
fig, ax4 = plt.subplots()
color = ax4.imshow(r)
# fig.colorbar(color, ax=ax4)
ax4.plot(dx, dy, 'rx')

#%%
"""
ALIGN IMAGES
"""
# NOTE: with cartesian phase correlation, only x/y displacement is found,
# and therefore the alignment is a crop only, without any rotation or scaling
# For the future, a different algorithm could scale and rotate the image first
# (e.g a qr code kind of thing) before being fed to the phase correlation 
# for displacement

# if dx>0, then im2 is shifted right from im1, and the left dx should be 
# cropped out of im1's columns (and vice versa). see notes 10-4-23 p.16
if dx>0:
    im1_crop = im1[:,dx:]
    im2_crop = im2[:,:-dx]
else: 
    im1_crop = im1[:,:dx]
    im2_crop = im2[:,-dx:]
    
# same for dy, but now taking slices from pics already cropped in x
# to complete crop
if dy>0:
    im1_crop = im1_crop[dy:,:]
    im2_crop = im2_crop[:-dy,:]
else: 
    im1_crop = im1_crop[:dy,:]
    im2_crop = im2_crop[-dy:,:]

    
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



