# generate_info.py - generates information to be parsed


import secrets
import string
import random


def random_uid():
    uid = 'nicolas' + str(random.randint(100000000000,999999999999))
    return uid
