import hmac
import hashlib

from db import DB

def calc_proof(session, secret):
    return hmac.new(session, secret, hashlib.sha512).digest()

def auth(session, user, proof):
    user = DB.get(user.decode('utf-8'))
    if not user:
        return False
    secret = user['secret'].encode('utf-8')
    truth = calc_proof(session, secret)
    return hmac.compare_digest(truth, proof)
