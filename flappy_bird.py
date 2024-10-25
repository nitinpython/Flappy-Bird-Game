import pygame as pg
from pygame.locals import *
from sys import exit
from random import randint


# Defining global constants
BIRD_CONSTANT = 4                       # Control bird movements like flapping speed, collision effect and upward movement
SPEED = BIRD_CONSTANT                   # Control the speed of Ground and Pipe scrolling


# Defining global variables
playing = False
collided = False


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
        if playing and not collided:
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

        # Reducing the flapping speed by showing same image for 4 iterations
        if self.counter <= BIRD_CONSTANT:   
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

        # Reset Ground sprite position
        if self.rect.x < self.scroll_limit:
            self.rect.x = 0


# Class for Pipe sprite
class Pipe(pg.sprite.Sprite):
    def __init__(self, x, y, flip:bool = False):
        super().__init__()

        self.img_filename = 'Images/pipe.png'
        self.image = pg.image.load(self.img_filename).convert_alpha()

        # Defining the gap between the pipes
        self.GAP = 80
    
        # Top pipe
        if flip:
            self.image = pg.transform.flip(self.image, False, True)
            
            # Changing y to give the pipe gap
            y -= self.GAP
            self.rect = self.image.get_rect(bottomleft=(x, y))

        # Bottom pipe
        else:
            # Changing y to give the pipe gap
            y += self.GAP
            self.rect = self.image.get_rect(topleft=(x, y))

    
    # Controlling scrolling animation
    def update(self):
        if playing and not collided:
            self.rect.x -= SPEED

        # Remove the pipe objects from the group when they move out of the game window
        if self.rect.right < 0:
            self.kill()             # Remove the sprite from all Groups


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
        self.MESSAGE_X = 340
        self.MESSAGE_Y = 100
        self.__GROUND_Y = 442
        self.BIRD_X = 100
        self.FPS = 60
        self.COLLISION_ANGLE = 90
        self.RESTART_X = self.__SCREEN_WIDTH//2 - 50
        self.RESTART_Y = self.__SCREEN_HEIGHT//2 - 100
        self.PIPE_TIME = 1500               # 1500 Milliseconds = 1.5 Seconds
        self.PIPE_Y_FROM = -110               # Lower limit for random y coordinate of pipe
        self.PIPE_Y_TO = 70                   # Upper limit for random y coordinate of pipe
        self.SCORE_X = self.__SCREEN_WIDTH//2
        self.SCORE_Y = 15

        # Defining variables
        self.collided_sky = False               # To create sky hitting effect
        self.collided_ground = False            # To create ground hitting effect
        self.collided_pipe = False              # To create pipe hitting effect
        self.last_pipe_time = None              # To track the time last pipe was generated
        self.score = 0
        self.bird_between_pipes = False         # To increment score

        # Defining font and text color for displaying score
        self.font = pg.font.SysFont('Aerial', 70, True)
        self.text_color = (255, 255, 255)
        
        # Game window
        self.SCREEN = pg.display.set_mode((self.__SCREEN_WIDTH, self.__SCREEN_HEIGHT))

        # Available images
        self.img_filenames = {
            'icon' : 'Images/bird up.png',
            'bg' : 'Images/bg.png',
            'message': 'Images/message.png',
            'restart': 'Images/restart.png'
        }

        # Loading images 
        self.images = dict()
        
        for key, value in self.img_filenames.items():
            self.images[key] = pg.image.load(value)

        # Available sounds
        self.sound_filenames = {
            'wing' : 'Sounds/wing.mp3',
            'hit' : 'Sounds/hit.mp3',
            'swoosh': 'Sounds/swoosh.mp3',
            'point': 'Sounds/point.mp3'
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
        self.bird = Bird(self.BIRD_X, self.__SCREEN_HEIGHT//3)
        self.bird_group = pg.sprite.Group()
        self.bird_group.add(self.bird)

        # Creating Pipe Group
        self.pipe_group = pg.sprite.Group()


    # Method to load and play game sounds
    @staticmethod
    def play_sound(filename: str):
        sound = pg.mixer.Sound(filename)
        sound.play()


    # Defining what will happen at the collision with sky, ground or pipe
    def collision(self, current_image: str):
        global collided

        # First load the current image to cancel the rotation, then rotate 90 degree
        self.bird.image = pg.image.load(current_image).convert_alpha() 
        self.bird.image = pg.transform.rotate(self.bird.image, -self.COLLISION_ANGLE)

        self.play_sound(self.sound_filenames['hit'])
        self.play_sound(self.sound_filenames['swoosh'])

        collided = True

    
    # Method to create a falling effect (bird jump) after collision
    def generate_falling_effect(self):
        
        # If the bird hits the sky
        if self.bird.rect.top <= self.__ZERO:
            self.bird.rect.top = self.__ZERO            # Protect the bird from going out of the screen

            self.collided_sky = True

        # If the bird hits the ground
        elif pg.sprite.groupcollide(self.bird_group, self.ground_group, False, False):
                    
            # Generate falling effect only if it does not hit the sky or pipe
            if not (self.collided_sky or self.collided_pipe) and not self.collided_ground:
                self.bird.increase_y = BIRD_CONSTANT * -3

                self.collided_ground = True
        
        # If the bird hits the pipe
        elif pg.sprite.groupcollide(self.bird_group, self.pipe_group, False, False):
            
            # Generate falling effect
            if not self.collided_pipe:
                self.bird.increase_y = BIRD_CONSTANT * -3

                self.collided_pipe = True


    # Generate Restart button when bird goes out of the screen
    def show_restart_and_check_if_clicked(self, loaded_image: pg.Surface, coordinate: tuple):
        global playing
        playing = False             # Bird goes out of the screen
                
        # Blitting Restart button image
        restart_button = self.SCREEN.blit(
            loaded_image.convert_alpha(), 
            coordinate
            )
        
        # Check if the mouse is hovering over the restart button image and then clicked
        if restart_button.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
                self.reset_game()


    # Reset the game
    def reset_game(self):
        global playing
        global collided
        global SPEED

        # Resetting game global variables
        playing = True
        collided = False
        SPEED = BIRD_CONSTANT

        # Resetting the game variables
        self.collided_ground = False
        self.collided_sky = False
        self.collided_pipe = False
        self.score = 0

        # Resetting the bird
        self.bird.__init__(self.BIRD_X, self.__SCREEN_HEIGHT//3)

        # Reset the pipes
        self.pipe_group.empty()             # Remove all sprites from the group


    # Method to generate pipes on the screen
    def generate_pipes(self, after: int):
        
        time_now = pg.time.get_ticks()          # Return the number of milliseconds since pygame.init() was called

        # Creating pipes after every 1.5 Seconds
        if time_now - self.last_pipe_time >= after:
                    
            # Generating random y coordinate for the pipes
            random_increase_y = randint(self.PIPE_Y_FROM, self.PIPE_Y_TO)
            new_y = self.__SCREEN_HEIGHT//2.5 + random_increase_y

            # Creating top and bottom pipes and adding them to the Group
            self.bottom_pipe = Pipe(self.__SCREEN_WIDTH, new_y)
            self.top_pipe = Pipe(self.__SCREEN_WIDTH, new_y, True)
                    
            self.pipe_group.add(self.bottom_pipe, self.top_pipe)

            # Updating self.last_pipe_time
            self.last_pipe_time = time_now
    
    
    # Method to increase score
    def increase_score(self):
        global SPEED

        bird_sprite_left = self.bird_group.sprites()[0].rect.left
        bird_sprite_right = self.bird_group.sprites()[0].rect.right

        pipe_sprite_left = self.pipe_group.sprites()[0].rect.left
        pipe_sprite_right = self.pipe_group.sprites()[0].rect.right

        # If the bird is between the pipes
        if (
            bird_sprite_left > pipe_sprite_left and
            bird_sprite_right < pipe_sprite_right
            ):
            
            self.bird_between_pipes = True

        # Increment the score if the bird crosses the pipe sucessfully after going between the pipes
        if bird_sprite_left > pipe_sprite_right and self.bird_between_pipes:
            
            self.score += 1

            self.play_sound(self.sound_filenames['point'])

            # Increasing speed after every 10 points to add game difficulty
            multiple_of_10 = self.score % 10 == self.__ZERO
            score_below_100 = self.score < 100                  # Increase speed only till the score is lesss than 100

            if multiple_of_10 and score_below_100:                
                SPEED += 1                  # Increasing Ground and Pipe scrolling speed
                
            self.bird_between_pipes = False 
    
    
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
                    self.last_pipe_time = pg.time.get_ticks() - self.PIPE_TIME

            # Move the bird upwards
            elif playing and not collided:

                if event.type == KEYDOWN and event.key == K_UP:
                    self.bird.increase_y = BIRD_CONSTANT * -2

                    self.play_sound(self.sound_filenames['wing']) 


    # Main game loop
    def game_loop(self):
        while True:
            # Update the clock
            self.clock.tick(self.FPS)

            # Blitting Background image
            self.SCREEN.blit(self.images['bg'].convert(), (self.__ZERO, self.__ZERO)) 

            # Drawing the Pipes
            self.pipe_group.draw(self.SCREEN)

            # Scrolling the Pipes
            self.pipe_group.update()

            # Drawing the Ground
            self.ground_group.draw(self.SCREEN)

            # Drawing the Bird
            self.bird_group.draw(self.SCREEN)

            # Creating animation
            if not collided:
                # Scrolling the Ground
                self.ground_group.update()

                # Flapping and Flying the bird
                self.bird_group.update()

            # Blitting the message
            if not playing and not collided:
                self.SCREEN.blit(
                    self.images['message'].convert_alpha(), 
                    (self.MESSAGE_X, self.MESSAGE_Y)
                    )

            # Check if the bird collided with the game screen
            if playing and not collided:

                # If bird hits the sky, ground or pipe
                if (
                    self.bird.rect.top <= self.__ZERO or 
                    self.bird.rect.bottom >= self.__GROUND_Y or
                    pg.sprite.groupcollide(self.bird_group, self.pipe_group, False, False)
                ):
                    self.collision(self.bird.img_filenames[self.bird.index])
            
            # After collision generating falling effect
            elif playing and collided:
                self.generate_falling_effect()

                # Falling of the bird and stop it when it is out of the screen
                if self.bird.rect.top <= self.__SCREEN_HEIGHT:
                    self.bird.bird_movement()

            # When bird goes out of the screen (vanishes from the screen)
            if self.bird.rect.top > self.__SCREEN_HEIGHT:

                self.show_restart_and_check_if_clicked(
                    self.images['restart'],
                    (self.RESTART_X, self.RESTART_Y)
                    )

            # Generating the pipes and handling score
            if playing and not collided:

                # Controlling speed of generating the Pipes
                generate_pipe_after = (self.PIPE_TIME - SPEED * 100) + 400 
                
                # Generating the Pipes
                self.generate_pipes(generate_pipe_after)

                self.increase_score()

            # Showing score while playing the game
            if playing:
                rendered_score = self.font.render(str(self.score), False, self.text_color).convert_alpha()
                self.SCREEN.blit(rendered_score, (self.SCORE_X, self.SCORE_Y))


            # Updating pygame display to create animation
            pg.display.update()

            # Event handler
            self.event_handler()
            

# Main module (Execution of main module)
if __name__ == '__main__':
    flappy_bird = FlappyBird()
    flappy_bird.game_loop()