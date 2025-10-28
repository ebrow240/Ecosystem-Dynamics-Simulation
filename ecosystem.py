import pygame
import random
import math
import csv
import time
from datetime import datetime

# Initialize pygame
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Ecosystem Simulation - 10 Runs")
clock = pygame.time.Clock()

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)

class Prey:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 150
        self.max_energy = 500
        self.speed = 1.3
        self.vision = 150
        self.birth_time = time.time()
        self.has_reproduced = False
        
        # LEARNING ALGORITHM: Simple success tracking
        self.successful_actions = 0
        self.total_actions = 0
        self.learning_level = 0.0  # 0 to 1, how much prey has learned
        
    def learn_from_experience(self, action_successful):
        """Prey learn from their experiences"""
        self.total_actions += 1
        if action_successful:
            self.successful_actions += 1
        
        # Update learning level based on success rate
        if self.total_actions > 5:  # After some experience
            self.learning_level = min(1.0, self.successful_actions / self.total_actions)
    
    def make_smart_move(self, resources):
        """ Use learning to make better decisions"""
        # More experienced prey are better at finding food
        if self.learning_level > 0.3:
            # Look for closest food more efficiently
            closest_food = None
            closest_distance = 1000
            
            for resource in resources:
                if resource.has_food:
                    distance = math.sqrt((self.x - resource.x)**2 + (self.y - resource.y)**2)
                    # Experienced prey have better "search intuition"
                    if distance < self.vision * (1 + self.learning_level) and distance < closest_distance:
                        closest_distance = distance
                        closest_food = resource
            
            if closest_food:
                return closest_food
        
        return None
    
    def move_random(self):
        self.x += random.randint(-4, 4)
        self.y += random.randint(-4, 4)
        self.x = max(5, min(self.x, screen_width - 5))
        self.y = max(5, min(self.y, screen_height - 5))
        
    def move_towards_food(self, food_x, food_y):
        dx = food_x - self.x
        dy = food_y - self.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        self.x += (dx/dist) * self.speed
        self.y += (dy/dist) * self.speed
        
    def eat(self, resource):
        if resource.has_food:
            resource.has_food = False
            self.energy = min(self.max_energy, self.energy + 20)
            self.learn_from_experience(True)  # LEARNING: Successful eat
            return True
        self.learn_from_experience(False)  # LEARNING: Failed eat
        return False
        
    def update(self, resources):
        self.energy -= 0.5
        
        # Use learning to find food smarter
        smart_target = self.make_smart_move(resources)
        
        if smart_target:
            self.move_towards_food(smart_target.x, smart_target.y)
            distance = math.sqrt((self.x - smart_target.x)**2 + (self.y - smart_target.y)**2)
            if distance < 10:
                self.eat(smart_target)
        else:
            # Fall back to normal behavior
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
                self.move_random()
                self.learn_from_experience(False)  # LEARNING: Wandering is less successful
            
    def is_alive(self):
        return self.energy > 0
        
    def should_reproduce(self):
        current_time = time.time()
        survival_time = current_time - self.birth_time
        if survival_time > 15 and not self.has_reproduced:
            self.has_reproduced = True
            return True
        return False
        
    def draw(self):
        # Color shows learning level (darker green = more learned)
        green_value = int(255 * (1 - self.learning_level * 0.5))
        color = (0, green_value, 0)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 4)

