import pygame
import sys
import enemy
import threading

class sword(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, dur):
        super().__init__()
        if dur > 4:
            self.origin_image = pygame.image.load('sprites/sword_stage_1.png')
        elif dur > 2:
            self.origin_image = pygame.image.load('sprites/sword_stage_2.png')
        else:
            self.origin_image = pygame.image.load('sprites/sword_stage_3.png')
        self.image = pygame.transform.rotate(self.origin_image, angle)
        self.rect = self.image.get_rect(center = (x,y))
        self.duration = 2

    def update(self, enemygroup):
        swordhits = pygame.sprite.spritecollide(self, enemygroup, dokill = True)
        self.duration -= 1
        if self.duration <= 0:
            self.kill()


class player(pygame.sprite.Sprite):
    def __init__(self, swordgroup):
        super().__init__()
        self.image = pygame.image.load('sprites/player_sprite.png')
        self.origin_image = self.image
        self.rect = self.image.get_rect(topleft = (150,100))
        self.sword_CD = 0 #w taktach, max 24
        self.sword_dur = 0 #w taktach, max 6
        self.swordmod = 'right'
        self.sword_group = swordgroup
        self.swinging = 0 #taki bool
        self.safe_pos = self.rect.center
        self.centerpos = self.rect.center
        self.angle = 180
        self.airtime = 0 #w taktach, max 106
        self.respawning = 0

    #logika gracza
    def update(self, walls, floors):
        #odradzanie sie
        if self.respawning > 1:
            self.rect.center = (-200, -200)
            self.airtime = 25
            self.respawning -= 1
        elif self.respawning == 1:
            self.rect.center = (388, 170)
            self.angle = 180
            self.respawning = 0
            self.airtime = 5
        self.InputCheck(floors)
        self.wall_collision(walls)
        #obracanie postaci
        if self.airtime > 0:
            self.origin_image = pygame.image.load('sprites/player_sprite_flying.png')
        elif self.airtime <= 0:
            self.origin_image = pygame.image.load('sprites/player_sprite.png')
        self.image = pygame.transform.rotate(self.origin_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        #ubieg czasu
        if self.airtime > 0:
            self.airtime -= 1
        if self.sword_CD > 0:
            self.sword_CD -= 1
        if self.sword_dur > 0 and self.swinging == 1:
            self.handlesword(self.swordmod)
            self.sword_dur -= 1
        if self.sword_dur <= 0 and self.swinging == 1:
            self.swinging = 0

    def death(self):
        self.rect.center = (-200,-200)
        self.safe_pos = self.rect.center
        self.respawning = 90

    #sprawdza klawiature i wykonuje czynnosci
    def InputCheck(self,floors):
        keys = pygame.key.get_pressed()
        #bez sensu IFy zeby visual zwijal caly blok
        if(True):
            if keys[pygame.K_a]: #lewo
                self.rect.centerx -= 8
                self.angle = 90
            if keys[pygame.K_d]: #prawo
                self.rect.centerx += 8
                self.angle = 270
            if keys[pygame.K_s]: #dol
                self.rect.centery += 8
                self.angle = 180
            if keys[pygame.K_w]: #gora
                self.rect.centery -= 8
                self.angle = 0
            if keys[pygame.K_a] and keys[pygame.K_w]: #lewy gorny
                self.angle = 45
            elif keys[pygame.K_a] and keys[pygame.K_s]: #lewy dolny
                self.angle = 135
            elif keys[pygame.K_d] and keys[pygame.K_w]: #prawy gorny
                self.angle = 315
            elif keys[pygame.K_d] and keys[pygame.K_s]: #prawy dolny
                self.angle = 225
            if self.airtime <= 0 and keys[pygame.K_SPACE]: #mozna skoczyc
                self.airtime = 25
            floor_hits = pygame.sprite.spritecollide(self, floors, False)
            if keys[pygame.K_SPACE] and floor_hits:
                self.airtime = 50
        if(self.sword_CD <= 0):  #mozna uzyc miecza
            if keys[pygame.K_RIGHT]:
                self.handlesword('right')
            elif keys[pygame.K_LEFT]:
                self.handlesword('left')
            elif keys[pygame.K_UP]:
                self.handlesword('up')
            elif keys[pygame.K_DOWN]:
                self.handlesword('down')
            if keys[pygame.K_RIGHT] and keys[pygame.K_UP]:
                self.handlesword('rightup')
            elif keys[pygame.K_RIGHT] and keys[pygame.K_DOWN]:
                self.handlesword('rightdown')
            elif keys[pygame.K_LEFT] and keys[pygame.K_UP]:
                self.handlesword('leftup')
            elif keys[pygame.K_LEFT] and keys[pygame.K_DOWN]:
                self.handlesword('leftdown')

    #obsluga miecza
    def handlesword(self, local_sword_mod):
        if self.sword_CD <= 0:
            self.sword_CD = 24
            self.sword_dur = 6
        self.swinging = 1
        swordhit = sword((self.rect.centerx + 70), self.rect.centery, 270, self.sword_dur)
        if local_sword_mod == 'right':
            swordhit = sword((self.rect.centerx + 70), self.rect.centery, 270, self.sword_dur)
        elif local_sword_mod == 'left':
            swordhit = sword((self.rect.centerx - 70), self.rect.centery, 90, self.sword_dur)
        elif local_sword_mod == 'up':
            swordhit = sword(self.rect.centerx, (self.rect.centery - 80), 0, self.sword_dur)
        elif local_sword_mod == 'down':
            swordhit = sword(self.rect.centerx, (self.rect.centery + 80), 180, self.sword_dur)
        elif local_sword_mod == 'rightup':
            swordhit = sword((self.rect.centerx + 70), (self.rect.centery - 80), 315, self.sword_dur)
        elif local_sword_mod == 'rightdown':
            swordhit = sword((self.rect.centerx + 70), (self.rect.centery + 80), 225, self.sword_dur)
        elif local_sword_mod == 'leftup':
            swordhit = sword((self.rect.centerx - 70), (self.rect.centery - 80), 45, self.sword_dur)
        elif local_sword_mod == 'leftdown':
            swordhit = sword((self.rect.centerx - 70), (self.rect.centery + 80), 135, self.sword_dur)
        self.sword_group.add(swordhit)
        self.swordmod = local_sword_mod

    #kolizje ze scianami
    def wall_collision(self, walls):
        self.image = pygame.transform.rotate(self.origin_image, 0)
        self.rect = self.image.get_rect(center=self.rect.center)
        wall_hits = pygame.sprite.spritecollide(self, walls, False)
        self_y = self.rect.centery #zachowaj y
        if not wall_hits:
            self.safe_pos = self.rect.center
        else:
            self.rect.center = self.safe_pos
        self.image = pygame.transform.rotate(self.origin_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)