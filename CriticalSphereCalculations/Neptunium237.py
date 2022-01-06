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

# Define classes

class Universe:
    def __init__(self, cells):
        self.bounding_surfaces = 'new'
        self.cells = cells
        self.root_universe = self.createUniverse()

    def createUniverse(self):
        universe = openmc.Universe(cells = self.cells)
        return universe

class Cell:
    def __init__(self, geometry):
        self.bounding_surfaces = 'new'
        self.geometry = geometry
        self.name = 'new'

class Geometry:
    def __init__(self, materials, characteristic_length=1.0):
        self.materials = materials
        self.characteristic_length = characteristic_length
        self.instantiate_material = openmc.Materials([materials])
        self.export_materials = self.instantiate_material.export_to_xml()
        self.shape = 'Sphere'
        self.shape_object = self.instantiate_object()
        self.origin = (0.0,0.0,0.0)
        #self.
    
    def instantiate_object(self):
        if self.shape == "Sphere":
            new_object = openmc.Sphere(r=self.characteristic_length)
            return new_object

class Material:
    def __init__(self, nuclide="H1", density=1.0, composition=2.0):
        self.name = "water"
        self.density = self.setdensity(density)
        self.add = self.addnuclide(nuclide, composition)
        self.export_xml = 
    
    def setdensity(self, density):
        self.name.set_density('g/cm3', density)
        return None

    def addnuclide(self, nuclide, composition):
        self.add_nuclide(nuclide, composition)
        return None



def main():
    print('z')
    ChangeDirectories()

