import pygame
import random
import csv
import os
import sys

if len(sys.argv) > 1:
    PARTICIPANT_ID = sys.argv[1]
else:
    PARTICIPANT_ID = "P01"

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
FPS = 60
GAME_DURATION = 297000
STEP_DURATION = 11000
INTERVAL_COUNT = GAME_DURATION // STEP_DURATION
NONRED_BALLOONS_TOTAL = 1000
RED = (255, 0, 0)
COLORS = [(0, 255, 0), (0, 0, 255), (255, 255, 0)]
BACKGROUND_COLOR = (30, 30, 30)
LINE_COLOR = (255, 255, 0)
BORDER_COLOR = (64, 64, 64)
CROSSHAIR_RED = (255, 0, 0)
CROSSHAIR_GREEN = (0, 255, 0)
LINE_MARGIN = 120
PATTERN = [2, 4, 6, 8, 10, 12, 14, 12, 10, 8, 6, 4, 2]
PHASE_COUNT = len(PATTERN)
CYCLE_DURATION = PHASE_COUNT * STEP_DURATION

class Balloon:
    def __init__(self, x, y, color, speed, spawn_time):
        self.x = x
        self.y = y
        self.radius = 20
        self.color = color
        self.speed = speed
        self.spawn_time = spawn_time
        self.touched_line = False
    def update(self, dt):
        self.y += self.speed * dt
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    def is_clicked(self, pos):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return dx*dx + dy*dy <= self.radius*self.radius

