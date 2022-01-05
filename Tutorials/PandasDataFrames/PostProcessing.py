# %%
import glob
import os
from typing import no_type_check
from IPython.display import Image
import matplotlib.pyplot as plt
import scipy.stats
import numpy as np
import pandas as pd
import openmc

# 1.6 enriched fuel

fuel = openmc.Material(name ='1.6% Fuel')
fuel.set_density('g/cm3', 10.31341)
fuel.add_nuclide('U235', 3.7503e-4)
fuel.add_nuclide('U238', 2.2625e-2)
fuel.add_nuclide('O16', 4.6007e-2)

water = openmc.Material(name ='Borated Water')
water.set_density('g/cm3', 0.740582)
water.add_nuclide('H1', 4.9457e-2)
water.add_nuclide('O16', 2.4732e-2)
water.add_nuclide('B10', 8.0042e-6)

zircaloy = openmc.Material(name ='Zircaloy')
zircaloy.set_density('g/cm3', 6.55)
zircaloy.add_nuclide('Zr90', 7.2758e-3)


# Instantiate a Materials collection
materials = openmc.Materials([fuel, water, zircaloy])

# Export to "materials.xml"
materials.export_to_xml()

# Create cylinders for the fuel and clad
fuel_outer_radius = openmc.ZCylinder(x0=0.0, y0=0.0, r=0.39218)
clad_outer_radius = openmc.ZCylinder(x0=0.0, y0=0.0, r=0.45729)

# Create boundary planes to surround the geometry
# Use both reflective and vacuum boundaries to make life interesting
min_x = openmc.XPlane(x0=-10.71, boundary_type = 'reflective')
max_x = openmc.XPlane(x0=+10.71, boundary_type = 'reflective')
min_y = openmc.XPlane(x0=-10.71, boundary_type = 'reflective')
max_y = openmc.XPlane(x0=+10.71, boundary_type = 'reflective')
min_z = openmc.XPlane(x0=-10.71, boundary_type = 'reflective')
max_z = openmc.XPlane(x0=+10.71, boundary_type = 'reflective')

# Create fuel cell
fuel_cell = openmc.Cell(name='1.6% Fuel', fill= fuel, region=-fuel_outer_radius)

# Create a clad cell
clad_cell = openmc.Cell(name='1.6% Clad', fill = zircaloy) 
clad_cell.region = +fuel_outer_radius & -clad_outer_radius

# Create a moderator cell
moderator_cell = openmc.Cell(name='1.6% Moderator', fill=water, region=+clad_outer_radius)

# Create a universe to encapsulate a fuel pin
pin_cell_universe = openmc.Universe(name='1.6% Fuel Pin', cells = [fuel_cell, clad_cell, moderator_cell])

# Create fuel assembly lattice
assembly = openmc.RectLattice(name='1.6% Fuel - 0BA')
assembly.pitch = (1.26, 1.26)
assembly.lower_left = [-1.26 * 17. / 2.0] * 2
assembly.universes = [[pin_cell_universe] * 17] * 17

# Create root cell
root_cell = openmc.Cell(name='root cell', fill=assembly)

# Add boundary planes
root_cell.region = +min_x & -max_x & +min_y & -max_y & +min_z & -max_z

# Create root universe
root_universe = openmc.Universe(name='root universe')
root_universe.add_cell(root_cell)

# Create geometry and export to "geometry.xml"
geometry = openmc.Geometry(root_universe)
geometry.export_to_xml()

# OpenMC simulation parameters
min_batches = 20
max_batches = 200
inactive = 5
particles = 2500

# Instantiate a settings object
settings = openmc.Settings()
settings.batches = min_batches
settings.inactive = inactive
settings.particles = particles
settings.output = {'tallies': False}
settings.trigger_active = True
settings.trigger_max_batches = max_batches

# Create an initial uniform spatial source distribution over fissionable zones
bounds = [-10.71, -10.71, -10, 10.71, 10.71, 10.]
uniform_dist = openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True)
settings.source = openmc.Source(space=uniform_dist)

#Export to "settings.xml"
settings.export_to_xml()

plot = openmc.Plot(plot_id=1)
os.system("convert materials-xy.ppm materials-xy.png")
plot.filename = 'materials-xy'
print(plot.filename)
plot.origin = [0, 0, 0]
plot.width = [21.5, 21.5]
plot.pixels = [250, 250]
plot.color_by = 'material'

openmc.plot_inline(plot)

# Instantiate an empty Tallies object
tallies = openmc.Tallies()

#Instantiate a tally Mesh

# %%
