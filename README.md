# Plain-Paper-Plane
Pilot a paper plane as you nimbly soar through an obstacle course of crates! See how far you can fly before you inevitably crumple!

https://github.com/SethGallucci/Plain-Paper-Plane/assets/3813675/6c9c1014-45a9-45e2-a144-f3f573c36e05


## Objective
Fly through as many obstacles as you can by avoiding collisions with the crates. Each gap that you fly through gives you one point.


## Controls
#### Splash Scene & Game Over Scene
Left-click to start a new game.
#### Game Scene
Hold the left mouse button to cause the paper plane to pitch upward, and release the left mouse button to allow it to pitch downward.

---

## Gymnasium Environment
#### Render Modes
- **Human:** A standard graphics window running at the framerate the game is intended to be played.
- **None:** Neither window nor graphics are displayed.
#### Observation Types
- **Numeric:** A nested collection of key-value game data pertaining to the position and velocity of the paper plane as well as the positions and gap numbers of the next two crate walls.
- **RGB Array:** A numpy array shaped as (3 color channels, 720 pixel rows, 1280 pixel columns) of uint8 values (integers 0 - 255).
#### Rewards
Each step resulting in a point scored yields a reward of 1, and otherwise yields a reward of 0.

---

Plain Paper Plane is a remake of a game that I made as part of a friendly bet, long ago. The purpose of remaking this game was to learn about Python's multiple inheritence, the [Entity-Component-System](https://en.wikipedia.org/wiki/Entity_component_system) pattern, [PyGame](https://www.pygame.org/docs/), and [Gymnasium](https://gymnasium.farama.org/).

---

Made with:
- gymnasium 0.29.1
- numpy 1.26.4
- pyenv 2.3.36
- pygame 2.5.2
- pyinstaller 6.4.0
- python 3.9.18
