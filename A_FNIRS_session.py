import pygame
import sys
import time
import subprocess
import os
import csv

# Paths to individual game scripts
codes_dir = os.path.dirname(os.path.abspath(__file__))
oneback_script = os.path.join(codes_dir, 'oneback_game.py')
threeback_script = os.path.join(codes_dir, 'threeback_game.py')
balloon_test2_script = os.path.join(codes_dir, 'red_balloon_shoot_game.py')

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
PURPLE = (160, 32, 240)
FONT = None
FONT_BIG = None
FONT_SMALL = None
FONT_MEDIUM = None

# Folder to save frustration ratings
frustration_folder = r"C:\\Users\\HP\\OneDrive\\Desktop\\Mendi_vs_Octamon_Study\\Frustration_Ratings"
os.makedirs(frustration_folder, exist_ok=True)
frustration_file = os.path.join(frustration_folder, f"{participant_id}_frustration_rating.csv")


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
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < duration_ms:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        screen.fill(BLACK)
        instr_text = "Please focus on '+' shown on the screen "
        instr_render = FONT.render(instr_text, True, WHITE)
        instr_rect = instr_render.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(instr_render, instr_rect)
        pygame.display.flip()
        clock.tick(FPS)


def init_screen():
    pygame.init()
    # Full screen mode
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Combined Session")
    clock = pygame.time.Clock()
    global FONT, FONT_BIG, FONT_SMALL, FONT_MEDIUM
    try:
        FONT = pygame.font.SysFont("lato", 48)
        FONT_BIG = pygame.font.SysFont("lato", 90)
        FONT_MEDIUM = pygame.font.SysFont("lato", 50)
        FONT_SMALL = pygame.font.SysFont("lato", 40)
    except Exception:
        FONT = pygame.font.SysFont("arial", 48)
        FONT_BIG = pygame.font.SysFont("arial", 90)
        FONT_MEDIUM = pygame.font.SysFont("arial", 50)
        FONT_SMALL = pygame.font.SysFont("arial", 40)
    return screen, clock


def get_frustration_rating(screen, clock, task_name):
    input_text = ""
    rating = None

    while rating is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        val = int(input_text)
                        if 0 <= val <= 100:
                            rating = val
                        else:
                            input_text = ""
                    except:
                        input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    if event.unicode.isdigit():
                        input_text += event.unicode

        # Clear screen
        screen.fill(BLACK)

        # Main big purple question
        big_question = FONT_BIG.render("How frustrated are you feeling?", True, PURPLE)
        rect = big_question.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 180))
        screen.blit(big_question, rect)

        # Slightly bigger white supporting text
        medium_lines = [
            "0 = Not frustrated at all   |   100 = Extremely frustrated",
            "Type a number (0–100) and press ENTER"
        ]
        y = HEIGHT // 2 - 20
        for line in medium_lines:
            render = FONT_MEDIUM.render(line, True, WHITE)
            rect = render.get_rect(center=(WIDTH // 2, y))
            screen.blit(render, rect)
            y += 70

        # Show input label and value in purple
        y += 60
        input_label = FONT_MEDIUM.render("Your input:", True, PURPLE)
        rect_label = input_label.get_rect(center=(WIDTH // 2, y))
        screen.blit(input_label, rect_label)

        y += 70
        input_display = FONT_BIG.render(input_text if input_text else "", True, PURPLE)
        rect_display = input_display.get_rect(center=(WIDTH // 2, y))
        screen.blit(input_display, rect_display)

        pygame.display.flip()
        clock.tick(FPS)

    return rating


def save_frustration(participant_id, task_name, rating):
    new_file = not os.path.exists(frustration_file)
    with open(frustration_file, "a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["participant_id", "task_name", "frustration"])
        writer.writerow([participant_id, task_name, rating])
    print(f"⭐ Saved frustration rating for {task_name}: {rating} to {frustration_file}")


def main():
    # 1-Back Test
    screen, clock = init_screen()
    show_instructions(screen, clock, 6000)
    show_fixation(screen, clock, FIXATION_MS)
    show_countdown(screen, clock, "1-Back Test")
    pygame.quit()
    subprocess.run([sys.executable, oneback_script, participant_id], check=True)

    # Prompt frustration after 1-back
    screen, clock = init_screen()
    frust1 = get_frustration_rating(screen, clock, "1-back Test")
    save_frustration(participant_id, "1-back", frust1)

    # 3-Back Test
    show_instructions(screen, clock, 6000)
    show_fixation(screen, clock, FIXATION_MS)
    show_countdown(screen, clock, "3-Back Test")
    pygame.quit()
    subprocess.run([sys.executable, threeback_script, participant_id], check=True)

    # Prompt frustration after 3-back
    screen, clock = init_screen()
    frust3 = get_frustration_rating(screen, clock, "3-back Test")
    save_frustration(participant_id, "3-back", frust3)

    # Balloon Test
    show_instructions(screen, clock, 6000)
    show_fixation(screen, clock, FIXATION_MS)
    show_countdown(screen, clock, "Balloon Game")
    pygame.quit()
    subprocess.run([sys.executable, balloon_test2_script, participant_id], check=True)

    # Prompt frustration after Balloon
    screen, clock = init_screen()
    frust_balloon = get_frustration_rating(screen, clock, "Balloon Game")
    save_frustration(participant_id, "Balloon", frust_balloon)

    # Final Fixation
    show_instructions(screen, clock, 6000)
    show_fixation(screen, clock, FIXATION_MS)
    pygame.quit()


if __name__ == "__main__":
    main()
