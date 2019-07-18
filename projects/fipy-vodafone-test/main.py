from network import LTE
from machine import WDT
import time
import socket

# NOTE: test the code. Changed prints during loops


#sqnsupgrade.info(verbose=False, debug=False)
print("#####################")
print("#####################")
print("NB-IoT Test v0.2")
wdt=WDT(timeout=20000000)

lte = LTE()
#lte.init()
for i in range(4):
    ccid=lte.iccid()
    print ("   ccid = " + str(ccid))
    if ccid:
       break
    time.sleep(1)
#Vodafone UK apn=nb.inetd.gdsp
print("Attempting to attach...", end="")
lte.attach(band=20,apn="ep.inetd.gdsp")
for j in range(10):
    print(".", end ="")
    time.sleep(1)
    if lte.isattached():
        print("\nAttached in attempt #"+str(j+1))
        break
    lte.send_at_cmd('AT+CEREG?').replace('\r\n','')
#NOTE: for Vodafone UK: AT+COPS=1,2,"23415"
    lte.send_at_cmd('AT+COPS=1,2,"23415"').replace('\r\n','')
lte.connect()
print("Attempting to connect..", end="")
for i in range(10):
    print(".", end ="")
    if lte.isconnected():
        print("\nConnected in attempt #"+str(i+1))
        break

packet = b'$\x1a\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01'
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(20)
s.connect(("8.8.8.8", 53))
s.send(packet)
resp=s.recv(100)
result=False
if (len(resp)>34): # very hacky error checking
    ip=resp[-4:]
    result=str(ip[0])+'.'+str(ip[1])+'.'+str(ip[2])+'.'+str(ip[3])
print("DNS result: "+str(result))

lte.pppsuspend() # can't send AT commands while in data mode
time.sleep_ms(100)
csq=lte.send_at_cmd('AT+CSQ').replace('\r\n','').replace('OK','')
sgnl=int(csq.split(',')[0].split(' ')[1])
if sgnl!=99:
    sgnl=-113+(2*sgnl)
    cesq=lte.send_at_cmd('AT+CESQ').replace('\r\n','').replace('OK','').split(',')
    rsrq=int(cesq[4])
    if rsrq!=255:
        rsrq=-20+(rsrq*0.5)
        rsrp=int(cesq[5])
    if rsrp!=255:
        rsrp=-140+rsrp

print(sgnl,rsrq,rsrp)
lte.pppresume()
