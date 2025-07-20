import pygame
import random
import csv
import os
import time
import sys

# Override default ID if passed via CLI
if len(sys.argv) > 1:
    PARTICIPANT_ID = sys.argv[1]
else:
    PARTICIPANT_ID = "P01"

# Initialize Pygame and set fullscreen
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("3-Back Game (Full Screen)")
clock = pygame.time.Clock()

# Settings
FPS = 60
TRIAL_DURATION_MS = 2000      # Total trial duration per letter (ms)
LETTER_DISPLAY_MS = 1000      # Letter display duration (ms)
FADE_DURATION_MS = 20         # Fade-out duration (ms)
TOTAL_DURATION_SEC = 150      # Total seconds to run game
TOTAL_TRIALS = TOTAL_DURATION_SEC * 1000 // TRIAL_DURATION_MS

# Prepare save directory and path
BASE_SAVE_DIR = os.path.join(
    os.path.expanduser("~"),
    "OneDrive", "Desktop", "Mendi_vs_Octamon_Study", "Three_back_performance"
)
os.makedirs(BASE_SAVE_DIR, exist_ok=True)
SAVE_PATH = os.path.join(BASE_SAVE_DIR, f"{PARTICIPANT_ID}_3-back_performance.csv")

# Colors & Fonts
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
PURPLE, DARK_PURPLE = (128, 0, 255), (88, 0, 180)
BLUE, DARK_BLUE = (0, 150, 255), (0, 100, 180)
try:
    FONT_LARGE = pygame.font.SysFont("lato", 350)
    FONT_MEDIUM = pygame.font.SysFont("lato", 60)
    FONT_SMALL = pygame.font.SysFont("lato", 36)
except:
    FONT_LARGE = pygame.font.SysFont("arial", 350)
    FONT_MEDIUM = pygame.font.SysFont("arial", 60)
    FONT_SMALL = pygame.font.SysFont("arial", 36)

# Button rects
no_match_btn = pygame.Rect(WIDTH//2 - 200, HEIGHT - 120, 180, 80)
match_btn    = pygame.Rect(WIDTH//2 + 20,  HEIGHT - 120, 180, 80)


def draw_text(text, font, color, x, y, alpha=255):
    surf = font.render(text, True, color)
    if alpha < 255:
        surf.set_alpha(alpha)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)


def draw_buttons(highlight):
    left_color  = DARK_PURPLE if highlight == "left"  else PURPLE
    right_color = DARK_BLUE   if highlight == "right" else BLUE
    pygame.draw.rect(screen, left_color,  no_match_btn, border_radius=10)
    pygame.draw.rect(screen, WHITE,      no_match_btn, 2, border_radius=10)
    draw_text("NO MATCH", FONT_SMALL, WHITE, no_match_btn.centerx, no_match_btn.centery)
    pygame.draw.rect(screen, right_color, match_btn, border_radius=10)
    pygame.draw.rect(screen, WHITE,       match_btn, 2, border_radius=10)
    draw_text("MATCH",     FONT_SMALL, WHITE, match_btn.centerx,    match_btn.centery)


def save_summary(correct, incorrect, reaction_times, total_trials):
    missed = total_trials - (correct + incorrect)
    accuracy = (correct / total_trials * 100) if total_trials > 0 else 0
    mean_rt = sum(reaction_times) / len(reaction_times) if reaction_times else 0

    try:
        with open(SAVE_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["metric", "value"])
            writer.writerow(["total_trials", total_trials])
            writer.writerow(["correct_responses", correct])
            writer.writerow(["incorrect_responses", incorrect])
            writer.writerow(["missed_targets", missed])
            writer.writerow(["accuracy", round(accuracy, 2)])
            writer.writerow(["mean_reaction_time", round(mean_rt, 2)])
        print(f"✅ 3-back results saved to: {SAVE_PATH}")
    except Exception as e:
        print(f"❌ Failed to save summary: {e}")


def run_game():
    # History for 3-back: [last, two-back, three-back]
    prev_letters = [None, None, None]
    current = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    match_prob = 0.5
    trial_index = 0

    response = None
    rt = None
    reaction_times = []
    correct = 0
    incorrect = 0

    trial_start = pygame.time.get_ticks()
    reaction_clock = trial_start
    running = True

    while running and trial_index < TOTAL_TRIALS:
        now = pygame.time.get_ticks()
        elapsed = now - trial_start

        # Advance trial
        if elapsed >= TRIAL_DURATION_MS:
            is_target = (current == prev_letters[2]) if trial_index > 2 else None
            if trial_index > 2:
                if response is not None:
                    if response == is_target:
                        correct += 1
                    else:
                        incorrect += 1
                    if rt is not None:
                        reaction_times.append(rt)
            # Shift history
            prev_letters[2] = prev_letters[1]
            prev_letters[1] = prev_letters[0]
            prev_letters[0] = current
            # Next letter
            if random.random() < match_prob and prev_letters[2] is not None:
                current = prev_letters[2]
            else:
                current = random.choice([c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c != prev_letters[2]])

            trial_index += 1
            trial_start = now
            reaction_clock = now
            response = None
            rt = None

        # Draw screen
        screen.fill(BLACK)
        draw_text("3-Back Game", FONT_MEDIUM, PURPLE, WIDTH//2, 60)
        if elapsed < LETTER_DISPLAY_MS:
            draw_text(current, FONT_LARGE, WHITE, WIDTH//2, HEIGHT//2)
        elif elapsed < LETTER_DISPLAY_MS + FADE_DURATION_MS:
            fade_elapsed = elapsed - LETTER_DISPLAY_MS
            alpha = max(0, 255 - int(255 * fade_elapsed / FADE_DURATION_MS))
            draw_text(current, FONT_LARGE, WHITE, WIDTH//2, HEIGHT//2, alpha)

        # Buttons inactive for first three trials
        highlight = None
        if trial_index > 2:
            if response is True:
                highlight = "right"
            elif response is False:
                highlight = "left"
        draw_buttons(highlight)
        pygame.display.flip()

        # Handle events
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                running = False
            if trial_index > 2 and response is None:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT:
                        response = False
                        rt = pygame.time.get_ticks() - reaction_clock
                    elif e.key == pygame.K_RIGHT:
                        response = True
                        rt = pygame.time.get_ticks() - reaction_clock
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = e.pos
                    if no_match_btn.collidepoint(mx, my):
                        response = False
                        rt = pygame.time.get_ticks() - reaction_clock
                    elif match_btn.collidepoint(mx, my):
                        response = True
                        rt = pygame.time.get_ticks() - reaction_clock

        clock.tick(FPS)

    # Save summary (exclude first three trials)
    total_effective = max(0, trial_index - 3)
    save_summary(correct, incorrect, reaction_times, total_effective)
    pygame.quit()

if __name__ == "__main__":
    run_game()
