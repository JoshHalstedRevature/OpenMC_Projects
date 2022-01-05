import glob
import os
from typing import no_type_check
from IPython.display import Image
import matplotlib.pyplot as plt
import scipy.stats
import numpy as np
import pandas as pd
import openmc

# Define global variables

CURRENT_DIRECTORY = os.getcwd()

# Define global functions

def ChangeDirectories():
    print(CURRENT_DIRECTORY)
    try:
        os.chdir("%s/Tutorials/PostProcessing"%(CURRENT_DIRECTORY))
    except FileNotFoundError:
        os.system("pwd")

class Universe:
    def __init__(self):
        self.bounding_surfaces = 'new'

class Cell:
    def __init__(self):
        self.bounding_surfaces = 'new'

class Geometry:
    def __init__(self):
        self.shape = 'Sphere'
        self.origin = (0.0,0.0,0.0)
        #self.

class Material:
    def __init__(self):
        self.element = 'Neptunium'
        self.mass_number = 237


def main():
    print('z')
    ChangeDirectories()

