# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 14:36:19 2023

@author: P3 Lab Office
"""

#%%
"""
IMPORTS
"""
import tkinter as Tkinter, tkinter.filedialog as tkFileDialog
from PIL import Image
import numpy as np
import os

#%%
"""
class with its own root tk node with a variety of simple user input methods
"""
class UI():
    # create a root tk element, hide it, and make it appear above other windows
    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.withdraw()
        self.root.wm_attributes("-topmost", 1)
        
    # this function opens a file select dialog through Tkinter and returns 
    # the path to the selected file
    def getfile(self, message="Choose a file"):
        filepath = tkFileDialog.askopenfilename(parent=self.root,title=message)    
        return filepath 
    
    # this function opens a file select dialog through Tkinter and returns 
    # the path to the selected file
    def getdir(self, message="Choose a directory"):
        dirpath = tkFileDialog.askdirectory(parent=self.root,title=message)    
        return dirpath 

    # this function opens a question dialog with 'yes' and 'no' buttons,
    # returning the string 'yes' or 'no' depending on the choice
    def ask(self, question):
        answer = Tkinter.messagebox.askquestion(message=question, 
                                                parent=self.root)
        return answer
    
#%%
"""
FUNCTIONS
"""
# returns the folder containing the FaradayPolarimetry scripts
def get_program_folder():
    # remove program file from prgram filepath to get folder it's in
    return '/'.join(__file__.split('/')[:-1])

# renames a file so that it has a prefix
# also works with directories
def prefix_file(path, prefix):
    filename = path.split('/')[-1]
    filename = prefix+filename
    os.rename(path, filename)

# prefix everything in a directory unless it's already prefixed or in 'skip'
def prefix_contents(directory, prefix, skip=[]):
    # swap working dir to provided one, so we can just use filenames for 
    # contents instead of full path
    owd = os.getcwd()
    os.chdir(directory)
    try: 
        contents = os.listdir(directory)
        for content in contents:
            if not (content in skip or prefix in content):
                prefix_file(content, prefix)
    finally:
        # swap back to old working dir before returning
        os.chdir(owd)

# prompt the user to select images from list 'names', and return
# dicts of [name]:[file] and [name]:[image array], as well as the path
# of the folder the first image is from
def select_images(names):
    ui = UI()     # create UI object for file select dialog
    
    # choose imgs to create calibration from
    files = {name:ui.getfile("Choose "+name) for name in names} 
    images = {name:np.array(Image.open(files[name])) for name in names}
    folder = '/'.join(files['im1'].split('/')[:-1]) 
    
    return (files, images, folder) 

# saves images in dict 'images' with keys in 'names' to 'folder'
# as "[name].tif"
def save_images(images, names, folder):
    for name in names:
        Image.fromarray(images[name]).save(
            folder+"/"+name+".tif")