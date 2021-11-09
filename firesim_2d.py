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


def transition_func(grid, neighbourstates, neighbourcounts, decaygrid):

    #Gets burning cells from grid
    buring_cells = (grid == 5)
    #Reduces decay val by 1 for the buring cells
    decaygrid[buring_cells] -= 1
    #Gets all cells that have fully burnt
    decayed_to_zero = (decaygrid == 0)

    #Sets cells that have fully decayed to burnt 
    grid[decayed_to_zero] = 0

    burnt, water, chaparral, canyon, forest, burning = neighbourcounts

    chaparral_to_burn = (burning >= 2) & (grid == 2)
    canyon_to_burn = (burning >= 1) & (grid == 3)
    forest_to_burn = (burning >= 3) & (grid == 4)

    grid[chaparral_to_burn | canyon_to_burn | forest_to_burn] = 5

    grid[decayed_to_zero] = 0



    """
        # dead = state == 0, live = state == 1
        # unpack state counts for state 0 and state 1
        dead_neighbours, live_neighbours = neighbourcounts
        # create boolean arrays for the birth & survival rules
        # if 3 live neighbours and is dead -> cell born
        birth = (live_neighbours == 3) & (grid == 0)
        # if 2 or 3 live neighbours and is alive -> survives
        survive = ((live_neighbours == 2) | (live_neighbours == 3)) & (grid == 1)
        # Set all cells to 0 (dead)
        grid[:, :] = 0
        # Set cells to 1 where either cell is born or survives
        grid[birth | survive] = 1
    """
    
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
    # ------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    # config.state_colors = [(0,0,0),(1,1,1)]
    # config.num_generations = 150

    # ----------------------------------------------------------------------

    if len(args) == 2:
        config.save()
        sys.exit()

    return config


def main():
    # Open the config object
    config = setup(sys.argv[1:])


    decaygrid = np.zeros(config.grid_dims)
    decaygrid.fill(1)

    """
    chaparral_post = (config.initial_grid == 2)
    decaygrid[chaparral_post] = np.random.random_integers(10, 25)
        
    canyon_post = (config.initial_grid == 3)
    decaygrid[canyon_post] = np.random.random_integers(1, 4)
    
    forest_post = (config.initial_grid == 4)
    decaygrid[forest_post] = np.random.random_integers(70, 200)
    """

    chaparral_pos = np.where(config.initial_grid == 2)
    canyon_pos = np.where(config.initial_grid == 3)
    forest_pos = np.where(config.initial_grid == 4)

    x, y = chaparral_pos
    for i in range(len(x)):
        decaygrid[x[i], y[i]] = np.random.randint(10, 25)

    x, y = canyon_pos
    for i in range(len(x)):
        decaygrid[x[i], y[i]] = np.random.randint(1, 4)

    x, y = forest_pos
    for i in range(len(x)):
        decaygrid[x[i], y[i]] = np.random.randint(70, 200)


    # Create grid object
    grid = Grid2D(config, (transition_func, decaygrid))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # save updated config to file
    config.save()
    # save timeline to file
    utils.save(timeline, config.timeline_path)


if __name__ == "__main__":
    main()
