import pygame
import random
import math
import csv
import time

# Initialize pygame
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ecosystem Simulation")
clock = pygame.time.Clock()

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Prey:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 50
        self.max_energy = 200
        self.speed = 2
        self.vision = 50
        self.birth_time = time.time()  # Track when prey was born
        self.has_reproduced = False    # Track if already reproduced
        
    def move_random(self):
        # Move more actively when no food nearby
        move_x = random.randint(-5, 5)
        move_y = random.randint(-5, 5)
        self.x += move_x
        self.y += move_y
        
        # Keep on screen
        self.x = max(5, min(self.x, screen_width - 5))
        self.y = max(5, min(self.y, screen_height - 5))
        
    def move_towards_food(self, food_x, food_y):
        # Move towards food
        dx = food_x - self.x
        dy = food_y - self.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        self.x += (dx/dist) * self.speed
        self.y += (dy/dist) * self.speed
        
    def eat(self, resource):
        if resource.has_food:
            resource.has_food = False
            self.energy = min(self.max_energy, self.energy + 20)
            return True
        return False
        
    def update(self, resources):
        # Lose energy over time
        self.energy -= 0.5
        
        # Look for food
        closest_food = None
        closest_distance = 1000
        
        for resource in resources:
            if resource.has_food:
                distance = math.sqrt((self.x - resource.x)**2 + (self.y - resource.y)**2)
                if distance < self.vision and distance < closest_distance:
                    closest_distance = distance
                    closest_food = resource
        
        if closest_food:
            self.move_towards_food(closest_food.x, closest_food.y)
            if closest_distance < 10:
                self.eat(closest_food)
        else:
            # No food nearby, move around more actively
            self.move_random()
            
    def is_alive(self):
        return self.energy > 0
        
    def should_reproduce(self):
        # Reproduce if survived for 15 seconds and hasn't reproduced yet
        current_time = time.time()
        survival_time = current_time - self.birth_time
        if survival_time > 7 and not self.has_reproduced:
            self.has_reproduced = True
            return True
        return False
        
    def draw(self):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), 4)

class Predator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 300
        self.max_energy = 350
        self.speed = 2.1
        self.vision = 300
        self.prey_eaten = 0
        
    def move_random(self):
        # Move more actively when no prey nearby
        move_x = random.randint(-8, 8)
        move_y = random.randint(-8, 8)
        self.x += move_x
        self.y += move_y
        
        # Keep on screen
        self.x = max(5, min(self.x, screen_width - 5))
        self.y = max(5, min(self.y, screen_height - 5))
        
    def move_towards_prey(self, prey_x, prey_y):
        # Move towards prey
        dx = prey_x - self.x
        dy = prey_y - self.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        self.x += (dx/dist) * self.speed
        self.y += (dy/dist) * self.speed
        
    def hunt(self, prey):
        if random.random() < 0.7:  # 70% success rate
            self.prey_eaten += 1
            self.energy = min(self.max_energy, self.energy + 100)
            return True
        return False
        
    def update(self, preys):
        # Lose energy over time
        self.energy -= 1
        
        # Look for prey
        closest_prey = None
        closest_distance = 1000
        
        for prey in preys:
            distance = math.sqrt((self.x - prey.x)**2 + (self.y - prey.y)**2)
            if distance < self.vision and distance < closest_distance:
                closest_distance = distance
                closest_prey = prey
        
        if closest_prey:
            self.move_towards_prey(closest_prey.x, closest_prey.y)
            if closest_distance < 15:
                if self.hunt(closest_prey):
                    preys.remove(closest_prey)
        else:
            # No prey nearby, move around more actively
            self.move_random()
            
    def is_alive(self):
        return self.energy > 0
        
    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 6)

class Resource:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.has_food = True
        self.regrow_timer = random.randint(1, 300)
        
    def update(self):
        if not self.has_food:
            self.regrow_timer += 1
            if self.regrow_timer > 200:  # Regrow after 200 ticks
                self.has_food = True
                self.regrow_timer = 0
                
    def draw(self):
        if self.has_food:
            pygame.draw.circle(screen, DARK_GREEN, (int(self.x), int(self.y)), 3)
        else:
            pygame.draw.circle(screen, BROWN, (int(self.x), int(self.y)), 2)

def save_data_to_csv(prey_count, predator_count, resource_count):
    # Simple CSV logging
    with open('simulation_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        # Write header if file is empty
        if file.tell() == 0:
            writer.writerow(['Time', 'Prey Count', 'Predator Count', 'Resource Count'])
        
        current_time = time.strftime('%H:%M:%S')
        writer.writerow([current_time, prey_count, predator_count, resource_count])

# Create initial objects
preys = []
predators = []
resources = []

# Add prey
for i in range(200):
    preys.append(Prey(random.randint(50, screen_width-50), random.randint(50, screen_height-50)))

# Add predators
for i in range(5):
    predators.append(Predator(random.randint(50, screen_width-50), random.randint(50, screen_height-50)))

# Add resources
for i in range(400):
    resources.append(Resource(random.randint(20, screen_width-20), random.randint(20, screen_height-20)))

# Main game loop
running = True
tick_count = 0
last_log_time = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Clear screen
    screen.fill((50, 120, 80))
    
    # Update and draw resources
    for resource in resources:
        resource.update()
        resource.draw()
    
    # Update prey and check for reproduction
    new_preys = []  # Store new prey to be added
    for prey in preys[:]:
        prey.update(resources)
        if prey.is_alive():
            prey.draw()
            # Check if prey should reproduce
            if prey.should_reproduce():
                # Spawn two new prey near the parent
                for i in range(2):
                    new_x = prey.x + random.randint(-30, 30)
                    new_y = prey.y + random.randint(-30, 30)
                    new_x = max(5, min(new_x, screen_width - 5))
                    new_y = max(5, min(new_y, screen_height - 5))
                    new_preys.append(Prey(new_x, new_y))
        else:
            preys.remove(prey)
    
    # Add new prey to the main list
    preys.extend(new_preys)
    
    # Update and draw predators
    for predator in predators[:]:
        predator.update(preys)
        if predator.is_alive():
            predator.draw()
        else:
            predators.remove(predator)
    
    # Occasionally add new resources
    tick_count += 1
    if tick_count % 50 == 0 and len(resources) < 400:
        resources.append(Resource(random.randint(20, screen_width-20), random.randint(20, screen_height-20)))
    
    # Log data every 5 seconds
    current_time = time.time()
    if current_time - last_log_time >= 5:
        prey_count = len(preys)
        predator_count = len(predators)
        resource_count = sum(1 for r in resources if r.has_food)
        
        save_data_to_csv(prey_count, predator_count, resource_count)
        print(f"Logged: {prey_count} prey, {predator_count} predators, {resource_count} resources")
        last_log_time = current_time
    
    # Display counts
    font = pygame.font.Font(None, 36)
    prey_text = font.render(f"Prey: {len(preys)}", True, WHITE)
    predator_text = font.render(f"Predators: {len(predators)}", True, WHITE)
    resource_text = font.render(f"Food: {sum(1 for r in resources if r.has_food)}", True, WHITE)
    
    screen.blit(prey_text, (10, 10))
    screen.blit(predator_text, (10, 50))
    screen.blit(resource_text, (10, 90))
    
    # Update display
    pygame.display.flip()
    clock.tick(30)  # 30 FPS

pygame.quit()
print("Simulation ended. Data saved to simulation_data.csv")