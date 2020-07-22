from hashlib import sha256
import src.database as db

# Hash password with given salt
def hashPass(password, salt):
    salted = salt + password
    return sha256(salted.encode()).hexdigest()

# Check if correct password
def correctPassword(user, pswd):

    # Query db and check exists
    savedPass = db.get_password(user)
    salt = db.get_salt(user)
    if savedPass == None:
        return False

    # Compare hashed passwords
    attempt = hashPass(pswd, salt)
    return (savedPass == attempt)

# Check if is admin
def isAdmin(user):
    type = db.get_type(user)
    if type == "A":
        return True
    return False

# Check if is consultant
def isConsultant(user):
    type = db.get_type(user)
    if type == "C":
        return True
    return False