class Predator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 120
        self.max_energy = 200
        self.speed = 1.7
        self.vision = 200
        self.prey_eaten = 0
        
    def move_random(self):
        self.x += random.randint(-4, 4)
        self.y += random.randint(-4, 4)
        self.x = max(5, min(self.x, screen_width - 5))
        self.y = max(5, min(self.y, screen_height - 5))
        
    def move_towards_prey(self, prey_x, prey_y):
        dx = prey_x - self.x
        dy = prey_y - self.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        self.x += (dx/dist) * self.speed
        self.y += (dy/dist) * self.speed
        
    def hunt(self, prey):
        if random.random() < 0.7:
            self.prey_eaten += 1
            self.energy = min(self.max_energy, self.energy + 30)
            return True
        return False
        
    def update(self, preys):
        self.energy -= 1
        
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
        self.regrow_timer = random.randint(100, 300)  # Different regrow times
        
    def update(self):
        if not self.has_food:
            self.regrow_timer -= 1
            if self.regrow_timer <= 0:
                self.has_food = True
                self.regrow_timer = random.randint(100, 300)
                
    def draw(self):
        if self.has_food:
            pygame.draw.circle(screen, DARK_GREEN, (int(self.x), int(self.y)), 3)
        else:
            pygame.draw.circle(screen, BROWN, (int(self.x), int(self.y)), 2)

def get_parameters_changed(description, prey, predators, resources, max_resources):
    """Generate a string describing what parameters were changed for this run"""
    baseline_prey = 50
    baseline_predators = 10
    baseline_resources = 400
    baseline_max_resources = 600
    
    changes = []
    
    if prey != baseline_prey:
        changes.append(f"prey={prey}(baseline:{baseline_prey})")
    if predators != baseline_predators:
        changes.append(f"predators={predators}(baseline:{baseline_predators})")
    if resources != baseline_resources:
        changes.append(f"resources={resources}(baseline:{baseline_resources})")
    if max_resources != baseline_max_resources:
        changes.append(f"max_resources={max_resources}(baseline:{baseline_max_resources})")
    
    # Add special condition changes
    if "Fast Metabolism" in description:
        changes.append("metabolism=3x_faster")
    elif "Slow Metabolism" in description:
        changes.append("metabolism=3x_slower")
    elif "Fast Reproduction" in description:
        changes.append("reproduction=3x_faster")
    elif "Slow Reproduction" in description:
        changes.append("reproduction=3x_slower")
    
    if not changes:
        return "baseline_parameters"
    
    return "; ".join(changes)

