#!/usr/bin/env python3
import pyotp
import socket
from db import DB

def save_db():
    try:
        open('db.py', 'w').write('DB = %r' % DB)
    except OSError:
        print('Can not write database file')
        exit(1)

print('Current users:')
for username, user in DB.items():
    print('- %-16s -> %r' % (username, list(user.keys())))

username = input('Username: ')
if username not in DB:
    print('User not exists')
    exit(1)

if 'otp_key' in DB[username]:
    print('This user already have OTP key.')
    print('R. (R)eset OTP key')
    print('U. (U)nset OTP key')
    choice = input(' => ').strip()
    if choice in 'Uu':
        del DB[username]['otp_key']
        save_db()
        print('OTP key removed for user %r' % username)
        exit()
    elif choice not in 'Rr':
        print('Invalid choice: %s' % choice)
        exit(1)


confirm = input('Are you sure you want to (re)set OTP key for %s? (y/N) ' % username)
if confirm.strip() not in 'Yy':
    print('Bye')
    exit()

otp_key = pyotp.random_base32()
DB[username]['otp_key'] = otp_key
save_db()

totp = pyotp.TOTP(otp_key)
url = totp.provisioning_uri(username, 'SSAA Guard - %s' % socket.gethostname())

try:
    import pyqrcode
    code = pyqrcode.create(url)
    print(code.terminal(background='white', quiet_zone=1))
    exit()
except ImportError:
    print('Warning: pyqrcode not installed, can not print QRcode')

print('Please input following secret key to Google Authenticator:')
print('')
print('  %s' % otp_key)
print('')
