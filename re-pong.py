import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "no"

import pygame as pg
import random
import math
pg.init()

clockspeed = 100
ball_speed = 5
paddle_speed = 5
ball_radius = 7
angle_blacklist = math.pi/2
max_anglechange = math.pi/4
enable_trail = True
trailsegmentlength = 1
trailwidth = ball_radius*2
enable_predictor = True
predictor_accelleration = 1
enable_overlay = True

keybinds = {
    "LEFT UP": pg.K_w,    # Left paddle up (W)
    "LEFT DOWN": pg.K_s,  # Left paddle down (S)
    "RIGHT UP": pg.K_UP,  # Right paddle up (UP arrow)
    "RIGHT DOWN": pg.K_DOWN,  # Right paddle down (DOWN arrow)
}




paddle_clr = (255,255,255)
ball_clr = (255,255,255)
background_clr = (0,0,0)
overlay_clr = (200,200,200)
trail_clr = (200,200,200)
predictor_clr = (255,0,0)
displaysize = (858,525)
display = pg.display.set_mode(displaysize)
pg.display.set_caption("PONG")


class paddle_class:
    def __init__(self,x):
        self.x = x
        self.w,self.h = 20,150
        self.y = (displaysize[1]-self.h)/2
        self.rect = pg.Rect(self.x,self.y,self.w,self.h)

    def draw_self(self):
        pg.draw.rect(display,paddle_clr,(self.x,self.y,self.w,self.h))
        self.rect = pg.Rect(self.x,self.y,self.w,self.h)


    def move_up(self):
        self.y = max(self.y - paddle_speed,0)
        
    def move_down(self):
        self.y = min(self.y + paddle_speed,displaysize[1]-self.h)


class ball_class:
    def __init__(self):
        self.radius = ball_radius
        self.x,self.y = displaysize[0]/2,displaysize[1]/2
        self.angle = random.random()*(math.pi*2)
        while (self.angle > ((3*math.pi)/2)-angle_blacklist/2 and self.angle < ((3*math.pi)/2)+angle_blacklist/2) or (self.angle > (math.pi/2) - angle_blacklist/2 and self.angle<(math.pi/2)+angle_blacklist/2):
            self.angle = random.random()*(math.pi*2)
        self.rect = pg.Rect(self.x-self.radius,self.y-self.radius,self.radius*2,self.radius*2)
        if enable_trail:
            self.trail = []
            self.trail_counter = trailsegmentlength

    def draw_self(self):
        self.rect = pg.Rect(self.x-self.radius,self.y-self.radius,self.radius*2,self.radius*2)

        if enable_trail:
            self.trail_counter -= 1
            if self.trail_counter == 0:
                self.trail_counter = trailsegmentlength
                self.trail.append([self.x,self.y])

            if len(self.trail) == 1:
                pg.draw.line(display,trail_clr,(self.x,self.y),self.trail[0],trailwidth)
            else:
                width = 0
                for i in range(len(self.trail)):
                    width += 1
                    try:
                        point1 = self.trail[i]
                        point2 =self.trail[i+1]
                        pg.draw.line(display,trail_clr,point1,point2,width)
                    except:
                        None
                try:
                    pg.draw.line(display,trail_clr,(self.x,self.y),self.trail[len(self.trail)-1],trailwidth)
                except:
                    None

            while len(self.trail) >= trailwidth:
                self.trail.pop(0)

        pg.draw.circle(display,ball_clr,(self.x,self.y),self.radius)                


    def bounce_self(self, paddle):
        center_y = paddle.y+paddle.h/2
        distance = abs((self.y+self.radius) - center_y)
        distance = 1/(paddle.h/2)*distance
        
        xvel,yvel = calculate_velocities(self.angle,ball_speed)

        if enable_trail:
            self.trail.append([self.x,self.y])
        

        xvel = -xvel
        while paddle.rect.colliderect(self.rect):

            self.x += xvel
            self.rect = pg.Rect(self.x-self.radius,self.y-self.radius,self.radius*2,self.radius*2)
        self.angle = calculate_angle(xvel,yvel)

        self.angle += max_anglechange*distance
        if (self.angle > ((3*math.pi)/2)-angle_blacklist/2 and self.angle < ((3*math.pi)/2)+angle_blacklist/2) or (self.angle > (math.pi/2) - angle_blacklist/2 and self.angle<(math.pi/2)+angle_blacklist/2):
            self.angle = calculate_angle(xvel,yvel)

        
        
        

    def move_self(self):
        global score

        xvel, yvel = calculate_velocities(self.angle, ball_speed)
        new_x, new_y = self.x + xvel, self.y + yvel

        if new_y - self.radius < 0 or new_y + self.radius > displaysize[1]:
            yvel = -yvel
            if enable_trail:
                self.trail.append([self.x,self.y])
        if new_x - self.radius < 0:
            self.__init__()
            score[1] += 1
        if new_x + self.radius > displaysize[0]:
            self.__init__()
            score[0] += 1
            

        self.x, self.y = self.x + xvel, self.y + yvel

        self.angle = calculate_angle(xvel, yvel)


        if paddleL.rect.colliderect(self.rect):
            self.bounce_self(paddleL)
        if paddleR.rect.colliderect(self.rect):
            self.bounce_self(paddleR)

        


        
