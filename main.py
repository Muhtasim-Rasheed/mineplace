import ensurepackages
ensurepackages.ensurepackages()

import ensureappdir
ensureappdir.ensureappdir()

import pygame
import sys, os
import time

import utils

import titlescr
import seedscr
import savescr
import worldsscr

import renderer

GAME_BLOCK_SCALE = 24
GAME_WIDTH, GAME_HEIGHT = GAME_BLOCK_SCALE * 64, GAME_BLOCK_SCALE * 32

def turn_alphanumeric_to_int(string):
    return sum(ord(char) for char in string)

def main():
    pygame.init()
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Mineplace")
    
    titlescreen = titlescr.TitleScreen(screen)
    option = titlescreen.run()

    if option == "exit":
        sys.exit()
    if option == "load":
        worldsscreen = worldsscr.WorldsScreen(screen)
        worldname = worldsscreen.run()
        if worldname == "exit":
            main()
        data = utils.WorldManager.load_world(worldname)
        world = data["world"]
        r = renderer.Renderer(screen, GAME_WIDTH // GAME_BLOCK_SCALE, GAME_HEIGHT // GAME_BLOCK_SCALE, GAME_BLOCK_SCALE)
        spawn = utils.Player.find_best_spawn(world)
        player = utils.Player(spawn[0], spawn[1])
        tick = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_PRINTSCREEN:
                        folder_to_save = ""
                        if os.name == "nt":
                            folder_to_save = os.getenv("APPDATA")
                        else:
                            folder_to_save = os.path.expanduser("~")
                        folder_to_save = os.path.join(folder_to_save, "mineplace", "screenshots")

                        if not os.path.exists(folder_to_save):
                            os.makedirs(folder_to_save)
                        
                        date = time.strftime("%Y-%m-%d")

                        pygame.image.save(screen, f"{folder_to_save}/screenshot_{date}_{tick}.png")

                player.keydown(world, event, tick)

            keys = pygame.key.get_pressed()    
            player.keypress(world, keys, tick)
            
            r.render(world, player)
            pygame.display.flip()

            world = utils.update_world(world)

            tick += 1

        # Save the world! (Not in that way)
        # We already have the world name, so we don't need to ask for it
        utils.WorldManager.save_world(worldname, world)

        main()
    elif option == "new":
        seedscreen = seedscr.SeedScreen(screen)
        seed = seedscreen.run()
        if seed == "exit":
            main()
        world = utils.WorldGenerator(turn_alphanumeric_to_int(seed), GAME_WIDTH // GAME_BLOCK_SCALE, GAME_HEIGHT // GAME_BLOCK_SCALE, scale=0.1)
        world = world.generate()
        r = renderer.Renderer(screen, GAME_WIDTH // GAME_BLOCK_SCALE, GAME_HEIGHT // GAME_BLOCK_SCALE, GAME_BLOCK_SCALE)
        spawn = utils.Player.find_best_spawn(world)
        player = utils.Player(spawn[0], spawn[1])
        tick = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                
                player.keydown(world, event, tick)

            keys = pygame.key.get_pressed()    
            player.keypress(world, keys, tick)
            
            r.render(world, player)
            pygame.display.flip()

            world = utils.update_world(world)

            tick += 1

        # Save the world! (Not in that way)
        savescreen = savescr.SaveScreen(screen)
        name = savescreen.run()
        if name == "exit" or name == "":
            main()

        utils.WorldManager.save_world(name, world)
        main()

    pygame.quit()

if __name__ == "__main__":
    main()
