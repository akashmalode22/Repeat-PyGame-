import pygame,sys
from new_player_details import *
from continue_game import *
from pickle import load,dump
import os,time
# Global constants
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
stop=True
jump=False
kill=False
is_open=False
is_press = False
pause = False
c_open = 0
comp=False
kills = 0
replay = False
# Colors
BLACK = (0, 0, 0)
YELLOW = (255,255,0)
WHITE = (255, 255, 255)
off_WHITE=(210,210,210)
GREEN = (0, 255, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
GREY=(192,192,192)
# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
class Player(pygame.sprite.Sprite):
    """ This class represents the bar at the bottom that the player
        controls. """ 
    # -- Methods
    def __init__(self):
        """ Constructor function """         
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image_r=[pygame.image.load("Run__00"+str(i)+".png") for i in range(1,10)]
        self.image_l=[]
        self.width = 40
        self.height = 60
        for i in range(0,9):
            self.image_r[i]=pygame.transform.scale(self.image_r[i],(self.width,self.height))
            imagel=pygame.transform.flip(self.image_r[i],True,False)
            self.image_l.append(imagel)
        self.image=pygame.image.load("Idle__001.png")
        self.image=pygame.transform.scale(self.image,(self.width,self.height))
        self.direction="R"
        # Set a referance to the image rect.
        self.rect = self.image.get_rect() 
        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0 
        # List of sprites we can bump against
        self.level = None       
    def update(self):
        """ Move the player. """
        global screen,kill,image_s,kills
        spike_hit = pygame.sprite.spritecollide(self,self.level.enemy_list,False)
        for spike in spike_hit:
            self.deadimage=pygame.image.load("Dead__009.png")
            self.deadimage=pygame.transform.scale(self.deadimage,(80,80))
            self.deadrect=self.deadimage.get_rect()
            self.deadrect.x=spike.rect.x
            self.deadrect.y=spike.rect.y-50
            self.rect.x=0
            self.rect.y=360
            kill=True
            kills+=1
        # Gravity
        self.calc_grav() 
        # Move left/right
        self.rect.x += self.change_x
        pos=self.rect.x
        if self.direction == "R" and not stop and not jump:
            frame = (pos // 30) % len(self.image_r)
            self.image = self.image_r[frame]
        elif self.direction == "L" and not stop and not jump:
            frame = (pos // 30) % len(self.image_l)
            self.image = self.image_l[frame]              
        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right 
        # Move up/down
        self.rect.y += self.change_y 
        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list: 
            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom 
            # Stop our vertical movement
            self.change_y = 0
        if "<Switch sprite(in 2 groups)>" in  str(block_hit_list):
            global is_press
            is_press = True            
    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35 
        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height 
    def jump(self):
        """ Called when user hits 'jump' button. """
        self.image=pygame.image.load("Idle__001.png")
        self.image=pygame.transform.scale(self.image,(self.width,self.height)) 
        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down
        # 1 when working with a platform moving down.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2 
        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10
    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6
        if current_level_no == 5:
            self.change_x +=12
        self.direction="L"           
    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6
        if current_level_no == 5:
            self.change_x -=12
        self.direction="R"           
    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0
        self.image=pygame.image.load("Idle__001.png")
        self.image=pygame.transform.scale(self.image,(self.width,self.height))
class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """ 
    def __init__(self, width, height):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this
            code. """
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK) 
        self.rect = self.image.get_rect()
class Level(object):
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """ 
    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving platforms
            collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.button_list = pygame.sprite.Group()
        self.player = player        
        # Background image
        self.background = None 
    # Update everythign on this level 
    def draw(self, screen):
        """ Draw everything on this level. """ 
        # Draw the background
        screen.fill(GREY) 
        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.button_list.draw(screen)
# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """ 
    def __init__(self, player,mess):
        """ Create level 1. """
        global current_level_no
        # Call the parent constructor
        Level.__init__(self, player) 
        # Array with width, height, x, and y of platform
        #          w    h    x  y
        level = [[150, 15,   0,270],
                 [150, 15,   0,360],
                 [100, 15, 270,390],
                 [100, 60, 420,540],
                 [190, 15, 460,299],
                 [125, 15, 800,200],
                 [150, 15,1050,270],
                 [150, 15,1050,360],
                 [100, 15, 270,130],
                 [200, 60,1000,540],
                 [190, 15, 500,150]]
        #          x    y   face
        enemies=[[ 450,517,   "up"],
                 [   0,500, "left"],
                 [   0, 50, "left"],
                 [1177,480,"right"],
                 [ 570,165, "down"]]
        redbuttons=[[555,285.5]]
        doors =[[1150,285,15,75]]
        for door in doors:
            self.main_door = Door(door[2],door[3])
            self.main_door.rect.x = door[0]
            self.main_door.rect.y = door[1]
            self.platform_list.add(self.main_door)
        for rb in redbuttons:
            switch = Switch()
            switch.rect.center=(rb[0],rb[1])
            self.button_list.add(switch)
            self.platform_list.add(switch)         
        for enemy in enemies:
            spike = Spikes(enemy[2])
            spike.rect.x=enemy[0]
            spike.rect.y=enemy[1]
            self.enemy_list.add(spike) 
        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)
        self.message = mess
    def update(self):
        """ Update everything in this level."""
        if is_open or current_level_no == 3:
            self.platform_list.remove(self.main_door)
        self.platform_list.update()
        self.enemy_list.update()
        self.button_list.update()
class Level_02(Level_01):
    """ Definition for level 2. """ 
    def __init__(self, player,mess):
        """ Create level 2. """                
        # Call the parent constructor
        Level_01.__init__(self, player,mess)
class Spikes(pygame.sprite.Sprite):
    #Spikes that kill player
    def __init__(self,facing="up"):
        pygame.sprite.Sprite.__init__(self)
        if facing=="up":add="hor"
        elif facing=="left":add="lt"
        elif facing=="down":add="d"
        else:add="rt"
        self.image=pygame.image.load("spikes_"+add+".png")
        self.rect=self.image.get_rect()        
class Switch(pygame.sprite.Sprite,Level):
    #switch that opens door
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load("red_button.png")
        self.image=pygame.transform.scale(self.image,(100,27))
        self.rect=self.image.get_rect()
        self.c_stop = 0
    def update(self):
        global c_open
        if self.c_stop == 0 and is_press:
            self.image = pygame.image.load("green_button .png")
            self.image=pygame.transform.scale(self.image,(100,27))
            c_open+=1
            self.c_stop = 1
        elif self.c_stop != 0 and is_press:
            pass            
        else:
            self.c_stop = 0
            self.image=pygame.image.load("red_button.png")
            self.image=pygame.transform.scale(self.image,(100,27))
        
class Door(pygame.sprite.Sprite,Level):
    #The door
    def __init__(self,width,height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width,height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
def fontrender(message,font,size,colour,position):
    try:
        Text = pygame.font.Font(font,size)
    except:
        Text = pygame.font.SysFont(font,size)
    textSurf = Text.render(message,False,colour)
    textRect = textSurf.get_rect()
    textRect.center = position    #position passed as tuple
    screen.blit(textSurf,textRect)
def button(msg,x,y,w,h,ic,ac,action,arg_t=None,color=BLACK,size=20):
    global screen
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(screen, ac,(x,y,w,h),1)
        if click[0] == 1:
            if arg_t == None:
                action()
            elif len(arg_t) == 1:
                action(arg_t[0])
            elif len(arg_t) == 2:
                action(arg_t[0],arg_t[1])
    else:
        pygame.draw.rect(screen, ic,(x,y,w,h),1)
    fontrender(msg,"comicsansms",size,color,(x+w/2,y+h/2))
def player_det_update():
    global next_level,score_lev
    f=open("Player_details.dat","rb")
    temp = open("temp.dat","wb")
    try:
        
        while True:
            cond = False
            a = load(f)
            try:
                if a.p_username == log_in.username and a.p_password == log_in.password: 
                    cond = True
            except NameError:
                if a.p_username == sign_up.p_username and a.p_password == sign_up.p_password:
                    cond = True
            if cond and next_level:                
                a.current_level_no +=1
                a.points += score_lev
                a.tot_time += game_time
                player_det.points += score_lev    
                player_det.current_level_no +=1
                player_det.tot_time += game_time
            dump(a,temp)
    except EOFError:
        f.close()
        temp.close()
        os.remove("Player_details.dat")
        os.rename("temp.dat","Player_details.dat")
class highscore:
    def __init__(self):
        self.name = ""
        self.score = 10
        self.total_time = 0
    def getdata(self):
        global player_det
        f = open("high_scores.dat","ab+")
        g = open("Temp.dat","ab")
        try:
            self.hiscore_list = load(f)
        except EOFError:
            self.hiscore_list = []
        l = [player_det.p_username,player_det.points,player_det.tot_time]
        self.hiscore_list.append(l)
        for i in range(len(self.hiscore_list) - 1):
            if self.hiscore_list[i][1]<self.hiscore_list[i+1][1]:
                self.hiscore_list[i],self.hiscore_list[i+1] = self.hiscore_list[i+1],self.hiscore_list[i]
            elif self.hiscore_list[i][1] == self.hiscore_list[i+1][1] and self.hiscore_list[i][2]>self.hiscore_list[i+1][2]:
                self.hiscore_list[i],self.hiscore_list[i+1] = self.hiscore_list[i+1],self.hiscore_list[i]
        dump(self.hiscore_list,g)
        f.close()
        g.close()
        os.remove("high_scores.dat")
        os.rename("Temp.dat","high_scores.dat")
        return self.hiscore_list
def highscore_save():
    global hiscore_list
    hs = highscore()
    hiscore_list = hs.getdata()
def high_sc_display():
    global screen,high_sc_d    
    high_sc_d = True
    while high_sc_d:
        a = 80
        r = 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(BLUE)
        button("<<Back",10,SCREEN_HEIGHT-80,100,50,BLUE,YELLOW,mainmenu,(screen,))
        fontrender("HI-SCORE","ARDARLING.ttf",40,YELLOW,(SCREEN_WIDTH/2,10))
        fontrender("Rank","ARDARLING.ttf",25,RED,(50,a))
        fontrender("Name","ARDARLING.ttf",25,RED,(200,a))
        fontrender("Total Points","ARDARLING.ttf",25,RED,(400,a))
        fontrender("Total Time","ARDARLING.ttf",25,RED,(600,a))
        f = open("high_scores.dat","rb")
        hs1 = load(f)
        a+=30
        for i in hs1:
            fontrender(str(r),"ARDARLING.ttf",25,GREEN,(50,a))
            fontrender(str(i[0]),"ARDARLING.ttf",25,GREEN,(200,a))
            fontrender(str(i[1]),"ARDARLING.ttf",25,GREEN,(400,a))
            fontrender(str(i[2])[:7],"ARDARLING.ttf",25,GREEN,(600,a))
            r+=1
            a+=20
        pygame.display.update()
def highscore_1():
    global intro
    high_sc_display()
def newgame():
    global intro,player_det,sign_up,screen
    screen.fill(BLACK)
    fontrender("*******PLEASE RETURN TO PYTHON INTERACTIVE MENU TO CONTINUE******","comicsansms",20,RED,(SCREEN_WIDTH/2, 20))
    pygame.display.update()
    sign_up = new_player_details()
    sign_up.get_details()
    sign_up.save()
    player_det = sign_up
    intro=False    
def continueg():
    global intro,player_det,log_in
    screen.fill(BLACK)
    fontrender("*******PLEASE RETURN TO PYTHON INTERACTIVE MENU TO CONTINUE******","comicsansms",20,RED,(SCREEN_WIDTH/2, 20))
    pygame.display.update()
    log_in = continue_game()
    log_in.log_in()
    f=open("Player_details.dat","rb")
    try:
        while True:
            a = load(f)
            if a.p_username == log_in.username and a.p_password == log_in.password:
                player_det = a
    except EOFError:
        f.close()
    intro=False
def howtoplay():
    global screen,how_cond
    how_cond = True
    while how_cond:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        a = 150
        screen.fill(BLUE)
        L = ["This Game is very simple","Start the Game","Solve each level with help of clue given",
             "All you have to do is press the Big Red Button(or not)","After button is pressed door opens",
             "Proceed to the end of the door platform to end level","After 5 levels, game ends hi-score will be saved",
             "Thank You"]
        fontrender("HOW TO PLAY","ARDARLING.ttf",50,YELLOW,(SCREEN_WIDTH/2,70))
        button("<<Back",10,10,100,50,BLUE,RED,mainmenu,(screen,),YELLOW)
        for st in L:
            fontrender(st,"COURIERNEW.ttf",35,GREEN,(SCREEN_WIDTH/2,a))
            a+=40
        pygame.display.update()         
def nextlevel():
    global next_level,dialog_up
    next_level = True
    dialog_up = False
def replay1():
    global dialog_up,replay
    dialog_up = False
    replay = True
def quitpy():
    pygame.quit()
    sys.exit()
time_p = 0
def pause_game():
    global pause,screen,time_p
    pause = True
    fontrender("Press P to continue","comicsansms",20,BLUE,(SCREEN_WIDTH/2, SCREEN_HEIGHT-10))
    timep_now = time.time()
    while pause:
        fontrender("PAUSED","ARDARLING.ttf",30,BLUE,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))
        fontrender("Press P to continue...","ARDARLING.ttf",30,RED,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2+30))
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                pause = False
            if event.type == pygame.QUIT:
                done = True
                # Be IDLE friendly. If you forget this line, the program will 'hang'

                # on exit.
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
        pygame.display.update()
    timep_lat = time.time()
    time_p = timep_lat - timep_now
