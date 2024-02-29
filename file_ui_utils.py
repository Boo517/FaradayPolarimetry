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
import datetime
import os

#%%
"""
class with its own root tk node and a variety of simple user input methods
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
# this function takes a path separated by single or double forward
# or backslashes, and returns a list of the path elements in order
# e.g IN: splitpath("C:\\foo\\bar.txt") OUT: ["C:", "foo", "bar.txt"]
def splitpath(path):
    if "\\" in path:
        return [i for i in path.split("\\") if i!='']
    return [i for i in path.split("/") if i!='']

# returns filepath string of parent of provided filepath
# e.g IN: get_parent("C:/foo/bar.txt") OUT: "C:/foo"
# specify a separation character if wanted (e.g "\\" for Unix style)
def get_parent(file, separator="/"):
    return separator.join(splitpath(file)[:-1])
    
# returns the folder containing the FaradayPolarimetry scripts
def get_program_folder():
    return get_parent(__file__)

# generates dateshot string based on today's date e.g "011923"
# and prompting user for shot #
def get_dateshot():
    # get date
    today = datetime.date.today()
    # 0 pad singel-digit months and days
    month = "0"+str(today.month) if today.month<10 else str(today.month)
    day = "0"+str(today.day) if today.day<10 else str(today.day)
    year = str(today.year)[-2:]
    # prompt user for shot string
    shot = input("Input shot string (e.g s4, c2):\n")
    return month+day+year+shot
    

# renames a file so that it has a prefix
# also works with directories
def prefix_file(path, prefix):
    filename = os.path.basename(path)
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
def unraw_dir(directory):
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
    files = {name:ui.getfile("Choose "+name) for name in names} 
    images = {name:np.array(Image.open(files[name])) for name in names}
    folder = get_parent(files(names[0])) 
    return (files, images, folder) 

# saves images in dict 'images' with keys in 'names' to 'folder'
# as "[name].tif"
def save_images(images, names, folder):
    for name in names:
        Image.fromarray(images[name]).save(
            folder+"/"+name+".tif")

def main():
    ui = UI()
    unraw_dir(ui.getdir("Choose a directory to unraw"))   

#%%
"""
MAIN
"""
if __name__ == "__main__":
    main()
