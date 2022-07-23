
import sys, os, importlib, inspect, time

import argparse

from programs.src.program import Program

import pygame

dir = 'programs'

def main(argc, argv) -> int:
    parser = argparse.ArgumentParser(description='Graphical python programs.', prog='pygraphics.py')
    parser.add_argument('-p', '--program', help='The program to run.', required=True, type=str)
    parser.add_argument('-t', '--title', help='The title of the window.', type=str, default='window', required=False)
    parser.add_argument('-w', '--width', help='The width of the window.', type=int, default=800)
    parser.add_argument('-l', '--height', help='The height of the window.', type=int, default=600)
    parser.add_argument('-o', '--options', help='The option to pass to the program.', type=str, nargs='+')

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

    screen = create_window(window_title, window_width, window_height)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    screen.blit(background, (0, 0))
    pygame.display.flip()

    prog_obj = program_class(program_options)
    running = True

    while(running):
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            screen.blit(background, (0, 0))

            prog_obj.update()
            prog_obj.draw(screen)

            pygame.display.flip()

        except KeyboardInterrupt:
            print('Keyboard interrupt, exiting.')
            running = False
            return 1
        except Exception as e:
            print(f'Encountered an uncaught {type(e).__name__}: {e}.')
            running = False
            return 1

def check_for_program(program: str) -> bool:
    program_file = os.path.join(dir, program + '.py')
    program_module_path = os.path.dirname(program_file) + '.' + program
    if not os.path.isfile(program_file):
        return False

    try:
        mod = importlib.import_module(program_module_path)
        class_members = inspect.getmembers(mod, inspect.isclass)
        for class_name, class_obj in class_members:
            if issubclass(class_obj, Program):
                return class_obj

        print(f'Could not find class of type {Program.__name__} in {program_file}.')
        
        return False
    except ImportError as e:
        print(f'Could not import {program_file}: {e}.')
        
        return False

def create_window(title: str, width: int, height: int) -> None:
    pygame.init()

    screen = pygame.display.set_mode((width, height))

    pygame.display.set_caption(title)

    return screen
