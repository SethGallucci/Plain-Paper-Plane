import pygame as pg

import src.scene.scene_manager as scene_manager
from src.scene.splash import Splash

pg.init()

pg.display.set_caption("Plain Paper Plane")
pg.display.set_icon(pg.image.load("res/plane.ico"))

screen = pg.display.set_mode(size=(1280, 720))
clock = pg.time.Clock()

scene_manager.set_scene(Splash())

while scene_manager.current_scene:

    scene_manager.process_events(pg.event.get())
    scene_manager.step()

    scene_manager.render(screen)
    pg.display.flip()

    scene_manager.set_scene(scene_manager.current_scene.next_scene)

    clock.tick(60)

pg.quit()
