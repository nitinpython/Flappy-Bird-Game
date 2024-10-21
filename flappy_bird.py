import pygame as pg
from pygame.locals import *
from sys import exit


# Defining global constants
SPEED = 4                       # Control the speed of Ground and Pipe scrolling and Bird flapping


# Defining global variables
playing = False
collided_screen = False


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
        if playing and not collided_screen:
            angle = self.increase_y * -2
            self.image = pg.transform.rotate(self.image, angle).convert_alpha()
                    
        # Control Jump and Gravity of the bird
        self.increase_y += 0.5
        self.rect.y += self.increase_y
    
    
    # Changing bird images to create flapping effect
    def change_index(self):
        if self.index < len(self.img_filenames) - 1:
            self.index += 1
                    
        # Resetting the index
        else:
            self.index = 0

    
    # Controlling the bird movement (flapping and flying)
    def update(self):

        if not collided_screen:

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
        if not collided_screen:
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
        self.COLLISION_ANGLE = 90

        # Defining variables
        self.collided_sky = False               # To create hitting effect
        self.collided_ground = False            # To create hitting effect

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

        # Available sounds
        self.sound_filenames = {
            'wing' : 'Sounds/wing.mp3',
            'hit' : 'Sounds/hit.mp3',
            'swoosh': 'Sounds/swoosh.mp3'
        }
        
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


    # Method to load and play game sounds
    @staticmethod
    def play_sound(filename):
        sound = pg.mixer.Sound(filename)
        sound.play()


    # Defining what will happen at the collision with sky or ground
    def collided_with_screen(self, current_image: str):
        global collided_screen

        # First load the current image to cancel the rotation, then rotate 90 degree
        self.bird.image = pg.image.load(current_image).convert_alpha() 
        self.bird.image = pg.transform.rotate(self.bird.image, -self.COLLISION_ANGLE)

        self.play_sound(self.sound_filenames['hit'])
        self.play_sound(self.sound_filenames['swoosh'])

        collided_screen = True

    
    # Method to create a falling effect after collision
    def generate_falling_effect(self):
        # If the bird hits the sky
        if self.bird.rect.top <= self.__ZERO:
            self.bird.rect.top = self.__ZERO            # Protect the bird from going out of the screen

            self.collided_sky = True

        # If the bird hits the ground
        elif pg.sprite.groupcollide(self.bird_group, self.ground_group, False, False):
                    
            # Generate falling effect only if it does not hit the sky
            if not self.collided_sky and not self.collided_ground:
                self.bird.increase_y = SPEED * -3

                self.collided_ground = True


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

            # Move the bird upwards
            elif playing and not collided_screen:

                if event.type == KEYDOWN and event.key == K_UP:
                    self.bird.increase_y = SPEED * -2

                    self.play_sound(self.sound_filenames['wing']) 


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

            # Check if the bird collided with the game screen
            if playing and not collided_screen:

                # If bird hits the sky or the ground
                if self.bird.rect.top <= self.__ZERO or self.bird.rect.bottom >= self.__GROUND_Y:
                    self.collided_with_screen(self.bird.img_filenames[self.bird.index])
            
            # After collision generating falling effect
            elif playing and collided_screen:
                self.generate_falling_effect()

                # Falling of the bird
                self.bird.bird_movement()
                
            # Updating pygame display to create animation
            pg.display.update()

            # Event handler
            self.event_handler()
            

# Main module (Execution of main module)
if __name__ == '__main__':
    flappy_bird = FlappyBird()
    flappy_bird.game_loop()