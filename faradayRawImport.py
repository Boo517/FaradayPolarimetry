# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 12:22:12 2024

@author: P3 Lab Office
"""
#%%
"""
IMPORTS
"""
import file_ui_utils as utils
import os

#%%
"""
FUNCTIONS
"""
# select raw faraday images, name them with date and shot number, and save them
# to a chosen location in a folder called 'raw', then convert them to 
# tiffs, saving these to a folder called 'unraw' at the same location
def main():
    # choose location to save raw images to 
    ui = utils.UI()
    savedir = ui.getdir("Choose Raw Image Save Location")
    owd = os.getcwd()
    # get dateshot string
    dateshot = utils.get_dateshot()
    try:
        os.chdir(savedir)
        # if chosen folder isn't 'raw', make a 'raw' folder and switch to it
        if os.path.basename(savedir) != "raw":
            os.makedirs("raw")
            os.chdir("raw")
            savedir = os.getcwd()
        # choose raw faraday images, save to chosen 'raw' folder
        images = ["Faraday1_bg", "Faraday1_shot", "Faraday2_bg", "Faraday2_shot"]
        for image in images:
            with open(ui.getfile("Select "+image), "rb") as f:
                # create copy of file
                copy = open("{}_{}.CR2".format(dateshot, image), "wb")
                copy.write(f.read())
                copy.close()
        # convert raws
        utils.unraw_dir(os.getcwd())
    finally:
        os.chdir(owd)
    
#%%
"""
MAIN
"""
if __name__ == "__main__":
    main()