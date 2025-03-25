import pygame, sys, time, random, os
from wekaI import Weka

# Initialize Weka and JVM
weka = Weka()
weka.start_jvm()

# DIFFICULTY settings
DIFFICULTY = 10

# Window size
FRAME_SIZE_X = 480
FRAME_SIZE_Y = 480

# Colors (R, G, B)
BLACK = pygame.Color(51, 51, 51)
WHITE = pygame.Color(255, 255, 255)
RED   = pygame.Color(204, 51, 0)
GREEN = pygame.Color(204, 255, 153)
BLUE  = pygame.Color(0, 51, 102)

# ARFF file header for the full dataset
ARFF_HEADER = """@RELATION snake_game_phase1

@ATTRIBUTE snake_head_x NUMERIC
@ATTRIBUTE snake_head_y NUMERIC
@ATTRIBUTE food_x NUMERIC
@ATTRIBUTE food_y NUMERIC
@ATTRIBUTE snake_len NUMERIC
@ATTRIBUTE snake_body_parts_x STRING
@ATTRIBUTE snake_body_parts_y STRING
@ATTRIBUTE current_score NUMERIC
@ATTRIBUTE action {UP,DOWN,LEFT,RIGHT}
@ATTRIBUTE next_score NUMERIC

@DATA
"""

