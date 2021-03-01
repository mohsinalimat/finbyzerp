import click, os, sys, shlex
import subprocess
from subprocess import STDOUT, check_call, CalledProcessError

@click.command('install-whatsapp')
def install_whatsapp():
    # cur_dir = os.getcwd() + "/../apps/finbyzerp/finbyzerp/webwhatsapi"
    # os.chdir(cur_dir)

    # os.system('sudo su')    
    os.system("sudo apt  install firefox")
    os.system("export GECKO_DRIVER_VERSION='v0.29.0'")
    os.system("wget https://github.com/mozilla/geckodriver/releases/download/$GECKO_DRIVER_VERSION/geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz")
    os.system("tar -xvzf geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz")
    os.system("rm geckodriver-$GECKO_DRIVER_VERSION-linux64.tar.gz")
    os.system("chmod +x geckodriver")
    os.system("sudo cp geckodriver /usr/local/bin/")

commands = [install_whatsapp]
