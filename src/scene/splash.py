from __future__ import annotations

from typing import List

import pygame as pg
from pygame import Surface, SurfaceType, Vector2
from pygame.event import Event
from pygame.font import Font

from src.scene.game import Game
from src.scene.scene import Scene


class Splash(Scene):

    def __init__(self, **init_data: dict):
        super().__init__(**init_data)

        self.background_color = "white"
        self.title_banner = Font("freesansbold.ttf", 128).render("Plain Paper Plane", True, "black")
        self.start_text = Font("freesansbold.ttf", 32).render("click to fly", True, "black")

    def process_events(self, events: List[Event]) -> None:
        for event in events:
            if event.type == pg.QUIT:
                self.set_next_scene(None)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.set_next_scene(Game())

    def step(self) -> None:
        pass

    def render(self, screen: Surface | SurfaceType) -> None:

        screen.fill(self.background_color, screen.get_rect())
        screen.blit(
            self.title_banner,
            self.title_banner.get_rect(center=Vector2(screen.get_rect().center) + Vector2(0, -75))
        )
        screen.blit(
            self.start_text,
            self.start_text.get_rect(center=Vector2(screen.get_rect().center) + Vector2(0, 75))
        )
