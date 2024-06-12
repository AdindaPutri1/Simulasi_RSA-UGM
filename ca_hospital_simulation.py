import numpy as np
import matplotlib.pyplot as plt
import random

# Initialize grid
width, height = 20, 20
grid = np.zeros((width, height))

# Define states
EMPTY = 0
WAITING = 1
REGISTERING = 2
REGISTERED = 3

# Initialize patients in waiting state
num_patients = 120
for _ in range(num_patients):
    x, y = random.randint(0, width-1), random.randint(0, height-1)
    grid[x, y] = WAITING

# Define registration desks capacity
desk_capacity = 3

# Function to update the grid
def update_grid(grid, desk_capacity):
    new_grid = grid.copy()
    for x in range(width):
        for y in range(height):
            if grid[x, y] == WAITING:
                if desk_capacity > 0:
                    new_grid[x, y] = REGISTERING
                    desk_capacity -= 1
                else:
                    # Move to a random neighboring cell
                    new_x, new_y = x + random.choice([-1, 0, 1]), y + random.choice([-1, 0, 1])
                    if 0 <= new_x < width and 0 <= new_y < height and grid[new_x, new_y] == EMPTY:
                        new_grid[new_x, new_y] = WAITING
                        new_grid[x, y] = EMPTY
            elif grid[x, y] == REGISTERING:
                new_grid[x, y] = REGISTERED
    return new_grid, desk_capacity

# Run the simulation
timesteps = 240
for _ in range(timesteps):
    grid, desk_capacity = update_grid(grid, desk_capacity)

# Plot the final state
plt.imshow(grid, cmap='viridis')
plt.show()
