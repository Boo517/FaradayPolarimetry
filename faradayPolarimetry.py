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
OPTIONS
"""
phasecorr_margin = 0
phasecorr_plotting = False

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
names = ["bg1", "shot1", "bg2", "shot2", "align1", "align2"]
# TODO: figure out imagej library or find another way to create a 
# subselection for alignment
# NOTE: align images are expected to not be mirrored, as that is required
# when manually cropping matching subelections in imagej stacks
# BE CAREFUL that the align images are flipped to match im1
# else the given translation and crop will flip sign (bc im2 is flipped)
# TODO: writeup user instructions for this program
files = {name:getfile("Choose "+name) for name in names} 
images = {name:np.array(Image.open(files[name])) for name in names}
#get path to folder containing first file in files
folder = '/'.join(files['bg1'].split('/')[:-1]) + '/' 
dateshot = folder.split('/')[-3]    # date and shot# string, eg 110223s4

# show images
# fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3,2)
# axes = {"bg1":ax1,"shot1":ax2,"bg2":ax3,"shot2":ax4,
        # "align1":ax5, "align2":ax6}
# for name in names:
#     axes[name].imshow(images[name])
#     axes[name].set_title(name)
    
#%%
"""
NORMALIZATION AND ALIGNMENT
"""
# unflip images which was mirrored by the beamsplitter
images["bg2"] = np.flip(images["bg2"], 1)
images["shot2"] = np.flip(images["shot2"], 1)

# normalize shots by backgrounds to eliminate camera/nd filter sensitivity
# no need to align shots with bgs on same camera, and in fact there's
# a bug rn that makes it so images too aligned return an empty array
# N1 = I_S+(x,y)/I_B+(x,y), N2 = I_S-(x,y)/I_B-(x,y)
images["N1"] = images["shot1"]/images["bg1"]
images["N2"] = images["shot2"]/images["bg2"]

# Use phase correlation to find displacement btwn images
# and align them through cropping. Using raw images instead of normalized
# because there are more features to align
# update 10-19: and using subselection of interest so we align 
# what we care about
(dx, dy) = phaseCorrelation.phaseCorrelate(images["align1"], images["align2"],
                       margin=phasecorr_margin, plotting=phasecorr_plotting)
# (dx, dy) = phaseCorrelation.phaseCorrelate(images["bg1"], images["bg2"])
# (dx, dy) = phaseCorrelation.phaseCorrelate(images["N1"], images["N2"])
(images["N1_aligned"], images["N2_aligned"]) = phaseCorrelation.cropAlign(
    images["N1"], images["N2"], dx, dy)
(images["bg1_aligned"], images["bg2_aligned"]) = phaseCorrelation.cropAlign(
    images["bg1"], images["bg2"], dx, dy)

#subtract normalized images to eliminate self-emission
#D = I_S+(x,y)/I_B+(x,y) - I_S-(x,y)/I_B-(x,y) = N1 - N2
images["D"] = images["N1_aligned"] - images["N2_aligned"]

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
             
# get rotation angle alpha from D, polarizer angle beta, and  
# ratio of background to shot probe beam intensities, probe_ratio
# placeholder for now TODO: find method to obtain (laser energy meter?)
probe_ratio = 1     
print("Enter polarizer angle, beta [deg]: ")
beta = eval(input())*np.pi/180  #[deg]->[rad]
alpha = getRotation(probe_ratio, images["D"], beta)
images["alpha_deg"] = alpha*180/np.pi

# get magnetic field strength from rotation angle, alpha = V*B*L
images["B"] = alpha/(V*L)
#%%
"""
PLOTTING
"""
# plot magnetic field in space
fig2, ax2 = plt.subplots()
color2 = ax2.pcolormesh(np.flip(images["B"], 0), cmap="plasma")
fig2.colorbar(color2, ax=ax2,label="Magnetic Field [T]")
#save figure
plt.savefig(folder+"B_plot")

plt.show()

#%%
"""
IMAGE EXPORT
"""
save_images = ["bg1_aligned", "bg2_aligned", "N1_aligned",
               "N2_aligned", "D", "alpha_deg", "B"]
for name in save_images:
    Image.fromarray(images[name]).save(folder+dateshot+"_"+name+".tif")





