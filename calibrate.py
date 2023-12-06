# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 12:48:43 2023

@author: P3 Lab Office
"""

#%%
"""
IMPORT
"""
import numpy as np
import tkinter as Tkinter, tkinter.filedialog as tkFileDialog
from PIL import Image#, ImageOps
import matplotlib.pyplot as plt
import imreg_dft as ird
import json
import os

#%%
"""
OPTIONS
"""
plot = False

#%%
"""
CHOOSE IMAGES
"""
def getfile(message):
    root = Tkinter.Tk()
    root.after(100, root.focus_force)
    root.after(200,root.withdraw)    
    filepath = tkFileDialog.askopenfilename(parent=root,title=message)    
    return filepath 

names = ["im1", "im2"]
files = {name:getfile("Choose "+name) for name in names} 
images = {name:np.array(Image.open(files[name])) for name in names}
folder = '/'.join(files['im1'].split('/')[:-1]) + '/' 

# unflip images
images["im2"]= np.flip(images["im2"], 1)

#%%
"""
PHASE CORRELATION IMAGE REGISTRATION USING IMREG_DFT
"""
result = ird.similarity(images["im1"], images["im2"], numiter=3)
images["im2_transform"] = result["timg"]

#%%
"""
SHOW RESULTS
"""
if plot:
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
    axes = [ax1, ax2, ax3, ax4]
    plot_ims = ["im1", "im2", "im1", "im2_transform"]
    
    for i in range(len(axes)):
        axes[i].imshow(images[plot_ims[i]])
        axes[i].set_title(plot_ims[i])

#%%
"""
SAVE TRANSFORMED IMAGE
"""
Image.fromarray(images["im2_transform"]).save(folder+"im2_transform"+".tif")

#%%
"""
SAVE RESULT DICT TO JSON
"""
calibration_dict = result.copy()
del calibration_dict["timg"]    # no need to save transformed image in json
# can't json-ize ndarray, so convert to python list
calibration_dict['tvec'] = list(calibration_dict['tvec'])   

# save in FaradayPolarimetry/calibration
os.makedirs("calibration", exist_ok=True)      # make sure directory exists
with open("calibration/calibration.json", 'w') as f:
    json.dump(calibration_dict, f)

# save in folder where images are from, too 
# which should be a folder specifically for the calibration, 
# e.g November/110223_calibration
with open(folder+"calibration.json", 'w') as f:
    json.dump(calibration_dict, f)
