from __future__ import annotations

import math
import random

import pygame as pg
from pygame import Surface, Vector2
from pygame.display import get_window_size
from pygame.event import Event
from pygame.font import Font

import src.scene.game_over as game_over
from src.scene.scene import Scene
from src.world.background import Background
from src.world.camera import Camera
from src.world.crate_wall import CrateWall
from src.world.plane import Plane
from src.world.system import DetectCollisions, Move, Parallax, Render, VisualizePolygons
from src.world.world import World


class Game(Scene):
    def __init__(self, init_data: dict | None = None):
        super().__init__(init_data=init_data)

        # Stored as a Vector2 for convenience
        self.window_size: Vector2 = Vector2(get_window_size())

        self.world = World()

        self.camera: Camera = Camera(
            surface=Surface(self.window_size),
            anchor=self.window_size.elementwise() * Vector2(0.05, 0.5),
            position=Vector2(0, 0)
        )
        self.world.add(self.camera)

        self.background = Background(render_height=-1)
        self.world.add(self.background)

        self.plane = Plane(
            position=Vector2(0, 0),
            rotation=0,
            render_height=0,
            linear_velocity=Vector2(10, 0),
            angular_velocity=0
        )
        self.world.add(self.plane)

        self.render_system = Render(camera=self.camera)
        self.move_system = Move()
        self.parallax_system = Parallax(
            camera=self.camera,
            parallax_origin=self.background.position,
            parallax_factor=(0.2, 0)
        )
        self.collision_detection_system = DetectCollisions()
        self.polygon_visualization_system = VisualizePolygons(
            camera=self.camera
        )

        self.distance_for_next_wall = 0
        self.score = 0
        self.score_font_color = "black"
        self.score_font = Font("freesansbold.ttf", 48)
        self.score_surface = self.score_font.render(str(self.score), True, self.score_font_color)

        self.scene_state = self.initial_cruise
        self.cruise_distance = 300

    def end_game(self) -> None:
        self.set_next_scene(
            game_over.GameOver(
                {
                    "score":      self.score,
                    "screenshot": self.camera.surface
                }
            )
        )

    def process_events(self, events: list[Event]) -> None:
        for event in events:
            if event.type == pg.QUIT:
                self.next_scene = None

    def initial_cruise(self) -> None:
        self.camera.position = self.plane.position.project(Vector2(1, 0))
        self.move_system(self.world.query())
        self.background.position = self.camera.position - self.camera.anchor
        if self.plane.position.x > self.cruise_distance:
            self.distance_for_next_wall = self.plane.position.x
            self.scene_state = self.acrobatic_flight

    def acrobatic_flight(self) -> None:
        plane_max_abs_angle: float = 75.0
        # Remap the angle values such that [0, 180) -> [0, 180) and [180, 360) -> [-180, 0)
        plane_rotation: float = (self.plane.rotation + 180) % 360 - 180
        if pg.mouse.get_pressed()[0]:
            if plane_rotation < -plane_max_abs_angle:
                self.plane.angular_velocity = 0.5
            else:
                self.plane.angular_velocity = -2.5
        else:
            if plane_rotation > plane_max_abs_angle:
                self.plane.angular_velocity = -0.5
            else:
                self.plane.angular_velocity = 2.5

        if self.plane.position.y < (-self.window_size.y + self.plane.surface.get_height()) / 2:
            self.plane.position.y = (-self.window_size.y + self.plane.surface.get_height()) / 2
            self.plane.linear_velocity.y *= -1
        elif self.plane.position.y > (self.window_size.y - self.plane.surface.get_height()) / 2:
            self.end_game()

        self.plane.linear_velocity.rotate_ip(self.plane.angular_velocity)
        self.plane.rotation = math.degrees(math.atan2(*self.plane.linear_velocity.yx))

        if self.plane.position.x > self.distance_for_next_wall:
            self.distance_for_next_wall += random.randint(*(self.window_size.elementwise() * Vector2(0.5, 1)))
            self.world.add(CrateWall(position=self.camera.position + Vector2(self.window_size.x, 0), render_height=1))

        self.camera.position = self.plane.position.project(Vector2(1, 0))
        self.move_system(self.world.query())
        self.background.position = self.camera.position - self.camera.anchor

        passed_wall = next(self.world.query(lambda entity: isinstance(entity, CrateWall) and entity.position.x < self.camera.position.x - entity.surface.get_width()), None)
        if passed_wall:
            self.plane.linear_velocity += Vector2(0.1, 0).rotate(self.plane.rotation)
            self.score += 1
            self.score_surface = self.score_font.render(str(self.score), True, self.score_font_color)
            self.world.remove(passed_wall)

        for e0, e1, polygon_pairs in self.collision_detection_system(self.world.query()):
            if len(polygon_pairs) > 0 and all(any(isinstance(entity, entity_type) for entity in (e0, e1)) for entity_type in (Plane, CrateWall)):
                self.end_game()

    def step(self) -> None:
        self.scene_state()

    def render(self, screen: Surface) -> None:

        self.parallax_system(self.world.query())
        self.render_system(self.world.query())

        screen.blit(self.camera.surface, dest=(0, 0))
        screen.blit(self.score_surface, dest=(screen.get_width() / 2, 10))
