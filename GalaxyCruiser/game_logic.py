from __future__ import division
import pygame
import random
from os import path
from constant import *
from init import *


# global vars
running = True
menu_display = True
paused = False

high_score_list = [0, 0, 0, 0, 0]
#



def main_menu():
    global screen

    while True:
        title = pygame.image.load(path.join(img_dir, "main.png")).convert()
        title = pygame.transform.scale(title, (WIDTH, HEIGHT), screen)

        #
        play_btn = pygame.image.load(path.join(img_dir, "main_play.png")).convert()
        play_btn_rect = play_btn.get_rect()
        play_btn_rect.midtop = (WIDTH/2, HEIGHT/2.6)
        screen.blit(play_btn, play_btn_rect)

        hs_btn = pygame.image.load(path.join(img_dir, "main_hs.png")).convert()
        hs_btn_rect = hs_btn.get_rect()
        hs_btn_rect.midtop = (WIDTH/2, HEIGHT/2.0)
        screen.blit(hs_btn, hs_btn_rect)

        exit_btn = pygame.image.load(path.join(img_dir, "main_exit.png")).convert()
        exit_btn_rect = exit_btn.get_rect()
        exit_btn_rect.midtop = (WIDTH/2, HEIGHT/1.63)
        screen.blit(exit_btn, exit_btn_rect)
        #

        screen.blit(title, (0,0))
        
        pygame.display.update()

        ev = pygame.event.poll()

        if ev.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = ev.pos
            if play_btn_rect.collidepoint(mouse_pos):
                break
            if hs_btn_rect.collidepoint(mouse_pos):
                high_score()
            if exit_btn_rect.collidepoint(mouse_pos):
                pygame.quit()
                quit()

        elif ev.type == pygame.QUIT:
            pygame.quit()
            quit()

        else:
            pygame.display.update()

    
    screen.fill((0,0,0))
    draw_text(screen, "GET READY!", 40, WIDTH/2, HEIGHT/2)
    pygame.display.update()


def high_score():
    hs = pygame.image.load(path.join(img_dir, "hs.png")).convert()
    hs = pygame.transform.scale(hs, (WIDTH, HEIGHT), screen)
    screen.blit(hs, (0, 0))

    menu_btn = pygame.image.load(path.join(img_dir, "main_menu.png")).convert()
    menu_btn_rect = menu_btn.get_rect()
    menu_btn_rect.midtop = (WIDTH/2, (HEIGHT/2)+100)
    screen.blit(menu_btn, menu_btn_rect)

    draw_text(screen, f"1. {high_score_list[0]}", 30, WIDTH/2, (HEIGHT/2)-120)
    draw_text(screen, f"2. {high_score_list[1]}", 30, WIDTH/2, (HEIGHT/2)-80)
    draw_text(screen, f"3. {high_score_list[2]}", 30, WIDTH/2, (HEIGHT/2)-40)
    draw_text(screen, f"4. {high_score_list[3]}", 30, WIDTH/2, (HEIGHT/2))
    draw_text(screen, f"5. {high_score_list[4]}", 30, WIDTH/2, (HEIGHT/2)+40)
    
    pygame.display.update()

    while True:
        ev = pygame.event.poll()

        if ev.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = ev.pos
            if menu_btn_rect.collidepoint(mouse_pos):
                break

        elif ev.type == pygame.QUIT:
            pygame.quit()
            quit()

        else:
            pygame.display.update()


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)       
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0 
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect= img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def newmob():
    mob_element = Mob()
    all_sprites.add(mob_element)
    mobs.add(mob_element)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0 
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        # time out for powerups
        if self.power >=2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # unhide 
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 30

        self.speedx = 0     # makes the player static in the screen by default. 
        # then we have to check whether there is an event for the arrow keys being 
        # pressed 

        
        keystate = pygame.key.get_pressed()     
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5

     
        if keystate[pygame.K_SPACE]:
            self.shoot()

        
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        self.rect.x += self.speedx

    def shoot(self):
        # to tell the bullet where to spawn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)

            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top) # Missile shoots from center of ship
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


# defines the enemies
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width *.90 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(5, 20)        # for randomizing the speed of the Mob

        # randomize the movements
        self.speedx = random.randrange(-3, 3)

        # adding rotation to the mob element
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()  # time when the rotation has to happen
        
    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50: 
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360 
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        #if the mob element goes out of the screen

        if (self.rect.top > HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > WIDTH + 20):
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)        # for randomizing the speed of the Mob

# defines the sprite for Powerups
class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # place the bullet according to the current position of the player
        self.rect.center = center
        self.speedy = 2

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        # kill the sprite after it moves over the top border
        if self.rect.top > HEIGHT:
            self.kill()

            

# defines the sprite for bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # place the bullet according to the current position of the player
        self.rect.bottom = y 
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        # kill the sprite after it moves over the top border
        if self.rect.bottom < 0:
            self.kill()


# fire missiles
class Missile(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


def set_vars():
    global all_sprites, player, mobs, bullets, powerups, score

    all_sprites = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    mobs = pygame.sprite.Group()
    for i in range(8):      # 8 mobs
        newmob()

    bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    score = 0


def game():
    global running, menu_display, paused, all_sprites, player, mobs, bullets, powerups, score
    while running:
        if menu_display:
            main_menu()
            pygame.time.wait(3000)
            set_vars()
            menu_display = False


        # Process input/events
        clock.tick(FPS)     # will make the loop run at the same speed all the time
        for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
            # listening for the the X button at the top right
            if event.type == pygame.QUIT:
                running = False

            # listening for the the p key to pause/unpause
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if paused:
                        paused = False
                    else:
                        paused = True

        if paused:
            draw_text(screen, "PAUSE", 40, WIDTH/2, HEIGHT/2)
            pygame.display.update()
            continue    

        #2 Update
        all_sprites.update()


        # check if a bullet hit a mob
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        
        for hit in hits:
            score += int(100/hit.radius)        
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.9:
                pow = Powerup(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
            newmob()        # spawn a new mob
            

        # check if the player collides with the mob
        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)        # gives back a list, True makes the mob element disappear
        for hit in hits:
            player.shield -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            newmob()
            if player.shield <= 0: 
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                
                player.hide()
                player.lives -= 1
                player.shield = 100

        # if the player hit a power up
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                player.shield += random.randrange(10, 30)
                if player.shield >= 100:
                    player.shield = 100
            if hit.type == 'gun':
                player.powerup()

        # if player died and the explosion has finished
        if player.lives == 0 and not death_explosion.alive():
            screen.fill((0,0,0))
            draw_text(screen, "GAME OVER!", 40, WIDTH/2, HEIGHT/2)
            draw_text(screen, f"score: {score}", 40, WIDTH/2, (HEIGHT/2)+40)
            if score < high_score_list[2]:
                pass
            else:
                high_score_list.append(score)
                high_score_list.sort(reverse=True)
                high_score_list.pop()

            menu_display = True
            pygame.display.update()
            pygame.time.wait(3000)


        # Draw
        screen.fill(BLACK)
        screen.blit(background, background_rect)

        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)     
        draw_shield_bar(screen, 5, 5, player.shield)

        draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)

        pygame.display.flip()