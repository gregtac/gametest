import pygame
import os
import random
import csv

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

#framerate
clock = pygame.time.Clock()
FPS = 60

#game var
GRAV = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 6
screen_scroll = 0
bg_scroll = 0
level = 1

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('BrainExe')

#player action
moving_left = False
moving_right = False
mob_moving_left = False
mob_moving_right = False
shoot = False

#load images
veins_img = pygame.image.load('images/background/veins.png').convert_alpha()
vessels_img = pygame.image.load('images/background/vessels.png').convert_alpha()
blood_img = pygame.image.load('images/background/blood.png').convert_alpha()
#stolre tiles in list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'images/tiles/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#bullet
bullet_img1 = pygame.image.load('images/icons/bullet1.png').convert_alpha()
bullet_img2 = pygame.image.load('images/icons/bullet2.png').convert_alpha()
ammo_box_img = pygame.image.load('images/icons/ammo_box.png').convert_alpha()
item_boxes = { 
    'Ammo' : ammo_box_img
    }

#define colors
BG = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    screen.blit(veins_img, (0, 0))
    screen.blit(vessels_img,(0, SCREEN_HEIGHT - vessels_img.get_height() - 350))
    screen.blit(blood_img, (0, SCREEN_HEIGHT - blood_img.get_height() + 400))