class Game:
    def __init__(self):
        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption('Red Balloon Shooter')
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        self.game_w = min(1000, WIDTH)
        self.game_h = min(800, HEIGHT)
        self.offset_x = (WIDTH - self.game_w) // 2
        self.offset_y = (HEIGHT - self.game_h) // 2
        self.interval_spawned = [0] * INTERVAL_COUNT
        self.interval_hits = [0] * INTERVAL_COUNT
        self.interval_reactions = [[] for _ in range(INTERVAL_COUNT)]
        self.interval_positions = [0] * INTERVAL_COUNT
        self.balloons = []
        self.line_y = self.offset_y + LINE_MARGIN
        self.crosshair_color = CROSSHAIR_RED
        self.shot_timer = 0
        self.red_schedule = []
        cycles = (GAME_DURATION + CYCLE_DURATION - 1) // CYCLE_DURATION
        for c in range(cycles):
            base = c * CYCLE_DURATION
            for i, count in enumerate(PATTERN):
                phase_start = base + i * STEP_DURATION
                if phase_start >= GAME_DURATION:
                    break
                interval = STEP_DURATION / count
                for j in range(count):
                    t = phase_start + j * interval
                    if t < GAME_DURATION:
                        self.red_schedule.append(t)
        self.red_schedule.sort()
        self.next_red_idx = 0
        self.last_nonred = pygame.time.get_ticks()
        self.nonred_spawned = 0

    def get_speed(self, elapsed):
        cycle_pos = elapsed % CYCLE_DURATION
        phase_idx = min(int(cycle_pos // STEP_DURATION), PHASE_COUNT - 1)
        half = PHASE_COUNT // 2
        ratio = phase_idx/half if phase_idx <= half else (PHASE_COUNT-1-phase_idx)/half
        ratio = max(0.0, min(ratio, 1.0))
        return 0.04 + (0.20 - 0.04) * ratio

    def save_data(self):
        save_dir = os.path.expanduser('~/OneDrive/Desktop/Mendi_vs_Octamon_Study/Balloon_performance')
        fn = f"{PARTICIPANT_ID}_balloon_performance.csv"
        os.makedirs(save_dir, exist_ok=True)
        path = os.path.join(save_dir, fn)
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['interval_start_s','spawned','hits','misses','avg_reaction_ms','range_pixels','line_pos_pixels'])
            interval_s = STEP_DURATION // 1000
            for i in range(INTERVAL_COUNT):
                start_s = (i+1) * interval_s
                spawned = self.interval_spawned[i]
                hits = self.interval_hits[i]
                misses = spawned - hits if spawned >= hits else 0
                reactions = self.interval_reactions[i]
                avg_rt = round(sum(reactions)/len(reactions), 2) if reactions else 0
                range_pixels = self.game_h - 2 * LINE_MARGIN
                pos_pixels = self.interval_positions[i] - (self.offset_y + LINE_MARGIN)
                w.writerow([start_s, spawned, hits, misses, avg_rt, range_pixels, pos_pixels])
        print(f"Results saved to {path}")

    def run(self):
        self.start_time = pygame.time.get_ticks()
        running = True
        while running:
            dt = self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            elapsed = now - self.start_time
            if elapsed >= GAME_DURATION:
                break
            speed = self.get_speed(elapsed)
            idx = min(int(elapsed // STEP_DURATION), INTERVAL_COUNT - 1)
            while self.next_red_idx < len(self.red_schedule) and elapsed >= self.red_schedule[self.next_red_idx]:
                x = random.randint(self.offset_x+20, self.offset_x+self.game_w-20)
                self.balloons.append(Balloon(x, self.offset_y, RED, speed, elapsed))
                self.interval_spawned[idx] += 1
                self.next_red_idx += 1
            if now - self.last_nonred >= 600 and self.nonred_spawned < NONRED_BALLOONS_TOTAL:
                x = random.randint(self.offset_x+20, self.offset_x+self.game_w-20)
                self.balloons.append(Balloon(x, self.offset_y, random.choice(COLORS), speed, elapsed))
                self.nonred_spawned += 1
                self.last_nonred = now
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    running = False
                if e.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = pygame.mouse.get_pos()
                    for b in self.balloons[:]:
                        if b.color == RED and b.is_clicked(click_pos):
                            reaction = elapsed - b.spawn_time
                            self.interval_reactions[idx].append(reaction)
                            self.interval_hits[idx] += 1
                            old_y = self.line_y
                            new_y = max(self.offset_y + LINE_MARGIN, self.line_y - 10)
                            self.line_y = new_y
                            self.crosshair_color = CROSSHAIR_GREEN
                            self.shot_timer = now
                            self.balloons.remove(b)
                            break
            if now - self.shot_timer > 150:
                self.crosshair_color = CROSSHAIR_RED
            drag = 0
            for b in self.balloons[:]:
                b.speed = speed
                b.update(dt)
                if b.color == RED and not b.touched_line and b.y + b.radius >= self.line_y:
                    b.touched_line = True
                if b.color == RED and b.y + b.radius >= self.line_y:
                    drag = max(drag, b.speed)
                if b.y > self.offset_y + self.game_h + b.radius:
                    self.balloons.remove(b)
            if drag > 0:
                old_y = self.line_y
                self.line_y = min(self.offset_y + self.game_h - LINE_MARGIN, self.line_y + drag * dt)
            self.screen.fill(BACKGROUND_COLOR)
            pygame.draw.rect(self.screen, BORDER_COLOR, (self.offset_x, self.offset_y, self.game_w, self.game_h), 3)
            pygame.draw.line(self.screen, LINE_COLOR, (self.offset_x, self.line_y), (self.offset_x + self.game_w, self.line_y), 3)
            self.interval_positions[idx] = self.line_y
            dash_len = 20
            half = dash_len // 2
            mid_y = self.offset_y + LINE_MARGIN
            top_y = self.offset_y + self.game_h - LINE_MARGIN
            pygame.draw.line(self.screen, CROSSHAIR_GREEN, (self.offset_x, mid_y), (self.offset_x + half, mid_y), 3)
            pygame.draw.line(self.screen, CROSSHAIR_GREEN, (self.offset_x + self.game_w - half, mid_y), (self.offset_x + self.game_w, mid_y), 3)
            pygame.draw.line(self.screen, CROSSHAIR_GREEN, (self.offset_x, top_y), (self.offset_x + half, top_y), 3)
            pygame.draw.line(self.screen, CROSSHAIR_GREEN, (self.offset_x + self.game_w - half, top_y), (self.offset_x + self.game_w, top_y), 3)
            for b in self.balloons:
                b.draw(self.screen)
            mx, my = pygame.mouse.get_pos()
            pygame.draw.circle(self.screen, self.crosshair_color, (mx, my), 21, 2)
            pygame.draw.circle(self.screen, self.crosshair_color, (mx, my), 13, 1)
            pygame.draw.line(self.screen, self.crosshair_color, (mx-21, my), (mx+21, my), 2)
            pygame.draw.line(self.screen, self.crosshair_color, (mx, my-21), (mx, my+21), 2)
            pygame.display.flip()
        self.save_data()
        pygame.quit()

if __name__ == '__main__':
    Game().run()
