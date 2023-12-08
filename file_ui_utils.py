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
    def getfile(self, message):
        filepath = tkFileDialog.askopenfilename(parent=self.root,title=message)    
        return filepath 

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
def get_program_folder():
    # remove program file from prgram filepath to get folder it's in
    return '/'.join(__file__.split('/')[:-1])