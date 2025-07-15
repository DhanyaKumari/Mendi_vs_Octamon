import pygame
import random
import csv
import os
import sys

# override default ID if passed via CLI
if len(sys.argv) > 1:
    PARTICIPANT_ID = sys.argv[1]
else:
    PARTICIPANT_ID = "P01"   # fallback

# Settings
WIDTH, HEIGHT = 800, 600
FPS = 60
GAME_DURATION = 302000  # 5 min 2 sec in ms

# Balloon count
RED_BALLOONS_TOTAL = 350  # fixed per participant (increased to 350)
NONRED_BALLOONS_TOTAL = 600

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
COLORS = [GREEN, BLUE, YELLOW]
BACKGROUND_COLOR = (30, 30, 30)
LINE_COLOR = (255, 255, 0)
CROSSHAIR_RED = (255, 0, 0)
CROSSHAIR_GREEN = (0, 255, 0)

# Participant & save
home = os.path.expanduser('~')
top_dir = os.path.join(home, 'OneDrive', 'Desktop', 'Mendi_vs_Octamon_Study','Balloon_performance' )

SAVE_PATH = os.path.join(top_dir, f"{PARTICIPANT_ID}_balloon_performance.csv")

# Speed settings
BORING_SPEED = 0.04
INTENSE_SPEED = 0.15

# Define major low/high phases (ms) for 7 phases: low, high, low, high, low, high, low
# Split GAME_DURATION into 7 equal windows
PHASE_COUNT = 7
phase_length = GAME_DURATION / PHASE_COUNT
major_phases = []
for i, label in enumerate(['boring', 'intense', 'boring', 'intense', 'boring', 'intense', 'boring']):
    start = int(i * phase_length)
    end = int((i + 1) * phase_length)
    major_phases.append((start, end, label))

# Assign red counts per phase: give fewer reds in boring and more in intense
boring_weight = 0.2
intense_weight = 1
phase_weights = [boring_weight if p[2]=='boring' else intense_weight for p in major_phases]
total_weight = sum(phase_weights)
unit = RED_BALLOONS_TOTAL/total_weight
red_per_phase = [int(round(w*unit)) for w in phase_weights]
# adjust rounding
diff = RED_BALLOONS_TOTAL - sum(red_per_phase)
for i in range(abs(diff)):
    idx = i % PHASE_COUNT
    red_per_phase[idx] += 1 if diff>0 else -1

# Build a phase-by-phase spawn schedule to guarantee distribution and interleaving
SPAWN_SCHEDULE = []  # list of 'red' or 'nonred'
for idx, (start, end, label) in enumerate(major_phases):
    phase_len = end - start
    # interval per phase
    interval = 200 if label=='intense' else 1500
    event_count = max(1, int(phase_len/interval))
    red_count = red_per_phase[idx]
    nonred_count = max(0, event_count - red_count)
    phase_list = ['red']*red_count + ['nonred']*nonred_count
    random.shuffle(phase_list)
    SPAWN_SCHEDULE.extend(phase_list)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Red Balloon Shooter')
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)

        self.balloons = []
        self.line_y = HEIGHT // 2
        self.red_shot = 0
        self.total_shots = 0
        self.crosshair_color = CROSSHAIR_RED
        self.shot_feedback_timer = 0

        # Use precomputed schedule
        self.spawn_schedule = SPAWN_SCHEDULE.copy()
        self.spawn_index = 0

        self.start_time = None
        self.last_spawn = None

    def run(self):
        self.start_time = pygame.time.get_ticks()
        self.last_spawn = self.start_time
        running = True

        while running:
            dt = self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            elapsed = now - self.start_time

            # End game
            if elapsed >= GAME_DURATION or self.spawn_index >= len(self.spawn_schedule):
                total_spawned = RED_BALLOONS_TOTAL
                missed = total_spawned - self.red_shot
                acc = round((self.red_shot/total_spawned)*100,2)
                try:
                    with open(SAVE_PATH,'w',newline='') as f:
                        w=csv.writer(f)
                        w.writerow(['participant_id','total_red_spawned','red_shot','red_missed','accuracy_percent','total_clicks'])
                        w.writerow([PARTICIPANT_ID,total_spawned,self.red_shot,missed,acc,self.total_shots])
                    print(f'✅ Red Balloon results saved to: {SAVE_PATH}')
                except:
                    fallback = os.path.join(os.getcwd(), f'{PARTICIPANT_ID}_balloon_performance.csv')
                    with open(fallback,'w',newline='') as f:
                        w=csv.writer(f)
                        w.writerow(['participant_id','total_red_spawned','red_shot','red_missed','accuracy_percent','total_clicks'])
                        w.writerow([PARTICIPANT_ID,total_spawned,self.red_shot,missed,acc,self.total_shots])
                    print(f'⚠️ Saved to: {fallback}')
                break

            # Determine speed & interval based on phase
            phase_idx = min(int(elapsed/phase_length), PHASE_COUNT-1)
            _,_,label = major_phases[phase_idx]
            speed = INTENSE_SPEED if label=='intense' else BORING_SPEED
            interval = 200 if label=='intense' else 1500

            # Spawn using schedule
            if now - self.last_spawn >= interval and self.spawn_index < len(self.spawn_schedule):
                entry = self.spawn_schedule[self.spawn_index]
                self.spawn_index += 1
                if entry=='red':
                    col = RED
                else:
                    col = random.choice(COLORS)
                self.balloons.append(Balloon(random.randint(20,WIDTH-20),col,speed))
                self.last_spawn = now