def run_simulation(run_number, description, initial_prey=50, initial_predators=10, 
                  initial_resources=150, max_resources=300, max_ticks=2000):
    """Run one simulation and save results to a numbered CSV file"""
    
    print(f"Starting Run {run_number:03d}: {description}")
    
    # Get parameters changed for this run
    parameters_changed = get_parameters_changed(description, initial_prey, initial_predators, 
                                              initial_resources, max_resources)
    
    # Create objects
    preys = [Prey(random.randint(50, screen_width-50), random.randint(50, screen_height-50)) 
            for _ in range(initial_prey)]
    predators = [Predator(random.randint(50, screen_width-50), random.randint(50, screen_height-50)) 
                for _ in range(initial_predators)]
    resources = [Resource(random.randint(20, screen_width-20), random.randint(20, screen_height-20)) 
                for _ in range(initial_resources)]
    
    # Data collection for this run
    run_data = []
    tick_count = 0
    predator_extinction_tick = None  # Track when predators went extinct
    
    # Update window title
    pygame.display.set_caption(f"Ecosystem Simulation - Run {run_number:03d}")
    
    running = True
    while running and tick_count < max_ticks and (preys or predators):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Clear screen
        screen.fill((50, 120, 80))
        
        # Update and draw resources
        for resource in resources:
            resource.update()
            resource.draw()
        
        # Update prey
        new_preys = []
        for prey in preys[:]:
            prey.update(resources)
            if prey.is_alive():
                prey.draw()
                if prey.should_reproduce():
                    for i in range(2):
                        new_x = prey.x + random.randint(-30, 30)
                        new_y = prey.y + random.randint(-30, 30)
                        new_x = max(5, min(new_x, screen_width - 5))
                        new_y = max(5, min(new_y, screen_height - 5))
                        new_preys.append(Prey(new_x, new_y))
            else:
                preys.remove(prey)
        
        preys.extend(new_preys)
        
        # Update predators
        for predator in predators[:]:
            predator.update(preys)
            if predator.is_alive():
                predator.draw()
            else:
                predators.remove(predator)
        
        # If no predators for 300 ticks, spawn 3 new ones
        if len(predators) == 0:
            if predator_extinction_tick is None:
                predator_extinction_tick = tick_count  # Record when predators went extinct
                print(f"  Predators went extinct at tick {tick_count}")
            
            # Check if 300 ticks have passed since extinction
            if tick_count - predator_extinction_tick >= 300:
                print(f"  Respawning 3 predators at tick {tick_count}")
                for i in range(3):
                    predators.append(Predator(random.randint(50, screen_width-50), 
                                            random.randint(50, screen_height-50)))
                predator_extinction_tick = None  # Reset for potential future extinctions
        else:
            predator_extinction_tick = None  # Reset if predators exist
        
        # Add resources if needed - MORE FREQUENT RESOURCE SPAWNING
        tick_count += 1
        if tick_count % 25 == 0 and len(resources) < max_resources:
            resources.append(Resource(random.randint(20, screen_width-20), random.randint(20, screen_height-20)))
        
        # Collect data every 50 ticks
        if tick_count % 50 == 0:
            avg_learning = sum(p.learning_level for p in preys) / len(preys) if preys else 0
            run_data.append({
                'tick': tick_count,
                'prey_count': len(preys),
                'predator_count': len(predators),
                'resource_count': sum(1 for r in resources if r.has_food),
                'avg_learning': round(avg_learning, 3),
                'total_prey_eaten': sum(p.prey_eaten for p in predators),
                'predators_respawned': 1 if predator_extinction_tick and tick_count - predator_extinction_tick >= 300 else 0,
                'parameters_changed': parameters_changed
            })
        
        # Display stats
        font = pygame.font.Font(None, 24)
        current_avg_learning = sum(p.learning_level for p in preys) / len(preys) if preys else 0
        
        # Show predator respawn status
        predator_status = f"Predators: {len(predators)}"
        if predator_extinction_tick is not None:
            ticks_since_extinction = tick_count - predator_extinction_tick
            predator_status = f"Predators: 0 (Respawning in {300-ticks_since_extinction} ticks)"
        
        stats = [
            f"Run {run_number:03d}: {description}",
            f"Tick: {tick_count}/{max_ticks}",
            f"Prey: {len(preys)}",
            predator_status,
            f"Food: {sum(1 for r in resources if r.has_food)}",
            f"Avg Learning: {current_avg_learning:.2f}",
            f"Params: {parameters_changed[:30]}..." if len(parameters_changed) > 30 else f"Params: {parameters_changed}"
        ]
        for i, stat in enumerate(stats):
            text = font.render(stat, True, WHITE)
            screen.blit(text, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(30)
    
    # Save results to numbered CSV file
    filename = f"run_{run_number:03d}.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Run_Number', 'Description', 'Tick', 'Prey_Count', 'Predator_Count', 
                        'Resource_Count', 'Avg_Learning', 'Total_Prey_Eaten', 'Predators_Respawned',
                        'Parameters_Changed'])
        
        for data_point in run_data:
            writer.writerow([
                run_number, description, data_point['tick'], data_point['prey_count'],
                data_point['predator_count'], data_point['resource_count'],
                data_point['avg_learning'], data_point['total_prey_eaten'],
                data_point['predators_respawned'], data_point['parameters_changed']
            ])
    
    final_prey = len(preys)
    final_predators = len(predators)
    print(f"Run {run_number:03d} completed at tick {tick_count}: {final_prey} prey, {final_predators} predators")
    print(f"Parameters: {parameters_changed}")
    print(f"Data saved to {filename}")
    
    return final_prey, final_predators, tick_count, parameters_changed

