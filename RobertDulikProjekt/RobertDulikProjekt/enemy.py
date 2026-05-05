from typing import Protocol
import pygame
import sys
import math
from collections import namedtuple
from typing import Protocol
import threading 

class wall(pygame.sprite.Sprite):
    def __init__(self, tx, ty, bx, by):
        super().__init__()
        self.image = pygame.Surface((bx-tx, by-ty), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft = (tx,ty))

class floor(pygame.sprite.Sprite):
    def __init__(self, tx, ty, bx, by):
        super().__init__()
        self.image = pygame.Surface((bx-tx, by-ty), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft = (tx,ty))

#naboje
class bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, player_center, speed):
        super().__init__()
        self.origin_image = pygame.image.load('sprites/base_bullet.png')
        self.image = pygame.transform.rotate(self.origin_image, angle)
        self.rect = self.image.get_rect(center = (x,y))
        self.angle_rad = math.radians(angle+90)
        self.vx = (math.cos(self.angle_rad) * speed) / 5
        self.vy = (math.sin(self.angle_rad) * speed * -1) / 5

    #poruszanie sie i kolizje, sprawdzane 5 razy
    def update(self, walls):
        for i in range(5):
            self.rect.centerx += self.vx
            self.rect.centery += self.vy
            if self.rect.centery >= 780 or self.rect.centery <= 0:
                self.kill()
            if self.rect.centerx >= 1400 or self.rect.centerx <= 0:
                self.kill()
            wall_hits = pygame.sprite.spritecollide(self, walls, False)
            if wall_hits:
                self.kill()

#struct do umieszczania przeciwnikow
Stats = namedtuple('statblock', ['x', 'y', 'spawnmin', 'spawnsec', 'type'])

#przyklad wykorzystania protocol, odpowiednika <concept>
class enemy(Protocol): 
    def update(self, player_center, respawning):
        a = 1
        a += 1
    def shoot(self, player_center):
        a = 1
#przyklad wykorzystania protocol, odpowiednika <concept>
def work_the_gun(mans: enemy, player_center, respawning): 
    mans.update(player_center, respawning) 

def work_all_guns(enemygroup, player_center, respawning):
    for mans in enemygroup:
        work_the_gun(mans,player_center, respawning)

class autoshooter(pygame.sprite.Sprite):
    def __init__(self, x, y, bulletgroup):
        super().__init__()
        self.image = pygame.image.load('sprites/autoshooter_sprite.png')
        self.origin_image = self.image
        self.rect = self.image.get_rect(center = (x,y))
        self.angle = 0
        self.bulletgroup = bulletgroup
        self.shot_CD = 0 #max 3 klatki
        self.bulletcount = 9
        self.burst_CD = 320 #max 320 klatek, 5 sekund

    #obraca sie wzgledem gracza
    def update(self, player_center, respawning):
        dx = player_center[0] - self.rect.centerx
        dy = player_center[1] - self.rect.centery
        self.angle = ((math.degrees(math.atan2(dy,dx)) * -1) - 90)
        self.image = pygame.transform.rotate(self.origin_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if respawning <= 0:
            self.shoot(player_center)

    def shoot(self, player_center):
        if self.burst_CD > 0: #jeszce nie mozna strzelac
            self.burst_CD -= 1
        else: #mozna strzelac
            if self.bulletcount > 0: #jest czym strzelac
                if self.shot_CD <= 0: #odstep miedzy strzalami
                    boolet = bullet(self.rect.centerx,self.rect.centery,self.angle,player_center, 9)
                    self.bulletgroup.add(boolet)
                    self.shot_CD = 5
                    self.bulletcount -= 1
                else:
                    self.shot_CD -= 1 #oczekiwanie na strzal
            elif self.bulletcount <= 0: #skonczyly sie naboje
                self.burst_CD = 320
                self.origin_image = pygame.image.load('sprites/autoshooter_sprite.png')
                self.bulletcount = 9
        if self.burst_CD <= 200: #zaraz strzeli
            self.origin_image = pygame.image.load('sprites/autoshooter_shooting.png')

class singleshooter(pygame.sprite.Sprite):
    def __init__(self, x, y, bulletgroup):
        super().__init__()
        self.image = pygame.image.load('sprites/singleshooter_sprite.png')
        self.origin_image = self.image
        self.rect = self.image.get_rect(center = (x,y))
        self.angle = 0
        self.bulletgroup = bulletgroup
        self.shot_CD = 150 #max 150 klatek, 2 sekundy

    #obraca sie wzgledem gracza
    def update(self, player_center, respawning):
        dx = player_center[0] - self.rect.centerx
        dy = player_center[1] - self.rect.centery
        self.angle = ((math.degrees(math.atan2(dy,dx)) * -1) - 90)
        self.image = pygame.transform.rotate(self.origin_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if respawning <= 0:
            self.shoot(player_center)

    def shoot(self, player_center):
        if self.shot_CD <= 0: #mozna strzelic
            boolet = bullet(self.rect.centerx,self.rect.centery,self.angle,player_center, 9)
            self.bulletgroup.add(boolet)
            self.shot_CD = 150
            self.origin_image = pygame.image.load('sprites/singleshooter_sprite.png')
        else: #jeszcze nie mozna strzelic
            self.shot_CD -= 1
        if self.shot_CD <= 90: #zaraz strzeli
            self.origin_image = pygame.image.load('sprites/singleshooter_shooting.png')

class sniper(pygame.sprite.Sprite):
    def __init__(self, x, y, bulletgroup, wallgroup, screen):
        super().__init__()
        self.image = pygame.image.load('sprites/sniper_sprite.png')
        self.origin_image = self.image
        self.rect = self.image.get_rect(center = (x,y))
        self.angle = 0
        self.bulletgroup = bulletgroup
        self.shot_CD = 350 #max max 350 klatek, 6 sekund
        self.walls = wallgroup
        self.screen = screen
    #obraca sie wzgledem gracza
    def update(self, player_center, respawning):
        dx = player_center[0] - self.rect.centerx
        dy = player_center[1] - self.rect.centery
        self.angle = ((math.degrees(math.atan2(dy,dx)) * -1) - 90)
        self.image = pygame.transform.rotate(self.origin_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if respawning <= 0:
            self.shoot(player_center)

    def shoot(self, player_center):
        if self.shot_CD <= 0: #mozna strzelic
            boolet = bullet(self.rect.centerx,self.rect.centery,self.angle,player_center, 50)
            self.bulletgroup.add(boolet)
            self.shot_CD = 350
            self.origin_image = pygame.image.load('sprites/sniper_sprite.png')
        else:
            pygame.draw.line(self.screen, (255, 0, 0), self.rect.center, player_center, 4)
            self.shot_CD -= 1 #jeszcze nie mozna strzelac
        if self.shot_CD <= 150:
            self.origin_image = pygame.image.load('sprites/sniper_shooting.png')
