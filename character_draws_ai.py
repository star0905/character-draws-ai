import math
from pathlib import Path

import pygame


WIDTH = 800
HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (245, 245, 240)
CIRCLE_CENTER = (WIDTH // 2, HEIGHT // 2)
CIRCLE_PATH_RADIUS = 150
MOTION_DURATION = 4.0
CIRCLE_ANGULAR_SPEED = math.tau / MOTION_DURATION
SQUARE_HALF_SIZE = 150
SQUARE_POINTS = (
    (CIRCLE_CENTER[0] + SQUARE_HALF_SIZE, CIRCLE_CENTER[1]),
    (CIRCLE_CENTER[0] + SQUARE_HALF_SIZE, CIRCLE_CENTER[1] + SQUARE_HALF_SIZE),
    (CIRCLE_CENTER[0] - SQUARE_HALF_SIZE, CIRCLE_CENTER[1] + SQUARE_HALF_SIZE),
    (CIRCLE_CENTER[0] - SQUARE_HALF_SIZE, CIRCLE_CENTER[1] - SQUARE_HALF_SIZE),
    (CIRCLE_CENTER[0] + SQUARE_HALF_SIZE, CIRCLE_CENTER[1] - SQUARE_HALF_SIZE),
    (CIRCLE_CENTER[0] + SQUARE_HALF_SIZE, CIRCLE_CENTER[1]),
)
SQUARE_PERIMETER = 8 * SQUARE_HALF_SIZE
TRIANGLE_RADIUS = 150
TRIANGLE_POINTS = (
    (CIRCLE_CENTER[0] + TRIANGLE_RADIUS, CIRCLE_CENTER[1]),
    (
        CIRCLE_CENTER[0] - TRIANGLE_RADIUS / 2,
        CIRCLE_CENTER[1] - TRIANGLE_RADIUS * math.sqrt(3) / 2,
    ),
    (
        CIRCLE_CENTER[0] - TRIANGLE_RADIUS / 2,
        CIRCLE_CENTER[1] + TRIANGLE_RADIUS * math.sqrt(3) / 2,
    ),
    (CIRCLE_CENTER[0] + TRIANGLE_RADIUS, CIRCLE_CENTER[1]),
)
TRIANGLE_PERIMETER = sum(
    math.dist(start, end)
    for start, end in zip(TRIANGLE_POINTS, TRIANGLE_POINTS[1:])
)
CHARACTER_IMAGE_PATH = Path(__file__).resolve().parent / "character.png"


def move_in_circle(screen, delta_time, state):
    angle = state["circle_angle"] + CIRCLE_ANGULAR_SPEED * delta_time
    motion_complete = angle >= math.tau
    if motion_complete:
        angle = math.tau

    x = CIRCLE_CENTER[0] + CIRCLE_PATH_RADIUS * math.cos(angle)
    y = CIRCLE_CENTER[1] + CIRCLE_PATH_RADIUS * math.sin(angle)

    character_image = state["character_image"]
    character_rect = character_image.get_rect(center=(round(x), round(y)))
    screen.blit(character_image, character_rect)

    state["circle_angle"] = 0.0 if motion_complete else angle
    return motion_complete


def move_along_path(screen, delta_time, state, distance_key, points, perimeter):
    distance = state[distance_key] + perimeter / MOTION_DURATION * delta_time
    motion_complete = distance >= perimeter
    distance = min(distance, perimeter)
    remaining_distance = distance

    for start, end in zip(points, points[1:]):
        segment_length = math.dist(start, end)
        if remaining_distance <= segment_length:
            progress = remaining_distance / segment_length
            x = start[0] + (end[0] - start[0]) * progress
            y = start[1] + (end[1] - start[1]) * progress
            break
        remaining_distance -= segment_length

    character_image = state["character_image"]
    character_rect = character_image.get_rect(center=(round(x), round(y)))
    screen.blit(character_image, character_rect)

    state[distance_key] = 0.0 if motion_complete else distance
    return motion_complete


def move_in_square(screen, delta_time, state):
    return move_along_path(
        screen,
        delta_time,
        state,
        "square_distance",
        SQUARE_POINTS,
        SQUARE_PERIMETER,
    )


def move_in_triangle(screen, delta_time, state):
    return move_along_path(
        screen,
        delta_time,
        state,
        "triangle_distance",
        TRIANGLE_POINTS,
        TRIANGLE_PERIMETER,
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Path Motion")
    clock = pygame.time.Clock()
    character_image = pygame.image.load(str(CHARACTER_IMAGE_PATH)).convert_alpha()
    motion_functions = (move_in_circle, move_in_square, move_in_triangle)
    motion_state = {
        "circle_angle": 0.0,
        "square_distance": 0.0,
        "triangle_distance": 0.0,
        "character_image": character_image,
    }
    motion_index = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)
        delta_time = clock.tick(FPS) / 1000
        motion_complete = motion_functions[motion_index](
            screen,
            delta_time,
            motion_state,
        )
        if motion_complete:
            motion_index = (motion_index + 1) % len(motion_functions)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()