import socket    # TCP Socket
import threading # handles multiple clients
import random    # to choose one of three transformatons


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # This creates a TCP socket rather
								     # UDP (which is DGRAM)

HOST = '127.0.0.1'                       # loopback only to keep incoming transmission to this machine
PORT = input(int("Enter Port Number to listen on (1024-65535): ").strip())		


def reverse_string(incoming):
	return incoming[::-1]


def replace_vowels(incoming):
	vowels = "aeiouAEIOU"
	out = incoming
	for v in vowels:
		out = out.replace(v, "*")
	return out


def count_words(incoming):
	words = len(incoming.split())
	return f"The message contains {words} word{'s' if words !=1 else ''}."


TRANSFORMS  = [reverse_string, replace_vowels, count_words]

def transform_message(msg: str) -> str: #Transforms message if it exists

	parts = msg.split(':', 1)
	content = parts[1].strip() if len(parts) == 2 else msg.strip()

	func = random.choice(TRANSFORMS)
	transformed = func(content)
	return f"SERVER_RESPONSE: {transformed}"

def client(conn: socket.socket, addr):
	with conn:
		while True:
			data = conn.recv(4096)
			if not data:
				break

			incoming = data.decode('utf-8', errors='replace').strip()
			response = transform_message(incoming)
			conn.sendall(response.encode('utf-8'))


def main():

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	server_socket.bind((HOST, PORT))
	server_socket.listen()

	print(f"TCP server listening on {HOST}:{PORT}")


	try:
		while True:
			conn, addr = server_socket.accept()
			
			t = threading.Thread(target=client, args =(conn, addr), daemon=True)
			t.start()
	except KeyboardInterrupt:
		print("\nShutting down connection...")
	finally:
		server_socket.close()

if __name__=="__main__":
	main()




