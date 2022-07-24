
import pygame

import json, math, random

from .src import program

class ConwayProgram(program.Program):

    FILE_NAME = 'game.grid'

     # Store alive cell indices (for sparse grids)
    EXPORT_MODE = 'positives'

    # Seconds between game rule updates
    DEFAULT_STEP = 0.5

    # Total cell dimension
    GRID_SIZE = 100

    # Pixel width of a cell
    GRID_SCALE = 20

    # Game states
    STATE_RUN = 'run'
    STATE_HOLD = 'hold'

    COLOR_GRIDLINES = (100, 100, 100)
    COLOR_EMPTY = (50, 50, 80)
    COLOR_FILL = (200, 200, 200)

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

        self.grid = [[1 if random.randint(0, 10) == 0 else 0 for _ in range(self.size)] for _ in range(self.size)]
        self.grid_swap = self.grid.copy()

        self.debug(f'Grid size: {len(self.grid)}x{len(self.grid[0])}')

        self.set_background(ConwayProgram.COLOR_EMPTY)

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
        surface = surface.convert()
        surface.fill(ConwayProgram.COLOR_EMPTY)

        # cell count to render horizontally
        cell_render_width = math.floor(screen.get_width() / self.scale)

        # cell count to render vertically
        cell_render_height = math.floor(screen.get_height() / self.scale)

        # cell cutoff
        cell_x_first = math.floor(self.xpan / self.scale)
        cell_y_first = math.floor(self.ypan / self.scale)

        # camera offset
        screen_offset_x = self.xpan % self.scale
        screen_offset_y = self.ypan % self.scale

        # gridlines
        for x in range(cell_render_width):
            pygame.draw.line(
                surface, 
                ConwayProgram.COLOR_GRIDLINES,
                (x * self.scale, 0),
                (x * self.scale, self.height)
            )
        for y in range(cell_render_height):
            pygame.draw.line(
                surface, 
                ConwayProgram.COLOR_GRIDLINES,
                (0, y * self.scale),
                (self.width, y * self.scale)
            )
        
        # cells
        for x, col in enumerate(self.grid[cell_x_first:cell_x_first+cell_render_width]):
            for y, cell in enumerate(col[cell_y_first:cell_y_first+cell_render_height]):
                if cell == 0:
                    continue

                cell_rect = pygame.Rect(
                    x * self.scale + screen_offset_x,
                    y * self.scale + screen_offset_y,
                    self.scale,
                    self.scale
                )

                pygame.draw.rect(surface, ConwayProgram.COLOR_FILL, cell_rect)


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
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                n += self.get_cell(x + i, y + j)

        # Switch cell state based on rules
        if self.grid[x][y] == 1:
            if n in ConwayProgram.GAME_RULES['on']:
                self.grid_swap[x][y] = 0
                return 2
        else:
            if n in ConwayProgram.GAME_RULES['off']:
                self.grid_swap[x][y] = 1
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
            inc = dec = 0
            for x in range(self.size):
                for y in range(self.size):
                    rc = self.update_cell(x, y)
                    if rc == 2:
                        dec += 1
                    elif rc == 1:
                        inc += 1

            # Swap grid
            self.grid = self.grid_swap.copy()

            ratio = 100

            if dec > 0:
                ratio = inc / dec

            self.debug(f'[{self.get_interval_count("step")}] cells born: {inc}, died: {dec}, %{ratio:.2f}')

        # Success
        return True


    def draw(self, screen) -> bool:

        grid_surface = self.get_grid_surface(screen)

        screen.blit(grid_surface, (0, 0))

        # Success
        return True
