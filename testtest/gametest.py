import pygame
import button

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#game window
screen_width = 800
screen_height = 640
lower_margin = 100
side_margin = 300

screen = pygame.display.set_mode((screen_width + side_margin, screen_height + lower_margin))
pygame.display.set_caption('Level Editor')

#game vars
rows = 16
max_cols = 75
tile_size = screen_height // rows
tile_types = 3
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1



#images
veins = pygame.image.load('images/background/veins.png').convert_alpha()
vessels = pygame.image.load('images/background/vessels.png').convert_alpha()
blood = pygame.image.load('images/background/blood.png').convert_alpha()
#function for drawing bground

#store tile in list
img_list = []
for x in range (tile_types):
    img = pygame.image.load(f'images/tiles/{x}.png')
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)

#color def
white = (255, 255, 255)
black = (0, 0, 0)

def draw_bg():
    screen.fill(white)
    width = veins.get_width()
    for x in range (2):
        screen.blit(veins, ((x * width)-scroll * 0.5, 0))
        screen.blit(vessels, ((x * width)-scroll * 0.6, screen_height - vessels.get_height() - 350))
        screen.blit(blood, ((x * width)-scroll * 0.7, screen_height - blood.get_height() + 400))

def draw_grid():
    #vertical lines
    for c in range(max_cols + 1):
        pygame.draw.line(screen, black,(c * tile_size - scroll, 0),(c * tile_size - scroll, screen_height))
    #horizontal
    for c in range(rows + 1):
        pygame.draw.line(screen, black,(0, c * tile_size),(screen_width, c * tile_size ))
        
#create buttons
#make button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(screen_width + (75 * button_col)+50, 75*button_row+50,img_list[i], 1)
    button_list.append(tile_button)



run = True
while run:

    clock.tick(FPS)

    draw_bg()
    draw_grid()

    #scroll map
    if scroll_left == True and scroll > 0:
        scroll -= 5 * scroll_speed
    if scroll_right == True:
        scroll += 5 * scroll_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #key press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 5

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_LSHIFT:
                scroll_speed = 1
    pygame.display.update()
pygame.quit()
