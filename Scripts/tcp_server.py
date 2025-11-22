import socket    # TCP Socket
import threading # handles multiple clients

HOST = '127.0.0.1'                       # loopback only to keep incoming transmission to this machine
PORT = int(input("Enter Port Number to listen on (1024-65535): ").strip()) #fixed issue input(int( gave me an error



"""
A channel is a named group of one or more clients. All clients receive
messages addressed to the channel. A channel is created when a client
joins. A client can reference the channel using the channel name. 
"""
class Channel:
	def __init__(self, name):
		self.name = name
		self.users = set()

	# Messages sent to the channel are broadcast to all users (except sender)
	def broadcast(self, sender, message):
		pass

	# Add a user to the channel when they use the /join command
	def add_user(self, user):
		self.users.add(user)

	# Remove a user when they use the /leave command
	def remove_user(self, user):
		self.users.remove(user)

	# Return the number of users in the channel
	def user_count(self):
		return len(self.users)
	

"""
A Server is a place where clients can connect to. It takes in a 
port number and a debug level (0 or 1) as arguments. Channels are 
created in servers. The server logs user interactions and manages
channels and clients. The server should automatically shutdown when
there is no activity for 3 minutes. A maximum of 4 clients can be
on the server at the same time. 
"""
class ChatServer:
	def __init__(self, port, debug_level=0):
		self.host = '127.0.0.1'
		self.port = port
		self.debug_level = debug_level
		self.socket = None
		self.channels = {}
		self.clients = {}

	# Server will start running at the port number
	def startup(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.socket.bind(('127.0.0.1', self.port))
		self.socket.listen(4) # Maximum of 4 threads (clients)

		print(f"TCP server listening on {self.host}:{self.port}")

	# Server will accept users
	def listen(self):
		try:
			while True:
				conn, addr = self.socket.accept()  #small change: use self.socket instead of global server_socket
				print(f"New client connected from {addr}")  #minimal feedback for testing

				#for now spawning a thread that does nothing
				t = threading.Thread(target=self.handle_object, args=(conn, addr), daemon=True)
				t.start()
		except KeyboardInterrupt:
			print("\nShutting down connection...")
		finally:
			self.socket.close()

	# Handling client objects (deserializing)
	def handle_object(self, conn, addr):
		
		conn.sendall("Enter your nickname: ".encode())
		nickname = conn.recv(1024).decode().strip()

		#save client in the server's client dictionary
		self.clients[nickname] = conn
		print(f"{nickname} connected from {addr}")
		print("Connected clients:", ", ".join(self.clients.keys()))
		
		try:
			while True:
				message = conn.recv(1024)
				if not message:
					break  #client disconnected

				message_text = message.decode()
				print(f"{nickname}: {message_text}")  #prints message

				#broadcast to all other clients
				for user, client_conn in self.clients.items():
					if user != nickname:
						try:
							client_conn.sendall(f"{nickname}: {message_text}".encode())
						except:
							pass

		except ConnectionResetError:
			print(f"{nickname} disconnected unexpectedly.")
		finally:
			# Remove client when they leave
			del self.clients[nickname]
			conn.close()
			print(f"{nickname} disconnected.")
			print("Connected clients:", ", ".join(self.clients.keys()) if self.clients else "No clients connected")

	# Create a channel when a client joins the server
	def create_channel(self):
		pass  # implement later

	# Create a log of user activity
	def logging(self):
		pass  # mumo will implement later

	def shutdown(self):
		pass  # jonathan will do later


def main():
	server = ChatServer(PORT)
	server.startup()
	server.listen()

if __name__=="__main__":
	main()
