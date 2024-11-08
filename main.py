import pygame
from dataclasses import dataclass, field
from typing import List
import random as rd
from abc import ABC, abstractmethod



pygame.init()
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Juegooo")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

GRID_SIZE = 15
CELL_SIZE = 40

@dataclass
class Positionable(ABC):  
    name: str
    position: List[int]

    @abstractmethod
    def move(self):
        pass

    def is_move_valid(self, position):
        return 0 <= position[0] < GRID_SIZE and 0 <= position[1] < GRID_SIZE

@dataclass
class Player(Positionable):
    health: int = 3
    inventory: dict = field(default_factory=lambda: {"Medicine": 0, "Weapons": 0})

    def move(self, direction: str, obstacles):
        new_position = self.position[:]
        
        if direction == 'up':
            new_position[0] -= 1
        elif direction == 'down':
            new_position[0] += 1
        elif direction == 'left':
            new_position[1] -= 1
        elif direction == 'right':
            new_position[1] += 1

        if self.is_move_valid(new_position) and new_position not in obstacles:
            self.position = new_position
            print(f'{self.name} moved to {self.position}')

@dataclass
class Obstacle(Positionable): 
    def move(self):
        pass

@dataclass
class Enemy(Positionable):
    def move(self):
        direction = rd.choice(['up', 'down', 'left', 'right'])
        new_position = self.position[:]
        
        if direction == 'up':
            new_position[0] -= 1
        elif direction == 'down':
            new_position[0] += 1
        elif direction == 'left':
            new_position[1] -= 1
        elif direction == 'right':
            new_position[1] += 1

        if self.is_move_valid(new_position):
            self.position = new_position

@dataclass
class Medicine(Positionable):
    def move(self):
        pass

@dataclass
class Game:
    player: Player = field(default_factory=lambda: Player("Player", [2, 2]))
    obstacles: List[Obstacle] = field(default_factory=list)
    enemies: List[Enemy] = field(default_factory=list)
    medicine: Medicine = None
    medicine_timer: int = 0
    enemy_pause: bool = False  
    
    def __post_init__(self):
        self.create_environment()


    def create_environment(self):
        for _ in range(15):    
            obstacle_position = [rd.randint(0, GRID_SIZE - 1), rd.randint(0, GRID_SIZE - 1)]
            self.obstacles.append(Obstacle('Obstacle', obstacle_position))

        for _ in range(4):
            enemy_position = [rd.randint(0, GRID_SIZE - 1), rd.randint(0, GRID_SIZE - 1)]
            self.enemies.append(Enemy('Enemy', enemy_position))

    def spawn_medicine(self):
        if not self.medicine and rd.random() < 0.1:
            position = [rd.randint(0, GRID_SIZE - 1), rd.randint(0, GRID_SIZE - 1)]
            self.medicine = Medicine("Medicine", position)
            print("Medicine spawned!")

    def draw_grid(self):
        screen.fill(WHITE)
        for x in range(0, GRID_SIZE * CELL_SIZE, CELL_SIZE):
            for y in range(0, GRID_SIZE * CELL_SIZE, CELL_SIZE):
                pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)

    def draw_elements(self):

        pygame.draw.rect(screen, BLUE, (self.player.position[1] * CELL_SIZE, self.player.position[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, BLACK, (obstacle.position[1] * CELL_SIZE, obstacle.position[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for enemy in self.enemies:
            pygame.draw.rect(screen, RED, (enemy.position[1] * CELL_SIZE, enemy.position[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        if self.medicine:
            pygame.draw.rect(screen, GREEN, (self.medicine.position[1] * CELL_SIZE, self.medicine.position[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def display_health(self):
        font = pygame.font.Font(None, 36)
        health_text = font.render(f'Health: {self.player.health}', True, BLACK)
        screen.blit(health_text, (10, 10))

    def move_player(self, direction):
        obstacles = [obstacle.position for obstacle in self.obstacles]
        self.player.move(direction, obstacles)
        self.enemy_pause = False  
        self.check_collisions()

    def move_enemies(self):
        if not self.enemy_pause:  
            for enemy in self.enemies:
                enemy.move()
            self.check_collisions()

    def check_collisions(self):
        for enemy in self.enemies:
            if enemy.position == self.player.position:
                self.player.health -= 1
                print(f'{self.player.name} was attacked by an enemy! Health left: {self.player.health}')
                if self.player.health <= 0:
                    print("Game Over!")
                    pygame.quit()
                    exit()
                
                self.enemy_pause = True

                enemy.position = [rd.randint(0, GRID_SIZE - 1), rd.randint(0, GRID_SIZE - 1)]
        
        if self.medicine and self.medicine.position == self.player.position:
            self.player.health = min(self.player.health + 1, 3)  # Restaurar hasta un máximo de 3
            print(f'{self.player.name} picked up a medicine! Health: {self.player.health}')
            self.medicine = None  # Eliminar medicina después de usarla

    def update_display(self):
        self.draw_grid()
        self.draw_elements()
        self.display_health()
        pygame.display.flip()


def main():
    game = Game()
    game.update_display()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.move_player('up')
                elif event.key == pygame.K_DOWN:
                    game.move_player('down')
                elif event.key == pygame.K_LEFT:
                    game.move_player('left')
                elif event.key == pygame.K_RIGHT:
                    game.move_player('right')

        game.move_enemies()
        
        game.spawn_medicine()

        game.update_display()
        
        clock.tick(5)

    pygame.quit()

if __name__ == "__main__":
    main()

