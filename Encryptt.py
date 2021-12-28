
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import ntpath


class EncryptionCont:


    def __init__(self, sak, directory):
        """
        - Encryption constructor, generate key to be used to encrypt and decrypt files
        Use AWS Sectret Access key as password for Password Based Key Derivation Function 2
        :param sak: Use AWS Secret Access Key to generate encryption key
        :param directory: Directory S3_Live_Folder is saved
        """
        self.s3_live_folder = directory + r"\S3_Live_Folder"
        password = sak.encode() # Convert to bytes
        salt = b'E\n\xbb\xfd\x9cv\xab\xc9\x9e\xda\xdcc\xb9\xf1]\x00' # SALT - random 16 byte, extra encryption
        kdf = PBKDF2HMAC(               #password based key derived function
            algorithm=hashes.SHA256(),  #Uses SHA256 hashing algorithm to determine key
            length=32,
            salt=salt,
            iterations=100000,          #100,000 iterations
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password)) 
        self.key = key


    def encrypt(self, input_file):
        """
        - Encrypt file and return file location
        Append encrypted file with extension
        :param input_file: File to be encrypte
        :return ef_file: Encrypted file 
        """
        ext = os.path.splitext(input_file)[-1]  #Parse filename extenstion
        with open(input_file, 'rb') as f:
            data = f.read()
        ef_file = self.s3_live_folder + "\\" + ntpath.basename((input_file.split(".")[0])) + ".encrypted"  
        fernet = Fernet(self.key)           # fernet encryption key
        encrypted = fernet.encrypt(data)    # encrypted data
        with open(ef_file, 'wb') as f:
            f.write(encrypted)          #save data
            f.write(ext.encode())       #Save file extension (in byte format) at end of encrypted file 
        return ef_file


    def decrypt(self, ef_file):
        """
        - Decrypt file and return new file name and path.
        :param ef_file: Name and location of encrypted file
        :return df_file: Name and location of decrypted file
        """


        with open(ef_file, 'rb') as f:
            data = f.read()
        ext = os.path.splitext(data)[1].decode()   #parse file extension of encrypted file
        data = os.path.splitext(data)[0]
        df_file = self.s3_live_folder + "\\" + ntpath.basename((ef_file.split(".")[0])) + ext
        fernet = Fernet(self.key)
        decrypted = fernet.decrypt(data)
        with open(df_file, 'wb') as f:
            f.write(decrypted)
        return df_file


    def is_encrypted(self, ef_file):
        """
        - Returns Boolean True if file is encrypted
        :param ef_file: Name and location of file in question.
        :return True/False: True if file is encrypted, false if not
        """
        try:
            #Attempt to decrypt the file.
            with open(ef_file, 'rb') as f:
                data = f.read()
            ext = os.path.splitext(data)[1].decode()   #parse file extension of encrypted file
            data = os.path.splitext(data)[0]
            df_file = self.s3_live_folder + "\\" + ntpath.basename((ef_file.split(".")[0])) + ext
            fernet = Fernet(self.key)
            decrypted = fernet.decrypt(data)
            with open(df_file, 'wb') as f:
                f.write(decrypted)
            os.remove(df_file)
            return True
        except:
            #File is not encrypted
            return False
