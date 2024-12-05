import os

def get_role_passwords():
    return {
        'police': os.getenv('BCHOC_PASSWORD_POLICE', 'P80P'),
        'lawyer': os.getenv('BCHOC_PASSWORD_LAWYER', 'L76L'),
        'analyst': os.getenv('BCHOC_PASSWORD_ANALYST', 'A65A'),
        'executive': os.getenv('BCHOC_PASSWORD_EXECUTIVE', 'E69E'),
        'creator': os.getenv('BCHOC_PASSWORD_CREATOR', 'C67C')
    }

def validate_password(password):
    valid_passwords = get_role_passwords().values()
    return password in valid_passwords

def get_owner(password):
    owners = get_role_passwords()
    owner = ""
    for singleOwner in owners:
        if owners[singleOwner] == password:
            owner = singleOwner.upper()
    owner = owner.encode()

    if owner == b'CREATOR':
        owner = b""

    return owner