from libqtile import bar, layout, qtile, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.bar import Gap
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile.core.manager import Qtile

import psutil

from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

# qtile devs, please annotate your library 🙏
qtile: Qtile = qtile

import os
import subprocess
import signal
import threading

# === VARIABLES ===
mod = "mod4"
terminal = 'alacritty'

# === USEFUL FUNCTIONS ===
def notify_msg(msg):
    subprocess.Popen(['notify-send', msg])

def spawn_command(cmd: list[str]):
    subprocess.Popen(cmd)

# === HOOKS ===
@hook.subscribe.startup_once
def watch_for_config_change():
    class Handler(FileSystemEventHandler):
        def on_modified(self, ev: FileModifiedEvent):
            if not ev.is_directory:
                os.kill(os.getpid(), signal.SIGUSR1)
                notify('reload!')

    obs = Observer()
    obs.schedule(Handler(), __file__)
    obs.start()
    
    spawn_command(['setxkbmap', '-layout', "us,ru", '-option', "grp:win_space_toggle"])
    spawn_command(['numlockx'])
    spawn_command(['picom'])
    spawn_command(['dunst'])
    spawn_command(['polybar', 'main', '--reload'])
    spawn_command(['flameshot'])
    spawn_command(["alacritty", "--command", "fish", "--init-command", "ff"])
    spawn_command(['Telegram', '-autostart'])

# === KEYBINDS ===
def switch_compositor(qtile):
    killed = False
    psutil.process_iter.cache_clear()

    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'picom':
            notify_msg(f'killing {proc.info['pid']}...')
            killed = True
            os.kill(proc.info['pid'], signal.SIGTERM)

    if not killed:
        notify_msg('starting picom...')
        spawn_command(['picom'])

keys = [
    Key([mod], "left", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "right", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "down", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "up", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "Tab", lazy.group.next_window(), desc='Move focus to next window'),
    
    Key([mod, "shift"], "left", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([mod, "shift"], "right", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([mod, "shift"], "down", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "up", lazy.layout.shuffle_up(), desc="Move window up"),
    Key([mod, "shift"], "Page_Up", lazy.window.bring_to_front(), desc='Bring window to front'),
    
    Key([mod, "control"], "left", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "right", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "down", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "up", lazy.layout.grow_up(), desc="Grow window up"),

    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),

    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod], "v", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod], "d", lazy.spawn('rofi -show drun'), desc="Spawn Rofi"),
    Key([mod], 'p', lazy.function(switch_compositor), desc='Switch compositor state'),
    Key([], 'Print', lazy.spawn('flameshot gui'), desc='Open screenshot prompt'),

    Key([mod, "mod1"], 'right', lazy.spawn('playerctl next')),
    Key([mod, "mod1"], 'left', lazy.spawn('playerctl previous')),
    Key([mod, "mod1"], 'space', lazy.spawn('playerctl play-pause')),
]

groups = [Group(i) for i in "123456789"]

for i in groups:
    keys.extend(
        [
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc=f"Switch to group {i.name}",
            ),
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc=f"Switch to & move focused window to group {i.name}",
            )
        ]
    )

layouts = [
    layout.Bsp(margin=4, border_focus="#1c7331", border_normal="#505050", border_width=2, margin_on_single=False)
]

widget_defaults = dict(
    font="sans",
    fontsize=12,
    padding=3,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        bottom=Gap(size=29),
        background='#101010',
        wallpaper='/home/d/.config/qtile/wallpaper.png',
        wallpaper_mode='fill'
        # x11_drag_polling_rate = 60,
    ),
]

mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = True
floats_kept_above = False
cursor_warp = False

floating_layout = layout.Floating(
    border_focus="#1c7331", border_normal="#505050", border_width=2,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(wm_class='alacritty-floating'),
    ]
)

auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

auto_minimize = False

wmname = "qtile"
