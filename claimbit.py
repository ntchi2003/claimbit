import subprocess
import sys
import re
import time
import requests
import pytz
from datetime import datetime
from colorama import init, Fore, Style

init()

xnhac = Style.BRIGHT + Fore.CYAN
do = Style.BRIGHT + Fore.RED
luc = Style.BRIGHT + Fore.GREEN
vang = Style.BRIGHT + Fore.YELLOW
xduong = Style.BRIGHT + Fore.BLUE
tim = Style.BRIGHT + Fore.MAGENTA
trang = Style.BRIGHT + Fore.WHITE
cyan = Style.BRIGHT + Fore.CYAN
reset = Style.RESET_ALL

gach_chan = "\033[4m"
nghieng = "\033[3m"
reset_ef = "\033[0m"


count = 1

class ClaimBit:
    def __init__(self, username, pw, proxy):
        self.session = requests.Session()
        
        self.username = username
        self.pw = pw
        
        self.session.proxies = self.config_proxy(proxy)
        self.ips()
        self.lock = threading.Lock()
        
    def config_proxy(self, proxy):
        ip, port, username, password = proxy.split(':')
        return {
            'http': f'http://{username}:{password}@{ip}:{port}',
            'https': f'http://{username}:{password}@{ip}:{port}'
        }

    def ips(self):
        res = self.session.get('https://api.ipify.org?format=json')
        self.ip = res.json()['ip']
    
    def login(self):
        url = "https://claimbits.net/"
        res = self.session.get(url)
        access_key = res.text.split("|regCountry|")[1].split("|")[0]
        datastt = res.text.split('id="loginStatus"')[1].split('class="form-group"')[0]
        token = res.text.split('value="')[1].split('"')[0]
        url = 'https://claimbits.net/system/ajax.php'
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Host': 'claimbits.net',
            'Origin': 'https://claimbits.net',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        }
        data = {
            'a': 'login',
            'access_key': access_key,
            'token': token,
            'username': self.username,
            'password': self.pw 
        }
        res = self.session.post(url, headers=self.headers, data=data)
        msg = res.json()['msg']
        msg = re.sub(r'<.*?>', '', msg)
        if msg == "SUCCESS: You're being redirected...":
            print(f"{luc}{nghieng}{msg}{reset_ef}            ", end='\r')
            time.sleep(1.5)
            return True
        else:
            print(f"{do}{nghieng}{msg}{reset_ef}            ", end='\r')
            print(self.username, self.pw)
            return False
        
    def claim(self):
        global count
        url = 'https://claimbits.net/faucet.html'
        res = self.session.get(url, headers=self.headers.update({'Referer': 'https://claimbits.net/faucet.html'}))
        token = res.text.split("var token = '")[1].split("'")[0]
        url = 'https://claimbits.net/system/ajax.php'
        data = {
            'a': 'getFaucet',
            'token': token,
            'captcha': 'icon-captcha',
            'challenge': False,
            'response': False
        }
        res = self.session.post(url, headers=self.headers, data=data)
        message = res.json()['message'].split('and you won ')[1]
        message = re.sub(r'<.*?>', '', message)
        res = self.session.get('https://claimbits.net/faucet.html')
        balance = res.text.split('class="text-primary"><b>')[1].split('</b>')[0]

        
        current_time = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        formatted_time = current_time.strftime("%H:%M:%S")
        
        with self.lock:
            print(f"{tim}[TC TOOL]{trang}[{formatted_time}] {do}➩  {trang}[{count}] {cyan}{nghieng}+ {message} {trang}- {vang}{balance} {trang}- IP: {do}{self.ip}{reset_ef}                            ")
            count += 1  
        
        for i in range(int(5*60), 0, -1):
            minutes, seconds = divmod(i, 60)
            print(f"{tim}[TC TOOL] {do}➩  {vang}CÒN LẠI {do}{gach_chan}{minutes} phút {seconds} giây{reset_ef}                       ", end='\r')
            time.sleep(1)
            if i == 1:
                break

import threading

def run_claimbit(username, pw, proxy):
    cl = ClaimBit(username, pw, proxy)
    cl.login()
    while True:
        try:
            cl.claim()
        except Exception as e:
            continue

if __name__ == "__main__":
    accounts = []
    with open('acc_claimbits.txt', 'r') as file:
        for line in file:
            parts = line.strip().split('|')
            if len(parts) == 5:
                username, password, email, password_mail, proxy = parts
                accounts.append((username, password, proxy))

    threads = []
    for username, password, proxy in accounts:
        t = threading.Thread(target=run_claimbit, args=(username, password, proxy))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()