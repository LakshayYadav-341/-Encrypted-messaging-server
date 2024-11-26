import socket
import json
import random
import hashlib
import logging
from tinyec import registry
from tinyec.ec import Point

curve = registry.get_curve('secp256r1')
p = curve.field.p

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

bob_private_key = None
bob_public_key = None
conn = None
server = None

def xor_strings(str1, str2):
    # Make sure both strings are the same length
    length = min(len(str1), len(str2))  # Choose the shorter length
    result = []

    for i in range(length):
        # XOR the characters and store the result
        xor_result = ord(str1[i]) ^ ord(str2[i])
        result.append(chr(xor_result))  # Convert back to character

    return ''.join(result)

def bob_start_server():
    global server, conn
    server_ip = '127.0.0.1'
    server_port = 65432
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(1)
    logger.info("Bob: Server started. Waiting for Alice...")
    conn, addr = server.accept()
    logger.info(f"Bob: Connection established with {addr}.")

def bob_generate_keys():
    global bob_private_key, bob_public_key
    bob_private_key = random.randint(1, curve.field.n - 1)
    bob_public_key = bob_private_key * curve.g
    logger.debug(f"Bob: Private Key = {bob_private_key}, Public Key = ({bob_public_key.x}, {bob_public_key.y})")

def bob_send_public_key():
    global bob_public_key, conn
    public_key_data = {
        "public_key": (bob_public_key.x, bob_public_key.y)
    }
    conn.sendall(json.dumps(public_key_data).encode())
    logger.debug("Bob: Public key sent to Alice.")

def hash_data(data):
    if isinstance(data, (int, float)):
        data = str(data)
    return hashlib.sha256(data.encode()).hexdigest()

def bob_process_message_from_alice():
    global conn, bob_private_key
    data = json.loads(conn.recv(1024).decode())
    logger.debug(f"Bob: Received Data: {data}")
    
    C = data["C"]
    h1 = data["h1"]

    C1 = Point(curve, C[0], C[1])
    C2 = Point(curve, C[2], C[3])
    logger.debug(f"Bob: C1 Point = ({C1.x}, {C1.y})")
    logger.debug(f"Bob: C2 Point = ({C2.x}, {C2.y})")

    M = bob_private_key * C1
    bob_ephemeral_points = C2 - M
    logger.debug(f"Bob: Calculated ephemeral point = ({bob_ephemeral_points.x}, {bob_ephemeral_points.y})")

    previous_session_params = (11559377393155667125263133427401878852421874756924672996586244211754533816722,
                               34398016232641581275493554573025958717367562792128669770789717795283718591666)

    C_str = f"{C[0]},{C[1]},{C[2]},{C[3]}"
    h2 = hash_data(f"{C_str}".join(map(str, previous_session_params)))

    if h1 == h2:
        logger.info("Bob: Hash matched.")
    else:
        logger.warning("Bob: Hash mismatch, h1 and h2 do not match.")

    h3 = hash_data(f"{bob_ephemeral_points.x},{bob_ephemeral_points.y}")
    CH1 = xor_strings(h1,h3)
    conn.sendall(json.dumps({"CH1": CH1}).encode())
    logger.info("Bob: Sent CH1 to Alice.")

def bob_cleanup():
    global conn, server
    if conn:
        conn.close()
    if server:
        server.close()
    logger.info("Bob: Server and connection closed.")
