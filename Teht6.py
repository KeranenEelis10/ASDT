import tkinter as tk
import threading
import time
import random
import numpy as np
from math import sin, cos, pi
import pygame  # Import pygame for sound functionality

class IslandSimulation:
    def __init__(self):
        pygame.mixer.init()  # Initialize the sound mixer
        self.root = tk.Tk()
        self.root.title("Tropical Island Simulation")
        
        # Load sound files (Ensure these sound files exist in the working directory)
        self.sounds = {
            "fetch": pygame.mixer.Sound("ASDT/fetch_sound.wav"),
            "dig": pygame.mixer.Sound("dig_sound.wav"),
            "error": pygame.mixer.Sound("error_sound.wav")
        }
        
        # Create matrices
        self.pool_matrix = np.zeros((20, 60))  # Swimming pool matrix
        self.trench_ernesti = np.ones(100)      # Ernesti's trench, filled with sand
        self.trench_kernesti = np.ones(100)     # Kernesti's trench, filled with sand
        
        # Canvas setup with increased size
        self.canvas = tk.Canvas(self.root, width=1000, height=800, bg='#1e90ff')
        self.canvas.pack(pady=10)
        
        # Progress labels with better formatting
        self.label_frame = tk.Frame(self.root)
        self.label_frame.pack(fill=tk.X, padx=20)
        
        self.progress_ernesti = tk.Label(self.label_frame, text="Ernesti's trench: 0% dug", 
                                       font=('Arial', 12), fg='#2c3e50')
        self.progress_ernesti.pack(side=tk.LEFT, padx=20)
        
        self.progress_kernesti = tk.Label(self.label_frame, text="Kernesti's trench: 0% dug",
                                        font=('Arial', 12), fg='#2c3e50')
        self.progress_kernesti.pack(side=tk.RIGHT, padx=20)
        
        # Monkey management
        self.monkeys = []
        self.monkey_lock = threading.Lock()
        self.active_diggers = {"Ernesti": [], "Kernesti": []}
        self.digging_positions = {"Ernesti": {}, "Kernesti": {}}
        
        # Create controls
        self.create_controls()
        
        # Initialize scene
        self.draw_scene()
        self.create_forest_monkeys(15)
        
        # Start animation loop
        self.animate()

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Ernesti's controls without frame
        ernesti_frame = tk.Frame(control_frame)
        ernesti_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Button(ernesti_frame, text="Get Monkey\n(Ernesti)", 
                  command=lambda: self.fetch_monkey("Ernesti"),
                  bg='#27ae60', fg='black', font=('Arial', 10), height=2, width=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(ernesti_frame, text="Start Digging\n(Ernesti)", 
                  command=lambda: self.start_digging("Ernesti"),
                  bg='#e67e22', fg='black', font=('Arial', 10), height=2, width=20).pack(side=tk.LEFT, padx=5)
        
        # Kernesti's controls without frame
        kernesti_frame = tk.Frame(control_frame)
        kernesti_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Button(kernesti_frame, text="Get Monkey\n(Kernesti)", 
                  command=lambda: self.fetch_monkey("Kernesti"),
                  bg='#27ae60', fg='black', font=('Arial', 10), height=2, width=20).pack(side=tk.LEFT, padx=5)
        
        tk.Button(kernesti_frame, text="Start Digging\n(Kernesti)", 
                  command=lambda: self.start_digging("Kernesti"),
                  bg='#e67e22', fg='black', font=('Arial', 10), height=2, width=20).pack(side=tk.LEFT, padx=5)

    def draw_scene(self):
        # Draw island
        self.canvas.create_oval(150, 150, 850, 650, fill='#f4d03f', outline='#d4b130',
                              width=3, tags='island')
        
        # Draw swimming pool
        self.pool_x1, self.pool_y1 = 400, 350
        self.pool_x2, self.pool_y2 = 600, 450
        self.canvas.create_rectangle(self.pool_x1, self.pool_y1, self.pool_x2, self.pool_y2,
                                   fill='#b2dffb', outline='#7f8c8d', width=2,
                                   tags='pool')
        
        # Draw trenches
        self.draw_trench("Ernesti", self.pool_x1 + 50, self.pool_y1)
        self.draw_trench("Kernesti", self.pool_x2 - 50, self.pool_y1)
        
        # Draw base forest area
        self.draw_forest()

    def draw_forest(self):
        forest_x, forest_y = 250, 400
        
        # Draw base forest area
        self.canvas.create_oval(forest_x-80, forest_y-80, forest_x+80, forest_y+80,
                              fill='#27ae60', outline='#229954', width=2,
                              tags='forest')

    def draw_trench(self, owner, x, y):
        trench_length = 200
        trench_width = 20
        
        trench_data = {
            "x": x,
            "y": y,
            "length": trench_length,
            "width": trench_width,
            "start_y": y,
            "end_y": y - trench_length
        }
        
        setattr(self, f'trench_{owner.lower()}_data', trench_data)
        
        self.canvas.create_rectangle(x - trench_width/2, y - trench_length,
                                   x + trench_width/2, y,
                                   fill='#e3d9c6', outline='#7f8c8d',
                                   tags=f'trench_{owner.lower()}')

    def create_forest_monkeys(self, count):
        forest_x, forest_y = 250, 400
        
        for i in range(count):
            angle = random.uniform(0, 2*pi)
            r = random.uniform(20, 60)
            x = forest_x + r * cos(angle)
            y = forest_y + r * sin(angle)
            
            monkey = {
                'id': i,
                'position': (x, y),
                'fetched': False,
                'owner': None,
                'canvas_id': self.draw_monkey(x, y, f'monkey_{i}')
            }
            self.monkeys.append(monkey)

    def draw_monkey(self, x, y, tag):
        monkey_color = '#8b4513'
        
        # Draw a simple brown circle representing the monkey
        return self.canvas.create_oval(x-10, y-10, x+10, y+10,
                                        fill=monkey_color, outline='black',
                                        tags=tag)

    def fetch_monkey(self, owner):
        with self.monkey_lock:
            available_monkeys = [m for m in self.monkeys if not m['fetched']]
            if not available_monkeys:
                self.play_sound('error')
                return
            
            monkey = available_monkeys[0]
            monkey['fetched'] = True
            monkey['owner'] = owner
            
            # Calculate position in trench
            trench_data = getattr(self, f'trench_{owner.lower()}_data')
            current_diggers = len(self.active_diggers[owner])
            start_y = trench_data['start_y']
            end_y = trench_data['end_y']
            
            # Calculate position along trench
            position = current_diggers * (start_y - end_y) // 10
            target_y = start_y - position
            
            self.animate_monkey_movement(monkey, trench_data['x'], target_y)
            self.play_sound('fetch')
            
            # Store monkey's digging position
            self.digging_positions[owner][monkey['id']] = position // 2
            self.active_diggers[owner].append(monkey)

    def animate_monkey_movement(self, monkey, target_x, target_y):
        current_x, current_y = monkey['position']
        steps = 50  # Number of animation steps
        x_step = (target_x - current_x) / steps
        y_step = (target_y - current_y) / steps
        
        for i in range(steps):
            current_x += x_step
            current_y += y_step
            self.canvas.move(monkey['canvas_id'], x_step, y_step)
            self.canvas.update()
            time.sleep(0.02)

        monkey['position'] = (target_x, target_y)

    def start_digging(self, owner):
        with self.monkey_lock:
            if self.active_diggers[owner]:
                for monkey in self.active_diggers[owner]:
                    threading.Thread(target=self.dig_trench, args=(monkey, self.digging_positions[owner][monkey['id']])).start()

    def dig_trench(self, monkey, start_position):
        owner = monkey['owner']
        trench = self.trench_ernesti if owner == "Ernesti" else self.trench_kernesti
        progress_label = self.progress_ernesti if owner == "Ernesti" else self.progress_kernesti
        
        position = start_position
        delay = 1  # initial delay for the first meter

        while position < 100:
            if trench[position] > 0:  # Only dig if there's still sand
                time.sleep(delay)  # Delay for digging

                with self.monkey_lock:
                    trench[position] -= 1
                    self.update_trench_visual(owner)

                    # Update progress
                    progress = (sum(trench <= 0) / 100) * 100
                    progress_label.config(text=f"{owner}'s trench: {progress:.1f}% dug")
                    
                    self.play_sound('dig')
                    
                position += 1
                delay *= 2  # Double the time for the next meter
            else:
                break  # Stop if the trench is fully dug

    def update_trench_visual(self, owner):
        trench = self.trench_ernesti if owner == "Ernesti" else self.trench_kernesti
        trench_data = getattr(self, f'trench_{owner.lower()}_data')
        x, y, width = trench_data["x"], trench_data["start_y"], trench_data["width"]
        
        # Clear previous trench visualization
        self.canvas.delete(f'trench_{owner.lower()}')
        
        # Redraw the trench with the updated state
        self.draw_trench(owner, x, y)
        
        for i in range(100):
            if trench[i] <= 0:
                self.canvas.create_rectangle(x - width / 2, y - (i + 1),
                                         x + width / 2, y - i,
                                         fill='grey', outline='black', tags=f'trench_{owner.lower()}')

    def play_sound(self, action):
        if action in self.sounds:
            self.sounds[action].play()  # Play sound for the given action

    def animate(self):
        self.root.after(100, self.animate)

if __name__ == "__main__":
    simulation = IslandSimulation()
    simulation.root.mainloop()
