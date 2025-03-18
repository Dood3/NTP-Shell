import socket
import os
import base64
import hashlib
from scapy.all import IP, UDP, Raw, send
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

receiver_ip = "192.168.10.50"
receiver_port = 12345

sender_ip = "192.168.10.25"
sender_port = 54321

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((sender_ip, sender_port))

print(f"🔒 Secure shell started. Type 'exit' to quit.")

while True:
    command = input("🔐 Encrypted Command> ").strip()
    if command.lower() == "exit":
        print("Exiting...")
        break

    encrypted_command = encrypt_data(command)
    ntp_packet = (
            IP(dst=receiver_ip) /
            UDP(sport=sender_port, dport=receiver_port) /
            Raw(load=encrypted_command.encode())
    )
    send(ntp_packet)

    print(f"📡 Sent encrypted command. Waiting for response...\n")

    full_response = ""
    while True:
        data, addr = sock.recvfrom(4096)
        decrypted_chunk = decrypt_data(data.decode("utf-8"))

        if decrypted_chunk == "__END__":
            break

        full_response += decrypted_chunk

    print(f"🔓 Decrypted Response:\n{full_response}\n")
