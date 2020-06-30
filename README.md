# Game

Setup:
 1. launch `shell.cmd`
 2. enter the command `venv`, make sure python 3.6+ is installed and in your PATH environment variable, it should setup
 the virtual environment and install the required packages
 
Launchers:
 - `launcher.cmd`: classic launcher, cmd not hidden
 - `launcherwoc.cmd`: launcher without console, hides cmd
 - `launcherdb.cmd`: debug launcher, launches the program with the `--debug` argument, gives access to new in-game
  commands, displays more logs and pauses the program after his execution
 - `structure_builder_launcher.cmd`: launcher for the structure builder
 
 Debug commands:
 - `F1`: activates debug draw
 - `F2`: deactivates debug draw
 - `F3`: raises an error, manually makes the program crash
 
Additional infos:
  - credits: see `credits.txt`
  - manually set the save data (not recommended unless you softlock or the game crashes at launch):
  launch the `save_modifier.py` file in the `sources/utils` folder, it should only use modules from the
  standard python library
  - to use the level builder and the structure builder, make sure you installed python with the tcl interpreter
  and the `tkinter` module
 