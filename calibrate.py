# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 12:48:43 2023

This program

@author: P3 Lab Office
"""

#%%
"""
IMPORT
"""
import numpy as np
from PIL import Image#, ImageOps
import matplotlib.pyplot as plt
import phaseCorrelation
import imreg_dft as ird
import file_ui_utils as utils
import json
import os

#%%
"""
OPTIONS
"""
plot = False    # whether or not to plot og and transformed images
save = True    # whether or not to save transformed images

#%%
"""
FUNCTIONS
"""
# NOTE: assuming im1, im2 already flipped correctly
def calibrate(im1, im2, folder):
    calibration = ird.similarity(im1, im2, numiter=3)
    del calibration["timg"]    # no need to save transformed image in json
    # can't json-ize ndarray, so convert to python list
    calibration["tvec"] = list(calibration["tvec"]) 
    calibration["path"] = folder
    return calibration

# save a calibration dict as a .json file in folder 'location'
def save_calibration(calibration, location):
    with open(location+"/calibration.json", 'w') as f:
        json.dump(calibration, f, indent=1)

# return calibration dict from filepath
def load_calibration(filepath):
    with open(filepath) as f:
        calibration = json.load(f)
    return calibration

# returns aligned and cropped im1 and im2 according to calibration,
# transforming im2 to match im1
# NOTE: does NOT flip im2
def apply_calibration(im1, im2, calibration):
    # use calibration to scale and rotate im2 using imreg_dft
    # 'scangle' stands for 'scale and angle'
    im2_scangle = ird.transform_img(im2, 
        scale=calibration["scale"], angle=calibration["angle"])
    # account for difference in coordinate choice
    (dy, dx) = calibration['tvec']
    dy = round(dy)
    dx = round(dx)

    # align N1 and N2 by cropping
    (im1_aligned, im2_aligned) = phaseCorrelation.cropAlign(
        im1, im2_scangle, dx, dy)
    return (im1_aligned, im2_aligned)

# finds a calibration file, searching first
def find_calibration(folder):
    ui = utils.UI()
    program_folder = utils.get_program_folder()   
    
    # look for calibration file in folder first
    owd = os.getcwd()
    try:
        os.chdir(folder)
        if os.path.isfile("calibration.json"):
            calibration = load_calibration("calibration.json")
            print("Using calibration file found in folder, from path "
              +calibration["path"])
            return calibration
    except:
        print("Problem checking specified folder")
    finally:
        os.chdir(owd)
        
    # asks user if they want to save a calibration to the provided folder
    def ask_save(calibration):
        message = """would you like to save the chosen calibration to the folder 
        to avoid choosing next time?"""
        answer = ui.ask(message)
        if answer == "yes":
            print("saving calibration to folder")
            save_calibration(calibration, folder)
        
    # if calibration in FaradayPolarimetry/calibration exists, 
    # ask if it is ok to use, and if not, ask to choose a calibration file
    try:
        os.chdir(program_folder)
        if os.path.isfile("calibration/calibration.json"):
            curcal = load_calibration("calibration/calibration.json") 
            # show user path of folder where images for calibration were taken
            answer = ui.ask("Is the current calibration, from "+curcal["path"]+
                     ", ok to use?")
            if answer == "yes":
                print("using calibration from program folder")
                ask_save(curcal)
                return curcal
    finally:
        os.chdir(owd)
        
    # if no calibration in provided folder or FaradayPolarimetry/calibration,
    # choose a calibration file
    file = ui.getfile("Choose a calibration file")
    calibration = load_calibration(file)
    ask_save(calibration)
    
    return calibration

# plot four images from dict 'images' with keys 'names', titled based on their
# names
def plot4(images, names):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
    axes = [ax1, ax2, ax3, ax4]
    for i in range(len(axes)):
        axes[i].imshow(images[names[i]])
        axes[i].set_title(names[i])
        
# allow the user to choose 2 images for calibration, then save the calibration
# to the folder the images were located in and the program folder,
# returning the images chosen, the calibration, 
# and the path to the folder the images were from
def calibrate_select():
    ui = utils.UI()     # create UI object for file select dialog
    
    # choose imgs to create calibration from
    names = ["im1", "im2"]
    files = {name:ui.getfile("Choose "+name) for name in names} 
    images = {name:np.array(Image.open(files[name])) for name in names}
    folder = utils.get_parent(files['im1'])

    # unflip 
    images["im2"]= np.flip(images["im2"], 1)
    
    # calibrate
    calibration = calibrate(images["im1"], images["im2"], folder)
    
    # save in folder where images are from,
    # which should be a folder specifically for the calibration, 
    # e.g November/110223_calibration
    save_calibration(calibration, folder)
    
    # and program folder, too
    program_folder = utils.get_program_folder()
    # make folder if !exists 
    os.makedirs(program_folder+"/calibration", exist_ok=True)   
    save_calibration(calibration, program_folder+"/calibration")
    return (images["im1"], images["im2"], calibration, folder)

# prompt user to select 2 images to apply a calibration to as well as
# the calibration file to use, then save the calibrated images
# to the folder the images were from
# NOTE: DOES flip im2
def apply_select():
    # get images to align
    names = ["im1", "im2"]
    (files, images, folder) = utils.select_images(names)
    images["im2"] = np.flip(images["im2"], 1)
    # get calibrationand apply it
    calibration = find_calibration(folder)
    (images["im1_aligned"], images["im2_aligned"]) = apply_calibration(
        images["im1"], images["im2"],calibration)
    # save aligned images to folder
    utils.save_images(images, ["im1_aligned", "im2_aligned"], folder)

# select images to create calibration from, use calibration to align the images
# used to create the calibration, plot them, and save them
def main(plot=False,save=True):
    # create calibration
    images = {}
    (images["im1"], images["im2"], calibration, folder) = calibrate_select()
    
    # apply calibration to align images
    (images["im1_aligned"], images["im2_aligned"]) = apply_calibration(
        images["im1"], images["im2"], calibration)
    
    # show images 
    if plot:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
        axes = [ax1, ax2, ax3, ax4]
        names = ["im1","im2", "im1_aligned", "im2_aligned"]
        for i in range(len(axes)):
            axes[i].imshow(images[names[i]])
            axes[i].set_title(names[i])
    
    # save images
    if save:
        names = ["im1_aligned", "im2_aligned"]
        utils.save_images(images, names, folder)
            
#%%
"""
MAIN
"""
if __name__ == "__main__":
    main(plot, save)


