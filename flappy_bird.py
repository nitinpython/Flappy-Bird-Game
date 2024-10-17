import pygame as pg
from pygame.locals import *
from sys import exit


# Defining global constants
SCROLL_SPEED = 4


# Class for Ground sprite
class Ground(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.img_filename = 'Images/ground.png'
        self.image = pg.image.load(self.img_filename).convert_alpha()
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.scroll_limit = -36

    # Controlling scrolling animation
    def update(self):
        self.rect.x -= SCROLL_SPEED
        if self.rect.x < self.scroll_limit:
            self.rect.x = 0



# Main game class containing the game code
class FlappyBird:
    def __init__(self):
        
        # Initializing pygame
        pg.init()

        # Initializing the clock
        self.clock = pg.time.Clock()            # Create an object to help track time

        # Defining constants
        self.__SCREEN_WIDTH = 864
        self.__SCREEN_HEIGHT = 610
        self.__ZERO = 0                         # x=y=0
        self.__MESSAGE_X = 340
        self.__MESSAGE_Y = 100
        self.__GROUND_Y = 442
        self.FPS = 60

        # Game window
        self.SCREEN = pg.display.set_mode((self.__SCREEN_WIDTH, self.__SCREEN_HEIGHT))

        # Available images
        self.img_filenames = {
            'icon' : 'Images/bird up.png',
            'bg' : 'Images/bg.png',
            'message': 'Images/message.png'
        }

        # Loading images 
        self.images = dict()
        
        for key, value in self.img_filenames.items():
            self.images[key] = pg.image.load(value)

        # Setting window title/caption and icon
        self.caption = 'Flappy Bird'
        pg.display.set_caption(self.caption)

        pg.display.set_icon(self.images['icon'])

        # Blitting Background image
        self.SCREEN.blit(self.images['bg'].convert(), (self.__ZERO, self.__ZERO)) 

        # Creating Ground object and adding it to the Group
        self.ground = Ground(self.__ZERO, self.__GROUND_Y)
        self.ground_group = pg.sprite.Group()
        self.ground_group.add(self.ground)
        
        # Blitting the message
        self.SCREEN.blit(self.images['message'].convert_alpha(), (self.__MESSAGE_X, self.__MESSAGE_Y))


    # Method for event handling
    @staticmethod
    def event_handler():
       
        for event in pg.event.get():
            # Close the game
            if event.type == QUIT:
                pg.quit()
                exit()


    # Main game loop
    def game_loop(self):
        while True:
            # Update the clock
            self.clock.tick(self.FPS)

            # Drawing the Ground
            self.ground_group.draw(self.SCREEN)

            # Scrolling the Ground
            self.ground_group.update()

            # Updating pygame display to create animation
            pg.display.update()

            # Event handler
            self.event_handler()
            

# Main module (Execution of main module)
if __name__ == '__main__':
    flappy_bird = FlappyBird()
    flappy_bird.game_loop()
    