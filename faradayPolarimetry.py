# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#%%
"""
PACKAGE IMPORTS
"""
import numpy as np
import tkinter as Tkinter, tkinter.filedialog as tkFileDialog
from PIL import Image
import matplotlib.pyplot as plt
import phaseCorrelation

#%%
""" 
EXPERIMENTAL VALUES
"""
#taken from Ann and Hanyu's MAE 199 report
V = 31.4    #[rad/(T*m)]Verdet constant
L = 0.011        #[m]Faraday glass length
#%%
"""
FILE IMPORTS
"""
#this function opens a file select dialog through Tkinter and returns 
#the path to the selected file
def getfile(message):
    root = Tkinter.Tk()
    root.after(100, root.focus_force)
    root.after(200,root.withdraw)    
    filepath = tkFileDialog.askopenfilename(parent=root,title=message)    
    return filepath 

#select bg and shot images, saving filenames and loading the images into arrays
# NOTE: For now, can't figure out how to get PIL to import raw images as 16-bit
# instead of 8-bit. Just use imagej module to convert to 16-bit tiff first
names = ["bg1", "shot1", "bg2", "shot2"]
files = {name:getfile("Choose "+name) for name in names} 
images = {name:np.array(Image.open(files[name])) for name in names}
#get path to folder containing first file in files
folder = '/'.join(files['bg1'].split('/')[:-1]) + '/'   

# show images
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
axes = {"bg1":ax1,"shot1":ax2,"bg2":ax3,"shot2":ax4}
for name in names:
    axes[name].imshow(images[name])
    axes[name].set_title(name)
    
#%%
"""
NORMALIZATION AND ALIGNMENT
"""
# normalize shots by backgrounds to eliminate camera/nd filter sensitivity
# no need to align shots with bgs on same camera, and in fact there's
# a bug rn that makes it so images too aligned return an empty array
# N1 = I_S+(x,y)/I_B+(x,y), N2 = I_S-(x,y)/I_B-(x,y)
N1 = images["shot1"]/images["bg1"]
N2 = images["shot2"]/images["bg2"]

# unflip normalized image which was mirrored by the beamsplitter
N2 = np.flip(N2, 1)

N1_im = Image.fromarray(N1)
N1_im.save(folder+"N1.tif")
N2_im = Image.fromarray(N2)
N2_im.save(folder+"N2.tif")
# Use phase correlation to find displacement btwn images
# and align them through cropping. Using raw images instead of normalized
# because there are more features to align
(dx, dy) = phaseCorrelation.phaseCorrelate(
    images["bg1"], np.flip(images["bg2"], 1))
(N1_aligned, N2_aligned) = phaseCorrelation.cropAlign(N1, N2, dx, dy)
#subtract normalized images to eliminate self-emission
#D = I_S+(x,y)/I_B+(x,y) - I_S-(x,y)/I_B-(x,y) = N1 - N2
D = N1_aligned - N2_aligned

#%%
"""
MATH
"""
#This function returns the Faraday rotation angle given by 
#the ratio of background to shot probe beam intensities, 
#either a 2D array or a scalar (probe_ratio), 
#the difference between the ratio of shot and background intensities 
#for each camera (D = I_S+(x,y)/I_B+(x,y) - I_S-(x,y)/I_B-(x,y)),
#and the angular offset of the polarizing filters from full Tx, beta
#utilizing the equation in the Swadling et al. paper
#Rev. Sci. Instrum. 85, 11E502 (2014); https://doi.org/10.1063/1.4890564
def getRotation(probe_ratio, D, beta):
    return 1/2*np.arcsin(-probe_ratio*D/(2*np.tan(beta)))   #beta from full
    # return 1/2*np.arcsin(-probe_ratio*D*np.tan(beta)/2)   #beta from extinct

#for testing, just import the D image created by hand in imageJ
# D = np.array(Image.open(getfile("Select D")))
             
#get rotation angle alpha from D, polarizer angle beta, and  
#ratio of background to shot probe beam intensities, probe_ratio
probe_ratio = 1     #placeholder for now TODO: find method to obtain
print("Enter polarizer angle, beta [deg]: ")
beta = eval(input())*np.pi/180  #[deg]->[rad]
alpha = getRotation(probe_ratio, D, beta)
alpha_deg = alpha*180/np.pi

#get magnetic field strength from rotation angle, alpha = V*B*L
#TODO: mask for glass? (like a pseudo-density map)
B = alpha/(V*L)
#%%
"""
PLOTTING
"""
#plot rotation angle in space
fig1, ax1 = plt.subplots()
color1 = ax1.pcolormesh(alpha_deg, cmap="plasma")
fig1.colorbar(color1, ax=ax1,label="Faraday Rotation Angle [Degrees]")
#save figure
plt.savefig(folder+"rotation_plot")

#plot magnetic field in space
fig2, ax2 = plt.subplots()
color2 = ax2.pcolormesh(B, cmap="plasma")
fig2.colorbar(color2, ax=ax2,label="Magnetic Field [T]")
#save figure
plt.savefig(folder+"B_plot")

plt.show()

#%%
"""
IMAGE EXPORT
"""
B_im = Image.fromarray(B)
B_im.save(folder+"bfield.tif")

alpha_deg_im = Image.fromarray(alpha_deg)
alpha_deg_im.save(folder+"alpha_deg.tif")



