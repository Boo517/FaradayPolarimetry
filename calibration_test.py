# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 16:54:10 2023

this program loads a calibration file and applies it to two images in order
to align them

@author: P3 Lab Office
"""
#%%
"""
PACKAGE IMPORTS
"""
import numpy as np
import tkinter as Tkinter, tkinter.filedialog as tkFileDialog
from PIL import Image
import phaseCorrelation
import imreg_dft as ird
import os
import json

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
names = ["im1", "im2"]
files = {name:getfile("Choose "+name) for name in names} 
images = {name:np.array(Image.open(files[name])) for name in names}
#get path to folder containing first file in files
folder = '/'.join(files['im1'].split('/')[:-1]) + '/' 

#%%
"""
ALIGNMENT
"""
# unflip im2
images["im2"] = np.flip(images["im2"], 1)

# Use calibration file to determine displacement, angle, and scale 
# which needs to be applied to im2 to align it with im1

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
images['im2_scangle'] = ird.transform_img(images["im2"], 
        scale=calibration["scale"], angle=calibration["angle"])
# account for difference in coordinate choice
(dy, dx) = calibration['tvec']
dy = round(dy)
dx = round(dx)

# align N1 and N2 by cropping
(images["im1_aligned"], images["im2_aligned"]) = phaseCorrelation.cropAlign(
    images["im1"], images["im2_scangle"], dx, dy)

#%%
"""
SAVE TRANSFORMED IMAGES
"""
save_images = ["im1_aligned", "im2_aligned"]
# create output folder if needed
os.makedirs(folder+"caltest", exist_ok=True)
for name in save_images:
    Image.fromarray(images[name]).save(folder+"caltest/"+name+".tif")