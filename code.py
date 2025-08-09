# code.py — MacroPad Menu + 5 modes with centered key overlay + brightness on knob
# Requires: CircuitPython for MacroPad + adafruit_macropad lib bundle

import time
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_hid.keycode import Keycode
from adafruit_macropad import MacroPad

# -----------------------
# Setup
# -----------------------
macropad = MacroPad()

# LEDs: white @ 50%
macropad.pixels.brightness = 0.5
macropad.pixels.fill((255, 255, 255))

display = macropad.display
root = displayio.Group()
# CP 9.x+
try:
    display.root_group = root
# CP 8.x and earlier fallback
except AttributeError:
    display.show(root)
display.auto_refresh = True

DEFAULT_ROT = display.rotation if hasattr(display, "rotation") else 0

# Main menu entries -> (name, image path)
MENU = [
    ("10Key", "/images/10Key.bmp"),
    ("MS",    "/images/MS.bmp"),
    ("Twinson",    "/images/TW.bmp"),
    ("Mac",    "/images/SW.bmp"),
    ("F360",  "/images/F360.bmp"),
]

# -----------------------
# UI helpers
# -----------------------
title = label.Label(
    terminalio.FONT, text="", color=0xFFFFFF,
    anchor_point=(0.5, 0.0),
    anchored_position=(display.width // 2, 2)
)
root.append(title)

msg = label.Label(
    terminalio.FONT, text="", color=0xFFFFFF,
    anchor_point=(0.5, 1.0),
    anchored_position=(display.width // 2, display.height - 2)
)
root.append(msg)
msg_expire = 0.0

info = label.Label(
    terminalio.FONT, text="", color=0xAAAAAA,
    anchor_point=(0.5, 1.0),
    anchored_position=(display.width // 2, display.height - 14)
)
root.append(info)

_img_file = None
_img_bitmap = None
_img_tile = None

def show_message(text, seconds=1.2):
    global msg_expire
    msg.text = text
    msg_expire = time.monotonic() + seconds

def clear_message():
    global msg_expire
    if msg_expire and time.monotonic() > msg_expire:
        msg.text = ""
        msg_expire = 0.0

def _unload_image():
    global _img_file, _img_tile
    if _img_tile and _img_tile in root:
        root.remove(_img_tile)
    _img_tile = None
    if _img_file:
        try:
            _img_file.close()
        except Exception:
            pass
    _img_file = None

def show_image(path):
    """Show centered BMP under the title."""
    global _img_file, _img_bitmap, _img_tile
    _unload_image()
    _img_file = open(path, "rb")
    _img_bitmap = displayio.OnDiskBitmap(_img_file)
    bmp_w = getattr(_img_bitmap, "width", display.width)
    bmp_h = getattr(_img_bitmap, "height", display.height)
    _img_tile = displayio.TileGrid(
        _img_bitmap,
        pixel_shader=_img_bitmap.pixel_shader,
        x=max(0, (display.width - bmp_w) // 2),
        y=max(0, (display.height - bmp_h) // 2),
    )
    root.append(_img_tile)

def refresh_info(mode_name=None):
    b = macropad.pixels.brightness
    if mode_name:
        info.text = f"Brightness: {b:.2f}"
    else:
        info.text = f"Brightness: {b:.2f}"

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

# -----------------------
# Full-screen centered overlay for key/app text
# -----------------------
flash = displayio.Group()
# black background
_flash_bg_bmp = displayio.Bitmap(display.width, display.height, 1)
_flash_bg_pal = displayio.Palette(1); _flash_bg_pal[0] = 0x000000
flash_bg = displayio.TileGrid(_flash_bg_bmp, pixel_shader=_flash_bg_pal)
flash_label = label.Label(
    terminalio.FONT,
    text="",
    color=0xFFFFFF,
    anchor_point=(0.5, 0.5),
    anchored_position=(display.width // 2, display.height // 2),
    scale=3,
)
flash.append(flash_bg)
flash.append(flash_label)
flash.hidden = True
root.append(flash)
_flash_until = 0.0

def _best_scale_for(text):
    # ~6 px/char at scale=1 (5 glyph + 1 spacing)
    for s in (4, 3, 2, 1):
        if 6 * s * len(text) <= display.width - 10:
            return s
    return 1

def flash_centered(text, seconds=0.9):
    global _flash_until
    if not text:
        text = " "
    flash_label.scale = _best_scale_for(text)
    flash_label.text = text
    flash.hidden = True  # ensure redraw toggles
    flash.hidden = False
    _flash_until = time.monotonic() + seconds

def update_flash():
    global _flash_until
    if _flash_until and time.monotonic() >= _flash_until:
        flash.hidden = True
        _flash_until = 0.0

# -----------------------
# Utility: typing & combos
# -----------------------
kbd = macropad.keyboard
layout = macropad.keyboard_layout

def send_combo(*keys):
    """Press a combo together."""
    kbd.press(*keys)
    time.sleep(0.02)
    kbd.release_all()

def type_text(s, per_char_delay=0.0):
    for ch in s:
        layout.write(ch)
        if per_char_delay:
            time.sleep(per_char_delay)

# -----------------------
# Mode mappings
# -----------------------

# 10Key: indices 0..11 laid out as:
# [0,1,2,
#  3,4,5,
#  6,7,8,
#  9,10,11]
TENKEY = [
    ("1", lambda: layout.write("1")),
    ("2", lambda: layout.write("2")),
    ("3", lambda: layout.write("3")),
    ("4", lambda: layout.write("4")),
    ("5", lambda: layout.write("5")),
    ("6", lambda: layout.write("6")),
    ("7", lambda: layout.write("7")),
    ("8", lambda: layout.write("8")),
    ("9", lambda: layout.write("9")),
    ("0", lambda: layout.write("0")),
    (".", lambda: layout.write(".")),
    ("Enter", lambda: kbd.send(Keycode.ENTER)),
]

# MS (Windows) app open via Start (Win) + typing + Enter
def win_open(app_name, use_direct=None):
    if use_direct == "EXPLORER":
        flash_centered("File Explorer")     # show centered name
        send_combo(Keycode.WINDOWS, Keycode.E)
        return
    flash_centered(app_name or " ")         # centered app name
    kbd.send(Keycode.WINDOWS)
    time.sleep(0.20)
    if app_name:
        type_text(app_name)
        time.sleep(0.10)
    kbd.send(Keycode.ENTER)

MS_WIN_APPS = [
    ("Teams",                lambda: win_open("Teams")),
    ("Slack",                lambda: win_open("Slack")),
    ("Outlook",              lambda: win_open("Outlook")),
    ("Word",                 lambda: win_open("Word")),
    ("PowerPoint",           lambda: win_open("PowerPoint")),
    ("Excel",                lambda: win_open("Excel")),
    ("Visio",                lambda: win_open("Visio")),
    ("Visual Studio Code",   lambda: win_open("Visual Studio Code")),
    ("File Explorer",        lambda: win_open("", use_direct="EXPLORER")),
    ("Chrome",               lambda: win_open("Chrome")),
    ("Brave",                lambda: win_open("Brave")),
    ("Anaconda Prompt",      lambda: win_open("Anaconda Prompt")),
]

# TW: key set (no rotation)
TW_KEYS = [
    ("Space", lambda: kbd.send(Keycode.SPACE)),
    ("F4",    lambda: kbd.send(Keycode.F4)),
    ("Space", lambda: kbd.send(Keycode.SPACE)),
    ("Alt",   lambda: kbd.send(Keycode.ALT)),
    ("F3",    lambda: kbd.send(Keycode.F3)),
    ("Alt",   lambda: kbd.send(Keycode.ALT)),
    ("Enter", lambda: kbd.send(Keycode.ENTER)),
    ("F2",    lambda: kbd.send(Keycode.F2)),
    ("H",     lambda: kbd.send(Keycode.H)),
    ("Ctrl",  lambda: kbd.send(Keycode.CONTROL)),
    ("F1",    lambda: kbd.send(Keycode.F1)),
    ("F6",    lambda: kbd.send(Keycode.F6)),
]

# SW (macOS) apps via Spotlight (Cmd+Space)
def mac_open(app_name):
    flash_centered(app_name)
    send_combo(Keycode.GUI, Keycode.SPACE)   # Command+Space
    time.sleep(0.15)
    type_text(app_name)
    time.sleep(0.10)
    kbd.send(Keycode.ENTER)

SW_MAC_APPS = [
    ("VS Code",          lambda: mac_open("Visual Studio Code")),
    ("Terminal",         lambda: mac_open("Terminal")),
    ("GitHub Desktop",   lambda: mac_open("GitHub Desktop")),
    ("Word",             lambda: mac_open("Microsoft Word")),
    ("PowerPoint",       lambda: mac_open("Microsoft PowerPoint")),
    ("Excel",            lambda: mac_open("Microsoft Excel")),
    ("Safari",           lambda: mac_open("Safari")),
    ("Brave",            lambda: mac_open("Brave")),
    ("Chrome",           lambda: mac_open("Google Chrome")),
    ("Bambu Studio",     lambda: mac_open("Bambu Studio")),
    ("Fusion 360",       lambda: mac_open("calculator")),
    ("iMovie",           lambda: mac_open("iMovie")),
]

# F360 (macOS) shortcuts — Command is GUI, Option is ALT on HID
F360_KEYS = [
    ("New Design ⌘N",              lambda: send_combo(Keycode.GUI, Keycode.N)),
    ("Open ⌘O",                    lambda: send_combo(Keycode.GUI, Keycode.O)),
    ("Save (Version) ⌘S",          lambda: send_combo(Keycode.GUI, Keycode.S)),
    ("Recovery Save ⇧⌘S",          lambda: send_combo(Keycode.SHIFT, Keycode.GUI, Keycode.S)),
    ("Cycle Tabs ⌘Tab",            lambda: send_combo(Keycode.GUI, Keycode.TAB)),
    ("ViewCube ⌥⌘V",               lambda: send_combo(Keycode.ALT, Keycode.GUI, Keycode.V)),
    ("Browser ⌥⌘B",                lambda: send_combo(Keycode.ALT, Keycode.GUI, Keycode.B)),
    ("Comments ⌥⌘A",               lambda: send_combo(Keycode.ALT, Keycode.GUI, Keycode.A)),
    ("Text Cmds ⌥⌘C",              lambda: send_combo(Keycode.ALT, Keycode.GUI, Keycode.C)),
    ("Nav Bar ⌥⌘N",                lambda: send_combo(Keycode.ALT, Keycode.GUI, Keycode.N)),
    ("Data Panel ⌥⌘P",             lambda: send_combo(Keycode.ALT, Keycode.GUI, Keycode.P)),
    ("Reset Layout ⌥⌘R",           lambda: send_combo(Keycode.ALT, Keycode.GUI, Keycode.R)),
]

# -----------------------
# Mode control
# -----------------------
MODE_MAP = {
    "10Key": TENKEY,
    "MS": MS_WIN_APPS,
    "Twinson": TW_KEYS,
    "Mac": SW_MAC_APPS,
    "F360": F360_KEYS,
}

def enter_mode(name):
    title.text = name
    _unload_image()
    refresh_info(name)
    show_message(f"{name} ready", 1.0)

def exit_mode():
    title.text = "Menu"
    refresh_info(None)
    show_image(MENU[current_index][1])

def run_action(mode_name, key_index):
    mapping = MODE_MAP.get(mode_name)
    if not mapping or not (0 <= key_index < len(mapping)):
        return
    label_text, fn = mapping[key_index]
    # Centered overlay showing ONLY the pressed key/shortcut/app
    flash_centered(label_text)
    # Execute
    fn()

# -----------------------
# Main loop: Menu & Modes
# -----------------------
current_index = 0
in_mode = None

def show_menu_item(idx):
    name, path = MENU[idx]
    show_image(path)
    refresh_info(None)

# Initial menu
show_menu_item(current_index)
last_encoder = macropad.encoder
macropad.encoder_switch_debounced.update()

while True:
    # ----- Encoder handling -----
    pos = macropad.encoder
    if in_mode is None:
        # In menu: rotate to change selection
        if pos != last_encoder:
            delta = pos - last_encoder
            last_encoder = pos
            current_index = (current_index + delta) % len(MENU)
            show_menu_item(current_index)
    else:
        # In a mode: rotate to change brightness
        if pos != last_encoder:
            delta = pos - last_encoder
            last_encoder = pos
            new_b = clamp(macropad.pixels.brightness + (delta * 0.05), 0.05, 1.0)
            macropad.pixels.brightness = new_b
            macropad.pixels.fill((255, 255, 255))
            refresh_info(in_mode)

    # Press to select / exit
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.fell:
        if in_mode is None:
            in_mode = MENU[current_index][0]
            enter_mode(in_mode)
        else:
            in_mode = None
            exit_mode()

    # ----- Key events -----
    event = macropad.keys.events.get()
    if event:
        if event.pressed and in_mode is not None:
            run_action(in_mode, event.key_number)

    # Hide transient footer message & overlay timeout
    clear_message()
    update_flash()
    time.sleep(0.01)
