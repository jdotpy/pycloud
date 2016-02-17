import paramiko
import threading

class Host():

class SSHSession():
    def __init__(self, hosts):
        ssh = paramiko.SSHClient()
        ssh.connect('127.0.0.1', pkeyusername='jesse', password='lol')

outlock = threading.Lock()

def workon(host):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='xy', password='xy')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write('xy\n')
    stdin.flush()

    with outlock:
        print stdout.readlines()

def main():
    hosts = ['10.10.3.10', '10.10.4.12', '10.10.2.15', ] # etc
    threads = []
    for h in hosts:
        t = threading.Thread(target=workon, args=(h,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

main()
