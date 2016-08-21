import os
import time
from multiprocessing import Process


def run(*args):
    return Process(target=os.execlp, args=[args[0], *args])

def run_script(script, *args):
    return run('python3', script, *args)

def killall(processes):
    for p in processes:
        try: p.terminate()
        except: pass

os.putenv('TARGET_PORT', '8080')

processes = [
    run('python3', '-m', 'http.server', '8080'),
    run_script('serv.py'),
    run_script('client.py', '127.0.0.1', '25564')
]

for p in processes: p.start()

try:
    print('wait...')
    for p in processes:
        p.join()
except KeyboardInterrupt:
    killall(processes)
