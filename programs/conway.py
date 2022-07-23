
import pygame

import json

from .src import program

class ConwayProgram(program.Program):

    FILE_NAME = 'game.grid'

     # Store alive cell indices (for sparse grids)
    EXPORT_MODE = 'positives'

    # Seconds between game rule updates
    DEFAULT_STEP = 1

    # Total cell dimension
    GRID_SIZE = 100

    # Pixel width of a cell
    GRID_SCALE = 10

    # Game states
    STATE_RUN = 'run'
    STATE_HOLD = 'hold'

    # Conway's Game of Life rules
    # Neighbor counts that will trigger a switch
    GAME_RULES = {
        'on':  [0, 1, 4, 5, 6, 7, 8],
        'off': [3]
    }
    
    def __init__(self, width, height, options) -> None:
        super().__init__(width, height, options)

        self.scale = ConwayProgram.GRID_SCALE

        self.step = self._get_opt('step', float, default=ConwayProgram.DEFAULT_STEP)
        self.interval = self.set_interval('step', self.step, periodic=True)

        self.size = self._get_opt('size', int, default=ConwayProgram.GRID_SIZE)

        self.state = ConwayProgram.STATE_HOLD

        #self.xpan = (self.size / 2) * self.scale
        #self.ypan = (self.size / 2) * self.scale

        self.xpan = 0
        self.ypan = 0

        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
    
        self.debug(f'Grid size: {len(self.grid)}x{len(self.grid[0])}')

        # Load grid from file
        if self._get_opt('file', str, default=None) is not None:
            self.info(f'Importing grid from file: {self._get_opt("file")}')
            try:
                self.import_grid(self._get_opt('file'))
            except Exception as e:
                self.error(f'Error importing grid: {e}')


    def export_grid(self, file) -> None:
        if ConwayProgram.EXPORT_MODE == 'positives':
            positives = []
            for x, col in enumerate(self.grid):
                for y, cell in enumerate(col):
                    if cell == 1:
                        positives.append((x, y))
            with open(file, 'w') as f:
                f.write(json.dumps(positives))
        else:
            self.error('Cannot export grid in mode: ' + ConwayProgram.EXPORT_MODE)


    def import_grid(self, file) -> None:
        if ConwayProgram.EXPORT_MODE == 'positives':
            with open(file, 'r') as f:
                data = json.loads(f.read())
                if not isinstance(data, list):
                    self.error('Invalid grid data for import mode: ' + ConwayProgram.EXPORT_MODE)
                for x, y in data:
                    self.grid[x][y] = 1
        else:
            self.error('Cannot import grid in mode: ' + ConwayProgram.EXPORT_MODE)


    def get_grid_surface(self, screen) -> pygame.Surface:
        surface = pygame.Surface((screen.get_width(), screen.get_height()))

        # cell count to render horizontally
        cell_render_width = screen.get_width() / self.scale

        # cell count to render vertically
        cell_render_height = screen.get_height() / self.scale



        return surface

    def get_cell(self, x, y):
        if x >= self.size or x < 0 or y >= self.size or y < 0:
            return 0
        return self.grid[x][y]


    def update_cell(self, x, y) -> None:
        if x >= self.size or x < 0 or y >= self.size or y < 0:
            self.warning(f'Cell out of bounds: {x}, {y} in [{self.size}x{self.size}]')
        
        # Count cell neighboors
        n = 0
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if i == 0 and j == 0:
                    continue
                n += self.get_cell(x + i, y + j)

        # Switch cell state based on rules
        if self.grid[x][y] == 1:
            if n in ConwayProgram.GAME_RULES['on']:
                self.grid[x][y] = 0
                return 1
        else:
            if n in ConwayProgram.GAME_RULES['off']:
                self.grid[x][y] = 1
                return 1

        # No update
        return 0


    def start(self) -> None:

        self.state = ConwayProgram.STATE_RUN


    def update(self) -> bool:

        if self.state == ConwayProgram.STATE_HOLD:
            return True

        # Time to update the grid
        if self.check_interval('step'):

            # Update all cells and count how many were switched
            updates = 0
            for x in range(self.size):
                for y in range(self.size):
                    updates += self.update_cell(x, y)

            self.debug(f'[{self.get_interval_count("step")}] cells updated: {updates}')

        # Success
        return True


    def draw(self, screen) -> bool:

        grid_surface = self.get_grid_surface(screen)

        screen.blit(grid_surface, (0, 0))

        # Success
        return True
