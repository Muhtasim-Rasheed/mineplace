def ensurepackages():
    try:
        import pygame
        import opensimplex
        import PIL
    except ImportError:
        import os
        os.system('python3 -m pip install pygame')
        os.system('python3 -m pip install opensimplex')
        os.system('python3 -m pip install pillow')