# Game state class
class GameState:
    def __init__(self, FRAME_SIZE):
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [90, 50], [80, 50]]
        self.food_pos = [random.randrange(1, (FRAME_SIZE[0]//10)) * 10, 
                         random.randrange(1, (FRAME_SIZE[1]//10)) * 10]
        self.food_spawn = True
        self.direction = 'RIGHT'
        self.score = 0

# Game Over
def game_over(game):
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, WHITE)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/4)
    game_window.fill(BLUE)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(game, 0, WHITE, 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

# Score
def show_score(game, choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(game.score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (FRAME_SIZE_X/8, 15)
    else:
        score_rect.midtop = (FRAME_SIZE_X/2, FRAME_SIZE_Y/1.25)
    game_window.blit(score_surface, score_rect)

# Movement function
def move_keyboard(game, event):
    change_to = game.direction
    if event.type == pygame.KEYDOWN:
        if (event.key == pygame.K_UP or event.key == ord('w')) and game.direction != 'DOWN':
            change_to = 'UP'
        if (event.key == pygame.K_DOWN or event.key == ord('s')) and game.direction != 'UP':
            change_to = 'DOWN'
        if (event.key == pygame.K_LEFT or event.key == ord('a')) and game.direction != 'RIGHT':
            change_to = 'LEFT'
        if (event.key == pygame.K_RIGHT or event.key == ord('d')) and game.direction != 'LEFT':
            change_to = 'RIGHT'
    return change_to

# Modified print_line_data()
def print_line_data(game, action, next_score):
    snake_head_x = game.snake_pos[0]
    snake_head_y = game.snake_pos[1]
    food_x = game.food_pos[0]
    food_y = game.food_pos[1]
    snake_len = len(game.snake_body)
    snake_body_parts_x = '|'.join(str(part[0]) for part in game.snake_body[1:])
    snake_body_parts_y = '|'.join(str(part[1]) for part in game.snake_body[1:])
    current_score = game.score
    return f"{snake_head_x},{snake_head_y},{food_x},{food_y},{snake_len},'{snake_body_parts_x}','{snake_body_parts_y}',{current_score},{action},{next_score}\n"

# Write instance to ARFF
def write_arff_instance(game, action, next_score, filename="training_keyboard.arff"):
    file_exists = os.path.exists(filename)
    mode = "a" if file_exists else "w"
    with open(filename, mode) as f:
        if not file_exists:
            f.write(ARFF_HEADER)
        f.write(print_line_data(game, action, next_score))

# Wall & body safety check
def is_safe_direction(game, direction):
    next_x, next_y = game.snake_pos[0], game.snake_pos[1]
    if direction == 'UP': next_y -= 10
    elif direction == 'DOWN': next_y += 10
    elif direction == 'LEFT': next_x -= 10
    elif direction == 'RIGHT': next_x += 10

    if next_x < 0 or next_x >= FRAME_SIZE_X or next_y < 0 or next_y >= FRAME_SIZE_Y:
        return False
    if [next_x, next_y] in game.snake_body:
        return False
    return True

# Prioritize direction toward food that's also safe
def best_direction_toward_food(game):
    directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    best_dir = None
    min_dist = float('inf')
    for d in directions:
        if not is_safe_direction(game, d):
            continue
        nx, ny = game.snake_pos[0], game.snake_pos[1]
        if d == 'UP': ny -= 10
        elif d == 'DOWN': ny += 10
        elif d == 'LEFT': nx -= 10
        elif d == 'RIGHT': nx += 10
        dist = abs(nx - game.food_pos[0]) + abs(ny - game.food_pos[1])
        if dist < min_dist:
            min_dist = dist
            best_dir = d
    return best_dir

# Initialize pygame
pygame.init()
pygame.display.set_caption('Snake Eater - Machine Learning (UC3M)')
game_window = pygame.display.set_mode((FRAME_SIZE_X, FRAME_SIZE_Y))
fps_controller = pygame.time.Clock()
game = GameState((FRAME_SIZE_X, FRAME_SIZE_Y))

# Main game loop
while True:
    current_action = game.direction
    current_score = game.score

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        game.direction = move_keyboard(game, event)

    x = [
        game.snake_pos[0],
        game.snake_pos[1],
        game.food_pos[0],
        game.food_pos[1],
        len(game.snake_body),
        game.score
    ]
    predicted_action = weka.predict("./j48.model", x, "./training_keyboard_filtered.arff")

    if not is_safe_direction(game, predicted_action):
        fallback = best_direction_toward_food(game)
        if fallback:
            predicted_action = fallback
    else:
        # Even if safe, check if best_direction_toward_food is better
        toward_food = best_direction_toward_food(game)
        if toward_food and toward_food != game.direction:
            predicted_action = toward_food

    if predicted_action == 'UP' and game.direction != 'DOWN':
        game.direction = 'UP'
    elif predicted_action == 'DOWN' and game.direction != 'UP':
        game.direction = 'DOWN'
    elif predicted_action == 'LEFT' and game.direction != 'RIGHT':
        game.direction = 'LEFT'
    elif predicted_action == 'RIGHT' and game.direction != 'LEFT':
        game.direction = 'RIGHT'

    if game.direction == 'UP': game.snake_pos[1] -= 10
    if game.direction == 'DOWN': game.snake_pos[1] += 10
    if game.direction == 'LEFT': game.snake_pos[0] -= 10
    if game.direction == 'RIGHT': game.snake_pos[0] += 10

    game.snake_body.insert(0, list(game.snake_pos))
    if game.snake_pos == game.food_pos:
        game.score += 100
        game.food_spawn = False
    else:
        game.snake_body.pop()
        game.score -= 1

    if not game.food_spawn:
        game.food_pos = [random.randrange(1, (FRAME_SIZE_X//10)) * 10, random.randrange(1, (FRAME_SIZE_Y//10)) * 10]
        game.food_spawn = True

    game_window.fill(BLUE)
    for pos in game.snake_body:
        pygame.draw.rect(game_window, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(game_window, RED, pygame.Rect(game.food_pos[0], game.food_pos[1], 10, 10))

    if game.snake_pos[0] < 0 or game.snake_pos[0] >= FRAME_SIZE_X or game.snake_pos[1] < 0 or game.snake_pos[1] >= FRAME_SIZE_Y or game.snake_pos in game.snake_body[1:]:
        game_over(game)

    show_score(game, 1, WHITE, 'consolas', 15)
    pygame.display.update()
    fps_controller.tick(DIFFICULTY)

    next_score = game.score
    write_arff_instance(game, current_action, next_score)
