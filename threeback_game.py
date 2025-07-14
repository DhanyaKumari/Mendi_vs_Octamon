import pygame
import random
import csv
import os
import time

import sys

# override default ID if passed via CLI
if len(sys.argv) > 1:
    PARTICIPANT_ID = sys.argv[1]
else:
    PARTICIPANT_ID = "P01"   # fallback

# Settings
WIDTH, HEIGHT = 800, 600
FPS = 60
TRIAL_DURATION_MS = 2000
LETTER_DISPLAY_MS = 1000
FADE_DURATION_MS = 20
TOTAL_DURATION_SEC = 150
TOTAL_TRIALS = TOTAL_DURATION_SEC * 1000 // TRIAL_DURATION_MS

SAVE_PATH = rf"C:\Users\HP\OneDrive\Desktop\Mendi_vs_Octamon_Study\Three_back_performance\{PARTICIPANT_ID}_3-back_performance.csv"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 255)
DARK_PURPLE = (88, 0, 180)
BLUE = (0, 150, 255)
DARK_BLUE = (0, 100, 180)
GRAY = (100, 100, 100)

pygame.init()

# Fonts
try:
    FONT_LARGE = pygame.font.SysFont("lato", 250)
    FONT_MEDIUM = pygame.font.SysFont("lato", 60)
    FONT_SMALL = pygame.font.SysFont("lato", 36)
except:
    FONT_LARGE = pygame.font.SysFont("arial", 250)
    FONT_MEDIUM = pygame.font.SysFont("arial", 60)
    FONT_SMALL = pygame.font.SysFont("arial", 36)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3-Back Game")
clock = pygame.time.Clock()

# Functions

def draw_text(text, font, color, x, y):
    label = font.render(text, True, color)
    rect = label.get_rect(center=(x, y))
    screen.blit(label, rect)


def draw_buttons(highlight=None):
    left_color = DARK_PURPLE if highlight == "left" else PURPLE
    right_color = DARK_BLUE if highlight == "right" else BLUE

    pygame.draw.rect(screen, left_color, no_match_btn, border_radius=10)
    pygame.draw.rect(screen, WHITE, no_match_btn, 2, border_radius=10)
    draw_text("NO MATCH", FONT_SMALL, WHITE, no_match_btn.centerx, no_match_btn.centery)

    pygame.draw.rect(screen, right_color, match_btn, border_radius=10)
    pygame.draw.rect(screen, WHITE, match_btn, 2, border_radius=10)
    draw_text("MATCH", FONT_SMALL, WHITE, match_btn.centerx, match_btn.centery)


def run_game():
    global no_match_btn, match_btn
    results = []
    prev_letters = [None, None, None]  # [last, two-back, three-back]
    current_letter = None
    match_prob = 0.5
    trial_index = 0
    user_response = None
    reaction_time = None
    reaction_times = []
    correct_responses = 0
    incorrect_responses = 0
    missed_targets = 0
    clicked = None

    no_match_btn = pygame.Rect(WIDTH // 2 - 200, HEIGHT - 120, 180, 80)
    match_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT - 120, 180, 80)

    trial_start_time = pygame.time.get_ticks()
    input_ready = False

    while trial_index < TOTAL_TRIALS:
        current_time = pygame.time.get_ticks()
        elapsed = current_time - trial_start_time

        # Advance trial
        if elapsed >= TRIAL_DURATION_MS:
            # Determine if target: only from fourth trial onward (trial_index > 2)
            is_target = (current_letter == prev_letters[2]) if trial_index > 2 else None
            correct = (user_response == is_target) if is_target is not None else None

            # Score updates start from fourth trial
            if trial_index > 2:
                if user_response is not None:
                    if correct:
                        correct_responses += 1
                    else:
                        incorrect_responses += 1
                    if reaction_time is not None:
                        reaction_times.append(reaction_time)
                elif is_target:
                    missed_targets += 1

            # Log
            results.append({
                "Trial": trial_index + 1,
                "Stimulus": current_letter,
                "Is Target": is_target,
                "Response": user_response,
                "Correct": correct,
                "Reaction Time (ms)": reaction_time
            })

            # Prep next
            trial_index += 1
            trial_start_time = current_time
            input_ready = False

            # Shift history
            prev_letters[2] = prev_letters[1]
            prev_letters[1] = prev_letters[0]
            prev_letters[0] = current_letter

            # Generate next letter
            is_match = (random.random() < match_prob and prev_letters[2] is not None)
            if is_match:
                current_letter = prev_letters[2]
            else:
                choices = [l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if l != prev_letters[2]]
                current_letter = random.choice(choices)

            user_response = None
            reaction_time = None
            reaction_clock = pygame.time.get_ticks()
            input_ready = True
            clicked = None

                # Draw
        screen.fill(BLACK)
        draw_text("3-Back Game", FONT_MEDIUM, PURPLE, WIDTH // 2, 60)
        trial_phase_time = pygame.time.get_ticks() - trial_start_time
        if trial_phase_time < LETTER_DISPLAY_MS:
            draw_text(current_letter, FONT_LARGE, WHITE, WIDTH // 2, HEIGHT // 2)
        # Only highlight buttons after the 3-back is valid (from fourth trial)
        if trial_index > 2:
            draw_buttons(clicked)
        else:
            draw_buttons(None)
        pygame.display.flip()

        # Handle events: responses only from fourth trial
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            # Only allow input after trial 3
            elif user_response is None and trial_index > 2:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        user_response = False
                        clicked = "left"
                        reaction_time = pygame.time.get_ticks() - reaction_clock
                    elif event.key == pygame.K_RIGHT:
                        user_response = True
                        clicked = "right"
                        reaction_time = pygame.time.get_ticks() - reaction_clock
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if no_match_btn.collidepoint(mx, my):
                        user_response = False
                        clicked = "left"
                        reaction_time = pygame.time.get_ticks() - reaction_clock
                    elif match_btn.collidepoint(mx, my):
                        user_response = True
                        clicked = "right"
                        reaction_time = pygame.time.get_ticks() - reaction_clock

        clock.tick(FPS)

    # Save
    try:
        with open(SAVE_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
            f.write("\n")
            total_trials = TOTAL_TRIALS - 3  # exclude first three
            accuracy = (correct_responses / total_trials) * 100 if total_trials > 0 else 0
            mean_rt = sum(reaction_times) / len(reaction_times) if reaction_times else 0
            summary = {
                "participant_id": PARTICIPANT_ID,
                "total_trials": total_trials,
                "correct_responses": correct_responses,
                "incorrect_responses": incorrect_responses,
                "missed_targets": missed_targets,
                "accuracy": round(accuracy, 2),
                "mean_reaction_time": round(mean_rt, 2)
            }
            for key, value in summary.items():
                f.write(f"{key},{value}\n")
        print(f"✅ Three back results saved to: {SAVE_PATH}")
    except Exception as e:
        print(f"Save failed: {e}")

    # End screen
    screen.fill(BLACK)
    draw_text("Time's Up!", FONT_SMALL, WHITE, WIDTH // 2, HEIGHT // 2)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()

if __name__ == "__main__":
    run_game()
