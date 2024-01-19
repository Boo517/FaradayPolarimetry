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
import rawpy
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
# converts a path separated by forward slashes by one separated by 
# backslashes
def backslashify(path):
    return "/".join(path.split("\\"))

def get_parent(file):
    return '/'.join(file.split('/')[:-1])
    
# returns the folder containing the FaradayPolarimetry scripts
def get_program_folder():
    # get parent of program file
    # NOTE: __file__ path style is  "C:\foo\bar", tkinter style is "C:/foo/bar"
    # and os style is "C:\\foo\\bar"
    return get_parent(backslashify(__file__))

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
    try: 
        os.chdir(directory)
        contents = os.listdir(directory)
        for content in contents:
            if not (content in skip or prefix in content):
                prefix_file(content, prefix)
    finally:
        # swap back to old working dir before returning
        os.chdir(owd)

# use rawpy to import a raw image file and convert it into a numpy array
def unraw(file):
    with rawpy.imread(file) as raw:
        # raw.raw_image is freed when raw is, so need to make a copy to return
        im = raw.raw_image.copy()
    return im

# prompts the user for a directory
# takes all the .CR2 images in that directory and converts them to .tiffs, 
# saving them in a new folder
def unraw_dir():
    ui = UI()
    directory = ui.getdir()
    types = [".cr2"]
    owd = os.getcwd()
    try:
        os.chdir(directory)
        contents = os.listdir()
        images = {}
        for content in contents:
            # check extension matches types,
            # converting ext to lowercase so no need to check for .cr2 vs .CR2
            if os.path.splitext(content)[-1].lower() in types:
                # save im array to images dict,  key=filename (sans extension)
                images[os.path.splitext(content)[0]] = unraw(content)
    finally:
        os.chdir(owd)
        
    # save images as tiffs in parent directory
    parent = get_parent(directory)
    try:
        os.chdir(parent)
        os.makedirs("unraw", exist_ok=True)
        save_images(images, images.keys(), "unraw")
    finally:
        os.chdir(owd)
                

# prompt the user to select images from list 'names', and return
# dicts of [name]:[file] and [name]:[image array], as well as the path
# of the folder the first image is from
# NOTE: works for raw images BUT will convert to 8-bit
def select_images(names):
    ui = UI()     # create UI object for file select dialog
    
    # choose imgs to create calibration from
    files = {name:ui.getfile("Choose "+name) for name in names} 
    images = {name:np.array(Image.open(files[name])) for name in names}
    folder = '/'.join(files[names[0]].split('/')[:-1]) 
    
    return (files, images, folder) 

# saves images in dict 'images' with keys in 'names' to 'folder'
# as "[name].tif"
def save_images(images, names, folder):
    for name in names:
        Image.fromarray(images[name]).save(
            folder+"/"+name+".tif")
        
if __name__ == "__main__":
    unraw_dir()
