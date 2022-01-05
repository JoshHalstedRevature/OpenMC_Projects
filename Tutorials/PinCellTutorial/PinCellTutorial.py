#%%

import openmc
import os

uo2 = openmc.Material(1, "uo2")
uo2.add_nuclide('U235', 0.03)
uo2.add_nuclide('U238', 0.97)
uo2.add_nuclide('O16', 2.0)
uo2.set_density('g/cm3', 10.0)
#print(uo2)

zirconium = openmc.Material(name="zirconium")
zirconium.add_element('Zr',1.0)
zirconium.set_density('g/cm3', 6.6)

water = openmc.Material(name="h2o")
water.add_nuclide('H1', 2.0)
water.add_nuclide('O16', 1.0)
water.set_density('g/cm3', 1.0)
water.add_s_alpha_beta('c_H_in_H2O')

materials = openmc.Materials([uo2, zirconium, water])
materials = openmc.Materials()
materials.append(uo2)
materials += [zirconium, water]

materials.export_to_xml()
export_materials = 'cat materials.xml'
#os.system(export_materials)

sphere = openmc.Sphere(r=1.0)
inside_sphere = -sphere
outside_sphere = +sphere

#print((0,0,0) in inside_sphere, (0,0,2) in inside_sphere)
#print((0,0,0) in outside_sphere, (0,0,2) in outside_sphere)

z_plane = openmc.ZPlane(z0=0)
northern_hemisphere = -sphere & +z_plane
bounding_box = northern_hemisphere.bounding_box

#cell = openmc.Cell()
#cell.region = northern_hemisphere

cell = openmc.Cell(region = northern_hemisphere)

cell.fill = water

universe = openmc.Universe()
universe.add_cell(cell)

universe = openmc.Universe(cells = [cell])

#universe.plot(width = (2.0, 2.0))
#universe.plot(width = (2.0, 2.0), basis ='xz')
#universe.plot(width=(2.0, 2.0), basis = 'xz', colors = {cell: 'fuchsia'})



fuel_outer_radius = openmc.ZCylinder(r=0.39)
clad_inner_radius = openmc.ZCylinder(r=0.40)
clad_outer_radius = openmc.ZCylinder(r=0.46)

fuel_region = -fuel_outer_radius
gap_region = +fuel_outer_radius & -clad_inner_radius
clad_region = +clad_inner_radius & -clad_outer_radius

fuel = openmc.Cell(name='fuel')
fuel.fill = uo2
fuel.region = fuel_region

gap = openmc.Cell(name='air gap')
gap.region = gap_region

clad = openmc.Cell(name = 'clad')
clad.fill = zirconium
clad.region = clad_region

pitch = 1.26
left = openmc.XPlane(x0=-pitch/2, boundary_type = 'reflective')
right = openmc.XPlane(x0=pitch/2, boundary_type = 'reflective')
bottom = openmc.YPlane(y0=-pitch/2, boundary_type = 'reflective')
top = openmc.YPlane(y0=pitch/2, boundary_type = 'reflective')

water_region = +left & -right & +bottom & -top & +clad_outer_radius

moderator = openmc.Cell(name='moderator')
moderator.fill = water
moderator.region = water_region

# or

box = openmc.rectangular_prism(width=pitch, height=pitch, boundary_type='reflective')

#print(type(box))

water_region = box & +clad_outer_radius

root_universe = openmc.Universe(cells=(fuel, gap, clad, moderator))

#geometry = openmc.Geometry()
#geometry.root_universe = root_universe

geometry = openmc.Geometry(root_universe)
geometry.export_to_xml()
#os.system('cat geometry.xml')

point = openmc.stats.Point((0, 0, 0))
source = openmc.Source(space=point)

settings = openmc.Settings()
settings.source = source
settings.batches = 100
settings.inactive = 10
settings.particles = 1000
settings.export_to_xml()
#os.system('cat settings.xml')

cell_filter = openmc.CellFilter(fuel)

tally = openmc.Tally(1)
tally.filters = [cell_filter]

tally.nucldes = ['U235']
tally.scores = ['total', 'fission', 'absorption', '(n,gamma)']

tallies = openmc.Tallies([tally])
tallies.export_to_xml()
#os.system('cat tallies.xml')

#os.system('cat $OPENMC_CROSS_SECTIONS | head -n 10')
#os.system('echo $OPENMC_CROSS_SECTIONS')

openmc.run()

plot = openmc.Plot()
plot.filename = 'pinplot'
plot.width = (pitch, pitch)
plot.pixels = (200, 200)
plot.color_by = 'material'
plot.colors = {uo2: 'yellow', water: 'blue'}
plots = openmc.Plots([plot])
plots.export_to_xml()
os.system("cat plots.xml")
openmc.plot_geometry()

os.system("convert pinplot.ppm pinplot.png")

from IPython.display import Image
Image("pinplot.png")

# %%