# Run all 10 simulations 
def run_all_simulations():
    simulations = [
        # (run_number, description, prey, predators, resources, max_resources)
        (1, "Baseline", 50, 10, 400, 600),          
        (2, "Very High Resources", 50, 10, 800, 1200), 
        (3, "Very Low Resources", 50, 10, 100, 150),  
        (4, "Many Predators", 50, 40, 400, 600),       
        (5, "Very Few Predators", 50, 3, 400, 600),    
        (6, "Fast Metabolism", 50, 10, 400, 600),      
        (7, "Slow Metabolism", 50, 10, 400, 600),      
        (8, "Fast Reproduction", 50, 10, 400, 600),    
        (9, "Slow Reproduction", 50, 10, 400, 600),    
        (10, "Balanced Large", 80, 15, 600, 800), 
    ]
    
    results = []
    for run_num, desc, prey, pred, res, max_res in simulations:
        # Apply variations based on run type
        if desc == "Fast Metabolism":
            # Modify prey and predator metabolism
            Prey.original_update = Prey.update
            Predator.original_update = Predator.update
            
            def fast_metabolism_prey_update(self, resources):
                self.energy -= 1.5  # Much faster energy drain
                Prey.original_update(self, resources)
            
            def fast_metabolism_predator_update(self, preys):
                self.energy -= 3.0  # Much faster energy drain
                Predator.original_update(self, preys)
            
            Prey.update = fast_metabolism_prey_update
            Predator.update = fast_metabolism_predator_update
            
        elif desc == "Slow Metabolism":
            Prey.original_update = Prey.update
            Predator.original_update = Predator.update
            
            def slow_metabolism_prey_update(self, resources):
                self.energy -= 0.2  # Much slower energy drain
                Prey.original_update(self, resources)
            
            def slow_metabolism_predator_update(self, preys):
                self.energy -= 0.4  # Much slower energy drain
                Predator.original_update(self, preys)
            
            Prey.update = slow_metabolism_prey_update
            Predator.update = slow_metabolism_predator_update
            
        elif desc == "Fast Reproduction":
            Prey.original_should_reproduce = Prey.should_reproduce
            
            def fast_reproduction(self):
                current_time = time.time()
                survival_time = current_time - self.birth_time
                if survival_time > 5 and not self.has_reproduced:  # Much faster reproduction
                    self.has_reproduced = True
                    return True
                return False
            
            Prey.should_reproduce = fast_reproduction
            
        elif desc == "Slow Reproduction":
            Prey.original_should_reproduce = Prey.should_reproduce
            
            def slow_reproduction(self):
                current_time = time.time()
                survival_time = current_time - self.birth_time
                if survival_time > 40 and not self.has_reproduced:  # Much slower reproduction
                    self.has_reproduced = True
                    return True
                return False
            
            Prey.should_reproduce = slow_reproduction
        
        final_prey, final_pred, final_tick, params = run_simulation(run_num, desc, prey, pred, res, max_res, max_ticks=1000)
        results.append((run_num, desc, final_prey, final_pred, final_tick, params))
        
        # Reset to default behaviors for next run
        if hasattr(Prey, 'original_update'):
            Prey.update = Prey.original_update
        if hasattr(Predator, 'original_update'):
            Predator.update = Predator.original_update
        if hasattr(Prey, 'original_should_reproduce'):
            Prey.should_reproduce = Prey.original_should_reproduce
        
        # Small pause between runs
        time.sleep(1)
    
    print("\n" + "="*50)
    print("ALL SIMULATIONS COMPLETED - SUMMARY")
    print("="*50)
    for run_num, desc, prey, pred, tick, params in results:
        status = "STABLE" if prey > 0 and pred > 0 else "EXTINCT"
        print(f"Run {run_num:02d} ({desc}): {prey} prey, {pred} predators at tick {tick} - {status}")
        print(f"  Parameters: {params}")

# Start the simulations
if __name__ == "__main__":
    run_all_simulations()
    pygame.quit()