def calculate_velocities(angle,magnitude):
    xv = math.cos(angle)*magnitude
    yv = math.sin(angle)*magnitude
    return xv,yv

def calculate_angle(xv,yv):
    return math.atan2(yv,xv)


def predict_direction(show_path):
    path = []
    x,y = ball.x,ball.y
    xvel,yvel = calculate_velocities(ball.angle,ball_speed*predictor_accelleration)
    while True:
        new_x, new_y = x + xvel, y + yvel
        path.append([x,y])


        if new_y - ball.radius < 0 or new_y + ball.radius > displaysize[1]:
            yvel = -yvel
            path.append([x,y])

        if new_x - ball.radius < 0 or new_x + ball.radius > displaysize[0]:
            if show_path:
                path.append([x,y])
                return path
            return new_x,new_y
        x,y = new_x,new_y



def process_bot(paddle):
    paddleref = paddle.y + (paddle.h / 2)
    target = predict_direction(False)
    
    target_lower_bound = target[1] - paddle_speed
    target_upper_bound = target[1] + paddle_speed
    
    if paddleref > target_upper_bound:
        paddle.move_up()
    elif paddleref < target_lower_bound:
        paddle.move_down()


def draw_overlay():
    pg.draw.line(display,overlay_clr,(displaysize[0]/2,0),(displaysize[0]/2,displaysize[1]))
    display.blit(font.render(str(score[0]),False,overlay_clr),(displaysize[0]/2-ball_radius-font.size(str(score[0]))[0],ball_radius))
    display.blit(font.render(str(score[1]),False,overlay_clr),(displaysize[0]/2+ball_radius,ball_radius))







def logic_calls(botl,botr):
    keystate = pg.key.get_pressed()

    
    if keystate[keybinds["LEFT UP"]]:
        paddleL.move_up()
    if keystate[keybinds["LEFT DOWN"]]:
        paddleL.move_down()
    if keystate[keybinds["RIGHT UP"]]:
        paddleR.move_up()
    if keystate[keybinds["RIGHT DOWN"]]:
        paddleR.move_down()

    if botr:
        process_bot(paddleR)
    if botl:
        process_bot(paddleL)
    ball.move_self()

    clock.tick(clockspeed)




def graphic_calls():
    display.fill(background_clr)
    if enable_predictor:
        dirs = predict_direction(True)
        for i in range(len(dirs)):
            try:
                pg.draw.line(display,predictor_clr,dirs[i],dirs[i+1],round(ball.radius/4))
            except:
                None
            
            
    ball.draw_self()
    paddleL.draw_self()
    paddleR.draw_self()
    if enable_overlay:
        draw_overlay()

    pg.display.flip()


def menu():
    global font
    while True:
        font = pg.font.SysFont("Calibri",10*ball_radius)
        display.fill(background_clr)
        

        display.blit(font.render("1 - Singleplayer (left)",False,ball_clr),(ball_radius,ball_radius))
        display.blit(font.render("2 - Singleplayer (right)",False,ball_clr),(ball_radius,11*ball_radius))
        display.blit(font.render("3 - Multiplayer",False,ball_clr),(ball_radius,21*ball_radius))    


        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0           
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return 0
                if event.key == pg.K_1:
                    return 1
                if event.key == pg.K_2:
                    return 2
                if event.key == pg.K_3:
                    return 3


        pg.display.flip()

def main(botl,botr):
    global ball, paddleL, paddleR, clock, score,clockspeed,enable_predictor,font
    defbotstate = tuple((botl,botr))
    score = [0,0]
    clock = pg.time.Clock()
    paddleL = paddle_class(20)
    paddleR = paddle_class(displaysize[0]-40)
    ball = ball_class()
    dead = 0
    while not dead:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                dead = 1
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    dead = 1
                elif event.key in (pg.K_KP_PLUS,pg.K_o):
                    clockspeed*=2

                elif event.key in (pg.K_KP_MINUS,pg.K_p):
                    clockspeed/=2

                elif event.key == pg.K_g:
                    enable_predictor = not enable_predictor

                elif event.key == pg.K_l:
                    if (botl,botr) != defbotstate:
                        botl,botr = defbotstate
                    else:
                        botl = True
                        botr = True

        logic_calls(botl,botr)
        graphic_calls()


out = menu()
if out == 0:
    pg.quit()
    quit()
elif out == 1:
    main(False,True)
    pg.quit()
    quit()
elif out == 2:
    main(True,False)
    pg.quit()
    quit()
elif out == 3:
    main(False,False)
    pg.quit()
    quit()



