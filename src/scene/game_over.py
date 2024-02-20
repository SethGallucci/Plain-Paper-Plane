from __future__ import annotations

import pygame as pg
from pygame import Color, Vector2
from pygame.event import Event
from pygame.font import Font
from pygame.surface import Surface, SurfaceType

import src.scene.game as game
from src.scene.scene import Scene


class GameOver(Scene):
    def __init__(self, init_data: dict | None = None):
        super().__init__(init_data=init_data)

        self.background: Surface = self.init_data["screenshot"].copy()
        lighten = Surface(self.background.get_size()).convert_alpha()
        pg.draw.rect(lighten, Color(255, 255, 255, 127), lighten.get_rect())
        self.background.blit(lighten, (0, 0))

        self.final_score_display = Font("freesansbold.ttf", 64).render(f"Score: {init_data['score']}", True, "black").convert_alpha()

        self.replay_text = Font("freesansbold.ttf", 32).render("click to fly again", True, "black").convert_alpha()

        self.scene_begin_time = pg.time.get_ticks()
        self.click_disable_duration = 1000

    def process_events(self, events: list[Event]) -> None:
        for event in events:
            if event.type == pg.QUIT:
                self.next_scene = None
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and pg.time.get_ticks() - self.scene_begin_time > self.click_disable_duration:
                self.set_next_scene(game.Game())

    def step(self) -> None:
        pass

    def render(self, screen: Surface | SurfaceType) -> None:

        screen.blit(self.background, (0, 0))

        screen.blit(
            self.final_score_display,
            self.final_score_display.get_rect(midtop=Vector2(screen.get_rect().midtop) + Vector2(0, 100))
        )

        screen.blit(
            self.replay_text,
            self.final_score_display.get_rect(center=Vector2(screen.get_rect().center) + Vector2(0, 75))
        )
