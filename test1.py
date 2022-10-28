import pygame
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

#framerate
clock = pygame.time.Clock()
FPS = 60

#game var
GRAV = 0.75

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('BrainExe')

#player action
moving_left = False
moving_right = False

#define colors
BG = (255, 255, 255)
RED = (255, 0, 0)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 550),(SCREEN_WIDTH, 550))







class Character(pygame.sprite.Sprite):
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
        animation_types = ['idle', 'walk', 'jump']
        for animation in animation_types:
            #reset temp list
            temp_list = []
            #count number of files in folder
            num_of_frames = len(os.listdir(f'images/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'images/{self.char_type}/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        #reset movement variables
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
            self.vel_y = -12
            self.jump = False
            self.in_air = True

        self.vel_y += GRAV
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #collission check
        if self.rect.bottom + dy > 550:
            dy = 550 - self.rect.bottom
            self.in_air = False


        #update rec pos
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 220
        #update image on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #animation loop
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0


    def update_action(self, new_action):
        #check if new action is different
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


player = Character('player', 100, 550, 1, 5)

run = True
while run:

    clock.tick(FPS)

    draw_bg()

    player.update_animation()
    player.draw()
    
    #update player actions
    if player.alive:
        if player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1) #1 is run
        else:
            player.update_action(0)
        player.move(moving_left, moving_right)




    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
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



    pygame.display.update()
pygame.quit()