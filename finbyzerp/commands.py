import click, os, sys, shlex
import subprocess
from subprocess import STDOUT, check_call, CalledProcessError

@click.command('install-whatsapp')
def install_whatsapp():
    cur_dir = os.getcwd() + "/../apps/finbyzerp/WebWhatsappWrapper"
    os.chdir(cur_dir)
    # os.system('sudo su')
    # subprocess.call(cmd, universal_newlines=True)
    print(os.getcwd())  
    os.system('apt-get update')
    # os.system('apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common')
    # os.system('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -')
    # os.system('apt-key fingerprint 0EBFCD88')
    # os.system('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')
    # os.system('apt-get install docker-ce docker-ce-cli containerd.io')
    # os.system('docker run hello-world')
    # os.system('docker network create selenium')
    # os.system('docker run -d -p 4444:4444 -p 5900:5900 --name firefox --network selenium -v /dev/shm:/dev/shm selenium/standalone-firefox-debug:3.14.0-curium')
    # os.system('docker build -t webwhatsapi .')
    # os.system("docker run --network selenium -it -e SELENIUM='http://firefox:4444/wd/hub' -v $(pwd):/app  webwhatsapi /bin/bash -c 'pip install ./;pip list;'")

    
    # os.chdir(os.getcwd() + '/../') # ../lexcru/
    # os.system('. env/bin/activate')
    # # os.system('. deactivate')
    # os.chdir(os.getcwd() + '/apps/finbyzerp/WebWhatsappWrapper')
    # os.system('pip install -r requirements/development.txt')


    # subprocess.call("sudo apt-get update", shell=True)
    

commands = [install_whatsapp]
