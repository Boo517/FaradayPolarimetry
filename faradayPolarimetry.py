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
import imreg_dft as ird
import os
import json

#%%
"""
OPTIONS
"""
# TODO: writeup user instructions for this program

#%%
""" 
EXPERIMENTAL VALUES
"""
# taken from Ann and Hanyu's MAE 199 report
V = 31.4    #[rad/(T*m)]Verdet constant
L = 0.011   #[m]Faraday glass length
#%%
"""
UI
"""
# create tkinter root
root = Tkinter.Tk()
root.withdraw()
root.wm_attributes("-topmost", 1)

# this function opens a file select dialog through Tkinter and returns 
# the path to the selected file
def getfile(message):
    filepath = tkFileDialog.askopenfilename(parent=root,title=message)    
    return filepath 

# this function opens a question dialog with 'yes' and 'no' buttons,
# returning the string 'yes' or 'no' depending on the choice
def ask(question):
    answer = Tkinter.messagebox.askquestion(message=question, parent=root)
    return answer

#%%
"""
FILE IMPORT
"""
# select bg and shot images, saving filenames and loading images into arrays
# NOTE: For now, can't figure out how to get PIL to import raw images as 16-bit
# instead of 8-bit. Just use imagej module to convert to 16-bit tiff first
names = ["bg1", "shot1", "bg2", "shot2"]
files = {name:getfile("Choose "+name) for name in names} 
images = {name:np.array(Image.open(files[name])) for name in names}
#get path to folder containing first file in files
folder = '/'.join(files['bg1'].split('/')[:-1]) + '/' 
dateshot = folder.split('/')[-3]    # date and shot# string, eg 110223s4
    
#%%
"""
NORMALIZATION
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

#%%
"""
ALIGNMENT
"""
# Use calibration file to determine displacement, angle, and scale 
# which needs to be applied to N2 to align it with N1

# look for calibration file in folder first
if os.path.isfile(folder+"calibration.json"):
    with open(folder+"calibration.json") as f:
        calibration = json.load(f)
    print("Using calibration file found in folder, from path "
          +calibration["path"])
    
# if calibration in FaradayPolarimetry/calibration exists, 
# ask if it is ok to use, and if not, ask to choose a calibration file
elif os.path.isfile("calibration/calibration.json"):
    with open("calibration/calibration.json") as f:
        curcal = json.load(f)
    answer = ask("Is the current calibration, from "+curcal["path"]+
             ", ok to use?")
    if answer == "yes":
        calibration=curcal
        using_curcal = True
    else:
        choosefile = True
        
# if no calibration file in image folder or FaradayPolarimetry/calibration
else:
    choosefile = True

# choose a calibration file
if choosefile:
    file = getfile("Choose a calibration file")
    with open(file) as f:
        calibration = json.load(f)

# allow the user to save calibration to folder if it wasn't already
if choosefile or using_curcal:
    message = """would you like to save the chosen calibration to the folder 
    to avoid choosing next time?"""
    answer = ask(message)
    if answer == "yes":
        with open(folder+"calibration.json", 'w') as f:
            json.dump(calibration, f, indent=1)

# use calibration to scale and rotate N2 using imreg_dft
# 'scangle' stands for 'scale and angle'
images["N2_scangle"] = ird.transform_img(images["N2"], 
    scale=calibration["scale"], angle=calibration["angle"])
images["bg2_scangle"] = ird.transform_img(images["bg2"], 
    scale=calibration["scale"], angle=calibration["angle"])
# account for difference in coordinate choice
(dy, dx) = calibration['tvec']
dy = round(dy)
dx = round(dx)

# align N1 and N2 by cropping
(images["N1_aligned"], images["N2_aligned"]) = phaseCorrelation.cropAlign(
    images["N1"], images["N2_scangle"], dx, dy)
(images["bg1_aligned"], images["bg2_aligned"]) = phaseCorrelation.cropAlign(
    images["bg1"], images["bg2_scangle"], dx, dy)

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
       
#subtract normalized images to eliminate self-emission
#D = I_S+(x,y)/I_B+(x,y) - I_S-(x,y)/I_B-(x,y) = N1 - N2
images["D"] = images["N1_aligned"] - images["N2_aligned"]
    
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
save_images = ["N1_aligned","N2_aligned", "D", "alpha_deg", "B"]
# create output folder if needed
os.makedirs(folder+"out", exist_ok=True)
for name in save_images:
    Image.fromarray(images[name]).save(folder+"out/"+dateshot+"_"+name+".tif")





