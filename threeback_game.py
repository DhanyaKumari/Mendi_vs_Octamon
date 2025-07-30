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
    PARTICIPANT_ID = "test"

# Initialize Pygame and set full screen
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("3-Back Game (Full Screen)")
clock = pygame.time.Clock()

# Settings
FPS = 60
TRIAL_DURATION_MS = 2000      # Total trial duration (ms)
LETTER_DISPLAY_MS = 1000      # Letter display duration (ms)
FADE_DURATION_MS = 20         # Fade duration (ms)
TOTAL_TRIALS = 75             # 3 warm-ups + 60 scored trials
TOTAL_DURATION_SEC = 150      # ~2 minutes 6 seconds to allow 63 letters
MATCH_RATIO = 0.3             # 30% matches

# Prepare save directory and path
BASE_SAVE_DIR = os.path.join(
    os.path.expanduser("~"),
    "OneDrive", "Desktop", "Mendi_vs_Octamon_Study", "Three_back_performance"
)
os.makedirs(BASE_SAVE_DIR, exist_ok=True)
def get_unique_save_path(base_dir, participant_id, task_name):
    i = 1
    base_name = f"{participant_id}_{task_name}.csv"
    full_path = os.path.join(base_dir, base_name)
    while os.path.exists(full_path):
        full_path = os.path.join(base_dir, f"{participant_id}_{task_name}_v{i}.csv")
        i += 1
    return full_path

SAVE_PATH = get_unique_save_path(BASE_SAVE_DIR, PARTICIPANT_ID, "3-back_performance")

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

# Button setup
btn_w, btn_h = 260, 90
spacing = 50
total_w = btn_w * 2 + spacing
x0 = WIDTH//2 - total_w//2
no_match_btn = pygame.Rect(x0, HEIGHT - btn_h - 40, btn_w, btn_h)
match_btn    = pygame.Rect(x0 + btn_w + spacing, HEIGHT - btn_h - 40, btn_w, btn_h)

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
    flags = []
    count = 0
    for i in range(n):
        remaining = n - i
        needed = target - count
        if i < 3 or needed <= 0 or (flags and flags[-1]):
            flags.append(False)
        else:
            if random.random() < needed / remaining:
                flags.append(True)
                count += 1
            else:
                flags.append(False)
    return flags

def generate_sequence(matches):
    seq = []
    letters = string.ascii_uppercase
    for i, is_match in enumerate(matches):
        if i < 3 or not is_match:
            if i >= 3:
                opts = [l for l in letters if l != seq[i-3]]
            else:
                opts = letters
            seq.append(random.choice(opts))
        else:
            seq.append(seq[i-3])
    return seq

to_match = generate_matches(TOTAL_TRIALS, MATCH_RATIO)
sequence = generate_sequence(to_match)

def save_summary(correct, incorrect, reaction_times, total_trials):
    missed = total_trials - (correct + incorrect)
    accuracy = (correct / total_trials) * 100 if total_trials > 0 else 0
    mean_rt = sum(reaction_times) / len(reaction_times) if reaction_times else 0

    try:
        with open(SAVE_PATH, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(["metric", "value"])
            w.writerow(["total_trials", total_trials])
            w.writerow(["correct_responses", correct])
            w.writerow(["incorrect_responses", incorrect])
            w.writerow(["missed_targets", missed])
            w.writerow(["accuracy_percent", round(accuracy, 2)])
            w.writerow(["mean_reaction_time_ms", round(mean_rt, 2)])
        print(f"✅ 3-back results saved to: {SAVE_PATH}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")

def run_game():
    correct = incorrect = 0
    reaction_times = []
    idx = 0
    response = None
    rt = None

    start_time = pygame.time.get_ticks()
    react_clock = start_time

    running = True
    while running:
        if idx >= TOTAL_TRIALS:
            break

        now = pygame.time.get_ticks()
        elapsed = now - start_time

        if elapsed >= TRIAL_DURATION_MS:
            if idx >= 3:
                if response is not None:
                    if response == to_match[idx]:
                        correct += 1
                    else:
                        incorrect += 1
                    if rt is not None:
                        reaction_times.append(rt)
            idx += 1
            response = None
            rt = None
            start_time = now
            react_clock = now
            if idx >= TOTAL_TRIALS:
                break

        screen.fill(BLACK)
        draw_text("3-Back Game", FONT_MEDIUM, PURPLE, WIDTH//2, 60)

        phase = pygame.time.get_ticks() - start_time
        if phase < LETTER_DISPLAY_MS:
            draw_text(sequence[idx], FONT_LARGE, WHITE, WIDTH//2, HEIGHT//2)
        elif phase < LETTER_DISPLAY_MS + FADE_DURATION_MS:
            fade = phase - LETTER_DISPLAY_MS
            alpha = max(0, 255 - int(255 * fade / FADE_DURATION_MS))
            draw_text(sequence[idx], FONT_LARGE, WHITE, WIDTH//2, HEIGHT//2, alpha)

        hl = None
        if idx >= 3 and response is not None:
            hl = "right" if response else "left"
        draw_buttons(hl)

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif idx >= 3 and response is None and ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_LEFT:
                    response = False
                    rt = pygame.time.get_ticks() - react_clock
                elif ev.key == pygame.K_RIGHT:
                    response = True
                    rt = pygame.time.get_ticks() - react_clock

        clock.tick(FPS)

    # scored trials = total - 3 warmups
    total_scored = max(0, idx - 3)
    save_summary(correct, incorrect, reaction_times, total_scored)
    pygame.quit()

if __name__ == "__main__":
    run_game()
