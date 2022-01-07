import openmc
import os
import yaml
import pathlib
from importlib.machinery import SourceFileLoader

FILE_DIRECTORY = str(pathlib.Path(__file__).parent.absolute())
PARENT_DIRECTORY = FILE_DIRECTORY.split('/')[-1]
PROJECT_DIRECTORY = FILE_DIRECTORY.split(PARENT_DIRECTORY)[0]
INPUT_FILE = os.path.join(PARENT_DIRECTORY, "Input.yml")

mymodule = SourceFileLoader('UsefulFunctions', '%s/UsefulFunctions/UsefulFunctions.py'%(PROJECT_DIRECTORY)).load_module()
mymodule.ChangeDirectory()
PROBLEM_DICTIONARY = mymodule.LoadYaml2Dictionary(INPUT_FILE)['Problem']
GEOMETRY_DICIONARY = PROBLEM_DICTIONARY['Geometry']
MATERIAL_DICTIONARY = PROBLEM_DICTIONARY['Material']
SOURCE_DICTIONARY = PROBLEM_DICTIONARY['Source']
SETTINGS_DICTIONARY = PROBLEM_DICTIONARY['Settings']
BC_DICTIONARY = GEOMETRY_DICIONARY['Cell']['BCs']

def Problem(radius):
    nep = openmc.Material(1, MATERIAL_DICTIONARY['Name'])
    nep.add_nuclide(MATERIAL_DICTIONARY['Isotope'], MATERIAL_DICTIONARY['Atom_Fraction'])
    nep.set_density(MATERIAL_DICTIONARY['Density']['Units'], MATERIAL_DICTIONARY['Density']['Value'])

    materials = openmc.Materials()
    materials.append(nep)
    materials.export_to_xml()

    sphere = openmc.Sphere(r=radius, boundary_type = BC_DICTIONARY['BC1']['Type'])

    cell = openmc.Cell(region = -sphere)
    cell.fill = nep

    universe = openmc.Universe()
    universe.add_cell(cell)

    universe = openmc.Universe(cells = [cell])

    geometry = openmc.Geometry(universe)
    geometry.export_to_xml()

    point = openmc.stats.Point((SOURCE_DICTIONARY['Location']['x'], SOURCE_DICTIONARY['Location']['y'], SOURCE_DICTIONARY['Location']['z']))
    source = openmc.Source(space=point)

    settings = openmc.Settings()
    settings.source = source
    settings.batches = SETTINGS_DICTIONARY['Batches']
    settings.inactive = SETTINGS_DICTIONARY['Inactive']
    settings.particles = SETTINGS_DICTIONARY['Particles']
    settings.export_to_xml()

    cell_filter = openmc.CellFilter(cell)

    tally = openmc.Tally(1)
    tally.filters = [cell_filter]

    tally.nuclides = [MATERIAL_DICTIONARY['Isotope']]
    tally.scores = ['total', 'fission', 'absorption']

    tallies = openmc.Tallies([tally])
    tallies.export_to_xml()

    model = openmc.model.Model(geometry, materials, settings)

    return model

crit_ppm, guesses, keffs = openmc.search_for_keff(  Problem, bracket=[1., 100.],
                                                    tol = 1e-3, print_iterations=True)
