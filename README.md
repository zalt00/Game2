# Game

Setup:
 1. launch `shell.cmd`
 2. enter the command `venv`, make sure python 3.6+ is installed and in your PATH environment variable, it should setup
 the virtual environment and install the required packages
 
Requirements:
 - required packages are listed in `requirements.txt`
 - these requirements are for the whole project, to launch the game you only need these packages:
    - `pymunk`
    - `pyglet`
    - `numpy`
    - `pyyaml`
 
Launchers:
 - `launcher.cmd`: classic launcher, cmd not hidden
 - `launcherdb.cmd`: debug launcher, launches the program with the `--debug` argument: gives access to new in-game
  commands, more logs are displayed and pauses the program after his execution
 - `map_editor.cmd`: launcher for the map editor
 
Debug/Dev commands:
 - `F1`: toggle debug draw
 - `F2`: raises an error, manually makes the program crash (does not work properly)
 - `F3`: pause/unpause the game
 - `F4`: start/stop and save player position recording (saved into `records.npy`)
 - `F5`: toggle god mode (infinite jump and dash)
 - `F6`: screenshot
 - `F12`: dev debug command
 
  
 