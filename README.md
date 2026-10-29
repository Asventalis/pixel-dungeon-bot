# Shattered Pixel Dungeon Farming Bot

A bot that plays repetitive farming loops in the Android roguelike Shattered Pixel Dungeon on a USB-connected phone. It takes screenshots through ADB (`screencap` + `pull`), reads the game state from the colour of fixed pixels (turn clock, attack button, enemy-in-sight indicator, health bar, hunger icon, food slot) and from OpenCV template matching of small icons, then sends taps and long presses with `adb shell input`. The main loop waits/sleeps until an enemy appears, attacks until it is gone and eats when health and hunger are low.

## How to run
Windows/Linux with Python 3, `opencv-python`, `numpy`, and `adb` with USB debugging enabled on the device. Set `DEVICE`, `ADB_PATH` and the pixel coordinates for your screen resolution (use `check_position("screenshot.png")` to read coordinates and colours by clicking), then `python spd_bot.py`.

## Notes
- Pixel positions and colours are calibrated for one specific phone/resolution and UI layout; they will need recalibration elsewhere.
- Template images (`enemy_symbol.png`, `sleep_symbol.png`, `finished_meat.png`) and a sample `screenshot.png` are included.
