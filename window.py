
import sys, os, importlib, inspect

import argparse

from programs.src.program import Program

import pygame

dir = 'programs'

def main(argc, argv) -> int:
    parser = argparse.ArgumentParser(description='Graphical python programs.', prog='run.py')
    parser.add_argument('-p', '--program', help='The program to run.', required=True, type=str)
    parser.add_argument('-t', '--title', help='The title of the window.', type=str, default='window', required=False)
    parser.add_argument('-w', '--width', help='The width of the window.', type=int, default=800)
    parser.add_argument('-l', '--height', help='The height of the window.', type=int, default=600)
    parser.add_argument('-o', '--options', help='List of options to pass to the program.', type=str, metavar='opt=val', nargs='+')

    args = parser.parse_args(argv[1:])

    window_width = args.width
    window_height = args.height
    window_title = args.title
    program = args.program

    program_options = {}
    if args.options:
        for option in args.options:
            key, value = option.split('=')
            program_options[key] = value

    if window_title == 'window':
        window_title = program.capitalize()

    program_class = check_for_program(program)
    if not program_class:
        print(f'Program not found: {program}.')
        return 1

    print(f'Running {program}...')

    screen = create_window(window_title, window_width, window_height)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    screen.blit(background, (0, 0))
    pygame.display.flip()

    prog_obj = program_class(window_width, window_height, program_options)
    running = True

    # Set the program files path using program name
    prog_obj._set_file_path(program)
    
    # Program startup
    prog_obj._start()

    # Main event loop
    while(running):
        try:

            # pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print(f'Exiting program: {program}')
                    running = False
                    break

            # Update
            update_ok = prog_obj._update()
            if update_ok is not None and not update_ok:
                print(f'Update failed, exiting.')
                running = False
                break

            # Draw
            draw_ok = prog_obj._draw(screen)
            if draw_ok is not None and not draw_ok:
                print(f'Draw failed, exiting.')
                running = False
                break

            # Buffer swap
            pygame.display.flip()

        except KeyboardInterrupt:
            print('Keyboard interrupt received from commandline, exiting.')
            running = False
            return 1
        # except Exception as e:
        #     print(f'Encountered an uncaught {type(e).__name__}: {e}.')
        #     running = False
        #     return 1


# Look for a program in the specified programs directory
def check_for_program(program: str) -> bool:
    program_file = os.path.join(dir, program + '.py')
    program_module_path = os.path.dirname(program_file) + '.' + program
    if not os.path.isfile(program_file):
        return False

    try:
        mod = importlib.import_module(program_module_path)
        class_members = inspect.getmembers(mod, inspect.isclass)
        for _, class_obj in class_members:
            if issubclass(class_obj, Program):
                return class_obj

        print(f'Could not find class of type {Program.__name__} in {program_file}.')
        
        return False
    except ImportError as e:
        print(f'Could not import {program_file}: {e}.')
        
        return False


# Create the pygame window and return the screen surface
def create_window(title: str, width: int, height: int) -> pygame.Surface:
    pygame.init()

    screen = pygame.display.set_mode((width, height))

    pygame.display.set_caption(title)

    return screen
