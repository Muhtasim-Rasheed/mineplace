def ensurepackages():
    try:
        import pygame
        import opensimplex
    except ImportError:
        import os
        os.system('pip install pygame')
        os.system('pip install opensimplex')
