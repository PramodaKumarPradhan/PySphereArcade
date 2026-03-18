import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

VALID_TOKENS = {"secure_token_123", "admin_token_456"}
clients = {} # Maps client_id to their websocket connection

async def handler(websocket, path):
    client_id = None
    try:
        # Step 1: Authentication upon connecting
        auth_msg = await websocket.recv()
        auth_data = json.loads(auth_msg)
        
        if auth_data.get('type') != 'AUTH' or auth_data.get('token') not in VALID_TOKENS:
            await websocket.send(json.dumps({'error': 'Authentication failed'}))
            logging.warning("Failed authentication attempt.")
            return
        
        client_id = auth_data.get('client_id')
        if not client_id or client_id in clients:
            await websocket.send(json.dumps({'error': 'Invalid or duplicate client_id'}))
            return
            
        clients[client_id] = websocket
        logging.info(f"Client {client_id} connected. Total clients: {len(clients)}")
        await websocket.send(json.dumps({'type': 'AUTH_SUCCESS', 'message': 'Authenticated'}))
        
        # Broadcast updated list of clients to everyone
        await broadcast_clients()

        # Step 2: Main message loop (Signaling Router)
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'SIGNAL':
                target_id = data.get('target_id')
                if target_id in clients:
                    # Forward the P2P connection metadata (like local IP, ephemeral port, encryption key)
                    await clients[target_id].send(json.dumps({
                        'type': 'SIGNAL',
                        'sender_id': client_id,
                        'payload': data.get('payload')
                    }))
                    logging.info(f"Routed SIGNAL from {client_id} to {target_id}")
                else:
                    await websocket.send(json.dumps({'error': f'Target {target_id} not found or offline'}))
            elif data['type'] == 'GET_CLIENTS':
                await broadcast_clients()
                
    except websockets.exceptions.ConnectionClosed:
        pass # Expected on disconnect
    except Exception as e:
        logging.error(f"Error handling connection: {e}")
    finally:
        if client_id in clients:
            del clients[client_id]
            logging.info(f"Client {client_id} disconnected. Total clients: {len(clients)}")
            await broadcast_clients()

async def broadcast_clients():
    """ Sends the current list of online clients to everyone connected. """
    client_list = list(clients.keys())
    for ws in clients.values():
        try:
            await ws.send(json.dumps({'type': 'CLIENT_LIST', 'clients': client_list}))
        except:
            pass

async def main():
    logging.info("Signaling Server starting on ws://localhost:8765...")
    # NOTE: Run behind an NGINX proxy or pass `ssl` arg to serve() to enforce WSS/TLS in production.
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
