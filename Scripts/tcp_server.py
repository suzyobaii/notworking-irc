import socket    # TCP Socket
import threading # handles multiple clients


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # This creates a TCP socket rather
								     # UDP (which is DGRAM)

HOST = '127.0.0.1'                       # loopback only to keep incoming transmission to this machine
PORT = input(int("Enter Port Number to listen on (1024-65535): ").strip())


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
				conn, addr = server_socket.accept()
				
				t = threading.Thread(target=self.handle_object, args =(conn, addr), daemon=True)
				t.start()
		except KeyboardInterrupt:
			print("\nShutting down connection...")
		finally:
			server_socket.close()

	# Handling client objects (deserializing)
	def handle_object(self):
		pass

	# Create a channel when a client joins the server
	def create_channel(self):
		pass

	# Create a log of user activity
	def logging(self):
		pass

	def shutdown(self):
		pass


def main():
	pass

if __name__=="__main__":
	main()




