import pygame
import sys
import time
import subprocess
import os

# Paths to individual game scripts
codes_dir = os.path.dirname(os.path.abspath(__file__))
oneback_script = os.path.join(codes_dir, 'one back test.py')
threeback_script = os.path.join(codes_dir, 'three back test.py')
balloon_test2_script = os.path.join(codes_dir, 'balloon test 2.py')

# Prompt for participant ID once
try:
    participant_id = input("Enter participant ID: ")
except Exception:
    participant_id = 'P01'

# Shared settings
FPS = 60
FIXATION_MS = 30000  # 30 seconds
COUNTDOWN_START = 3

# Colors and fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = None


def show_fixation(screen, clock, duration_ms):
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < duration_ms:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        screen.fill(BLACK)
        cx, cy = WIDTH // 2, HEIGHT // 2
        size = 20
        pygame.draw.line(screen, WHITE, (cx - size, cy), (cx + size, cy), 2)
        pygame.draw.line(screen, WHITE, (cx, cy - size), (cx, cy + size), 2)
        pygame.display.flip()
        clock.tick(FPS)


def show_countdown(screen, clock, label):
    for i in range(COUNTDOWN_START, 0, -1):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        screen.fill(BLACK)
        text = f"{label} starting in {i}..."
        render = FONT.render(text, True, WHITE)
        rect = render.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(render, rect)
        pygame.display.flip()
        time.sleep(1)


def show_instructions(screen, clock, duration_ms):
    """
    Display an instruction message for duration_ms milliseconds.
    """
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < duration_ms:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        screen.fill(BLACK)
        instr_text = "Please focus on the screen"
        instr_render = FONT.render(instr_text, True, WHITE)
        instr_rect = instr_render.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(instr_render, instr_rect)
        pygame.display.flip()
        clock.tick(FPS)


def init_screen():
    pygame.init()
    # Full screen mode
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    # Update global dimensions
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Combined Session")
    clock = pygame.time.Clock()
    global FONT
    try:
        FONT = pygame.font.SysFont("lato", 48)
    except Exception:
        FONT = pygame.font.SysFont("arial", 48)
    return screen, clock


def main():
    # 1-Back Test
    screen, clock = init_screen()
    show_instructions(screen, clock, 6000)
    show_fixation(screen, clock, FIXATION_MS)
    show_countdown(screen, clock, "1-Back Test")
    pygame.quit()
    subprocess.run([sys.executable, oneback_script, participant_id], check=True)

    # 3-Back Test
    screen, clock = init_screen()
    show_instructions(screen, clock, 6000)
    show_fixation(screen, clock, FIXATION_MS)
    show_countdown(screen, clock, "3-Back Test")
    pygame.quit()
    subprocess.run([sys.executable, threeback_script, participant_id], check=True)

    # Balloon Test2
    screen, clock = init_screen()
    show_instructions(screen, clock, 6000)
    show_fixation(screen, clock, FIXATION_MS)
    show_countdown(screen, clock, "Balloon Test2")
    pygame.quit()
    subprocess.run([sys.executable, balloon_test2_script, participant_id], check=True)

    # Final Fixation
    screen, clock = init_screen()
    show_instructions(screen, clock, 6000)
    show_fixation(screen, clock, FIXATION_MS)
    pygame.quit()


if __name__ == "__main__":
    main()
