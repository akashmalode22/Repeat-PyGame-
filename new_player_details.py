from pickle import load,dump
from os import path
class new_player_details:
    def __init__(self):
        self.p_name = ""
        self.p_username = ""
        self.p_password = ""
        self.current_level_no = 1
        self.points = 0
        self.tot_time = 0
    def get_details(self):
        self.p_name = raw_input("Enter your Name: ")
        while True:
            self.p_username = raw_input("Enter Username: ")
            p_reusername = raw_input("Re-Type Username: ")
            if self.p_username == p_reusername:
                break
            else:
                print "Usernames do not Match. Please Re-Type"
        while True:
            while True:
                self.p_password= raw_input("Enter Password: ")
                if self.checkpass():
                    print "Password Unavailable.Please choose another"
                else:
                    break
            p_repassword = raw_input("Re-Type Password: ")
            if self.p_password == p_repassword:
                break
            else:
                print "Passwords do not Match. Please Re-Type"
        print "Login Successfull"
    def checkpass(self):
        if path.isfile("Player_details.dat"):
            f = open("Player_details.dat","rb")
            try:
                c = 0
                while True:
                    x = load(f)
                    c+=1
                    if x.p_password == self.p_password:
                        return True
            except EOFError:
                if c == 0 :
                    return False
                else:
                    return False
        else:
            return False
        f.close()
    def save(self):
        f = open("Player_details.dat","ab")
        dump(self,f)
        f.close()


         


            
