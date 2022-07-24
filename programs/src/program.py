
import time, datetime, os

import pygame

class Program:
    
    # Fixed FPS target
    DEFAULT_FPS = 60

    # Clear the screen before each draw
    DEFAULT_DRAW_MODE = 'clear'

    # Default background color
    DEFAULT_BACKGROUND_COLOR = (250, 250, 250)

    # Enable debug by default
    DEFAULT_DEBUG = False

    # Root directory to store program files
    PROGRAM_FILES_DIR = 'program_files'

    # Log level names
    LOG_LEVELS = [
        'debug',
        'info',
        'warning',
        'error',
        'fatal'
    ]

    # Default log level
    DEFAULT_LOG_LEVEL = 'info'


    # Initialize program
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

        self.files_dir = None

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


    # Set program files path for a program name
    def _set_file_path(self, name) -> None:
        try:
            if not os.path.exists(Program.PROGRAM_FILES_DIR):
                self.debug(f'Creating program files dir: {Program.PROGRAM_FILES_DIR}')
                os.mkdir(Program.PROGRAM_FILES_DIR)
            if not os.path.exists(os.path.join(Program.PROGRAM_FILES_DIR, name)):
                self.debug(f'Creating program files dir for: {name}')
                os.mkdir(os.path.join(Program.PROGRAM_FILES_DIR, name))
        except Exception as e:
            self.fatal(f'Failed to create program files dir: {e}')

        self.files_dir = os.path.join(Program.PROGRAM_FILES_DIR, name)


    # Get program files path to a file
    def get_file_path(self, file) -> str:
        if not os.path.exists(self.files_dir):
            self.fatal(f'Program files dir does not exist: ${self.files_dir}')
            return
        
        if not os.path.isfile(os.path.join(self.files_dir, file)):
            return False

        return os.path.join(self.files_dir, file)


    # Background color
    def set_background(self, color: tuple) -> None:
        self.debug(f'Setting background color to {color}')
        self.background.fill(color)


    # Set a display on/off
    def set_display(self, display: str, enable: bool) -> None:
        pass


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
