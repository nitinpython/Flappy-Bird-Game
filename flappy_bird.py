import pygame as pg
from pygame.locals import *
from sys import exit


# Defining global constants
SPEED = 4                       # Control the speed of Ground and Pipe scrolling and Bird flapping


# Defining global variables
playing = False


# Class for Bird sprite
class Bird(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Available bird images
        self.img_filenames = (
            'Images/bird up.png',
            'Images/bird straight.png',
            'Images/bird down.png'
            )
        
        self.index = 0                      # To change bird images
        self.counter = 1                    # To reduce flap speed

        self.image = pg.image.load(self.img_filenames[self.index]).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

        # Control Jump and Gravity of the bird
        self.increase_y = 0


    def bird_movement(self):
        # Controlling rotation of the bird
        angle = self.increase_y * -2
        self.image = pg.transform.rotate(self.image, angle).convert_alpha()
                
        # Control Jump and Gravity of the bird
        self.increase_y += 0.5
        self.rect.y += self.increase_y
    
    
    def change_index(self):
        if self.index < len(self.img_filenames) - 1:
            self.index += 1
                    
        else:
            self.index = 0

    
    # Controlling the bird movement (flapping and flying)
    def update(self):
        # Reducing the flapping speed by showing same image for 4 iterations
        if self.counter <= SPEED:   
            self.image = pg.image.load(self.img_filenames[self.index]).convert_alpha()
            self.counter += 1
            
            # Move the bird if user is playing the game
            if playing:
                self.bird_movement()


        # Changing the bird images to create the flapping effect
        else:
            # Reset the counter after 4 iterations
            self.counter = 0

            # Changing the index to change the images
            self.change_index()
            

# Class for Ground sprite
class Ground(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.img_filename = 'Images/ground.png'
        self.image = pg.image.load(self.img_filename).convert()
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.scroll_limit = -36

    # Controlling scrolling animation
    def update(self):
        self.rect.x -= SPEED
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
        self.__BIRD_X = 100
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

        # Creating Ground object and adding it to the Group
        self.ground = Ground(self.__ZERO, self.__GROUND_Y)
        self.ground_group = pg.sprite.Group()
        self.ground_group.add(self.ground)

        # Creating Bird object and adding it to the Group
        self.bird = Bird(self.__BIRD_X, self.__SCREEN_HEIGHT//3)
        self.bird_group = pg.sprite.Group()
        self.bird_group.add(self.bird)


    # Method for event handling
    def event_handler(self):
        global playing
       
        for event in pg.event.get():
            # Close the game
            if event.type == QUIT:
                pg.quit()
                exit()

            # Start the game
            if not playing:
                if pg.mouse.get_pressed()[0] or (event.type == KEYDOWN and event.key == K_SPACE):
                    playing = True

            else:
                # Move the bird upwards
                if event.type == KEYDOWN and event.key == K_UP:
                    self.bird.increase_y = SPEED * -2

                    pg.mixer.music.load('Sounds/wing.mp3')
                    pg.mixer.music.play() 


    # Main game loop
    def game_loop(self):
        while True:
            # Update the clock
            self.clock.tick(self.FPS)

            # Blitting Background image
            self.SCREEN.blit(self.images['bg'].convert(), (self.__ZERO, self.__ZERO)) 

            # Drawing the Ground
            self.ground_group.draw(self.SCREEN)

            # Scrolling the Ground
            self.ground_group.update()

            # Blitting the message
            if not playing:
                self.SCREEN.blit(self.images['message'].convert_alpha(), (self.__MESSAGE_X, self.__MESSAGE_Y))

            # Drawing the bird
            self.bird_group.draw(self.SCREEN)

            # Flapping and Flying the bird
            self.bird_group.update()
            
            # Updating pygame display to create animation
            pg.display.update()

            # Event handler
            self.event_handler()
            

# Main module (Execution of main module)
if __name__ == '__main__':
    flappy_bird = FlappyBird()
    flappy_bird.game_loop()