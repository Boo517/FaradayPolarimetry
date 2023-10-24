# -*- coding: utf-8 -*-
"""
phaseCorrelation is a collection of functions for the phase correlation 
method for aligning images

Created on Wed Oct 18 13:00:21 2023

@author: P3 Lab Office
"""
#%%
"""
PACKAGE IMPORTS
"""
import numpy as np
import matplotlib.pyplot as plt
#%%
"""
(dx, dy) = phaseCorrelation(im1, im2)
phaseCorrelate returns the displacement of the second image frame 
with respect to the first, in the usual camera coordinate system 
with (0,0) at the top left
optional margin and plotting arguments are for discarding the edge values
of the inverse ft of the phase correlation, as there can be significant high
amplitude noise there, and plotting sets whether or not to plot the 
inverse ft and its maximum (which determines the displacement)
"""
def phaseCorrelate(im1, im2, margin=10, plotting=False):
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
    # NOTE: for some reason, getting high amplitude artifacts at edges, so
    # also get rid of margin # of edge values
    if margin>0:
        r[:margin,:] = 0
        r[-margin:, :] = 0
        r[:, :margin] = 0
        r[:, -margin:] = 0
    (dy, dx) = np.unravel_index(np.argmax(r), r.shape)
    
    # results of phase correlation in physical space, max marked w red 'X'
    if plotting:
        fig, ax = plt.subplots()
        ax.pcolormesh(r)
        ax.plot(dx, dy, 'rx')
    
    # account for negative displacements, which are weird (see notes 10-4-23)
    # in short, negative displacements give a maximum at (dx+Lx, dy+Ly)
    # instead of (dx, dy), which is detected by seeing if the given displacements
    # are > half of image length (b/c negative displacement shouldn't be 
    # big enough to cause dx+Lx to be less than Lx/2 [|dx|<Lx/2]
    # and normal displacements also shouldn't be greater than that [dx<Lx/2]
    # NOTE: this then means that this algorithm won't work for displacements
    # greater than half the image length
    (Ly, Lx) = r.shape
    dx = dx-Lx if dx > Lx//2 else dx
    dy = dy-Ly if dy > Ly//2 else dy
    return (dx, dy)

#%%
"""
(im1_crop, im2_crop) = cropAlign(im1, im2, dx, dy)
cropALign returns the cropped and aligned im1 and im2 given the original 
images and the displacment of im2 from im1 in the usual camera  
coordinate system with (0,0) at the top left
"""
def cropAlign(im1, im2, dx, dy):
    # NOTE: with cartesian phase correlation, only x/y displacement is found,
    # and therefore the alignment is a crop only, without rotation or scaling
    # In future, different algorithm could scale and rotate the image first
    # (e.g a qr code kind of thing) before being fed to the phase correlation 
    # for displacement
    
    # if dx>0, then im2 is shifted right from im1, and the left dx should be 
    # cropped out of im1's columns (and vice versa). see notes 10-4-23 p.16
    # dx==0 breaks indexing (-0 doesn't work), so special case
    if dx==0:
        # no change, but must create crop vars to return
        im1_crop = im1
        im2_crop = im2
    elif dx>0:
        im1_crop = im1[:,dx:]
        im2_crop = im2[:,:-dx]
    else: 
        im1_crop = im1[:,:dx]
        im2_crop = im2[:,-dx:]
        
    # same for dy, but now taking slices from pics already cropped in x
    # to complete crop
    if dy==0:
        pass
    elif dy>0:
        im1_crop = im1_crop[dy:,:]
        im2_crop = im2_crop[:-dy,:]
    else: 
        im1_crop = im1_crop[:dy,:]
        im2_crop = im2_crop[-dy:,:]
    
    return (im1_crop, im2_crop)