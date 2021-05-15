
import re

regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

common_passwords = open('recommend/common_passwords.txt').read().split('\n')

def validate_username(username):
    '''The username validation rules are as follows:
        length<20 characters
        no spaces
        no special characters apart from - and _'''
    if len(username) > 19: return False
    for i in list(username):
        if i in list(' ,.[]{}`~§±!@€£#$%^&*()+=\|";:/?'): return False
    return True


def validate_password(password):
    '''Ensures that the password has at least one capital, one lowercase letter, and one number and is more than 7 characters'''
    if len(password) < 7: return False
    capital = False
    lowercase = False
    number = False
    for i in list(password):
        if i in list('1234567890'): number = True
        if i in list('abcdefghijklmnopqrstuvwxyz'): lowercase = True
        if i in list('abcdefghijklmnopqrstuvwxyz'.upper()): capital = True
    if capital and lowercase and number: return True
    return False


def validate_email(email):
    '''Ensures an email using the validation rules ^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'''
    if (re.search(regex, email)): return True
    return False


def is_common_password(password):
    '''Ensures the password is not in a list of the 1000 most common passwords. .lower() ensures that it is not just a common password with some capitals added.'''
    if password.lower() in common_passwords: return True
    return False