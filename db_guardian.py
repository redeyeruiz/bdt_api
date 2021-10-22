import os
import hashlib
import hmac

class Guardian:
    def __init__(self):
        
        self.__salt = os.urandom(hashlib.blake2b.SALT_SIZE) # in bytes
        self.__pepper = '+/*AZ!]hJS7421.Sgrs////////M74444422222222222222hugu3Gy' # in str

    def hide_psw(self, password):
        # Appends pepper to psw
        pepper_psw = password + self.__pepper

        # Coverts to bytes
        b_pepper_psw = pepper_psw.encode("utf-8")

        # Generates hash with salt!
        hashed_psw = hashlib.blake2b(b_pepper_psw, salt=self.__salt).hexdigest()

        return hashed_psw
    
    def verify_psw(self, user_input, registry):
        hashed_input = self.hide_psw(user_input)
        return hmac.compare_digest(hashed_input, registry)
    
    def get_salt(self):
        return self.__salt

    def set_salt(self, salt):
        self.__salt = salt



# guardian = Guardian()
# hashed = guardian.hide_psw('helloMotto!')
# salt = guardian.get_salt()

# print("HASH GENERATED: ")
# print(hashed)
# print("SALT GENERATED: ")
# print(type(salt))
# print(salt)

# print('\n\n')

# guardian2 = Guardian()
# guardian2.set_salt(salt)
# print("SALT SET: ")
# print(type(guardian2.get_salt()))
# print(guardian2.get_salt())
# print(guardian2.verify_psw('helloMotto!', hashed))