def mainmenu(screen):
    global intro,how_cond,high_sc_d
    intro=True
    w = 257
    b = -2
    change = 0
    how_cond = False
    high_sc_d = False
    while intro:
        if change%2 == 0:
            w-=2
            b+=2
            if w<0 or b>255:
                w = 255
                b = 0
        blue=(b,b,w)  
        screen.fill(BLACK)
        fontrender("REPEAT","ARDARLING.ttf",100,blue,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2-200))
        button("New game",SCREEN_WIDTH/2-60,SCREEN_HEIGHT/2-25,120,50,BLACK,WHITE,newgame,None,BLUE)
        button("Continue",SCREEN_WIDTH/2-60,SCREEN_HEIGHT/2 + 60-25,120,50,BLACK,YELLOW,continueg,None,BLUE)
        button("High Scores",SCREEN_WIDTH/2-60,SCREEN_HEIGHT/2 + 120-25,120,50,BLACK,GREEN,highscore_1,None,BLUE)              
        button("How to Play",SCREEN_WIDTH/2-60,SCREEN_HEIGHT/2 + 180-25,120,50,BLACK,RED,howtoplay,None,BLUE)
        change += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
def mainscreen(screen):        
    screen.fill(BLACK)
    pygame.display.update()
    pygame.time.delay(100)
    screen.fill(WHITE)
    fontrender("REPEAT","ARDARLING.ttf",50,BLACK,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))
    change=0
    w=256
    b = -2
    y = 0
    while change<636:
        if change%5==0:
            w-=2
            b+=2
        blue=(w,b,b)
        green=(b,w,b)
        screen.fill(WHITE)
        fontrender("REPEAT","ARDARLING.ttf",50,green,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))
        load = pygame.Surface((y,15))
        load.fill(blue)
        load_rect = load.get_rect()
        load_rect.x = 430
        load_rect.y = 330
        screen.blit(load,load_rect)
        y += 0.5
        change+=1
        clock.tick(60)
        pygame.display.update()
