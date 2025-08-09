# MacroPad Menu & Modes — README

![Adafruit MacroPad with my newly released 3D printed housing](macropad.png)

A ready‑to‑use CircuitPython project for the Adafruit **MacroPad** with:

* A **main menu** (images + encoder to scroll, press to select)
* Five modes: **10Key**, **MS** (Windows app launcher), **TW** (key grid), **Mac** (macOS app launcher), **F360** (Fusion 360 shortcuts)
* **Centered overlay** that briefly shows the pressed key/shortcut/app
* **LEDs** set to white at 50% by default; rotate encoder to adjust brightness; press to return to menu

---

## Hardware & Software

* **Board:** Adafruit MacroPad RP2040 Starter Kit (12 keys + encoder + display)
* **Firmware:** CircuitPython **9.x** recommended (project includes a small fallback for 8.x)
* **Libraries (from the Adafruit CircuitPython Bundle):**

  * `adafruit_macropad`
  * `adafruit_hid`
  * `adafruit_display_text`

---

## Folder Layout

```
CIRCUITPY/
├─ code.py                 # main program (provided)
└─ images/                 # menu images (BMP)
   ├─ 10Key.bmp
   ├─ MS.bmp
   ├─ TW.bmp
   ├─ SW.bmp
   └─ F360.bmp
```

* Images are **BMP** and render via `displayio`. Recommended: **1‑bit** or **RGB565**.
---

## Quick Start

1. **Install CircuitPython** on the MacroPad (per Adafruit’s guide).
2. Copy the needed **libraries** into `CIRCUITPY/lib/`.
3. Put the provided **`code.py`** at the root of `CIRCUITPY`.
4. Create an **`images/`** folder with the five BMPs.
5. Eject the drive; the MacroPad will reset and show the menu.

---

## How It Works (UX)

* **Main Menu:** rotate the encoder to highlight **10Key / MS / TW / SW / F360**; press the encoder to select.
* **In a Mode:** rotate the encoder to adjust **LED brightness** (0.05–1.0, step 0.05). Press the encoder to **return** to the menu.
* **Key Press Overlay:** when you press any key in any mode, the screen shows a **full‑screen, centered** label (e.g., `"1"`, `"Open: Word"`, or `"⌘N"`) for \~0.9s. The normal UI stays untouched underneath and reappears automatically.

---

## Modes & Key Maps

### 10Key (Numeric Pad)

```
| 1 | 2 | 3 |
| 4 | 5 | 6 |
| 7 | 8 | 9 |
| 0 | . | Enter |
```

### MS (Windows – App Launcher)

Uses **Win** (Start) → types app name → **Enter**. **File Explorer** uses **Win+E**.
```
| Teams  | Slack      | Outlook           |
| Word   | PowerPoint | Excel             |
| Visio  | VS Code    | File Explorer     |
| Chrome | Brave      | Anaconda Terminal |
```
### TW (Key Grid)
```
| Space | F4 | Space |
| Alt   | F3 | Alt   |
| Enter | F2 | H     |
| Ctrl  | F1 | F6    |
```
### Mac (macOS – App Launcher)

Uses **Spotlight** (**⌘ Space**) → types app name → **Enter**.
```
| VS Code      | Terminal   | GitHub Desktop |
| Word         | PowerPoint | Excel          |
| Safari       | Brave      | Chrome         |
| Bambu Studio | Fusion 360 | iMovie         |
```
### F360 (macOS – Fusion 360 Shortcuts)
```
| New Design **⌘N**      | Open **⌘O**         | Save (Version) **⌘S** |
| Recovery Save **⇧⌘S**  | Cycle Tabs **⌘Tab** | ViewCube **⌥⌘V**      |
| Browser **⌥⌘B**        | Comments **⌥⌘A**    | Text Commands **⌥⌘C** |
| Navigation Bar **⌥⌘N** | Data Panel **⌥⌘P**  | Reset Layout **⌥⌘R**  |
```
---

## Customization

* **Change menu entries/images:** edit `MENU` in `code.py` and add BMPs to `images/`.
* **Remap keys:** edit the lists `TENKEY`, `MS_WIN_APPS`, `TW_KEYS`, `SW_MAC_APPS`, `F360_KEYS`.

  * For Windows/macOS app launchers, change the strings passed to `win_open("App")` or `mac_open("App")`.
  * For shortcuts, use `send_combo(Keycode.GUI, Keycode.N)` etc. (GUI=⌘ on macOS, Windows key on Windows).
* **Overlay duration:** change the `seconds` default in `flash_centered(text, seconds=0.9)`.
* **Brightness step:** tweak `0.05` inside the main loop when adjusting brightness.
* **Minimum brightness:** change the clamp lower bound from `0.05` to whatever you prefer.

---

## Troubleshooting

* **Error:** `AttributeError: .show(x) removed. Use .root_group = x`

  * You’re on CircuitPython 9.x. Use `display.root_group = group`. The code already tries 9.x first and falls back to `display.show()` for 8.x.

* **Encoder button not selecting / exiting**

  * Ensure you’re using the **debouncer edge**: the code checks `macropad.encoder_switch_debounced.fell` each loop.

* **Text runs off the right edge**

  * Switch the info footer to a **two‑line layout** or left‑align (`anchor_point=(0,1.0)`). (This project keeps it concise and centered by default.)

* **Images too big**

  * Use the included 96×48 versions or scale your own to fit beneath the title. The code centers whatever size you provide.

* **App not launching** (MS/SW modes)

  * Make sure the app name you type matches the system’s search name.

---

## Credits

* Built with Adafruit’s **MacroPad** library and **displayio**.
* Icons/bitmaps are simple monochrome BMPs designed for clarity on small displays.
* Vibe coded with ChatGPT and images created by ChatGPT.

---

## License

MIT License (MIT)
See the [LICENSE](LICENSE) file for details.

*This project is not affiliated with Adafruit.*