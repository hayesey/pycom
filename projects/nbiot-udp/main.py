from network import LTE
import time
import socket

lte = LTE()
#Vodafone UK apn=nb.inetd.gdsp
print("Attempting to attach...", end="")
lte.attach(band=20,apn="ep.inetd.gdsp")
for j in range(10):
    print(".", end ="")
    time.sleep(1)
    if lte.isattached():
        print("\nAttached in attempt #"+str(j+1))
        break
lte.connect()
print("Attempting to connect..", end="")
for i in range(10):
    print(".", end ="")
    if lte.isconnected():
        print("\nConnected in attempt #"+str(i+1))
        break

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(20)
s.connect(("3.9.21.110", 6789))
result = s.send(b'helloworld')
print("Sent bytes: "+str(result))

lte.disconnect()
lte.dettach()
