import pygame
from .bird import Bird
from .pipe import Pipe

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.flap_sound = pygame.mixer.Sound("sounds/freesound_community-flappy_whoosh-43099(1).mp3")
        self.die_sound = pygame.mixer.Sound("sounds/flappy_bird_fail.mp3")
        self.bird = Bird(width // 4, height // 2)

        self.DIFFICULTY_SETTINGS = {
            "EASY": {
                "gap": 180,
                "speed": 3
            },
            "NORMAL": {
                "gap": 150,
                "speed": 4
            },
            "HARD": {
                "gap": 120,
                "speed": 5
            }
        }

        self.difficulty = "NORMAL"
        self.menu_option = 0
        self.difficulties = ["EASY", "NORMAL", "HARD"]

        self.pipe_speed = self.DIFFICULTY_SETTINGS[self.difficulty]["speed"]
        self.pipe_gap = self.DIFFICULTY_SETTINGS[self.difficulty]["gap"]

        self.pipe_interval = 90
        self._spawn_timer = 0

        self.pipes = [
            Pipe(
                width + 100,
                height,
                gap=self.pipe_gap,
                speed=self.pipe_speed
            )
        ]

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over = False

    def handle_event(self, event):
        if not self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.bird.flap()
                self.flap_sound.play()

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.bird.flap()
                self.flap_sound.play()

        else:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    self.menu_option = (self.menu_option - 1) % 3

                elif event.key == pygame.K_DOWN:
                    self.menu_option = (self.menu_option + 1) % 3

                elif event.key == pygame.K_RETURN:

                    # REPLAY
                    if self.menu_option == 0:
                        self.reset()

                    # DIFFICULTY
                    elif self.menu_option == 1:
                        current_index = self.difficulties.index(self.difficulty)
                        current_index = (current_index + 1) % len(self.difficulties)
                        self.difficulty = self.difficulties[current_index]

                    # EXIT
                    elif self.menu_option == 2:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass
    def reset(self):
        self.bird = Bird(self.width // 4, self.height // 2)

        self.pipe_speed = self.DIFFICULTY_SETTINGS[self.difficulty]["speed"]
        self.pipe_gap = self.DIFFICULTY_SETTINGS[self.difficulty]["gap"]

        self._spawn_timer = 0

        self.pipes = [
            Pipe(
                self.width + 100,
                self.height,
                gap=self.pipe_gap,
                speed=self.pipe_speed
            )
        ]

        self.score = 0
        self.game_over = False
        self._game_over_logged = False
    def update(self):
        if self.game_over:
            return

        self.bird.update()

        if self.bird.y - self.bird.radius <= 0 or self.bird.y + self.bird.radius >= self.height:
            self.game_over = True
            return

        self._spawn_timer += 1

        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(
                Pipe(
                    self.width,
                    self.height,
                    gap=self.pipe_gap,
                    speed=self.pipe_speed
                )
            )

        for pipe in self.pipes:
            pipe.move()

            bird_top = (self.bird.x, self.bird.y - self.bird.radius)
            bird_bottom = (self.bird.x, self.bird.y + self.bird.radius)

            if (pipe.top_rect().collidepoint(bird_top) or
                pipe.top_rect().collidepoint(bird_bottom) or
                pipe.bottom_rect().collidepoint(bird_top) or
                pipe.bottom_rect().collidepoint(bird_bottom)):
                self.game_over = True

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1

        self.pipes = [p for p in self.pipes if not p.off_screen()]
    def draw_game_over(self, screen):
        font = pygame.font.Font(None, 64)
        score_font = pygame.font.Font(None, 40)
        button_font = pygame.font.Font(None, 36)

        game_over_text = font.render("GAME OVER", True, (255, 255, 255))
        score_text = score_font.render(
            f"Score: {self.score}", True, (255, 255, 255)
        )

        replay_color = (255, 255, 0) if self.menu_option == 0 else (255, 255, 255)
        difficulty_color = (255, 255, 0) if self.menu_option == 1 else (255, 255, 255)
        exit_color = (255, 255, 0) if self.menu_option == 2 else (255, 255, 255)

        replay_text = button_font.render("REPLAY", True, replay_color)

        difficulty_text = button_font.render(
            f"DIFFICULTY: {self.difficulty}",
            True,
            difficulty_color
        )

        exit_text = button_font.render("EXIT", True, exit_color)

        screen.blit(
            game_over_text,
            game_over_text.get_rect(
                center=(screen.get_width() // 2, 150)
            )
        )

        screen.blit(
            score_text,
            score_text.get_rect(
                center=(screen.get_width() // 2, 210)
            )
        )

        screen.blit(
            replay_text,
            replay_text.get_rect(
                center=(screen.get_width() // 2, 290)
            )
        )

        screen.blit(
            difficulty_text,
            difficulty_text.get_rect(
                center=(screen.get_width() // 2, 350)
            )
        )

        screen.blit(
            exit_text,
            exit_text.get_rect(
                center=(screen.get_width() // 2, 410)
            )
        )

    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over and not getattr(self, "_game_over_logged", False):
            print("Game over! Final score:", self.score)
            self._game_over_logged = True

        if self.game_over:
            self.draw_game_over(screen)


