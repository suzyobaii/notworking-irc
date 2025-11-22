import socket
import threading
import sys
import os
import signal

## ANSI colors for terminal output
class Color:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
def color(text,cc): #cc is color code
    return f"{cc}{text}{Color.RESET}"

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

/quite                         - Leave chat and Disconnect from the server.

/help                          - Display this help message.

"""
    print(help_message)


def connect_to_server(server_name, port):
    
	# connect to a server using the provided server name and port
    
	global client_socket, connected
      
	if connected:
		print(color("---Already connected to a server.---", Color.YELLOW)) #added ansi color yellow for the already connected message
		return
	
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((server_name, port))
		connected = True

		threading.Thread(target=receive_messages, daemon = True).start()
		print(color(f"--- Connected to server {server_name}:{port} ---", Color.GREEN)) #added ansi color green for the connection success message

	except Exception as e:
		print(color(f"--- Connection failed: {e} ---", Color.RED)) #added ansi color red for the connection failure message
		connected = False
		client_socket = None	


def disconnect_from_server():

	global client_socket, connected

	if connected:
		try:

			if client_socket:
				client_socket.sendall("/quit".encode('utf-8'))
			client_socket.close()
		
		except:
			pass
		finally:
			connected = False
			client_socket = None
			print(color("--- Disconnected from server.---", Color.RED)) #added ansi color red for the disconnection message
		os._exit(0)
	

def receive_messages():
	global connected

	while connected:
		try:
			data = client_socket.recv(1024)
			if not data:
				print(color("\n--- Server closed the connection. ---", Color.RED)) #added ansi color red for the server disconnection message
				disconnect_from_server()
				break

			print(f"\r{data.decode('utf-8')}\n", end='')
			sys.stdout.write(f"{nickname}>")
			sys.stdout.flush()
		
		except ConnectionResetError:
			print(color("\n--- Connection lost. ---", Color.RED)) #added ansi color red for the connection lost message
			connected = False
			break
		except Exception as e:
			if connected:
				print(color(f"\n--- Error receiving message: {e} ---", Color.RED)) #added ansi color red for the error message
			connected = False
			break


def send_message(message):
	global client_socket, connected

	if connected and client_socket:
		try:
			client_socket.sendall(message.encode('utf-8'))
		except Exception as e:
			print(f"--- Error sending message: {e} ---")
			connected = False
			client_socket.close()
	else:
		print(color("--- Not connected to any server. ---", Color.YELLOW)) #added ansi color yellow for the not connected message



def user_interface_loop():
	# This function will handle user input and command functionality

	global nickname, connected, client_socket # Access global variables

	def signal_handler(sign, frame):
		# This is how we handle Ctrl+C
		print(color(f"\n --- Keyboard Interupt. Exiting. . . ---", Color.BLUE)) #added ansi color BLUE for the keyboard interrupt message and edited typo

		disconnect_from_server()

	signal.signal(signal.SIGINT, signal_handler)
	
	display_help()

	while True:
		try:
			
			prompt = color(f"{nickname}>", Color.CYAN) #added ansi color cyan for the prompt
			sys.stdout.write(prompt)
			sys.stdout.flush()

			message = sys.stdin.readline().strip()

			if not message:
				continue

			if message.startswith('/'):
				split = message.split()
				command = split[0].lower()
				args = split[1:]

				if command == '/connect':
					host = args[0]
					port = int(args[1]) if len(args) > 1 else 65432 # maximum port number
					connect_to_server(host, port)
				
				elif command == '/quit':
					disconnect_from_server()

				elif command == '/help':
					display_help()
				
				elif connected:
					if command == '/nick':
						if len(args) != 1:
							print("Usage: /nick <nickname>")
						else:
							nickname = args[0]
							client_socket.sendall(f"/nick {nickname}".encode())
					
					elif command == '/list':
						client_socket.sendall("/list".encode())
					
					elif command == '/join':
						if len(args) != 1:
							print("Usage: /join <channel>")
						else:
							client_socket.sendall(f"/join {args[0]}".encode())
					
					elif command == '/leave':
						channel = args[0] if args else ""
						client_socket.sendall(f"/leave {channel}".encode())
					
					else:
						print(color("Unknown command. Type /help for a list of commands.", Color.YELLOW)) #added ansi color yellow for the unknown command message


				else:
					print(color("Not connected to any server. Use /connect to connect.", Color.YELLOW)) #added ansi color yellow for the not connected message

				
			elif connected:
				send_message(message)

			else:
				print(color("Not connected to any server. Use /connect to connect.", Color.YELLOW)) #added ansi color yellow for the not connected message

		except EOFError:
			disconnect_from_server()
		
		except Exception as e:
			disconnect_from_server()

if __name__ == "__main__":
	user_interface_loop()