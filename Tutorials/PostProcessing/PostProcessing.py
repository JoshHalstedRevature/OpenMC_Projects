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

CURRENT_DIRECTORY = os.getcwd()
print(CURRENT_DIRECTORY)
try:
    os.chdir("%s/Tutorials/PostProcessing"%(CURRENT_DIRECTORY))
except FileNotFoundError:
    os.system("pwd")


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
min_x = openmc.XPlane(x0=-0.63, boundary_type = 'reflective')
max_x = openmc.XPlane(x0=+0.63, boundary_type = 'reflective')
min_y = openmc.YPlane(y0=-0.63, boundary_type = 'reflective')
max_y = openmc.YPlane(y0=+0.63, boundary_type = 'reflective')
min_z = openmc.ZPlane(z0=-0.63, boundary_type = 'reflective')
max_z = openmc.ZPlane(z0=+0.63, boundary_type = 'reflective')

# Create a universe to encapsulate a fuel pin
pin_cell_universe = openmc.Universe(name='1.6% Fuel Pin')

# Create fuel cell
fuel_cell = openmc.Cell(name='1.6% Fuel', fill= fuel, region=-fuel_outer_radius)
pin_cell_universe.add_cell(fuel_cell)

# Create a clad cell
clad_cell = openmc.Cell(name='1.6% Clad', fill = zircaloy) 
clad_cell.region = +fuel_outer_radius & -clad_outer_radius
pin_cell_universe.add_cell(clad_cell)

# Create a moderator cell
moderator_cell = openmc.Cell(name='1.6% Moderator', fill=water, region=+clad_outer_radius)
pin_cell_universe.add_cell(moderator_cell)

# Create root cell
root_cell = openmc.Cell(name='root cell')
root_cell.fill = pin_cell_universe

# Add boundary planes
root_cell.region = +min_x & -max_x & +min_y & -max_y & +min_z & -max_z

# Create root universe

root_universe = openmc.Universe(universe_id=0, name = 'root universe')
root_universe.add_cell(root_cell)

# Create geometry and export to "geometry.xml"
geometry = openmc.Geometry(root_universe)
geometry.export_to_xml()

# Instantiate a settings object
settings = openmc.Settings()
settings.batches = 100
settings.inactive = 10
settings.particles = 5000

# Create an initial uniform spatial source distribution over fissionable zones
bounds = [-0.63, -0.63, -0.63, 0.63, 0.63, 0.63]
uniform_dist = openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True)
settings.source = openmc.Source(space=uniform_dist)

#Export to "settings.xml"
settings.export_to_xml()

plot = openmc.Plot.from_geometry(geometry)
plot.filename = 'materials-xy'
os.system('pwd')
os.system("convert materials-xy.ppm materials-xy.png")
plot.pixels = (250, 250)
plot.to_ipython_image()

# Instantiate an empty Tallies object

tallies = openmc.Tallies()

# Create mesh which will be used for tally
mesh = openmc.RegularMesh()
mesh.dimension = [100, 100]
mesh.lower_left = [-0.63, -0.63]
mesh.upper_right = [0.63, 0.63]

# Create mesh filter for tally
mesh_filter = openmc.MeshFilter(mesh)

# Create mesh tally to score flux and fission rate
tally = openmc.Tally(name = 'flux')
tally.filters = [mesh_filter]
tally.scores = ['flux', 'fission']
tallies.append(tally)

# Export to "tallies.xml"
tallies.export_to_xml()

# Run OpenMC!
openmc.run()

#Load the statepiont file
sp = openmc.StatePoint('statepoint.100.h5')

tally = sp.get_tally(scores=['flux'])
print(tally)
print(tally.sum)
print(tally.mean.shape)
print(tally.mean, tally.std_dev)

flux = tally.get_slice(scores=['flux'])
fission = tally.get_slice(scores = ['fission'])
print(flux)

flux.std_dev.shape = (100, 100)
flux.mean.shape = (100, 100)
fission.std_dev.shape = (100, 100)
fission.mean.shape = (100, 100)

fig = plt.subplot(121)
fig.imshow(flux.mean)
fig2 = plt.subplot(122)
fig2.imshow(fission.mean)

# Determine relative error
relative_error = np.zeros_like(flux.std_dev)
nonzero = flux.mean > 0
relative_error[nonzero] = flux.std_dev[nonzero] / flux.mean[nonzero]

# Distribution of relative errors
ret = plt.hist(relative_error[nonzero], bins = 50)

#ret.savefig('RelativeError.png')

# Create log-spaced energy bins from 1 keV to 10 MeV
energy_bins = np.logspace(3,7)

# Calculate pdf for source energies
probability, bin_edges = np.histogram(sp.source['E'], energy_bins, density = True)

# Make sure integrating the PDF gives us unity
print(sum(probability*np.diff(energy_bins)))

# Plot source energy PDF
SourceEnergyPDF = plt.semilogx(energy_bins[:-1], probability*np.diff(energy_bins), drawstyle='steps')
plt.xlabel('Energy (eV)')
plt.ylabel('Probability/eV')
#SourceEnergyPDF.savefig('SourceEnergyPDF.png')
# Spatial distribution of sites

SiteSpatialDistribution = plt.quiver( sp.source['r']['x'], sp.source['r']['y'],
            sp.source['u']['x'], sp.source['u']['y'],
            np.log(sp.source['E']), cmap='jet', scale=20.0)
plt.colorbar()
plt.xlim((-0.5, 0.5))
plt.ylim((-0.5, 0.5))
SiteSpatialDistribution.savefig('SiteSpatialDistribution.png')
# %%
