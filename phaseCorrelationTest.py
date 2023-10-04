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


#%%
"""
PHASE CORRELATION
"""
# TODO: try zero-padding the images to see if it has an effect

# flip one image horizontally bc they're mirrored from the beamsplitter
im2_flip = np.flip(im2, 1)

# plot raw and flipped images
fig1, (ax1, ax2) = plt.subplots(1,2)
ax1.imshow(im1)
ax2.imshow(im2_flip)

# get cross-power spectrum of two images
# operations from wikipedia page on phase correlation
G1 = np.fft.fft2(im1)
G2 = np.fft.fft2(im2_flip)
GG = G1*np.conjugate(G2)
R = GG/np.absolute(GG)
r = np.fft.ifft2(R)
r = np.real(r)  # remove imaginary component

# get max, whose coordinates should be the displacement
displacement = np.unravel_index(np.argmax(r), r.shape)

# plot phase correlation
fig, ax4 = plt.subplots()
color = ax4.imshow(r)
# fig.colorbar(color, ax=ax4)
ax4.plot(displacement[1], displacement[0], 'rx')