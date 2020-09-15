from sys import argv
from secrets import token_bytes

secret_key_length = int(argv[1])

secret_key = token_bytes(32)
with open("app/config/secret", 'wb') as secret_file:
	secret_file.write(secret_key)
