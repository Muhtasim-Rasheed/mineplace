import ensurepackages
ensurepackages.ensurepackages()

import ensureappdir
ensureappdir.ensureappdir()

import pygame
import sys, os
import time
import json

import utils

import titlescr
import seedscr
import savescr
import worldsscr
import creditsscr
import keybindsscr
import settingsscr

import renderer

GAME_BLOCK_SCALE = 24
GAME_WIDTH, GAME_HEIGHT = GAME_BLOCK_SCALE * 64, GAME_BLOCK_SCALE * 32
KEYBINDS = keybindsscr.KEYBINDS

def turn_alphanumeric_to_int(string):
    return sum(ord(char) for char in string)

def main():
    pygame.init()
    screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Mineplace")

    utils.SoundManager.checkmixer_online()
    settings_file = ""
    if os.name == "nt":
        settings_file = os.getenv("APPDATA")
    else:
        settings_file = os.path.expanduser("~")
    settings_file = os.path.join(settings_file, "mineplace", "settings.json")
    if not os.path.exists(settings_file):
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, "w") as f:
            f.write(json.dumps({
                "volume": 100,
                "panorama_blur": 8
            }))
    else:
        with open(settings_file) as f:
            settings = json.loads(f.read())
            utils.SettingsManager.apply_settings(settings)
    
    titlescreen = titlescr.TitleScreen(screen)
    option = titlescreen.run()

    if option == "exit":
        sys.exit()
    if option == "settings":
        settingsscreen = settingsscr.SettingsScreen(screen)
        settingsscreen.run()
        main()
    if option == "credits":
        creditsscreen = creditsscr.CreditsScreen(screen)
        creditsscreen.run()
        main()
    if option == "keybinds":
        keybindsscreen = keybindsscr.KeybindsScreen(screen)
        keybindsscreen.run()
        main()
    if option == "load":
        worldsscreen = worldsscr.WorldsScreen(screen)
        worldname = worldsscreen.run()
        if worldname == "exit":
            main()
        data = utils.WorldManager.load_world(worldname)
        world = data["world"]
        renderworld = []
        for y in range(len(world)):
            row = []
            for x in range(len(world[y])):
                row.append(world[y][x].copy())
            renderworld.append(row)
        r = renderer.Renderer(screen, GAME_WIDTH // GAME_BLOCK_SCALE, GAME_HEIGHT // GAME_BLOCK_SCALE, GAME_BLOCK_SCALE)
        spawn = utils.Player.find_best_spawn(world)
        player = utils.Player(spawn[0], spawn[1])
        tick = 0
        isNight = False
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == KEYBINDS.close_menus):
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == KEYBINDS.prt_sc:
                        folder_to_save = ""
                        if os.name == "nt":
                            folder_to_save = os.getenv("APPDATA")
                        else:
                            folder_to_save = os.path.expanduser("~")
                        folder_to_save = os.path.join(folder_to_save, "mineplace", "screenshots")

                        if not os.path.exists(folder_to_save):
                            os.makedirs(folder_to_save)
                        
                        date = time.strftime("%Y-%m-%d")
                        _time = time.strftime("%H-%M-%S")

                        pygame.image.save(screen, f"{folder_to_save}/screenshot_{date}_{_time}_{tick}.png")
                    if event.key == pygame.K_F3:
                        added_up = [player.pos[0] + player.blockselector[0], player.pos[1] + player.blockselector[1]]
                        print(f"Block: {world[added_up[1]][added_up[0]]}")
                        print(f"BlockSel pos: {added_up}")

                player.keydown(world, event, tick)

            keys = pygame.key.get_pressed()    
            player.keypress(world, keys, tick)
            
            r.render(renderworld, player, isNight)
            pygame.display.flip()

            world = utils.update_world(world, tick)
            renderworld = []
            for y in range(len(world)):
                row = []
                for x in range(len(world[y])):
                    row.append(world[y][x].copy())
                renderworld.append(row)

            if tick % (60 * 60 * 10) == 0:
                if tick != 0:
                    isNight = not isNight

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
        if seed == "flat":
            world = utils.FlatWorldGenerator(GAME_WIDTH // GAME_BLOCK_SCALE, GAME_HEIGHT // GAME_BLOCK_SCALE)
            world = world.generate()
        renderworld = []
        for y in range(len(world)):
            row = []
            for x in range(len(world[y])):
                row.append(world[y][x].copy())
            renderworld.append(row)
        r = renderer.Renderer(screen, GAME_WIDTH // GAME_BLOCK_SCALE, GAME_HEIGHT // GAME_BLOCK_SCALE, GAME_BLOCK_SCALE)
        spawn = utils.Player.find_best_spawn(world)
        player = utils.Player(spawn[0], spawn[1])
        tick = 0
        isNight = False
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == KEYBINDS.close_menus):
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == KEYBINDS.prt_sc:
                        folder_to_save = ""
                        if os.name == "nt":
                            folder_to_save = os.getenv("APPDATA")
                        else:
                            folder_to_save = os.path.expanduser("~")
                        folder_to_save = os.path.join(folder_to_save, "mineplace", "screenshots")

                        if not os.path.exists(folder_to_save):
                            os.makedirs(folder_to_save)
                        
                        date = time.strftime("%Y-%m-%d")
                        _time = time.strftime("%H-%M-%S")

                        pygame.image.save(screen, f"{folder_to_save}/screenshot_{date}_{_time}_{tick}.png")

                
                player.keydown(world, event, tick)

            keys = pygame.key.get_pressed()    
            player.keypress(world, keys, tick)
            
            r.render(renderworld, player, isNight)
            pygame.display.flip()

            world = utils.update_world(world, tick)
            renderworld = []
            for y in range(len(world)):
                row = []
                for x in range(len(world[y])):
                    row.append(world[y][x].copy())
                renderworld.append(row)

            if tick % ( 60 * 60 * 10 ) == 0:
                if tick != 0:
                    isNight = not isNight

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