def point_calc():
    global player_det,game_time,score_lev
    if game_time <= 20:
        score_lev = 20
    elif game_time <= 30:
        score_lev = 10
    elif game_time >30:
        score_lev = 5
def solution():
    global current_level_no,is_open,comp,player,is_press,c_open,kills,time_now
    if current_level_no in (1,4,5):
        if is_press == True:
            is_open = True
            c_open = 0
    elif current_level_no == 2:
        is_press = False
        if c_open >=3 and kills >=3:
            is_press = True
            is_open = True
            c_opem = 0
    elif current_level_no == 3:
        #solution already in program
        is_open  = True
    else:
        is_open = False
        comp=False
    if player.rect.x >=1150 and player.rect.y <= 360 and player.rect.y >= 285 and is_open:
        comp=True
        comp_screen()
        time_now = time.time()
def comp_screen():
    global screen,current_level_no,done,is_open,is_press,time_now,game_time,dialog_up,score_lev,time_p
    if comp:
        time_later = time.time()
        game_time = (time_later - time_now) - time_p
        time_p = 0
        point_calc()
        times=0
        a=256
        compsc = pygame.Surface((740,500))
        compsc.fill(BLACK)
        comp_rect = compsc.get_rect()
        comp_rect.center = (SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
        dialog_up = True
        while dialog_up:
            screen.fill(WHITE)
            screen.blit(compsc,comp_rect)
            fontrender("LEVEL COMPLETED","ARDARLING.ttf",50,WHITE,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2-200))
            fontrender("Time Elapsed: "+str(game_time)+"s","ARDARLING.ttf",50,WHITE,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2-100))
            fontrender("You won "+str(score_lev)+" points","ARDARLING.ttf",50,GREY,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))
            button("Replay",SCREEN_WIDTH/2-260,SCREEN_HEIGHT/2+100,120,50,BLACK,BLUE,replay1,None,YELLOW)
            button("Next Level",SCREEN_WIDTH/2-60,SCREEN_HEIGHT/2+100,120,50,BLACK,GREEN,nextlevel,None,YELLOW)
            button("Quit",SCREEN_WIDTH/2+140,SCREEN_HEIGHT/2+100,120,50,BLACK,RED,quitpy,None,YELLOW)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
        if next_level:
            if current_level_no == 5:
                player_det_update()
                for i in range(1000):
                    screen.fill(BLACK)
                    fontrender("THE","ARDECODE.ttf",50,YELLOW,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2-50))
                    fontrender("END","ARDECODE.ttf",50,RED,(SCREEN_WIDTH/2,SCREEN_HEIGHT/2))
                    pygame.display.update()
                pygame.quit()
                highscore_save()
                print ("HI-SCORE SAVED")
                sys.exit()
            else:
                player_det_update()
                score_lev = 0
        done = True
        is_open = False
        is_press = False
