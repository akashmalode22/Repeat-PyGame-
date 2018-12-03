from pickle import load,dump
class highscore:
    def __init__(self):
        self.name = ""
        self.score = 10
        self.total_time = 0
    def getdata(self):
        global player_det
        f = open("high_scores.dat","ab+")
        g = open("Temp.dat","ab")
        self.hiscore_list = []
        try:
            self.hiscore_list = f.load()
            f.close()
        except:
            self.hiscore_list = []
        l = [player_det.p_name,player_det.point,player_det.tot_time]
        self.hiscore_list += l
        for i in range(len(self.hiscore_list) - 1):
            if self.hiscore_list[i][1]>self.hiscore_list[i+1][1]:
                self.hiscore_list[i],self.hiscore_list[i+1] = self.hiscore_list[i+1],self.hiscore_list[i]
            elif self.hiscore_list[i][1] == self.hiscore_list[i+1][1] and self.hiscore_list[i][2]>self.hiscore_list[i+1][2]:
                self.hiscore_list[i],self.hiscore_list[i+1] = self.hiscore_list[i+1],self.hiscore_list[i]
        g.dump(self.hiscore_list)
        f.close()
        g.close()
        os.remove("high_scores.dat")
        os.rename("Temp.dat","high_scores.dat")
        return self.hiscore_list
