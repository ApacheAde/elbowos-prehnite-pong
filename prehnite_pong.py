#!/usr/bin/env python3
"""Prehnite Pong — neon pong/volley arcade for ElbowOS. Python 3 + pygame."""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv

if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/PREHNITE_PONG_ElbowOS.mp4")
TITLE, HANDLE = "PREHNITE PONG", "x.com/ElbowOS"

NAVY = (6, 10, 28)
CYAN = (0, 255, 220)
MAGENTA = (255, 40, 180)
GOLD = (255, 215, 0)
WHITE = (240, 245, 255)
TEAL = (0, 180, 200)
PURPLE = (140, 60, 220)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            self.screen = pygame.display.set_mode((W, H))
        self.font = pygame.font.SysFont("monospace", 64, bold=True)
        self.font_md = pygame.font.SysFont("monospace", 48, bold=True)
        self.font_sm = pygame.font.SysFont("monospace", 36)
        self.reset()

    def reset(self):
        self.ball_x = float(W // 2)
        self.ball_y = float(H // 2)
        self.ball_vx = random.choice([-14.0, 14.0])
        self.ball_vy = random.uniform(-10.0, 10.0)
        self.paddle_h = 220
        self.paddle_w = 28
        self.left_y = float(H // 2 - self.paddle_h // 2)
        self.right_y = float(H // 2 - self.paddle_h // 2)
        self.score_l = 0
        self.score_r = 0
        self.ball_r = 22

    def clamp_paddle(self, y):
        return max(80.0, min(float(H - 80 - self.paddle_h), y))

    def update(self, left_ai=True, right_ai=True):
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy
        if self.ball_y - self.ball_r < 60 or self.ball_y + self.ball_r > H - 60:
            self.ball_vy *= -1
            self.ball_y = max(self.ball_r + 60, min(H - 60 - self.ball_r, self.ball_y))

        # left paddle
        if self.ball_x - self.ball_r < 70 and abs(self.ball_y - (self.left_y + self.paddle_h / 2)) < self.paddle_h / 2 + 15:
            self.ball_vx = abs(self.ball_vx) + 0.3
            self.ball_vy += random.uniform(-3, 3)
            self.ball_x = 70 + self.ball_r

        # right paddle
        if self.ball_x + self.ball_r > W - 70 and abs(self.ball_y - (self.right_y + self.paddle_h / 2)) < self.paddle_h / 2 + 15:
            self.ball_vx = -abs(self.ball_vx) - 0.3
            self.ball_vy += random.uniform(-3, 3)
            self.ball_x = W - 70 - self.ball_r

        # score
        if self.ball_x < 0:
            self.score_r += 1
            self.reset_ball(dir=1)
        elif self.ball_x > W:
            self.score_l += 1
            self.reset_ball(dir=-1)

        # AI
        if left_ai:
            target = self.ball_y - self.paddle_h / 2
            self.left_y += (target - self.left_y) * 0.18
        if right_ai:
            target = self.ball_y - self.paddle_h / 2
            self.right_y += (target - self.right_y) * 0.18
        self.left_y = self.clamp_paddle(self.left_y)
        self.right_y = self.clamp_paddle(self.right_y)

    def reset_ball(self, dir=1):
        self.ball_x = float(W // 2)
        self.ball_y = float(H // 2)
        self.ball_vx = 14.0 * dir
        self.ball_vy = random.uniform(-12.0, 12.0)

    def draw(self):
        self.screen.fill(NAVY)
        # neon grid
        for x in range(0, W, 60):
            pygame.draw.line(self.screen, (20, 30, 60), (x, 0), (x, H), 1)
        for y in range(0, H, 60):
            pygame.draw.line(self.screen, (20, 30, 60), (0, y), (W, y), 1)
        # center line
        for y in range(100, H - 100, 50):
            pygame.draw.rect(self.screen, TEAL, (W // 2 - 4, y, 8, 25))
        # paddles with glow
        pygame.draw.rect(self.screen, CYAN, (30, int(self.left_y), self.paddle_w, self.paddle_h), border_radius=8)
        pygame.draw.rect(self.screen, (0, 180, 160), (30, int(self.left_y), self.paddle_w, self.paddle_h), 3, border_radius=8)
        pygame.draw.rect(self.screen, MAGENTA, (W - 58, int(self.right_y), self.paddle_w, self.paddle_h), border_radius=8)
        pygame.draw.rect(self.screen, (200, 20, 140), (W - 58, int(self.right_y), self.paddle_w, self.paddle_h), 3, border_radius=8)
        # ball
        pygame.draw.circle(self.screen, GOLD, (int(self.ball_x), int(self.ball_y)), self.ball_r)
        pygame.draw.circle(self.screen, WHITE, (int(self.ball_x), int(self.ball_y)), self.ball_r, 3)
        # overlays
        title = self.font.render(TITLE, True, GOLD)
        self.screen.blit(title, title.get_rect(center=(W // 2, 120)))
        score = self.font_md.render(f"{self.score_l}   —   {self.score_r}", True, WHITE)
        self.screen.blit(score, score.get_rect(center=(W // 2, 210)))
        handle = self.font_sm.render(HANDLE, True, CYAN)
        self.screen.blit(handle, handle.get_rect(center=(W // 2, H - 80)))
        hint = self.font_sm.render("W/S or ↑↓  |  ESC quit", True, TEAL)
        self.screen.blit(hint, hint.get_rect(center=(W // 2, H - 140)))

    def record(self):
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", OUT
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(FPS * SECS):
            self.update(True, True)
            self.draw()
            raw = pygame.image.tostring(self.screen, "RGB")
            proc.stdin.write(raw)
        proc.stdin.close()
        stderr = proc.stderr.read().decode() if proc.stderr else ""
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}): {stderr[-800:]}")
        print("wrote", OUT)
        pygame.quit()

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.left_y -= 14
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.left_y += 14
            self.left_y = self.clamp_paddle(self.left_y)
            self.update(left_ai=False, right_ai=True)
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()

if __name__ == "__main__":
    main()
