# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 13:54:00 2023

@author: P3 Lab Office
"""

#%%
"""
PACKAGE IMPORTS
"""
import numpy as np
# import tkinter as Tkinter, tkinter.filedialog as tkFileDialog
# from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import cm
#%%
"""
PLOTTING AND SCHEMING
"""
rad2deg = 180/np.pi
D_full = lambda a,b : -2*np.sin(2*a)*np.tan(b)
D_ext = lambda a,b : -2*np.sin(2*a)/np.tan(b)

alpha = np.linspace(-np.pi/4, np.pi/4, 50)
beta = np.linspace(np.pi/64, np.pi/4, 50)
A, B = np.meshgrid(alpha, beta)

# Plot the surface for beta set off full transmission
fig1, ax1 = plt.subplots(subplot_kw={"projection": "3d"})

full = D_full(A, B)
surf_full = ax1.plot_surface(A*rad2deg, B*rad2deg, full, cmap=cm.coolwarm)

ax1.set_xlabel("Alpha [deg]")
ax1.set_ylabel("Beta [deg]")
fig1.suptitle("Beta set off Full Transmission")
         
# beta set around extinction              
fig2, ax2 = plt.subplots(subplot_kw={"projection": "3d"})

ext = D_ext(A, B)
surf_ext = ax2.plot_surface(A*rad2deg, B*rad2deg, ext, cmap=cm.coolwarm)

ax2.set_xlabel("Alpha [deg]")
ax2.set_ylabel("Beta [deg]")
fig2.suptitle("Beta set off Extinction")