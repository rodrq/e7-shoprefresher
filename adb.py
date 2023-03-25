import subprocess

def adb_command(text:str):
    return subprocess.run([word for word in text.split()])

def adb_connect():
    adb_command('adb start-server')