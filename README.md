# Shooting Rocket

This is a simple action game written in asynchronous Python using the `ncurses` library, which creates a pseudo-graphical interface.

## Gameplay

You control a spaceship rocket and shoot the space garbage that drifts towards you. Each piece of debris you vaporize explodes in a bright flash and adds to your score, pushing you toward the next wave where junk drifts faster.

**Controls**
- `← → ↑ ↓` — thrust in the given direction.
- `Space` — fire a blaster bolt from the rocket's nose.
- `R` — restart the run instantly (during play or on the game over screen).
- `Q` — quit to the terminal at any time.

Destroy every piece of debris before it reaches you. Colliding with cosmic garbage ends the run, but you can restart the game right away to try again.

**HUD**
- `Score` — increases for every piece of garbage destroyed.
- `Wave` — advances every 10 hits and speeds up the incoming junk.
- `Missed` — counts debris that slipped by. Once it reaches 10, the orbit is overwhelmed and the game ends automatically.
- `High Scores / Best` — persistent leaderboard stored in `highscores.json` so you can chase personal records.

![game screenshot](shooting_rocket_screenshot.gif)

The sky is full of blinking stars, space junk drifts in at random speeds, and you carve a safe path by shooting it down before the debris storm overwhelms the orbit.

## Getting the game

Pre-requisites:

- Git installed on your system.

On Linux or Mac:

- Launch your terminal emulator
- Go to the directory you want to download the game to
- Issue the command

      git clone git@github.com:hyperfield/shooting_rocket.git

  or

      git clone https://github.com/hyperfield/shooting_rocket.git

You will have the Shooting Rocket files downloaded to your disk.

On Windows:

- Run `cmd.exe` or Power Shell
- Do the same steps as above

or

- Use the graphical shell for GitHub.

## Running the game

Pre-requisites:

- Python 3 installed on your system.

On Linux, Mac or Windows:

- Launch a terminal emulator
- Go to the game directory
- Issue the command

      python3 main.py
