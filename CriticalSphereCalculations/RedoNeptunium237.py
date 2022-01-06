import openmc
import os

CURRENT_DIRECTORY = os.getcwd()
print(CURRENT_DIRECTORY)
try:
    os.chdir("%s/Tutorials/PostProcessing"%(CURRENT_DIRECTORY))
except FileNotFoundError:
    os.system("pwd")

def Problem(radius):
    nep = openmc.Material(1, "nep")
    nep.add_nuclide('Np237', 1.0)
    nep.set_density('g/cm3', 20.25)

    materials = openmc.Materials()
    materials.append(nep)
    materials.export_to_xml()

    sphere = openmc.Sphere(r=radius, boundary_type = 'vacuum')

    cell = openmc.Cell(region = -sphere)
    cell.fill = nep

    universe = openmc.Universe()
    universe.add_cell(cell)

    universe = openmc.Universe(cells = [cell])

    geometry = openmc.Geometry(universe)
    geometry.export_to_xml()

    point = openmc.stats.Point((0, 0, 0))
    source = openmc.Source(space=point)

    settings = openmc.Settings()
    settings.source = source
    settings.batches = 500
    settings.inactive = 100
    settings.particles = 5000
    settings.export_to_xml()

    cell_filter = openmc.CellFilter(cell)

    tally = openmc.Tally(1)
    tally.filters = [cell_filter]

    tally.nuclides = ['Np237']
    tally.scores = ['total', 'fission', 'absorption']

    tallies = openmc.Tallies([tally])
    tallies.export_to_xml()

    model = openmc.model.Model(geometry, materials, settings)

    return model

crit_ppm, guesses, keffs = openmc.search_for_keff(  Problem, bracket=[1., 100.],
                                                    tol = 1e-3, print_iterations=True)
