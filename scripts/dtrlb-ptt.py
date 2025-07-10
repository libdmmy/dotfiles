
# DTRLB-PTT
# =========
# requires: yt-dlp, libnotify
# WARNING: NOT FINISHED!

from multiprocessing.connection import Listener, Connection
from threading import Thread
import signal
import subprocess
import os
import sys
from pathlib import Path
import uuid

server = Listener(('127.0.0.1', 6969))

# TODO: add useful arguments
def notify(msg: str | list[str]) -> subprocess.Popen:
    if (isinstance(msg, list)):
        return subprocess.Popen(['notify-send', *msg])
    else:
        return subprocess.Popen(['notify-send', str(msg)])

def get_tmux_cmd() -> str:
    return 'TODO'

def notify_exc(ex: Exception):
    process = subprocess.Popen(
        ['notify-send', 'something went wrong 😔', f'{ex.__class__.__name__}: {str(ex)}\n\ntldr: \"{get_tmux_cmd()}\" or just middle-click on me', '--urgency', 'critical', '--icon', 'dialog-error', '--action=tmux=tmux'],
        stdout=subprocess.PIPE, text=True
    )
    process.wait()

    output = process.stdout.readline().rstrip('\n')

    if output == 'tmux':
        subprocess.Popen(f'alacritty --class alacritty-floating --command {get_tmux_cmd()}'.split(' '))

    raise ex

def handle_client(client: Connection):
    while True:
        try:
            msg = client.recv()
        except EOFError:
            break

        if msg == 'close':
            break

        # TODO: make it better
        if isinstance(msg, dict):
            if msg['cmd'] == 'add-music':
                Thread(target=add_music, args=[msg]).start()

        print(msg)
    
    try: client.close()
    except: pass

def add_music(msg: dict):
    url = msg['url']
    id = str(uuid.uuid4())[:8]
    folder = Path.home() / 'tmp' / id

    try:
        folder.mkdir(parents=True)
    except Exception as e:
        notify_exc(e)

    notify([f'adding music... ({id})', url, '--urgency', 'low', '--icon', 'folder-download-symbolic'])

    # TODO: improve -o argument
    try:
        process = subprocess.Popen(
            ['yt-dlp', '-x', 
                '--print', 'filename',
                '--audio-format', 'mp3',
                '--audio-quality', '0',
                '--add-metadata', '--embed-thumbnail',
                '-o', r'%(title)s.mp3', '--restrict-filenames',
                url],

            cwd=str(folder.resolve(strict=True)),
            stdout=subprocess.PIPE,
            stderr=sys.stdout,
            text=True
        )

        process.wait()
    except Exception as e:
        notify_exc(e)

    if process.returncode != 0:
        notify_exc(Exception(f'exit-code is {process.returncode}'))

    filepath = (folder / process.stdout.readline().rstrip('\n')).resolve(strict=True)

    notify(str(filepath))

    # TODO: find a better icon
    notify([f'task {id} is done!', '--urgency', 'low', '--icon', 'mail-mark-notjunk'])

print('hiii')

while True:
    client = server.accept()
    print(f'new connection! {server.last_accepted}')
    Thread(target=handle_client, args=[client]).start()
