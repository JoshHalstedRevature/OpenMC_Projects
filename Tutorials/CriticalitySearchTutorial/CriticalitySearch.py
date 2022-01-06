import matplotlib.pyplot as plt
import numpy as numpy
import os
import openmc
import openmc.model

# Create the mode. 'ppm_Boron' will be the parametric variable.

CURRENT_DIRECTORY = os.getcwd()
print(CURRENT_DIRECTORY)
try:
    os.chdir("%s/Tutorials/CriticalitySearchTutorial"%(CURRENT_DIRECTORY))
except FileNotFoundError:
    os.system("pwd")

def build_model(ppm_Boron):


    # Create the pin materials
    fuel = openmc.Material(name = '1.6% Fuel')
    fuel.set_density('g/cm3', 10.31341)
    fuel.add_element('U', 1., enrichment=1.6)
    fuel.add_element('O', 2.)

    zircaloy = openmc.Material(name = 'Zircaloy')
    zircaloy.set_density('g/cm3', 6.55)
    zircaloy.add_element('Zr', 1.)

    water = openmc.Material(name = 'Borated Water')
    water.set_density('g/cm3', 0.741)
    water.add_element('H', 2.)
    water.add_element('O', 1.)

    # Includethe amount of boron in the water based on the ppm,
    # neglecting the other constituents of boric acid
    water.add_element('B', ppm_Boron * 1e-6)

    # Instantiate a Materials object
    materials = openmc.Materials([fuel, zircaloy, water])

    # Create cylinders for the fuel and clad
    fuel_outer_radius = openmc.ZCylinder(r=0.39218)
    clad_outer_radius = openmc.ZCylinder(r=0.45720)

    # Create boundary planes to surround the geometry
    min_x = openmc.XPlane(x0=-0.63, boundary_type='reflective')
    max_x = openmc.XPlane(x0=+0.63, boundary_type='reflective')
    min_y = openmc.YPlane(y0=-0.63, boundary_type='reflective')
    max_y = openmc.YPlane(y0=+0.63, boundary_type='reflective')

    # Create fuel cell
    fuel_cell = openmc.Cell(name='1.6% Fuel')
    fuel_cell.fill = fuel
    fuel_cell.region = -fuel_outer_radius

    # Create a clad cell
    clad_cell = openmc.Cell(name='1.6% Clad')
    clad_cell.fill = zircaloy
    clad_cell.region = +fuel_outer_radius & -clad_outer_radius

    # Create a moderator cell
    moderator_cell = openmc.Cell(name='1.6% Moderator')
    moderator_cell.fill = water
    moderator_cell.region = +clad_outer_radius & (+min_x & -max_x & +min_y & -max_y)

    # Create root Universe
    root_universe = openmc.Universe(name = 'root universe')
    root_universe.add_cells([fuel_cell, clad_cell, moderator_cell])

    # Create geometry and set root universe
    geometry = openmc.Geometry(root_universe)

    # Instantiate a settings object
    settings = openmc.Settings()

    # Set simulation parameters
    settings.batches = 300
    settings.inactive = 20
    settings.particles = 1000

    # Create an initial uniform spatial source distribution over fissionable zones
    bounds = [-0.63, -0.63, -10, 0.63, 0.63, 10.]
    uniform_dist = openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True)
    settings.source = openmc.source.Source(space=uniform_dist)

    # We don't need a tallies file so don't waste the disk input/output time
    settings.output = {'tallies': False}

    model = openmc.model.Model(geometry, materials, settings)

    return model

# Perform the search
crit_ppm, guesses, keffs = openmc.search_for_keff(  build_model, bracket=[1000., 2500.],
                                                    tol = 1e-2, print_iterations=True)

plt.figure(figsize=(8, 4.5))
plt.title('Eigenvalue versus Boron Concentration')
# Create a scatter plot using the mean value of keff
plt.scatter(guesses, [keffs[i].nominal_value for i in range(len(keffs))])
plt.xlabel('Boron Concetnration [ppm]')
plt.ylabel('Eigenvalue')
plt.show()