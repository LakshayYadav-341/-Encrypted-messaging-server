import socket
import json
import random
import hashlib
import logging
from tinyec import registry
from tinyec.ec import Point

curve = registry.get_curve('secp256r1')

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

alice_private_key = None
alice_public_key = None
soc = None

def alice_generate_keys():
    global alice_private_key, alice_public_key
    alice_private_key = random.randint(1, curve.field.n - 1)
    alice_public_key = alice_private_key * curve.g
    logger.debug(f"Alice: Private Key = {alice_private_key}, Public Key = ({alice_public_key.x}, {alice_public_key.y})")

def alice_connect_to_bob():
    global soc
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(('127.0.0.1', 65432))
    logger.info("Alice: Connected to Bob.")

def validate_ephemeral_point(ephemeral_point):
    max_ascii = 256
    validation_value = (ephemeral_point.x * max_ascii + ephemeral_point.y) % curve.field.n
    return 0 <= validation_value < curve.field.n

def hash_data(data):
    if isinstance(data, (int, float)):
        data = str(data)
    return hashlib.sha256(data.encode()).hexdigest()

def alice_send_c_and_h1():
    global ephemeral_point, h1
    while True:
        s = random.randint(1, curve.field.n - 1)
        ephemeral_point = s * curve.g

        if validate_ephemeral_point(ephemeral_point):
            alpha = ephemeral_point.x
            beta = ephemeral_point.y
            break
    global soc, alice_private_key
    bob_data = json.loads(soc.recv(1024).decode())
    bob_public_key = Point(curve, bob_data["public_key"][0], bob_data["public_key"][1])
    logger.debug(f"Alice: Received Bob's Public Key: ({bob_public_key.x}, {bob_public_key.y})")

    r = random.randint(1, curve.field.n)
    C1 = r * curve.g
    C2 = r * bob_public_key + ephemeral_point
    C = (C1.x, C1.y, C2.x, C2.y)

    C_str = f"{C[0]},{C[1]},{C[2]},{C[3]}"
    previous_session_params = (11559377393155667125263133427401878852421874756924672996586244211754533816722,
                               34398016232641581275493554573025958717367562792128669770789717795283718591666)

    h1 = hash_data(f"{C_str}".join(map(str, previous_session_params)))
    data = {"C": C, "h1": h1}
    soc.sendall(json.dumps(data).encode())
    logger.info("Alice: Sent C and h1 to Bob.")

def xor_strings(str1, str2):
    length = min(len(str1), len(str2))
    result = []

    for i in range(length):
        xor_result = ord(str1[i]) ^ ord(str2[i])
        result.append(chr(xor_result))

    return ''.join(result)

def alice_validate_ch1():
    global soc, ephemeral_point, h1
    response = json.loads(soc.recv(1024).decode())
    CH1 = response["CH1"]

    alpha = ephemeral_point.x
    beta = ephemeral_point.y

    h4 = hash_data(f"{alpha},{beta}")
    CH2 = xor_strings(h1, CH1)

    if CH2 == h4:
        logger.info("Alice: Authentication succeeded.")
    else:
        logger.warning("Alice: Authentication failed.")

def alice_cleanup():
    global soc
    if soc:
        soc.close()
    logger.info("Alice: Connection closed.")
