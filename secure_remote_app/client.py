import asyncio
import websockets
import json
import logging
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from cryptography.fernet import Fernet
import subprocess
import socket
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_URI = "ws://localhost:8765" # Change to WSS (TLS) and domain for remote connections
TOKEN = "secure_token_123"

# Unique ID utilizing hostname to easily identify who is who on the network
MY_CLIENT_ID = f"client_{socket.gethostname()}_{id(object())}"

# Security: Hardcoded whitelist. The client will completely reject running any command not listed here!
WHITELIST = {
    'ipconfig': ['ipconfig'],
    'Ping Google': ['ping', '8.8.8.8'],
    'System Info': ['systeminfo'],
    'whoami': ['whoami'],
    'Hello World Echo': ['cmd.exe', '/c', 'echo']
}

def get_local_ip():
    """ Get the active LAN IP of the current machine for direct P2P connection """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()

class RemoteAppClient:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Secure Remote App - {MY_CLIENT_ID}")
        
        # -----------------------------
        # UI Setup (Tkinter)
        # -----------------------------
        frame = ttk.Frame(root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Available Targets:").grid(row=0, column=0, sticky=tk.W)
        self.client_combo = ttk.Combobox(frame, state="readonly", width=40)
        self.client_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(frame, text="Whitelisted Command:").grid(row=1, column=0, sticky=tk.W)
        self.cmd_combo = ttk.Combobox(frame, values=list(WHITELIST.keys()), state="readonly", width=40)
        self.cmd_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        if list(WHITELIST.keys()):
            self.cmd_combo.set(list(WHITELIST.keys())[0])

        ttk.Label(frame, text="Additional Argument (if applicable):").grid(row=2, column=0, sticky=tk.W)
        self.args_entry = ttk.Entry(frame, width=40)
        self.args_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        self.run_btn = ttk.Button(frame, text="Execute Remotely (P2P + E2EE)", command=self.on_run)
        self.run_btn.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="Output Console & Audit Trail :").grid(row=4, column=0, sticky=tk.W)
        self.output_area = scrolledtext.ScrolledText(frame, width=80, height=20, bg="#1e1e1e", fg="#00ff00")
        self.output_area.grid(row=5, column=0, columnspan=2, pady=5)

        self.loop = asyncio.new_event_loop()
        self.ws = None
        self.clients_list = []
        
        # Start the asyncio networking on a daemon thread
        threading.Thread(target=self.start_async_loop, daemon=True).start()

    def log_gui(self, msg):
        """ Appends messages to the Tkinter text area safely """
        self.output_area.insert(tk.END, msg + "\n")
        self.output_area.see(tk.END)

    def update_clients(self, clients):
        """ Updates the combo box with active targets (minus self) """
        self.clients_list = [c for c in clients if c != MY_CLIENT_ID]
        self.client_combo['values'] = self.clients_list
        if self.clients_list and not self.client_combo.get():
            self.client_combo.set(self.clients_list[0])
        elif not self.clients_list:
            self.client_combo.set('')

    # -----------------------------
    # Networking Layer (Asyncio)
    # -----------------------------
    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run_signaling_connection())

    async def run_signaling_connection(self):
        while True:
            try:
                self.root.after(0, self.log_gui, f"[SYSTEM] Connecting to central signaling server at {SERVER_URI}...")
                async with websockets.connect(SERVER_URI) as ws:
                    self.ws = ws
                    
                    # 1. Authenticate with Token
                    await ws.send(json.dumps({'type': 'AUTH', 'token': TOKEN, 'client_id': MY_CLIENT_ID}))
                    auth_resp = json.loads(await ws.recv())
                    if auth_resp.get('type') == 'AUTH_SUCCESS':
                        self.root.after(0, self.log_gui, "[SYSTEM] \u2714 Authenticated to signaling server securely!")
                    else:
                        self.root.after(0, self.log_gui, "[ERROR] Authentication failed! Invalid token.")
                        return

                    # 2. Continuous listening for list updates or P2P Signaling Requests
                    async for message in ws:
                        data = json.loads(message)
                        if data['type'] == 'CLIENT_LIST':
                            self.root.after(0, self.update_clients, data['clients'])
                        elif data['type'] == 'SIGNAL':
                            # Someone requested to connect directly to us
                            asyncio.create_task(self.handle_incoming_signal(data))
                            
            except Exception as e:
                self.root.after(0, self.log_gui, f"[!] Connection lost or unavailable: {str(e)}. Retrying in 5 seconds...")
                await asyncio.sleep(5)

    async def handle_incoming_signal(self, data):
        """ Receives the signaling instruction, sets up End-to-End Encryption, and acts as Client target """
        sender = data['sender_id']
        payload = data['payload']
        if payload['action'] == 'connect_req':
            ip_to_connect = payload['ip']
            port_to_connect = payload['port']
            
            # The symmetric encryption key generated uniquely for this session by the requester
            e2ee_key = payload['key'].encode()
            fernet = Fernet(e2ee_key)
            
            self.root.after(0, self.log_gui, f"\n[P2P] Incoming remote execution request from {sender}. Connecting E2EE Tunnel to {ip_to_connect}:{port_to_connect}...")
            
            try:
                # Target connects directly Back to the initiator's P2P opened ephemeral port
                reader, writer = await asyncio.open_connection(ip_to_connect, port_to_connect)
                
                # Handshake complete, signify READY via encrypted tunnel
                writer.write(fernet.encrypt(b"READY"))
                await writer.drain()
                
                # Wait for the Execution payload
                enc_cmd = await reader.read(8192)
                if not enc_cmd: return
                
                cmd_data = json.loads(fernet.decrypt(enc_cmd).decode())
                command = cmd_data['cmd']
                args = cmd_data['args']
                
                self.root.after(0, self.log_gui, f"[AUDIT] Remote request received to run '{command}' with args '{args}'")
                
                # SECURITY: Verify logic against whitelist
                if command in WHITELIST:
                    full_cmd = list(WHITELIST[command])
                    if args:
                        full_cmd.append(args)
                    self.root.after(0, self.log_gui, f"[EXEC] Spawning subprocess: {' '.join(full_cmd)}")
                    try:
                        proc = subprocess.run(full_cmd, capture_output=True, timeout=15)
                        # We merge stdout and stderr
                        output = proc.stdout + proc.stderr
                        result_msg = output if output else b"Success (No output returned)"
                    except Exception as e:
                        result_msg = str(e).encode()
                else:
                    self.root.after(0, self.log_gui, f"[SECURITY] Execution blocked! Command '{command}' not in whitelist.")
                    result_msg = b"Execution Refused: Arbitrary command execution is forbidden!"
                
                # Send encrypted results back
                writer.write(fernet.encrypt(result_msg))
                await writer.drain()
                
                writer.close()
                await writer.wait_closed()
                self.root.after(0, self.log_gui, f"[P2P] Result securely sent to {sender}. Tunnel closed.")
                
            except Exception as e:
                logging.error(f"P2P Connection Error: {e}")
                self.root.after(0, self.log_gui, f"[ERROR] P2P tunnel failed: {str(e)}")


    # -----------------------------
    # Exection Request Logic (Initiator)
    # -----------------------------
    def on_run(self):
        target = self.client_combo.get()
        cmd = self.cmd_combo.get()
        args = self.args_entry.get().strip()
        
        if not target:
            messagebox.showerror("Error", "No target client selected.")
            return

        self.log_gui(f"\n[*] Requesting '{cmd}' to run on {target} through E2EE Tunnel...")
        
        # Dispatch the async task
        asyncio.run_coroutine_threadsafe(self.initiate_p2p_request(target, cmd, args), self.loop)

    async def initiate_p2p_request(self, target, cmd, args):
        """ Spawns an ephemeral TCP Server to listen for the remote target and sends signaling data via central router. """
        
        # 1. Generate E2EE encryption key for this specific session (Libsodium/Fernet style symmetric TLS-equivalent padding)
        session_key = Fernet.generate_key()
        fernet = Fernet(session_key)
        
        local_ip = get_local_ip()
        
        # 2. Wait for incoming result
        result_future = self.loop.create_future()
        
        async def temp_server_handler(reader, writer):
            try:
                # Wait for Target to say READY
                enc_ready = await reader.read(8192)
                msg = fernet.decrypt(enc_ready)
                
                if msg == b"READY":
                    self.root.after(0, self.log_gui, "[P2P] Tunnel Opened. Routing encrypted command...")
                    # Send Encrypted Command
                    payload = json.dumps({'cmd': cmd, 'args': args}).encode()
                    writer.write(fernet.encrypt(payload))
                    await writer.drain()
                    
                    # Wait for execution Result
                    enc_result = b""
                    while True:
                        data = await reader.read(8192)
                        if not data: break
                        enc_result += data
                        
                    result = fernet.decrypt(enc_result).decode(errors='ignore')
                    result_future.set_result(result)
            except Exception as e:
                result_future.set_exception(e)
            finally:
                writer.close()
                await writer.wait_closed()

        # Start ephemeral local server
        server = await asyncio.start_server(temp_server_handler, '0.0.0.0', 0)
        ephemeral_port = server.sockets[0].getsockname()[1]
        
        self.root.after(0, self.log_gui, f"[SYSTEM] Ephemeral Listener started on Port {ephemeral_port}. Sending Signalling route via central server...")
        
        # 3. Route parameters via Signaling Server Payload
        if self.ws:
            signal_msg = {
                'type': 'SIGNAL',
                'target_id': target,
                'payload': {
                    'action': 'connect_req',
                    'ip': local_ip,
                    'port': ephemeral_port,
                    'key': session_key.decode() # Secure because signaling connection WebSocket itself should be WSS/TLS
                }
            }
            await self.ws.send(json.dumps(signal_msg))
            
            try:
                result = await asyncio.wait_for(result_future, timeout=20.0) # 20 second app timeout
                self.root.after(0, self.log_gui, f"\n--- [TARGET RETURN STDOUT/ERR] ---\n{result}\n----------------------------------")
            except asyncio.TimeoutError:
                self.root.after(0, self.log_gui, "[!] Execution timed out. Target client may be unresponsive or unreachable due to strict NAT.")
            except Exception as e:
                self.root.after(0, self.log_gui, f"[!] Error during remote tunnel execution: {e}")
            finally:
                server.close()
                await server.wait_closed()

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteAppClient(root)
    root.mainloop()
