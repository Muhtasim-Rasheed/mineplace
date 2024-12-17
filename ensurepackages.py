def ensurepackages():
    try:
        import pygame
        import opensimplex
        import PIL
    except ImportError or ModuleNotFoundError:
        import os
        os.system('pip install pygame')
        os.system('pip install opensimplex')
        os.system('pip install pillow')
