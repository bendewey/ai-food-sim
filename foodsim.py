# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)

import math
import random
import sys
import os
from random import randint, choice

import neat
import pygame

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1200
HEIGHT = 800

PLAYER_SIZE_X = 60    
PLAYER_SIZE_Y = 60

BORDER_COLOR = (255, 255, 255, 255) # Color To Crash on Hit

current_generation = 0 # Generation counter

class Person:
    def __init__(self) -> None:
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('graphics/player.png').convert() # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (PLAYER_SIZE_X, PLAYER_SIZE_Y))
        self.rotated_sprite = self.sprite 

        self.direction_font = pygame.font.SysFont("Arial", 20)

        # self.position = [690, 740] # Starting Position
        self.position = [randint(0,23)*50, randint(0,11)*50] # Starting Position
        self.angle = 0
        self.speed = 0

        self.radars = []

        self.speed_set = False # Flag For Default Speed Later on

        self.center = [self.position[0] + PLAYER_SIZE_X / 2, self.position[1] + PLAYER_SIZE_Y / 2] # Calculate Center

        self.alive = True # Boolean To Check If Car is Crashed

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed
        self.food_eaten = 0
        self.age = 0
        self.radar_direction = 0

    def is_alive(self):
        return self.alive

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position) # Draw Sprite
        self.draw_radar(screen) #OPTIONAL FOR SENSORS

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)
        text = self.direction_font.render(str(self.direction) + '-' + str(self.food_eaten), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = self.center
        screen.blit(text, text_rect)

    def update(self, game_map):
        # 7  0  1
        # 6  8  2
        # 5  4  3
        # -- 360/8 = 45
        if self.angle < 0: return

        #direction = int((self.angle) / 45)
        direction = self.direction
        self.radar_direction = direction
        #print(f'angle={int(self.angle)} dir={direction}')
        if direction == 0:
            self.position[1] = self.position[1] - 50
        elif direction == 1:
            self.position[0] = self.position[0] + 50
            self.position[1] = self.position[1] - 50
        elif direction == 2:
            self.position[0] = self.position[0] + 50
        elif direction == 3:
            self.position[0] = self.position[0] + 50
            self.position[1] = self.position[1] + 50
        elif direction == 4:
            self.position[1] = self.position[1] + 50
        elif direction == 5:
            self.position[0] = self.position[0] - 50
            self.position[1] = self.position[1] + 50
        elif direction == 6:
            self.position[0] = self.position[0] - 50
        elif direction == 7:
            self.position[0] = self.position[0] - 50
            self.position[0] = self.position[0] - 50
        else:
            pass
        self.position[0] = max(self.position[0], 0)
        self.position[0] = min(self.position[0], 1150)
        self.position[1] = max(self.position[1], 0)
        self.position[1] = min(self.position[1], 750)

        self.center = [self.position[0] + PLAYER_SIZE_X / 2, self.position[1] + PLAYER_SIZE_Y / 2] # Calculate Center

    def get_reward(self):
        return self.food_eaten
    
    def get_data(self, food):
        self.radars.clear()

        if (food.__len__() == 0): return [-1, -1]
        self.age += 1
        closest_food = food[0]
        closest_food_distance = 10000
        closest_food_angle = 0
        for f in food:
            r = calculate_angle_between_points(self.position, f.position)                                              
            distance = r[0]
            angle = r[1]

            if distance < 50:
                f.kill()
                food.remove(f)
                self.food_eaten += 1
                self.age = 0
                continue
            if distance < closest_food_distance:
                closest_food_distance = distance
                closest_food_angle = angle
                closest_food = f

        self.radars.append([closest_food.position[0]+25, closest_food.position[1]+25])

        #print(f'age={self.age}, alive={self.alive}')
        #print(f'distance={food_distance}, angle={food_angle}')
        if self.age > 40: self.alive = False

        return [closest_food_distance, closest_food_angle]
   
class Food(pygame.sprite.Sprite):
    def __init__(self,type):
        super().__init__()

        if type == 'apple':
            apple = pygame.image.load('graphics/apple.png').convert_alpha()
            #fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
            #fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
            self.frames = [apple]
            y_pos = 210
        else:
            apple = pygame.image.load('graphics/apple.png').convert_alpha()
            #snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
            #snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
            self.frames = [apple]
            y_pos  = 300

        self.animation_index = 0
        self.image = self.frames[0]#self.animation_index]
        self.position =  [randint(0,23)*50, randint(0,11)*50];
        #self.rect = self.image.get_rect(midbottom = (randint(900,1100),y_pos))

    def animation_state(self):
        self.animation_index += 0.1 
        if self.animation_index >= len(self.frames): self.animation_index = 0
        self.image = self.frames[0]#int(self.animation_index)]

    def draw(self,screen):
        screen.blit(self.image, self.position)

    def update(self):
        self.animation_state()
        #self.rect.x -= 6
        #self.destroy()

    def destroy(self):
        #if self.rect.x <= -100: 
        self.kill()

def calculate_angle_between_points(p1, p2):
    #quadrants
    # 4  1
    # 3  2
    xdif = p2[0] - p1[0]
    ydif = p2[1] - p1[1]
    quadrant = 1
    if xdif >= 0 and ydif < 0: quadrant = 1
    elif xdif <= 0 and ydif <= 0: quadrant = 4
    elif xdif <= 0 and ydif >= 0: quadrant = 3
    elif xdif >= 0 and ydif >= 0: quadrant = 2  

    if xdif == 0:
        #print('xdif=0')
        distance = ydif
        food_angle = 0
    if ydif == 0:
        #print(f'ydif=0, xdif={xdif}')
        distance = xdif
        food_angle = 0
    else:
        side1 = p1[0] - p2[0]
        distance = calculate_hypotenuse(side1, p1[1] - p2[1])
        food_angle = round(calculate_angle(distance, side1))
        if food_angle < 0: food_angle = 90 + food_angle
    
    
    #print(f'xd={xdif}, yd={ydif}, d={int(distance)}, q={quadrant}, fa={food_angle}')
    angle = food_angle + ((quadrant-1) * 90)
    return [distance, angle]

def calculate_hypotenuse(a, b):
    return math.sqrt(a * a + b * b)

def calculate_angle(c, a):
    return math.degrees(math.asin(a / c))

def run_simulation(genomes, config):

    counter = 0

    # Empty Collections For Nets and Cars
    nets = []
    people = []
    food = []

    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Food Simulator")

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        people.append(Person())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load('graphics/world.png').convert() # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Timer 
    food_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(food_timer, 100)

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

            if event.type == food_timer:
                food.append(Food(choice(['apple'])))

        # For Each Car Get The Acton It Takes
        for i, person in enumerate(people):
            input = person.get_data(food)
            output = nets[i].activate(input)
            dir = output.index(max(output))
            #dir = int(input[1] / 45)
            #outFloat = output[0]
            #print(outFloat)

            #newAngle = abs(int(360 * outFloat)) % 360
            #print(f'{input[4]} - out={outFloat} new={newAngle}')
            #person.angle = input[1]
            #print(f'dir={dir}, angle={input[1]}')
            person.direction = dir

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, person in enumerate(people):
            if person.is_alive():
                still_alive += 1
                person.update(game_map)
                genomes[i][1].fitness += person.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40: # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for person in people:
            if person.is_alive():
                person.draw(screen)
        
        for f in food:
            f.draw(screen)

        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (600, 100)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (600, 200)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(10) # 60 FPS

if __name__ == "__main__":
    
    # Load Config
    config_path = "./foodsim-config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
    
    # print(f'angle 0= {calculate_angle_between_points([50,50], [50,0])}')
    # print(f'angle 45= {calculate_angle_between_points([50,50], [100,0])}')
    # print(f'angle 90= {calculate_angle_between_points([50,50], [100,50])}')
    # print(f'angle 95= {calculate_angle_between_points([50,50], [100,55])}')
    # print(f'angle 135= {calculate_angle_between_points([50,50], [100,100])}')
    # print(f'angle 180= {calculate_angle_between_points([50,50], [50,100])}')
    # print(f'angle 185= {calculate_angle_between_points([50,50], [45,108])}')
    # print(f'angle 225= {calculate_angle_between_points([50,50], [0,100])}')
    # print(f'angle 270= {calculate_angle_between_points([50,50], [0,50])}')
    # print(f'angle 315= {calculate_angle_between_points([50,50], [0,0])}')