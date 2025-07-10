from multiprocessing.connection import Client
import sys

client = Client(('127.0.0.1', 6969))

while True:
    url = input('what url? ')

    if url == '':
        break

    client.send({
        'cmd': 'add-music',
        'url': url
    })

client.close()