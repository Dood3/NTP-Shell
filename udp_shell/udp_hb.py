import socket

TARGET_IP = '192.168.10.25'  # Change this to your satellite IP
TARGET_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)

print("[*] Homebase ready. Type commands to send. Use 'exit' to quit.")

while True:
    cmd = input("CMD> ").strip()
    if not cmd:
        continue

    sock.sendto(cmd.encode(), (TARGET_IP, TARGET_PORT))

    if cmd.lower() in ['exit', 'quit']:
        print("[*] Exiting.")
        break

    try:
        data, _ = sock.recvfrom(8192)
        print(data.decode())
    except socket.timeout:
        print("[!] No response received (timeout).")

sock.close()
