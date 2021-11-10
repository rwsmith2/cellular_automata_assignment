# Name: Fire simulation
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, CAConfig, randomise2d
import capyle.utils as utils
import numpy as np


def transition_func(grid, neighbourstates, neighbourcounts, decaygrid, countgrid):

    #Gets burning cells from grid
    buring_cells = (grid == 5)
    #Reduces decay val by 1 for the buring cells
    decaygrid[buring_cells] -= 1
    #Gets all cells that have fully burnt
    decayed_to_zero = (decaygrid == 0)

    #Sets cells that have fully decayed to burnt 
    grid[decayed_to_zero] = 0

    burning = neighbourcounts[5]

    #Increases countgrid value when next to a burning cell
    next_to_burning = (burning >= 1)
    countgrid[next_to_burning] += 1

    #Finds cells that will burn in next step based on number of buring neighbours
    # and how long its been next to something burning
    chaparral_to_burn = (burning >= 2) & (grid == 2) & (countgrid >= 2)
    canyon_to_burn = (burning >= 1) & (grid == 3)
    forest_to_burn = (burning >= 3) & (grid == 4) & (countgrid >= 4)

    #Sets cells in the grid to burning
    grid[chaparral_to_burn | canyon_to_burn | forest_to_burn] = 5

    grid[decayed_to_zero] = 0

    
    return grid


def setup(args):
    config_path = args[0]
    config = utils.load(config_path)
    # ---THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED---
    config.title = "Fire simulation"
    config.dimensions = 2

    # 0 = burnt
    # 1, 2, 3, 4 = water, chaparral, canyon, forest
    # 5 = burning
    config.states = (0, 1, 2, 3, 4, 5)

    config.state_colors = [(0,0,0), (0.243, 0.686, 0.980), (0.902, 0.725, 0.325), 
                            (0.388, 0.275, 0), (0.114, 0.310, 0.055), (0.820, 0.4007, 0.059)]

    config.grid_dims = (200,200)

    base_grid = np.full(config.grid_dims, 2)
    #Sets initial blocks of different materials in grid
    base_grid[60:80, 30:40] = 1
    base_grid[130:140, 120:180] = 1

    base_grid[20:180, 50:60] = 3

    base_grid[80:160, 40:50] = 4
    base_grid[20:120, 60:80] = 4
    base_grid[100:120, 80:200] = 4

    base_grid[79:81, 19:21] = 5

    config.set_initial_grid(base_grid)

    config.num_generations = 600

    config.wrap = False

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])


    decaygrid = np.zeros(config.grid_dims)
    decaygrid.fill(3)

    #Sets decaygrid values based on what medium that cell is
    chaparral_pos = np.where(config.initial_grid == 2)
    canyon_pos = np.where(config.initial_grid == 3)
    forest_pos = np.where(config.initial_grid == 4)

    x, y = chaparral_pos
    for i in range(len(x)):
        decaygrid[x[i], y[i]] = np.random.randint(10, 25)

    x, y = canyon_pos
    for i in range(len(x)):
        decaygrid[x[i], y[i]] = np.random.randint(2, 5)

    x, y = forest_pos
    for i in range(len(x)):
        decaygrid[x[i], y[i]] = np.random.randint(70, 200)


    countgrid = np.zeros(config.grid_dims)

    # Create grid object
    grid = Grid2D(config, (transition_func, decaygrid, countgrid))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
