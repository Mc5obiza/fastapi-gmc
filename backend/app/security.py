import bcrypt

def hash_password(password:str) -> str:
    return bcrypt.hashpw(password.encode(),bcrypt.gensalt()).decode()
def verify_password(password:str, password_hash:str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(),hash_password.encode())
    except ValueError:
        return False