# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#-----------------------------------------------------------------------------#
"""
IMPORTS
"""
import numpy as np

#-----------------------------------------------------------------------------#
"""
This function returns the Faraday rotation angle given by 
the ratio of probe intensities, either a 2D array or a scalar (probe_ratio), 
the difference between the ratio of shot and background intensities 
for each camera (D = I_S+(x,y)/I_B+(x,y) - I_S-(x,y)/I_B-(x,y)),
and the angular offset of the polarizing 
utilizing the equation in the 
"""
def getRotation(probe_ratio, D, beta):
    return 1/2*np.arcsin(probe_ratio*D*np.tan(beta)/2)