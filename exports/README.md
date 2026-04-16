Exported Snake files

Included files:
- `micro_snake.py` : MicroPython-adapted Snake (menu, options, pre-start direction, restart/menu on game over). Designed for Casio MicroPython with `casioplot` API.
- `SNAKE_basic.txt` : Casio Basic listing (fx-9750GIII style) with a simple menu wrapper that launches the original snake code.
- `snake_pygame.py` : (not included here) Your pygame desktop version remains in the repo root.

How to use:

MicroPython (Casio):
- Copy `micro_snake.py` to your device's filesystem as `main.py` (or run it with your MicroPython/Casio environment).
- The script expects a `casioplot`-like API with: `clear()`, `text(x,y,s)`, `rect(x,y,w,h)`, `fill_rect(x,y,w,h)`, `show()`, and `is_pressed(keycode)`.
- Controls: arrow keys to set direction, `EXE` to select/start, `AC` to back/return to menu.

Casio Basic:
- `SNAKE_basic.txt` is a text representation of a Casio BASIC program. Paste it into your fx-series calculator editor or import using your usual tool.
- Use arrow keys to navigate the menu, `EXE` to select.

Notes:
- MicroPython and Casio Basic hardware limitations mean the UI and visuals are simplified compared to the desktop pygame version.
- The MicroPython script uses a small cell pixel size and simple border drawing to keep the game playable on small screens.

If you want, I can:
- Copy the desktop `snake_pygame.py` into the `exports` folder as well.
- Tweak the MicroPython/Casio Basic code to better match the exact keycodes or `casioplot` version you have — tell me which device and firmware so I can adjust.
