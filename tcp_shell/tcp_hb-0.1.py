import socket

TARGET_IP = '192.168.10.25'  # Change this to your satellite's IP
TARGET_PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TARGET_IP, TARGET_PORT))

print("[*] Connected to satellite via TCP. Type commands to send. Use 'exit' to quit.")

while True:
    cmd = input("CMD> ").strip()
    if not cmd:
        continue

    sock.sendall(cmd.encode())

    if cmd.lower() in ['exit', 'quit']:
        print("[*] Exiting.")
        break

    response = sock.recv(8192)
    print(response.decode())

sock.close()
