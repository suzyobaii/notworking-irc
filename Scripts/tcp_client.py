import socket
import threading
import sys
import os
import signal
from ChatProtocol import Command, Event, Message, serialize, deserialize

client_socket = None
connected = False
nickname = "Guest"

def display_help():
    # List available commands
    
	# multi-line formatted string defining the help messages
    help_message = f"""
--- Chat Client Help Commands ---

/connect <server-name> [port#] - connect to the specified server.

/nick <nickname>               - Pick a unique nickname.

/list                          - List all connected users.

/join <channel>                - Join a specific channel.

/leave [<channel>]             - Leave the current or specific channel.

/quit					       - Leave chat and Disconnect from the server.

/help						   - Display this help message.

"""
    print(help_message)

def connect_to_server(server_name, port):
    
	# connect to a server using the provided server name and port
    
	global client_socket, connected
      
	if connected:
		print("---Already connected to a server.---")
		return
	
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((server_name, port))
		connected = True

		threading.Thread(target=receive_messages, daemon = True).start()
		print(f"--- Connected to server {server_name}:{port} ---")
	except Exception as e:
		print(f"--- Connection failed: {e} ---")
		connected = False
		client_socket = None	


def disconnect_from_server():

	global client_socket, connected

	if connected:
		try:

			if client_socket:
				client_socket.sendall(serialize(Command(cmd="/quit")).encode('utf-8'))
			client_socket.close()
		
		except:
			pass
		finally:
			connected = False
			client_socket = None
			print("--- Disconnected from server.---")
		os._exit(0)
	

def receive_messages():
	global connected, nickname

	while connected:
		try:
			data = client_socket.recv(1024)
			if not data:
				print("\n--- Server closed the connection. ---")
				disconnect_from_server()
				break

			response = deserialize(data.decode('utf-8'))

			if isinstance(response, Event):
				print(f"\r{response.notif}\n", end='')

				if response.type == "nick":
					nickname = response.optional

			elif isinstance(response, Message):
				print(f"\r{response.sender}>{response.content}\n", end='')

			else:
				raise ValueError("Unknown response sent.")

			sys.stdout.write(f"{nickname}>")
			sys.stdout.flush()
		
		except ConnectionResetError:
			print("\n--- Connection lost. ---")
			connected = False
			break
		except Exception as e:
			if connected:
				print(f"\n--- Error receiving message: {e} ---")
			connected = False
			break


def send_message(message):
	global client_socket, connected

	if connected and client_socket:
		try:
			msg = Message(content=message)
			client_socket.sendall(serialize(msg).encode('utf-8'))
		except Exception as e:
			print(f"--- Error sending message: {e} ---")
			connected = False
			client_socket.close()
	else:
		print("--- Not connected to any server. ---")



def user_interface_loop():
	# This function will handle user input and command functionality

	global nickname, connected, client_socket # Access global variables

	def signal_handler(sign, frame):
		# This is how we handle Ctrl+C
		print(f"\n --- Keyboard Intrrpt. Exiting. . . ---")
		disconnect_from_server()

	signal.signal(signal.SIGINT, signal_handler)
	
	display_help()

	while True:
		try:
			
			prompt = f"{nickname}>"
			sys.stdout.write(prompt)
			sys.stdout.flush()

			message = sys.stdin.readline().strip()

			if not message:
				continue

			if message.startswith('/'): # if the message is a command
				split = message.split()
				cmd = split[0].lower()
				args = split[1:]

				if cmd == '/connect':
					host = args[0]
					port = int(args[1]) if len(args) > 1 else 65432 # maximum port number
					connect_to_server(host, port)
				
				elif cmd == '/quit':
					disconnect_from_server()

				elif cmd == '/help':
					display_help()
				
				elif connected:
					command = Command(cmd=cmd, args=args)

					if cmd == '/nick':
						if len(args) != 1:
							print("Usage: /nick <nickname>")
						else:
							#nickname = args[0]
							client_socket.sendall(serialize(command).encode('utf-8'))
					
					elif cmd == '/list':
						client_socket.sendall(serialize(command).encode('utf-8'))
					
					elif cmd == '/join':
						if len(args) != 1:
							print("Usage: /join <channel>")
						else:
							client_socket.sendall(serialize(command).encode('utf-8'))
					
					elif cmd == '/leave':
						client_socket.sendall(serialize(command).encode('utf-8'))
					
					else:
						print("Unknown command. Type /help for a list of commands.")

				else:
					print("Not connected to any server. Use /connect to connect.")
				
			elif connected:
				send_message(message)

			else:
				print("Not connected to any server. Use /connect to connect.")
		except EOFError:
			disconnect_from_server()
		
		except Exception as e:
			disconnect_from_server()

if __name__ == "__main__":
	user_interface_loop()