import pygame
import random
import csv
import os
import time
import sys
import string

# Override default ID if passed via CLI
if len(sys.argv) > 1:
    PARTICIPANT_ID = sys.argv[1]
else:
    PARTICIPANT_ID = "P01"

# Initialize Pygame and set full screen
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("1-Back Game (Full Screen)")
clock = pygame.time.Clock()

# Settings
FPS = 60
TRIAL_DURATION_MS = 2000      # Total trial duration (ms)
LETTER_DISPLAY_MS = 1000      # Letter display duration (ms)
FADE_DURATION_MS = 20         # Fade duration (ms)
TOTAL_TRIALS = 73             # 1 warm-up + 60 scored
TOTAL_DURATION_SEC = 146      # ~2 minutes + 2 seconds to allow 61 trials
MATCH_RATIO = 0.3             # 30% matches

# Prepare save directory and path
BASE_SAVE_DIR = os.path.join(
    os.path.expanduser("~"),
    "OneDrive", "Desktop", "Mendi_vs_Octamon_Study", "One_back_performance"
)
os.makedirs(BASE_SAVE_DIR, exist_ok=True)
SAVE_PATH = os.path.join(BASE_SAVE_DIR, f"{PARTICIPANT_ID}_1-back_performance.csv")

# Colors & Fonts
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
PURPLE, DARK_PURPLE = (128, 0, 255), (88, 0, 180)
BLUE, DARK_BLUE = (0, 150, 255), (0, 100, 180)
try:
    FONT_LARGE = pygame.font.SysFont("lato", 500)
    FONT_MEDIUM = pygame.font.SysFont("lato", 90)
    FONT_BUTTON = pygame.font.SysFont("lato", 50)
    FONT_SMALL = pygame.font.SysFont("lato", 36)
except:
    FONT_LARGE = pygame.font.SysFont("arial", 500)
    FONT_MEDIUM = pygame.font.SysFont("arial", 90)
    FONT_BUTTON = pygame.font.SysFont("arial", 50)
    FONT_SMALL = pygame.font.SysFont("arial", 36)

btn_w, btn_h = 260, 90
spacing = 50
total_width = btn_w * 2 + spacing
x_start = WIDTH//2 - total_width//2
no_match_btn = pygame.Rect(x_start, HEIGHT - btn_h - 40, btn_w, btn_h)
match_btn    = pygame.Rect(x_start + btn_w + spacing, HEIGHT - btn_h - 40, btn_w, btn_h)

def draw_text(text, font, color, x, y, alpha=255):
    surf = font.render(text, True, color)
    if alpha < 255:
        surf.set_alpha(alpha)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)

def draw_buttons(highlight):
    left_color  = DARK_PURPLE if highlight == "left" else PURPLE
    right_color = DARK_BLUE   if highlight == "right" else BLUE
    pygame.draw.rect(screen, left_color,  no_match_btn, border_radius=15)
    pygame.draw.rect(screen, WHITE,       no_match_btn, 3, border_radius=15)
    draw_text("NO MATCH", FONT_BUTTON, WHITE, no_match_btn.centerx, no_match_btn.centery)
    pygame.draw.rect(screen, right_color, match_btn,    border_radius=15)
    pygame.draw.rect(screen, WHITE,       match_btn,    3, border_radius=15)
    draw_text("MATCH",    FONT_BUTTON, WHITE, match_btn.centerx,    match_btn.centery)

def generate_matches(n, ratio):
    target = int(n * ratio)
    matches = []
    count = 0
    for i in range(n):
        remaining = n - i
        rem_needed = target - count
        if i == 0 or rem_needed <= 0:
            matches.append(False)
        else:
            if matches[-1]:
                matches.append(False)
            else:
                if random.random() < rem_needed / remaining:
                    matches.append(True)
                    count += 1
                else:
                    matches.append(False)
    return matches

def generate_sequence(matches):
    seq = []
    letters = string.ascii_uppercase
    for i, is_match in enumerate(matches):
        if i == 0 or not is_match:
            opts = letters
            if len(seq) >= 2 and seq[-1] == seq[-2]:
                opts = [l for l in letters if l != seq[-1]]
            elif seq:
                opts = [l for l in letters if l != seq[-1]]
            seq.append(random.choice(opts))
        else:
            seq.append(seq[-1])
    return seq

to_match = generate_matches(TOTAL_TRIALS, MATCH_RATIO)
sequence = generate_sequence(to_match)

def save_summary(correct, incorrect, reaction_times, total_trials):
    missed = total_trials - (correct + incorrect)
    accuracy = (correct / total_trials * 100) if total_trials > 0 else 0
    mean_rt = sum(reaction_times) / len(reaction_times) if reaction_times else 0
    
    try:
        with open(SAVE_PATH, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(["metric","value"])
            w.writerow(["total_trials", total_trials])
            w.writerow(["correct_responses", correct])
            w.writerow(["incorrect_responses", incorrect])
            w.writerow(["missed_targets", missed])
            w.writerow(["accuracy", round(accuracy,2)])
            w.writerow(["mean_reaction_time", round(mean_rt,2)])
        print(f"✅ 1-back results saved to: {SAVE_PATH}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")

def run_game():
    correct = incorrect = 0
    reaction_times = []
    idx = 0
    response = None
    rt = None
    start = pygame.time.get_ticks()
    react_clock = start
    running = True

    while running and idx < TOTAL_TRIALS:
        now = pygame.time.get_ticks()
        elapsed = now - start
        if elapsed >= TRIAL_DURATION_MS:
            if idx > 0 and response is not None:
                if response == to_match[idx]: correct += 1
                else: incorrect += 1
                if rt is not None: reaction_times.append(rt)
            idx += 1
            response = rt = None
            start = now
            react_clock = now

        screen.fill(BLACK)
        draw_text("1-Back Game", FONT_MEDIUM, PURPLE, WIDTH//2, 60)
        if idx < TOTAL_TRIALS:
            letter = sequence[idx]
            if elapsed < LETTER_DISPLAY_MS:
                draw_text(letter, FONT_LARGE, WHITE, WIDTH//2, HEIGHT//2)
            elif elapsed < LETTER_DISPLAY_MS + FADE_DURATION_MS:
                fade = elapsed - LETTER_DISPLAY_MS
                alpha = max(0, 255 - int(255 * fade / FADE_DURATION_MS))
                draw_text(letter, FONT_LARGE, WHITE, WIDTH//2, HEIGHT//2, alpha)

        highlight = None if idx == 0 else ("right" if response else ("left" if response == False else None))
        draw_buttons(highlight)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE): running = False
            if idx > 0 and e.type == pygame.KEYDOWN and response is None:
                if e.key == pygame.K_LEFT:
                    response = False
                    rt = pygame.time.get_ticks() - react_clock
                elif e.key == pygame.K_RIGHT:
                    response = True
                    rt = pygame.time.get_ticks() - react_clock
        clock.tick(FPS)

    # Exclude first warm-up trial from scoring -> leaves exactly 60 scored trials
    total_scored_trials = max(0, idx - 1)
    save_summary(correct, incorrect, reaction_times, total_scored_trials)
    pygame.quit()

if __name__ == "__main__":
    run_game()