diff = RED_BALLOONS_TOTAL - sum(red_per_phase)
for i in range(abs(diff)):
    idx = i % PHASE_COUNT
    red_per_phase[idx] += 1 if diff>0 else -1
diff = RED_BALLOONS_TOTAL - sum(red_per_phase)
for i in range(abs(diff)):
    idx = i % PHASE_COUNT
    red_per_phase[idx] += 1 if diff>0 else -1

class Balloon:
    def __init__(self, x, color, speed):
        self.x, self.y = x, 0
        self.radius = 19
        self.color = color
        self.speed = speed
    def update(self, dt): self.y += self.speed * dt
    def draw(self, screen): pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    def is_clicked(self, pos): dx, dy = pos[0]-self.x, pos[1]-self.y; return dx*dx+dy*dy<=self.radius*self.radius

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Red Balloon Shooter')
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)

        self.balloons = []
        self.line_y = HEIGHT // 2
        self.red_shot = 0
        self.total_shots = 0
        self.crosshair_color = CROSSHAIR_RED
        self.shot_feedback_timer = 0

        # Phase counters
        self.red_phase_remaining = red_per_phase.copy()
        self.nonred_remaining = NONRED_BALLOONS_TOTAL

        self.start_time = None
        self.last_spawn = None

    def get_speed(self, elapsed):
        # same detailed speed phases as before
        t = GAME_DURATION - elapsed
        to_ms = lambda s: s * 1000
        phases = [
            (302, 264, 'boring'), (264, 258, 'ramp_up'), (258, 220, 'intense'), (220, 214, 'ramp_down'),
            (214, 176, 'boring'), (176, 170, 'ramp_up'), (170, 132, 'intense'), (132, 126, 'ramp_down'),
            (126, 88, 'boring'), (88, 82, 'ramp_up'), (82, 44, 'intense'), (44, 38, 'ramp_down'), (38, 0, 'boring')
        ]
        for start, end, label in phases:
            if to_ms(end) <= t < to_ms(start):
                if label == 'boring':
                    return BORING_SPEED
                if label == 'intense':
                    return INTENSE_SPEED
                p = (to_ms(start) - t) / (to_ms(start) - to_ms(end))
                if label == 'ramp_up':
                    return BORING_SPEED + p * (INTENSE_SPEED - BORING_SPEED)
                if label == 'ramp_down':
                    return INTENSE_SPEED - p * (INTENSE_SPEED - BORING_SPEED)
        return BORING_SPEED

    def run(self):
        self.start_time = pygame.time.get_ticks()
        self.last_spawn = self.start_time
        running = True

        while running:
            dt = self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            elapsed = now - self.start_time

            # End game
            if elapsed >= GAME_DURATION:
                total_spawned = sum(red_per_phase)  # 300 exactly
                missed = total_spawned - self.red_shot
                acc = round((self.red_shot / total_spawned) * 100, 2)
                try:
                    with open(SAVE_PATH, 'w', newline='') as f:
                        w = csv.writer(f)
                        w.writerow(['participant_id', 'total_red_spawned', 'red_shot', 'red_missed', 'accuracy_percent', 'total_clicks'])
                        w.writerow([PARTICIPANT_ID, total_spawned, self.red_shot, missed, acc, self.total_shots])
                    print(f'✅ Red balloon results saved to: {SAVE_PATH}')
                except Exception:
                    fallback = os.path.join(os.getcwd(), f'{PARTICIPANT_ID}_balloon_performance.csv')
                    with open(fallback, 'w', newline='') as f:
                        w = csv.writer(f)
                        w.writerow(['participant_id', 'total_red_spawned', 'red_shot', 'red_missed', 'accuracy_percent', 'total_clicks'])
                        w.writerow([PARTICIPANT_ID, total_spawned, self.red_shot, missed, acc, self.total_shots])
                    print(f'Saved to: {fallback}')
                break

            # Determine speed & interval
            speed = self.get_speed(elapsed)
            if speed >= INTENSE_SPEED:
                interval = 200
            elif speed <= BORING_SPEED:
                interval = 1500
            else:
                interval = 700

            # Spawn logic
            if now - self.last_spawn >= interval:
                # determine current major phase index
                phase_idx = min(int(elapsed / phase_length), PHASE_COUNT - 1)
                phase_start, phase_end, _ = major_phases[phase_idx]
                # compute spawn events left in phase
                remaining_phase_time = phase_end - elapsed
                spawn_events_left = max(1, int(remaining_phase_time / interval))
                # probability of red for target distribution
                red_left = self.red_phase_remaining[phase_idx]
                prob_red = red_left / spawn_events_left
                if random.random() < prob_red and red_left > 0:
                    col = RED
                    self.red_phase_remaining[phase_idx] -= 1
                else:
                    col = random.choice(COLORS)
                    if self.nonred_remaining > 0:
                        self.nonred_remaining -= 1
                self.balloons.append(Balloon(random.randint(20, WIDTH - 20), col, speed))
                self.last_spawn = now

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.total_shots += 1
                    for b in self.balloons[:]:
                        if b.color == RED and b.is_clicked(pos):
                            self.balloons.remove(b)
                            self.red_shot += 1
                            # Move line up one step when red is shot
                            self.line_y = max(0, self.line_y - 10)
                            self.crosshair_color = CROSSHAIR_GREEN
                            self.shot_feedback_timer = now
                            break

            # Reset crosshair color
            if now - self.shot_feedback_timer > 150:
                self.crosshair_color = CROSSHAIR_RED

            # Update balloons & line
            dragging = 0
            for b in list(self.balloons):
                b.speed = speed
                b.update(dt)
                if b.color == RED and b.y + b.radius >= self.line_y:
                    dragging = max(dragging, b.speed)
                if b.y > HEIGHT + b.radius:
                    self.balloons.remove(b)
            if dragging > 0:
                self.line_y = min(HEIGHT - 40, self.line_y + dragging * dt)

            # Draw everything
            self.screen.fill(BACKGROUND_COLOR)
            pygame.draw.line(self.screen, LINE_COLOR, (0, self.line_y), (WIDTH, self.line_y), 3)
            for b in self.balloons:
                b.draw(self.screen)
            x, y = pygame.mouse.get_pos()
            size = 21;
            inner_size = 13;
            pygame.draw.circle(self.screen, self.crosshair_color, (x, y), size, 2)
            pygame.draw.circle(self.screen, self.crosshair_color, (x, y), inner_size, 1)
            pygame.draw.line(self.screen, self.crosshair_color, (x - size, y), (x + size, y), 2)
            pygame.draw.line(self.screen, self.crosshair_color, (x, y - size), (x, y + size), 2)
            pygame.display.flip()

        pygame.quit()

if __name__ == '__main__':
    Game().run()
