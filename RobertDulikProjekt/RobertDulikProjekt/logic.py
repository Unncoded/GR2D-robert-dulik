from collections import namedtuple
from pydoc import text
import pygame
import sys
import enemy
import playerclass
import ctypes.wintypes
from pathlib import Path
import threading
import time

def get_desktop_path():
    # Constant for Desktop
    CSIDL_DESKTOP = 0
    SHGFP_TYPE_CURRENT = 0

    # Prepare buffer
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)

    # Call Windows API
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOP, None, SHGFP_TYPE_CURRENT, buf)

    return Path(buf.value)

def mainloop(screen, runscore):
    clock = pygame.time.Clock()
    #stworz sciany
    if True:
        wallgroup = pygame.sprite.Group()
        wallgroup.add(enemy.wall(-5,-5,1405,20))
        wallgroup.add(enemy.wall(-5,-5,3,240))
        wallgroup.add(enemy.wall(1392,-5,1405,790))
        wallgroup.add(enemy.wall(67,269,70,647))
        wallgroup.add(enemy.wall(720,293,953,307))
        wallgroup.add(enemy.wall(892,360,896,555))
        wallgroup.add(enemy.wall(710,705,825,709))
    #stworz podloge
    if True:
        floorgroup = pygame.sprite.Group()
        floorgroup.add(enemy.floor(0,0,466,220))
        floorgroup.add(enemy.floor(0,0,466,220))
        floorgroup.add(enemy.floor(73,268,231,641))
        floorgroup.add(enemy.floor(215,270,394,400))
        floorgroup.add(enemy.floor(0,0,466,220))
        floorgroup.add(enemy.floor(339,410,481,545))
        floorgroup.add(enemy.floor(427,550,590,700))
        floorgroup.add(enemy.floor(0,0,1400,20))
        floorgroup.add(enemy.floor(960,0,1400,222))
        floorgroup.add(enemy.floor(600,100,846,263))
        floorgroup.add(enemy.floor(710,388,820,700))
        floorgroup.add(enemy.floor(1037,300,1115,370))
        floorgroup.add(enemy.floor(1033,460,1120,510))
        floorgroup.add(enemy.floor(930,590,1395,780))
        floorgroup.add(enemy.floor(1387,225,1400,590))
        floorgroup.add(enemy.floor(720,280,952,315))
        floorgroup.add(enemy.floor(880,360,907,553))
        floorgroup.add(enemy.floor(-300,-300,0,0))
    #inicjowanie absolutnie wszytkiego
    test_font = pygame.font.Font(None, 60)
    final_font = pygame.font.Font(None, 90)
    bg_surface = pygame.image.load('sprites/bg_sprite.png')
    start_ticks = pygame.time.get_ticks()
    swordgroup = pygame.sprite.Group()
    playergroup = pygame.sprite.GroupSingle()
    mainplayer = playerclass.player(swordgroup)
    playergroup.add(mainplayer)
    bulletgroup = pygame.sprite.Group()

    removingbool = 0
    deathcount = 0
    #tworzenie kolejki przeciwnikow    
    enemygroup = pygame.sprite.Group()
    spawnlist = []
    enemygroup.add(enemy.singleshooter(770, 600, bulletgroup))
    spawnlist.extend([enemy.Stats(100, 80, 0, 3, 'single'), enemy.Stats(1081, 490, 0, 8, 'sniper'), enemy.Stats(1310, 90, 0, 13, 'single')])
    spawnlist.extend([enemy.Stats(780, 420, 0, 17, 'auto'), enemy.Stats(110, 645, 0, 17, 'sniper'), enemy.Stats(650, 140, 0, 25, 'single')])
    spawnlist.extend([enemy.Stats(1300, 66, 0, 30, 'auto'), enemy.Stats(130, 300, 0, 30, 'auto'), enemy.Stats(1335, 750, 0, 30, 'auto')])
    spawnlist.extend([enemy.Stats(680, 130, 0, 37, 'single'), enemy.Stats(770, 540, 0, 40, 'sniper')])
    gameover = False
    running = True
    final_deaths = ""
    final_time = ""
    input_text = ""
    custom_orange = (255,121,32)
    #main loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        #sprawdzanie czasu
        elapsed_sec = (pygame.time.get_ticks() - start_ticks) // 1000
        tenths = ((pygame.time.get_ticks() - start_ticks) // 100) % 10
        minutes = elapsed_sec // 60
        seconds = elapsed_sec % 60
        timer_text = f"{minutes:01}:{seconds:02}:{tenths:01}"
        #dodawanie czlowieczkow
        if tenths == 0 and len(spawnlist) > 0:
            for spawn in spawnlist:
                if spawn.spawnmin == minutes and spawn.spawnsec == seconds:
                    if spawn.type == 'auto':
                        enemygroup.add(enemy.autoshooter(spawn.x, spawn.y, bulletgroup))
                    elif spawn.type == 'single':
                        enemygroup.add(enemy.singleshooter(spawn.x, spawn.y, bulletgroup))
                    elif spawn.type == 'sniper':
                        enemygroup.add(enemy.sniper(spawn.x, spawn.y, bulletgroup, wallgroup, screen))
                    removingbool = 1
            if removingbool == 1:
                spawnlist.pop(0)
                removingbool = 0
                
        #rysowanie wszystkiego
        screen.blit(bg_surface,(0,0))
        wallgroup.draw(screen)
        floorgroup.draw(screen)
        swordgroup.update(enemygroup)
        #aktualizacja gracza
        thread_player = threading.Thread(target=mainplayer.update(wallgroup, floorgroup))
        thread_player.start()
        #sprawdza czy stoi na podlodze
        floor_hits = pygame.sprite.spritecollide(mainplayer, floorgroup, False)
        if mainplayer.airtime <= 0 and not floor_hits:
            mainplayer.death()
            deathcount += 1
        playergroup.draw(screen)
        swordgroup.draw(screen)
        #for mans in enemygroup:
        #    enemy.work_the_gun(mans,mainplayer.rect.center, mainplayer.respawning)
        #aktualizacja przeciwnikow
        thread_enemy = threading.Thread(target=enemy.work_all_guns(enemygroup, mainplayer.rect.center, mainplayer.respawning))
        thread_enemy.start()
        thread_bullet = threading.Thread(target=bulletgroup.update(wallgroup))
        thread_bullet.start()
        thread_bullet.join()
        thread_player.join()
        thread_enemy.join()
        bulletgroup.draw(screen)
        #sprawdza czy dostal naboejm
        bullet_hits = pygame.sprite.spritecollide(mainplayer,bulletgroup,False)
        if bullet_hits:
            mainplayer.death()
            deathcount +=1
        enemygroup.draw(screen)
        #wynik
        time_text = test_font.render(timer_text, True, (223, 212, 5))
        deaths_text = test_font.render(str(deathcount), True, (223, 212, 5))
        screen.blit(time_text, (1270, 20))
        screen.blit(deaths_text, (1350, 65))
        pygame.display.update()
        #skonczyli sie przeciwnicy, konczenie gry
        if not spawnlist and not enemygroup:
            running = False
            gameover = True
            final_time = final_font.render(f"TIME: {timer_text}", True, custom_orange)
            runscore.append(timer_text)
            final_deaths = final_font.render(f"{str(deathcount)} DEATHS", True, custom_orange)
            runscore.append(str(deathcount))
        clock.tick(60)
    #ekran po ukonczeniu
    while gameover:
        screen.blit(bg_surface,(0,0))
        wallgroup.draw(screen)
        floorgroup.draw(screen)
        playergroup.draw(screen)
        screen.blit(final_time, (0, 200))
        screen.blit(final_deaths, (1000, 200))
        ask_for_name = final_font.render("INSERT NAME AND PRESS ENTER", True, custom_orange)
        screen.blit(ask_for_name, (40, 350))
        #obsluga wpisywania z klawiatury
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameover = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1] #skasuj ostatni znak
                elif event.key == pygame.K_RETURN:
                    gameover = False #wroc do menu
                    runscore.append(input_text)
                else:
                    input_text += event.unicode #dopisz znak
        input_text = input_text.upper()
        text_surface = final_font.render(input_text, True, custom_orange)
        screen.blit(text_surface,(100, 500))
        pygame.display.update()
