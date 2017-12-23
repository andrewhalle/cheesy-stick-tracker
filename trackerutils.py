import random
import string
import hashlib

def get_password_hash_and_salt(password, salt=None):
    # returns the tuple (SHA256(password), salt), if salt is not provided it generates
    # a random one
    m = hashlib.sha256()
    if salt == None:
        salt = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(15))
    m.update((password + salt).encode("utf-8"))
    return (m.hexdigest(), salt)