def main():
    """ Main Program """
    global stop,jump,screen,kill,current_level_no,player,done,kills,time_now,next_level
    pygame.init() 
    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size) 
    pygame.display.set_caption("Repeat")
    icon=pygame.image.load("Idle__001.png")
    pygame.display.set_icon(icon)
    pygame.mixer.music.load("bgm.mid")
    pygame.mixer.music.play(-1)

    #mainscreen(screen)
    mainmenu(screen)
    pygame.mixer.music.load("bgm2.mid")
    pygame.mixer.music.play(-1)
    
    # Create the player
    player = Player() 
    # Create all the levels
    level_list = []
    level_list.append( Level_01(player,"1.As easy as it Looks") )
    level_list.append( Level_02(player,"2.Thrice the charm") )
    level_list.append( Level_01(player,"3.Do not believe your eyes") )
    level_list.append( Level_01(player,"4.You WAS not trying") )
    level_list.append( Level_01(player,"5.Property of plane mirror") )
    # Set the current level    
    while True:
        next_level = False
        if replay:
            player.rect.x = 0
            player.rect.y = 360
            level_list = []
            level_list.append( Level_01(player,"1.As easy as it Looks") )
            level_list.append( Level_02(player,"2.Thrice the charm") )
            level_list.append( Level_01(player,"3.Do not believe your eyes") )
            level_list.append( Level_01(player,"4.You WAS not trying") )
            level_list.append( Level_01(player,"5.Property of plane mirror") )
        current_level_no = player_det.current_level_no
        current_level = level_list[current_level_no-1]
        kills = 0
        active_sprite_list = pygame.sprite.Group()
        player.level = current_level 
        player.rect.x = 0
        player.rect.y = 360
        player.stop()
        active_sprite_list.add(player)
        messfont=pygame.font.Font("ARDARLING.ttf",30)
        text=messfont.render(current_level.message,False,WHITE)
        textrect=text.get_rect()
        textrect.center=(200,100)
        # Loop until the user clicks the close button.
        done = False  
        # -------- Main Program Loop -----------
        time_now = time.time()
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    # Be IDLE friendly. If you forget this line, the program will 'hang'
                    # on exit.
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit() 
                if event.type == pygame.KEYDOWN:
                    if not pause:
                        if (event.key == pygame.K_LEFT and current_level_no != 4)  or (event.key == pygame.K_a and current_level_no == 4):
                            player.go_left()                    
                        if (event.key == pygame.K_RIGHT and current_level_no != 4) or (event.key == pygame.K_s and current_level_no == 4):
                            player.go_right()                    
                        if (event.key == pygame.K_UP  and current_level_no != 4) or (event.key == pygame.K_w and current_level_no == 4):
                            player.jump()
                            jump=True
                    if event.key == pygame.K_p:
                        pygame.mixer.music.load("bgm.mid")
                        pygame.mixer.music.play(-1)
                        pause_game()
                        pygame.mixer.music.load("bgm2.mid")
                        pygame.mixer.music.play(-1)
                    stop=False 
                if event.type == pygame.KEYUP:
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_a or current_level_no == 5) and (player.change_x < 0 or (current_level_no == 5 and player.change_x >0)):
                        player.stop()
                        jump=False
                    if (event.key == pygame.K_RIGHT or event.key == pygame.K_s or current_level_no == 5) and (player.change_x > 0 or (current_level_no == 5 and player.change_x < 0)):
                        player.stop()
                        jump=False
                    stop=True              
            # Update the player.
            player.update() 
            # Update items in the level
            current_level.update() 
            # If the player gets near the right side, shift the world left (-x)
            if player.rect.right > SCREEN_WIDTH:
                player.rect.right = SCREEN_WIDTH 
            # If the player gets near the left side, shift the world right (+x)
            if player.rect.left < 0:
                player.rect.left = 0 
            current_level.draw(screen)
            active_sprite_list.draw(screen)
            screen.blit(text,textrect)
            if current_level_no == 3:
                img = pygame.Surface((15,75))
                img.fill(RED)
                img_rect = img.get_rect()
                img_rect.x = 1150
                img_rect.y = 285
                screen.blit(img,img_rect)
            if kill:
                screen.blit(player.deadimage,player.deadrect)
            solution() 
            # Limit to 60 frames per second
            clock.tick(60) 
            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip() 
if __name__ == "__main__":
    main()
