from pickle import load,dump
class continue_game:
    def log_in(self):        
        while True:
            self.username = raw_input("Enter Username: ")
            self.password = raw_input("Enter Password: ")
            if self.check():
                break
            else:
                print "Username or Password does not exist in our server please re-type"
    def __str__(self):
        return "WORKS"
    def check(self):
        f=open("Player_details.dat","rb")
        try:
            while True:
                a = load(f)
                if a.p_username == self.username and a.p_password == self.password:
                    player_det = a
                    return True
        except EOFError:
            f.close()
            return False
