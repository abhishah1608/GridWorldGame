import pygame
import numpy as np

class GridWorld:
    aisles = {}  # store locations in a dictionary
    # Set the dimensions of the grid
    actions = ['up', 'right', 'down', 'left']
    grid_width, grid_height = 11, 11
    start_row = None
    start_col = None
    isTrained = False
    rewards = np.full((grid_width, grid_height), -100)
    q_values = np.zeros((grid_width, grid_height, 4))
    def __int__(self):
        pygame.init()


    # Set the size of each grid cell
    cell_size = 40



    # Set the window size based on the grid dimensions and cell size
    window_width = cell_size * grid_width
    window_height = cell_size * grid_height

    def draw_text_in_rect(self,text, font, color, rect, window):
        surface = font.render(text, True, color)
        text_rect = surface.get_rect(center=rect.center)
        window.blit(surface, text_rect)

    def addRobot(self, window, image, rect):
        window.blit(image, rect)

    # define a function that determines if the specified location is a terminal state
    def is_terminal_state(self,current_row_index, current_column_index):
        # if the reward for this location is -1, then it is not a terminal state (i.e., it is a 'white square')
        if self.rewards[current_row_index, current_column_index] == -1.:
            return False
        else:
            return True

    def get_starting_location(self):
        # get a random row and column index
        current_row_index = np.random.randint(self.grid_width)
        current_column_index = np.random.randint(self.grid_height)
        # continue choosing random row and column indexes until a non-terminal state is identified
        # (i.e., until the chosen state is a 'white square').
        while self.is_terminal_state(current_row_index, current_column_index):
            current_row_index = np.random.randint(self.grid_width)
            current_column_index = np.random.randint(self.grid_width)
        return current_row_index, current_column_index

    def get_next_action(self,current_row_index, current_column_index, epsilon):
        # if a randomly chosen value between 0 and 1 is less than epsilon,
        # then choose the most promising value from the Q-table for this state.
        if np.random.random() < epsilon:
            return np.argmax(self.q_values[current_row_index, current_column_index])
        else:  # choose a random action
            return np.random.randint(4)

    def get_next_location(self,current_row_index, current_column_index, action_index):
        new_row_index = current_row_index
        new_column_index = current_column_index
        if self.actions[action_index] == 'up' and current_row_index > 0:
            new_row_index -= 1
        elif self.actions[action_index] == 'right' and current_column_index < self.grid_height - 1:
            new_column_index += 1
        elif self.actions[action_index] == 'down' and current_row_index < self.grid_width - 1:
            new_row_index += 1
        elif self.actions[action_index] == 'left' and current_column_index > 0:
            new_column_index -= 1
        return new_row_index, new_column_index

    def get_shortest_path(self,start_row_index, start_column_index):
        # return immediately if this is an invalid starting location
        if self.is_terminal_state(start_row_index, start_column_index):
            return []
        else:  # if this is a 'legal' starting location
            current_row_index, current_column_index = start_row_index, start_column_index
            shortest_path = []
            shortest_path.append([current_row_index, current_column_index])
            # continue moving along the path until we reach the goal (i.e., the item packaging location)
            while not self.is_terminal_state(current_row_index, current_column_index):
                # get the best action to take
                action_index = self.get_next_action(current_row_index, current_column_index, 1.)
                # move to the next location on the path, and add the new location to the list
                current_row_index, current_column_index = self.get_next_location(current_row_index, current_column_index,
                                                                            action_index)
                shortest_path.append([current_row_index, current_column_index])
            return shortest_path

    def train_Grid(self):
        # define training parameters
        epsilon = 0.9  # the percentage of time when we should take the best action (instead of a random action)
        discount_factor = 0.9  # discount factor for future rewards
        learning_rate = 0.9  # the rate at which the AI agent should learn

        # run through 1000 training episodes
        for episode in range(1000):
            # get the starting location for this episode
            row_index, column_index = self.get_starting_location()

            # continue taking actions (i.e., moving) until we reach a terminal state
            # (i.e., until we reach the item packaging area or crash into an item storage location)
            while not self.is_terminal_state(row_index, column_index):
                # choose which action to take (i.e., where to move next)
                action_index = self.get_next_action(row_index, column_index, epsilon)

                # perform the chosen action, and transition to the next state (i.e., move to the next location)
                old_row_index, old_column_index = row_index, column_index  # store the old row and column indexes
                row_index, column_index = self.get_next_location(row_index, column_index, action_index)

                # receive the reward for moving to the new state, and calculate the temporal difference
                reward = self.rewards[row_index, column_index]
                old_q_value = self.q_values[old_row_index, old_column_index, action_index]
                temporal_difference = reward + (
                            discount_factor * np.max(self.q_values[row_index, column_index])) - old_q_value

                # update the Q-value for the previous state and action pair
                new_q_value = old_q_value + (learning_rate * temporal_difference)
                self.q_values[old_row_index, old_column_index, action_index] = new_q_value

        print('Training complete!')
        self.isTrained = True

    def AnimateRobotForPath(self,r,c, window):
        path = self.get_shortest_path(r,c)
        white = (255, 255, 255)
        image = pygame.image.load("images/robot.jpg")

        # Resize the image to fit the cell size
        image = pygame.transform.scale(image, (self.cell_size, self.cell_size))
        for p in path:
            new_row = p[0]
            new_col = p[1]
            rect_position = pygame.draw.rect(window, white,
                                          (new_col * self.cell_size, new_row * self.cell_size, self.cell_size,
                                           self.cell_size))
            self.addRobot(window, image, rect_position)

    # Initialize Pygame
    def drawGrid(self):
        # Create the window
        window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Grid")
        image = pygame.image.load("images/robot.jpg")

        # Resize the image to fit the cell size

        image = pygame.transform.scale(image, (self.cell_size, self.cell_size))

        # Define the colors
        white = (255, 255, 255)
        yellow = (255, 255, 0)
        black = (0, 0, 0)
        green = (0, 255, 0)

        # Function to draw the grid
        def draw_grid():

            pygame.font.init()
            self.aisles[0] = []
            self.aisles[1] = [i for i in range(1, 10)]
            self.aisles[2] = [1, 7, 9]
            self.aisles[3] = [i for i in range(1, 8)]
            self.aisles[3].append(9)
            self.aisles[4] = [3, 7]
            self.aisles[5] = [i for i in range(11)]
            self.aisles[6] = [5]
            self.aisles[7] = [i for i in range(1, 10)]
            self.aisles[8] = [3, 7]
            self.aisles[9] = [i for i in range(11)]
            self.aisles[10] = []
            self.rewards = np.full((self.grid_width, self.grid_height), -100)


            for row in range(self.grid_height):
                for col in range(self.grid_width):
                    # color = white if (row + col) % 2 == 0 else black
                    if(row == 0 and col == 5):
                        color = green
                        # set the reward for the packaging area (i.e., the goal) to 100
                        self.rewards[row, col] = 100
                    elif (col in self.aisles[row]):
                        color = white
                        self.rewards[row, col] = -1
                    else:
                        color = black
                    rect = pygame.draw.rect(window, color, (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size))

                    font = pygame.font.Font(None, 12)

                    # Add text inside the rectangle
                    text ="100" if (color== green) else ("-100" if (color == black) else "-1")
                    self.draw_text_in_rect(text, font, yellow, rect, window)
            if(self.start_row is None):
                self.start_row, self.start_col = self.get_starting_location()
                rect_start = pygame.draw.rect(window, white,
                                        (self.start_col * self.cell_size, self.start_row * self.cell_size, self.cell_size, self.cell_size))
                self.addRobot(window, image, rect_start)
                self.train_Grid()
            else:
                rect_start = pygame.draw.rect(window, white,
                                              (self.start_col * self.cell_size, self.start_row * self.cell_size,
                                               self.cell_size, self.cell_size))
                self.addRobot(window, image, rect_start)
        # Main loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Clear the window
            window.fill(white)

            # Draw the grid
            draw_grid()

            if(self.isTrained == True):
                self.AnimateRobotForPath(self.start_row,self.start_col, window)

            # Update the display
            pygame.display.update()



    def __del__(self):

        # Quit Pygame
        pygame.quit()
