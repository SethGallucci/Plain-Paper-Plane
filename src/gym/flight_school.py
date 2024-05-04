from __future__ import annotations

from typing import Any, Callable

import gymnasium as gym
import numpy as np
import pygame as pg
from gymnasium import spaces
from gymnasium.core import ObsType
from pygame import Surface
from pygame.event import Event

from src.event.event_handler import EventHandler
from src.scene.game import Game
from src.world.crate_wall import CrateWall

# :param is_pitching_up: A boolean
# Example: Event(PLANE_CONTROL_EVENT, is_pitching_up=True)
PLANE_CONTROL_EVENT: int = pg.USEREVENT


class AgentEventHandler(EventHandler):
    def __init__(self, set_plane_is_pitching_up: Callable[[bool], None], **kwargs):
        super().__init__(**kwargs)
        self.set_plane_is_pitching_up: Callable[[bool], None] = set_plane_is_pitching_up

    def __call__(self, event: Event):
        if event.type == PLANE_CONTROL_EVENT:
            if event.is_pitching_up:
                return self.set_plane_is_pitching_up(True)
            else:
                return self.set_plane_is_pitching_up(False)


class FlightSchool(gym.Env):
    metadata = {
        "render_modes": ["human", None],
        "render_fps":   60,
        "obs_types":    ["numeric", "rgb_array"]
    }

    _crate_walls_per_obs: int = 2

    def __init__(self, render_mode, obs_type):

        self.render_mode = render_mode
        self.obs_type = obs_type
        self.action_space = spaces.MultiBinary(1)

        if obs_type == "numeric":
            self._get_obs = self._get_numeric_obs
            self.observation_space = \
                spaces.Dict(dict(
                    plane=spaces.Dict(dict(
                        position=spaces.Dict(dict(
                            x=spaces.Box(
                                low=0.0,
                                high=np.inf
                            ),
                            y=spaces.Box(
                                low=-360.0,
                                high=360.0
                            )
                        )),
                        velocity=spaces.Dict(dict(
                            x=spaces.Box(
                                low=0.0,
                                high=np.inf
                            ),
                            y=spaces.Box(
                                low=-np.inf,
                                high=np.inf
                            )
                        ))
                    )),
                    # Defined as a Tuple Space so that the FlattenObservation wrapper can be used.
                    # Note: Flattening Discrete Spaces results in one-hot encoding.
                    # https://gymnasium.farama.org/api/wrappers/observation_wrappers/#gymnasium.wrappers.FlattenObservation
                    crate_walls=spaces.Tuple((
                        spaces.Dict(dict(
                            position=spaces.Box(
                                low=0,
                                high=np.inf
                            ),
                            gap_location=spaces.Discrete(
                                n=5,
                                start=1
                            )
                        )),
                        spaces.Dict(dict(
                            position=spaces.Box(
                                low=0,
                                high=np.inf
                            ),
                            gap_location=spaces.Discrete(
                                n=5,
                                start=1
                            )
                        ))
                    ))
                ))
        elif obs_type == "rgb_array":
            self._get_obs = self._get_rgb_array_obs
            self.observation_space = spaces.Box(
                low=0,
                high=255,
                shape=(3, self.game.window_size.y, self.game.window_size.x),
                dtype=np.uint8
            )

        pg.init()

        self.window: Surface | None = None
        if self.render_mode == "human":
            self.window = pg.display.set_mode(size=Game.window_size)
            self.clock = pg.time.Clock()

        self.game: Game = Game(event_handler=AgentEventHandler)
        self.current_score: int = self.game.score

    def _get_obs(self) -> ObsType:
        raise ValueError("method: _get_obs must be set to _get_numeric_obs or _get_rgb_array_obs during initialization.")

    def _get_numeric_obs(self) -> ObsType:

        plane_obs: dict[str, dict[str, float]] = dict(
            position=dict(
                x=self.game.plane.position.x,
                y=self.game.plane.position.y
            ),
            velocity=dict(
                x=self.game.plane.linear_velocity.x,
                y=self.game.plane.linear_velocity.y
            )
        )

        # noinspection PyTypeChecker
        position_ordered_crate_walls: list[CrateWall] = sorted(
            self.game.world.query(lambda entity: isinstance(entity, CrateWall)),
            key=lambda cw: cw.position.x
        )

        # Ensure the number of CrateWalls in the observation equals self._crate_walls_per_obs
        if len(position_ordered_crate_walls) > self._crate_walls_per_obs:
            position_ordered_crate_walls = position_ordered_crate_walls[:self._crate_walls_per_obs]
        elif len(position_ordered_crate_walls) < self._crate_walls_per_obs:
            position_ordered_crate_walls += ([CrateWall(position=np.inf)] * (self._crate_walls_per_obs - len(position_ordered_crate_walls)))

        crate_walls_obs: tuple[dict[str, float], ...] = tuple(
            dict(
                position=cw.position.x,
                gap_location=cw.metal_frame_location
            ) for cw in position_ordered_crate_walls
        )

        return dict(
            plane=plane_obs,
            crate_walls=crate_walls_obs
        )

    def _get_rgb_array_obs(self) -> ObsType:
        obs_surface: Surface = Surface(self.game.window_size)
        self.game.render(obs_surface)
        return np.transpose(pg.surfarray.pixels3d(obs_surface), axes=(2, 1, 0))

    def _get_info(self) -> dict[str, Any]:
        return {}

    def reset(self, *, seed=None, options=None) -> tuple[ObsType, dict[str, Any]]:
        super().reset(seed=seed, options=options)

        self.game = Game(event_handler=AgentEventHandler)
        self.current_score = self.game.score

        return self._get_obs(), self._get_info()

    def step(self, action) -> tuple[ObsType, float, bool, bool, dict[str, Any]]:

        pg.event.post(pg.event.Event(PLANE_CONTROL_EVENT, is_pitching_up=bool(action)))

        if self.render_mode == "human":
            self.clock.tick(self.metadata.get("render_fps"))

        self.game.process_events(pg.event.get())
        self.game.step()

        observation = self._get_obs()
        reward: int = self.game.score - self.current_score
        self.current_score = self.game.score
        terminated: bool = self.game.next_scene is not self.game
        truncated: bool = False
        info: dict = self._get_info()
        return observation, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "human":
            self.game.render(self.window)
            pg.display.flip()
            return None

    def close(self):
        if self.window:
            pg.quit()
