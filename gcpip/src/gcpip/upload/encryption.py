# https://nitratine.net/blog/post/encryption-and-decryption-in-python/
import logging
from cryptography.fernet import Fernet
from gcpip.utils.encryption import get_kms_key_path

logger = logging.getLogger(__name__)


def generate_key():
    """
    Generates a fresh fernet key. Keep this some place safe! If you lose it
    you’ll no longer be able to decrypt messages; if anyone else gains
    access to it, they’ll be able to decrypt all of your messages, and
    they’ll also be able forge arbitrary messages that will be
    authenticated and decrypted.
    Returns (str): A URL-safe base64-encoded 32-byte key

    """
    return Fernet.generate_key()


def write_key_into_file(key, filename):
    """
    It writes the key into a file.
    Args:
        key (str): A Key.
        filename (str): A file name to record the key.

    Returns: A file that has the key.

    """
    file = open(filename, 'wb')
    file.write(key)  # The key is type bytes still
    file.close()


def encrypt_file(input_file, key):
    """
    Encrypt a file using given key. The result of this encryption is known as
    a “Fernet token” and has strong privacy and authenticity guarantees.
    Args:
        input_file (str): Full path to the input file.
        key (str): A URL-safe base64-encoded 32-byte key

    Returns: Encrypted file and write an new file with .encrypted extension
    added to the original file.

    """
    output_file = '{}.encrypted'.format(input_file)
    with open(input_file, 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)

    with open(output_file, 'wb') as f:
        f.write(encrypted)


def decrypt_file(input_file, key):
    """
    Decrypt a file using given key.
    Args:
        input_file: Full path to the input file.
        key: A URL-safe base64-encoded 32-byte key

    Returns: Decrypted file and write it as a new file. If .encrypted  exist in
    the name of file it remove it and if it doesn't exist it add .decrypted
    extension.
    """
    with open(input_file, 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    decrypted = fernet.decrypt(data)

    if '.encrypted' in input_file:
        output_file = input_file.replace('.encrypted', '')
    else:
        output_file = '{}.decrypted'.format(input_file)

    with open(output_file, 'wb') as f:
        f.write(decrypted)

    return output_file


def encrypt_dek(kms_client, dek, project_id, location_id, key_ring_id, key_id):
    """
    Encrypt data encryption key (DEK) using GCP KMS key

    Args:
        kms_client (google.cloud.kms_v1.KeyManagementServiceClient): 
            KMS client object
        dek (bytes): DEK
        kms_key (str): KMS key resource name

    Returns:
        bytes: Encrypted DEK
    """

    logger.debug("Encrypting DEK via GCP KMS")

    kms_key = get_kms_key_path(
        kms_client, project_id, location_id, key_ring_id, key_id)

    response = kms_client.encrypt(kms_key, dek)
    return response.ciphertext


def decrypt_dek(kms_client, dek, project_id, location_id, key_ring_id, key_id):
    """
    Decrypt data encryption key (DEK) using GCP KMS key

    Args:
        kms_client (google.cloud.kms_v1.KeyManagementServiceClient): 
            KMS client object
        dek (bytes): DEK
        kms_key (str): KMS key resource name

    Returns:
        bytes: Plaintext DEK
    """

    logger.debug("Encrypting DEK via GCP KMS")

    kms_key = get_kms_key_path(
        kms_client, project_id, location_id, key_ring_id, key_id)

    response = kms_client.decrypt(kms_key, dek)
    return response.plaintext
