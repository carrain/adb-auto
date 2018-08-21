import re

f = open("ip.txt")
e = open("new_ip.txt","w+")

ip = f.readlines()
reg = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
leng = 0
while leng < len(ip):
    new_ip = reg.findall(ip[leng])
    leng = leng +1
    if len(new_ip) >0:
        ip_leng = 0
        ip_txt = ""
        e.write(new_ip[0])
        e.write("\n")
        print new_ip[0]