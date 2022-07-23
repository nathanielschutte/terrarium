
import time, datetime

import pygame

class Program:
    
    DEFAULT_FPS = 60

    DEFAULT_DRAW_MODE = 'clear'

    DEFAULT_BACKGROUND_COLOR = (250, 250, 250)

    DEFAULT_DEBUG = False

    LOG_LEVELS = [
        'debug',
        'info',
        'warning',
        'error',
        'fatal'
    ]

    DEFAULT_LOG_LEVEL = 'info'

    def __init__(self, width, height, options) -> None:
        self.running = True

        self.options = options

        self.start_time = 0
        self.start_time_basic = 0
        self.current_time = 0
        self.current_time_basic = 0
        self.last_frame_time = 0

        self.width = width
        self.height = height

        self.draw_mode = Program.DEFAULT_DRAW_MODE
        
        background = pygame.Surface((width, height))
        self.background = background.convert()
        self.background.fill(Program.DEFAULT_BACKGROUND_COLOR)

        self.expected_frame_time = 1.0 / Program.DEFAULT_FPS

        self.log_level = Program.DEFAULT_LOG_LEVEL

        if 'log' in options and options['log'] in Program.LOG_LEVELS:
            self.log_level = options['log']

        if Program.DEFAULT_DEBUG or ('debug' in options and options['debug'] == 'true'):
            self.log_level = 'debug'
            self._log('Debug mode enabled.', level='debug')
            self._log('Options:', level='debug')

        for opt, value in options.items():
            self._log(f' > {opt}: {value}', level='debug')

        self.time_intervals = {}

        print()

    # Get an option value from the options dictionary
    def _get_opt(self, opt: str, type=str, default=None) -> str:
        if opt not in self.options:
            return default
        value = self.options[opt]
        if isinstance(value, type):
            return value
        if type is int:
            try:
                return int(value)
            except:
                pass
        if type is float:
            try:
                return float(value)
            except:
                pass
        return default

    # Formatted time helper
    def _formatted_time(self) -> str:
        return datetime.datetime.now().strftime('%H:%M:%S')

    # Internal start called before implementation
    def _start(self) -> None:
        self.running = True

        self.start_time = time.perf_counter()
        self.start_time_basic = time.time()
        self.last_frame_time = time.perf_counter()

        self.start()

    # Interval update called before implementation
    def _update(self) -> bool:

        frame_time = time.perf_counter() - self.last_frame_time

        if frame_time < self.expected_frame_time:
            time.sleep(self.expected_frame_time - frame_time)

        self.current_time = time.perf_counter()
        self.current_time_basic = time.time()
        self.last_frame_time = self.current_time

        #print(f'Frame time: {frame_time}')

        return self.running and self.update()

    # Internal draw called before implementation
    def _draw(self, screen) -> bool:

        # Automatically clear the screen before draw
        if self.draw_mode == 'clear':
            screen.blit(self.background, (0, 0))

        return self.running and self.draw(screen)

    # Internal logging
    def _log(self, *args, level=DEFAULT_LOG_LEVEL, source='Program') -> None:
        if level not in Program.LOG_LEVELS:
            level = Program.DEFAULT_LOG_LEVEL
        level_idx = Program.LOG_LEVELS.index(level)
        if level_idx >= Program.LOG_LEVELS.index(self.log_level):
            print(f'{source} {self._formatted_time()} [{level.upper()}] | ', *args)


    # Set a time interval with a name
    def set_interval(self, name: str, interval: float, periodic=True) -> None:
        self.time_intervals[name] = (interval, self.current_time, periodic, 0)

    # Check if a time interval has passed by name. Reset on True
    def check_interval(self, name: str) -> None:
        if name not in self.time_intervals:
            return False
        interval, interval_start, periodic, count = self.time_intervals[name]
        if self.current_time - interval_start >= interval:
            if periodic:
                self.time_intervals[name] = (interval, self.current_time, periodic, count + 1)
            else:
                del self.time_intervals[name]
            return True
        return False

    # Get the number of times an interval has been triggered
    def get_interval_count(self, name: str) -> int:
        if name not in self.time_intervals:
            return None
        _, _, _, count = self.time_intervals[name]
        return count


    # Logging helpers
    def log(self, *args, level=DEFAULT_LOG_LEVEL) -> None:
        self._log(*args, level=level, source=self.__class__.__name__)

    def debug(self, *args) -> None:
        self.log(*args, level='debug')

    def info(self, *args) -> None:
        self.log(*args, level='info')

    def warning(self, *args) -> None:
        self.log(*args, level='warning')

    def error(self, *args) -> None:
        self.log(*args, level='error')
    
    def fatal(self, *args) -> None:
        self.log(*args, level='fatal')
        self.running = False


    # Exposed impletementation functions
    def start(self) -> None:
        pass

    def update(self) -> bool:
        pass
    
    def draw(self, screen) -> bool:
        pass
