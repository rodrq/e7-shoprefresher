import subprocess

def adb_command(text:str):
    return subprocess.run([word for word in text.split()])

def adb_connect():
    adb_command('adb start-server')

def adb_tap(x, y):
    return adb_command(f"adb shell input tap {x} {y}")