class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 20
        self.max_health = self.health
        self.direction = 1
        self.jump = False
        self.in_air = True
        self.vel_y = 0
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        #ai variables
        self.move_counter = 0


        #load all images for player
        animation_types = ['idle', 'walk', 'jump', 'death']
        for animation in animation_types:
            #reset temp list
            temp_list = []
            #count number of files in folder
            num_of_frames = len(os.listdir(f'images/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'images/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        

    def move(self, moving_left, moving_right):
        #reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0
           
        #assign movement
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -14
            self.jump = False
            self.in_air = True

        self.vel_y += GRAV
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #collission check
        for tile in world.obstacle_list:
            #check collission for x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            #y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below ground/jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above ground
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

            


        #update rec pos
        self.rect.x += dx
        self.rect.y += dy

        #update scroll on player pos
        if self.char_type == 'player':
            if self.rect.right > SCREEN_WIDTH - SCROLL_THRESH or self.rect.left < SCROLL_THRESH:
                self.rect.x -= dx
                screen_scroll = -dx
        
        return screen_scroll


    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery - 22, self.direction)
            bullet_group.add(bullet)
            #reducing ammo
            self.ammo -= 1


    def ai(self):
        if self.alive and player.alive:
            if self.direction == 1:
                ai_moving_right = True
            else:
                ai_moving_right = False
            ai_moving_left = not ai_moving_right
            self.move(ai_moving_left, ai_moving_right)
            self.move_counter += 1
            if self.move_counter > TILE_SIZE:
                self.direction *= -1
                self.move_counter *= -1

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 180
        #update image on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #animation loop
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0


    def update_action(self, new_action):
        #check if new action is different
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        
        
class World():
    def __init__(self):
        self.obstacle_list = []
    
    def process_data(self, data):
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 1:
                        self.obstacle_list.append(tile_data)
                    elif tile == 2:
                        decs = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decor_group.add(decs)
                    elif tile == 3:
                        #temp for creating item boxes
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 4: #player
                        player = Character('player', x * TILE_SIZE, y * TILE_SIZE, 1, 4, 20)
                        health_bar = HPBar(10, 10, player.health, player.health)
                    elif tile == 5: #enemies
                        enemy1 = Enemies('enemy1', x * TILE_SIZE, y * TILE_SIZE, 1, 3, 9999)
                        enemy_group.add(enemy1)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Enemies(pygame.sprite.Sprite):
    def __init__(enemy, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(enemy)
        enemy.alive = True
        enemy.char_type = char_type
        enemy.speed = speed
        enemy.ammo = ammo
        enemy.start_ammo = ammo
        enemy.shoot_cooldown = 0
        enemy.health = 10
        enemy.max_health = enemy.health
        enemy.direction = 1
        enemy.jump = False
        enemy.in_air = True
        enemy.vel_y = 0
        enemy.flip = False
        enemy.animation_list = []
        enemy.frame_index = 0
        enemy.action = 0
        enemy.update_time = pygame.time.get_ticks()

        #ai specific variables
        enemy.move_counter = 0
        enemy.vision = pygame.Rect(0, 0, 600, 20)
        enemy.idling = False
        enemy.idling_counter = 0


        #load all images for player
        animation_types = ['idle', 'walk', 'jump', 'death']
        for animation in animation_types:
            #reset temp list
            temp_list = []
            #count number of files in folder
            num_of_frames = len(os.listdir(f'images/{enemy.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'images/{enemy.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            enemy.animation_list.append(temp_list)

        enemy.image = enemy.animation_list[enemy.action][enemy.frame_index]
        enemy.rect = enemy.image.get_rect()
        enemy.rect.center = (x, y)
        enemy.width = enemy.image.get_width()
        enemy.height = enemy.image.get_height()

    def update(enemy):
        enemy.update_animation()
        enemy.check_alive()
        #update cooldown
        if enemy.shoot_cooldown > 0:
            enemy.shoot_cooldown -= 1

        

    def move(enemy, mob_moving_left, mob_moving_right):
        #reset movement variables
        dx = 0
        dy = 0
           
        #assign movement
        if mob_moving_left:
            dx = -enemy.speed
            enemy.flip = True
            enemy.direction = -1

        if mob_moving_right:
            dx = enemy.speed
            enemy.flip = False
            enemy.direction = 1

        #jump
        if enemy.jump == True and enemy.in_air == False:
            enemy.vel_y = -12
            enemy.jump = False
            enemy.in_air = True

        enemy.vel_y += GRAV
        if enemy.vel_y > 10:
            enemy.vel_y
        dy += enemy.vel_y

        #collission check
        for tile in world.obstacle_list:
            #check collission for x direction
            if tile[1].colliderect(enemy.rect.x + dx, enemy.rect.y, enemy.width, enemy.height):
                dx = 0
            #y direction
            if tile[1].colliderect(enemy.rect.x, enemy.rect.y + dy, enemy.width, enemy.height):
                #check if below ground/jumping
                if enemy.vel_y < 0:
                    enemy.vel_y = 0
                    dy = tile[1].bottom - enemy.rect.top
                #check if above ground
                elif enemy.vel_y >= 0:
                    enemy.vel_y = 0
                    enemy.in_air = False
                    dy = tile[1].top - enemy.rect.bottom


        #update rec pos
        enemy.rect.x += dx
        enemy.rect.y += dy


    def shoot(enemy):
        if enemy.shoot_cooldown == 0 and enemy.ammo > 0:
            enemy.shoot_cooldown = 50
            bullet = mob_Bullet(enemy.rect.centerx + (0.8 * enemy.rect.size[0] * enemy.direction), enemy.rect.centery, enemy.direction)
            bullet_group.add(bullet)
            #reducing ammo
            enemy.ammo -= 1

    def ai(enemy):
        if enemy.alive and player.alive:
            if enemy.idling == False and random.randint(1, 200) == 1:
                enemy.update_action(0)
                enemy.idling = True
                enemy.idling_counter = 50
            #check if ai is near player
            if enemy.vision.colliderect(player.rect):
                enemy.update_action(0)
                enemy.shoot()

            else:
                if enemy.idling == False:
                    if enemy.direction == 1:
                        ai_mob_moving_right = True
                    else:
                        ai_mob_moving_right = False
                    ai_mob_moving_left = not ai_mob_moving_right
                    enemy.move(ai_mob_moving_left, ai_mob_moving_right)
                    enemy.update_action(1)
                    enemy.move_counter += 1
                    #ai vision
                    enemy.vision.center = (enemy.rect.centerx + 300 * enemy.direction, enemy.rect.centery)
                    pygame.draw.rect(screen, RED, enemy.vision)


                    if enemy.move_counter > TILE_SIZE:
                        enemy.direction *= -1
                        enemy.move_counter *= -1
                else:
                    enemy.idling_counter -= 1
                    if enemy.idling_counter <= 0:
                        enemy.idling = False

        enemy.rect.x += screen_scroll

    def update_animation(enemy):
        #update animation
        ANIMATION_COOLDOWN = 1000
        #update image on current frame
        enemy.image = enemy.animation_list[enemy.action][enemy.frame_index]
        #check if enough time has passed
        if pygame.time.get_ticks() - enemy.update_time > ANIMATION_COOLDOWN:
            enemy.update_time = pygame.time.get_ticks()
            enemy.frame_index += 1
        #animation loop
        if enemy.frame_index >= len(enemy.animation_list[enemy.action]):
            if enemy.action == 3:
                enemy.frame_index = len(enemy.animation_list[enemy.action]) - 1
            else:
                enemy.frame_index = 0


    def update_action(enemy, new_action):
        #check if new action is different
        if new_action != enemy.action:
            enemy.action = new_action
            #update animation settings
            enemy.frame_index = 0
            enemy.update_time = pygame.time.get_ticks()


    def check_alive(enemy):
        if enemy.health <= 0:
            enemy.health = 0
            enemy.speed = 0
            enemy.alive = False
            enemy.update_action(3)

    def draw(enemy):
        screen.blit(pygame.transform.flip(enemy.image, enemy.flip, False), enemy.rect)

#for boss
class Boss(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.jump = False
        self.in_air = True
        self.vel_y = 0
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()


        #load all images for player
        animation_types = ['idle', 'walk', 'jump', 'death']
        for animation in animation_types:
            #reset temp list
            temp_list = []
            #count number of files in folder
            num_of_frames = len(os.listdir(f'images/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'images/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        #check if player picks up item
        if pygame.sprite.collide_rect(self, player):
            #check what box
            if self.item_type == 'Ammo':
                print(player.ammo)
                #if player.ammo > 
                player.ammo += 10
            #delete the item
            self.kill()

class HPBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update new health
        self.health = health
        #calculate ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class mob_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 7
        self.image = bullet_img2
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check collision with characters
        #collision check with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 2
                self.kill()
        #for enemy1 in enemy_group:
            #if pygame.sprite.spritecollide(enemy1, bullet_group, False):
                #if enemy1.alive:
                    #enemy1.health -= 1
                    #self.kill()



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img1
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check collision with characters
        #collision check with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 2
                self.kill()
        for enemy1 in enemy_group:
            if pygame.sprite.spritecollide(enemy1, bullet_group, False):
                if enemy1.alive:
                    enemy1.health -= 1
                    self.kill()



#sprite groups
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decor_group = pygame.sprite.Group()






#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline = '') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)





run = True
while run:

    clock.tick(FPS)

    #update
    draw_bg()
    #world map
    world.draw()

    #show player health
    health_bar.draw(player.health)

    #show ammo
    draw_text(f'Ammo: {player.ammo}', font, RED, 10, 35)


    player.update()
    player.draw()


    for enemy1 in enemy_group:
        enemy1.ai()
        enemy1.update()
        enemy1.draw()

    #update and draw group
    bullet_group.update()
    bullet_group.draw(screen)
    item_box_group.update()
    item_box_group.draw(screen)
    
    #update player actions
    if player.alive:
        #shoot bullets
        if shoot:
            player.shoot()

        if player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1) #1 is run
        else:
            player.update_action(0)
        screen_scroll = player.move(moving_left, moving_right)

    




    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        #control release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False



    pygame.display.update()
pygame.quit()