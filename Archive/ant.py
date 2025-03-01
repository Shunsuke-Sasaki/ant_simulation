#!/usr/bin/env python3
from math import pi, sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
import numpy as np
'''
NAnts - Ant pheromone trail simulation. Surfarray version. WIP
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''
FLLSCRN = False         # True for Fullscreen, or False for Window
ANTS = 1000            # Number of Ants to spawn
WIDTH = 1200      # default 1200
HEIGHT = 800      # default 800
FPS = 60           # 48-90
VSYNC = True            # limit frame rate to refresh rate
PRATIO = 5              # Pixel Size for Pheromone grid, 5 is best
SHOWFPS = True          # show framerate debug

class Ant(pg.sprite.Sprite):
    food_collected_total = 0   # 食べ物を巣に持ち帰った量を保持する変数
    def __init__(self, drawSurf, nest, pheroLayer):
        super().__init__()
        self.drawSurf = drawSurf
        self.curW, self.curH = self.drawSurf.get_size()
        self.pgSize = (int(self.curW/PRATIO), int(self.curH/PRATIO))
        self.isMyTrail = np.full(self.pgSize, False)
        self.phero = pheroLayer
        self.nest = nest
        self.image = pg.Surface((12, 21)).convert()
        self.image.set_colorkey(0)
        cBrown = (100,42,42)
        # Draw Ant
        pg.draw.aaline(self.image, cBrown, [0, 5], [11, 15])
        pg.draw.aaline(self.image, cBrown, [0, 15], [11, 5]) # legs
        pg.draw.aaline(self.image, cBrown, [0, 10], [12, 10])
        pg.draw.aaline(self.image, cBrown, [2, 0], [4, 3]) # antena l
        pg.draw.aaline(self.image, cBrown, [9, 0], [7, 3]) # antena r
        pg.draw.ellipse(self.image, cBrown, [3, 2, 6, 6]) # head
        pg.draw.ellipse(self.image, cBrown, [4, 6, 4, 9]) # body
        pg.draw.ellipse(self.image, cBrown, [3, 13, 6, 8]) # rear
        # save drawing for later
        self.orig_img = pg.transform.rotate(self.image.copy(), -90)
        self.rect = self.image.get_rect(center=self.nest)
        self.ang = randint(0, 360)
        self.desireDir = pg.Vector2(cos(radians(self.ang)),sin(radians(self.ang)))
        self.pos = pg.Vector2(self.rect.center)
        self.vel = pg.Vector2(0,0)
        self.last_sdp = (nest[0]/10/2,nest[1]/10/2)
        self.mode = 0

    def update(self, dt):  # behavior
        mid_result = left_result = right_result = [0,0,0]
        mid_GA_result = left_GA_result = right_GA_result = [0,0,0]
        randAng = randint(0,360)
        accel = pg.Vector2(0,0)
        foodColor = (20,150,2)  # color of food to look for
        wandrStr = .12  # how random they walk around
        maxSpeed = 12  # 10-12 seems ok
        steerStr = 3  # 3 or 4, dono
        # Converts ant's current screen coordinates, to smaller resolution of pherogrid.
        scaledown_pos = (int(self.pos.x/PRATIO), int(self.pos.y/PRATIO))
        #scaledown_pos = (int((self.pos.x/self.curW)*self.pgSize[0]), int((self.pos.y/self.curH)*self.pgSize[1]))
        # Get locations to check as sensor points, in pairs for better detection.
        mid_sens = Vec2.vint(self.pos + pg.Vector2(20, 0).rotate(self.ang))
        left_sens = Vec2.vint(self.pos + pg.Vector2(18, -8).rotate(self.ang)) # -9
        right_sens = Vec2.vint(self.pos + pg.Vector2(18, 8).rotate(self.ang)) # 9

        if self.drawSurf.get_rect().collidepoint(mid_sens):
            mspos = (mid_sens[0]//PRATIO,mid_sens[1]//PRATIO)
            mid_result = self.phero.img_array[mspos]
            mid_isID = self.isMyTrail[mspos]
            mid_GA_result = self.drawSurf.get_at(mid_sens)[:3]
        if self.drawSurf.get_rect().collidepoint(left_sens):
            left_result, left_isID, left_GA_result = self.sensCheck(left_sens)
        if self.drawSurf.get_rect().collidepoint(right_sens):
            right_result, right_isID, right_GA_result = self.sensCheck(right_sens)

        #pg.draw.circle(self.drawSurf, (200,0,200), mid_sens, 1)
        #pg.draw.circle(self.drawSurf, (200,0,200), left_sens, 1)
        #pg.draw.circle(self.drawSurf, (200,0,200), right_sens, 1)

        if self.mode == 0 and self.pos.distance_to(self.nest) > 21:
            self.mode = 1

        elif self.mode == 1:  # Look for food, or trail to food.
            setAcolor = (0,0,100)
            if scaledown_pos != self.last_sdp and scaledown_pos[0] in range(0,self.pgSize[0]) and scaledown_pos[1] in range(0,self.pgSize[1]):
                self.phero.img_array[scaledown_pos] += setAcolor
                self.isMyTrail[scaledown_pos] = True
                self.last_sdp = scaledown_pos
            if mid_result[1] > max(left_result[1], right_result[1]):
                self.desireDir += pg.Vector2(1,0).rotate(self.ang).normalize()
                wandrStr = .1
            elif left_result[1] > right_result[1]:
                self.desireDir += pg.Vector2(1,-2).rotate(self.ang).normalize() #left (0,-1)
                wandrStr = .1
            elif right_result[1] > left_result[1]:
                self.desireDir += pg.Vector2(1,2).rotate(self.ang).normalize() #right (0, 1)
                wandrStr = .1
            if left_GA_result == foodColor and right_GA_result != foodColor :
                self.desireDir += pg.Vector2(0,-1).rotate(self.ang).normalize() #left (0,-1)
                wandrStr = .1
            elif right_GA_result == foodColor and left_GA_result != foodColor:
                self.desireDir += pg.Vector2(0,1).rotate(self.ang).normalize() #right (0, 1)
                wandrStr = .1
            elif mid_GA_result == foodColor: # if food
                self.desireDir = pg.Vector2(-1,0).rotate(self.ang).normalize() #pg.Vector2(self.nest - self.pos).normalize()
                #self.lastFood = self.pos + pg.Vector2(21, 0).rotate(self.ang)
                maxSpeed = 5
                wandrStr = .01
                steerStr = 5
                self.mode = 2
                
        
        elif self.mode == 2:  # Once found food, either follow own trail back to nest, or head in nest's general direction.
            setAcolor = (0,80,0)
             
            if scaledown_pos != self.last_sdp and scaledown_pos[0] in range(0,self.pgSize[0]) and scaledown_pos[1] in range(0,self.pgSize[1]):
                self.phero.img_array[scaledown_pos] += setAcolor
                self.last_sdp = scaledown_pos
            if self.pos.distance_to(self.nest) < 24:
            
                Ant.food_collected_total += 1
                print(Ant.food_collected_total)
                
                #self.desireDir = pg.Vector2(self.lastFood - self.pos).normalize()
                self.desireDir = pg.Vector2(-1,0).rotate(self.ang).normalize()
                self.isMyTrail[:] = False #np.full(self.pgSize, False)
                maxSpeed = 5
                wandrStr = .01
                steerStr = 5
                self.mode = 1
            elif mid_result[2] > max(left_result[2], right_result[2]) and mid_isID: #and mid_result[:2] == (0,0):
                self.desireDir += pg.Vector2(1,0).rotate(self.ang).normalize()
                wandrStr = .1
            elif left_result[2] > right_result[2] and left_isID: #and left_result[:2] == (0,0):
                self.desireDir += pg.Vector2(1,-2).rotate(self.ang).normalize() #left (0,-1)
                wandrStr = .1
            elif right_result[2] > left_result[2] and right_isID: #and right_result[:2] == (0,0):
                self.desireDir += pg.Vector2(1,2).rotate(self.ang).normalize() #right (0, 1)
                wandrStr = .1
            else:  # maybe first add ELSE FOLLOW OTHER TRAILS?
                self.desireDir += pg.Vector2(self.nest - self.pos).normalize() * .08
                wandrStr = .1   #pg.Vector2(self.desireDir + (1,0)).rotate(pg.math.Vector2.as_polar(self.nest - self.pos)[1])

        wallColor = (50,50,50)  # avoid walls of this color
        if left_GA_result == wallColor:
            self.desireDir += pg.Vector2(0,2).rotate(self.ang) #.normalize()
            wandrStr = .1
            steerStr = 7
        elif right_GA_result == wallColor:
            self.desireDir += pg.Vector2(0,-2).rotate(self.ang) #.normalize()
            wandrStr = .1
            steerStr = 7
        elif mid_GA_result == wallColor:
            self.desireDir = pg.Vector2(-2,0).rotate(self.ang) #.normalize()
            maxSpeed = 4
            wandrStr = .1
            steerStr = 7

        # Avoid edges
        if not self.drawSurf.get_rect().collidepoint(left_sens) and self.drawSurf.get_rect().collidepoint(right_sens):
            self.desireDir += pg.Vector2(0,1).rotate(self.ang) #.normalize()
            wandrStr = .01
            steerStr = 5
        elif not self.drawSurf.get_rect().collidepoint(right_sens) and self.drawSurf.get_rect().collidepoint(left_sens):
            self.desireDir += pg.Vector2(0,-1).rotate(self.ang) #.normalize()
            wandrStr = .01
            steerStr = 5
        elif not self.drawSurf.get_rect().collidepoint(Vec2.vint(self.pos + pg.Vector2(21, 0).rotate(self.ang))):
            self.desireDir += pg.Vector2(-1,0).rotate(self.ang) #.normalize()
            maxSpeed = 5
            wandrStr = .01
            steerStr = 5

        randDir = pg.Vector2(cos(radians(randAng)),sin(radians(randAng)))
        self.desireDir = pg.Vector2(self.desireDir + randDir * wandrStr).normalize()
        dzVel = self.desireDir * maxSpeed
        dzStrFrc = (dzVel - self.vel) * steerStr
        accel = dzStrFrc if pg.Vector2(dzStrFrc).magnitude() <= steerStr else pg.Vector2(dzStrFrc.normalize() * steerStr)
        velo = self.vel + accel * dt
        self.vel = velo if pg.Vector2(velo).magnitude() <= maxSpeed else pg.Vector2(velo.normalize() * maxSpeed)
        self.pos += self.vel * dt
        self.ang = degrees(atan2(self.vel[1],self.vel[0]))
        # adjusts angle of img to match heading
        self.image = pg.transform.rotate(self.orig_img, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        # actually update position
        self.rect.center = self.pos

    def sensCheck(self, pos): #, pos2): # checks given points in Array, IDs, and pixels on screen.
        sdpos = (int(pos[0]/PRATIO),int(pos[1]/PRATIO))
        array_r = self.phero.img_array[sdpos]
        ga_r = self.drawSurf.get_at(pos)[:3]
        return array_r, self.isMyTrail[sdpos], ga_r

class PheroGrid():
    def __init__(self, bigSize):
        self.surfSize = (int(bigSize[0]/PRATIO), int(bigSize[1]/PRATIO))
        self.image = pg.Surface(self.surfSize).convert()
        self.img_array = np.array(pg.surfarray.array3d(self.image),dtype=float)#.astype(np.float64)
    def update(self, dt):
        self.img_array -= .2 * (60/FPS) * ((dt/10) * FPS) #[self.img_array > 0] # dt might not need FPS parts
        self.img_array = self.img_array.clip(0,255)
        pg.surfarray.blit_array(self.image, self.img_array)
        return self.image

class Food(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pg.Surface((16, 16))
        self.image.fill(0)
        self.image.set_colorkey(0)
        pg.draw.circle(self.image, [20,150,2], [8, 8], 4)
        self.rect = self.image.get_rect(center=pos)
    def pickup(self):
        self.kill()

class Vec2():
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	def vint(self):
		return (int(self.x), int(self.y))

def main():
    pg.init()  # prepare window
    pg.display.set_caption("NAnts")
    try: pg.display.set_icon(pg.img.load("nants.png"))
    except: print("FYI: nants.png icon not found, skipping..")
    # setup fullscreen or window mode
    if FLLSCRN:  #screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED | pg.NOFRAME | pg.FULLSCREEN, vsync=VSYNC)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED, vsync=VSYNC)

    cur_w, cur_h = screen.get_size()
    screenSize = (cur_w, cur_h)
    nest = (cur_w/3, cur_h/2)

    #background = pg.img.load("background.png").convert_alpha()

    workers = pg.sprite.Group()
    pheroLayer = PheroGrid(screenSize)

    for n in range(ANTS):
        workers.add(Ant(screen, nest, pheroLayer))

    foodList = []
    foods = pg.sprite.Group()
    font = pg.font.Font(None, 30)
    clock = pg.time.Clock()
    fpsChecker = 0
    # main loop
    c=0
    while True:
        c+=1
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
            elif e.type == pg.MOUSEBUTTONDOWN:
                mousepos = pg.mouse.get_pos()
                if e.button == 1: # and pg.Vector2(mousepos).distance_to(nest) > 242:
                    foodBits = 200
                    fRadius = 50
                    for i in range(0, foodBits): # spawn food bits evenly within a circle
                        dist = pow(i / (foodBits - 1.0), 0.5) * fRadius
                        angle = 2 * pi * 0.618033 * i
                        fx = mousepos[0] + dist * cos(angle)
                        fy = mousepos[1] + dist * sin(angle)
                        foods.add(Food((fx,fy)))
                    foodList.extend(foods.sprites())
                if e.button == 3:
                    for fbit in foodList:
                        if pg.Vector2(mousepos).distance_to(fbit.rect.center) < fRadius+5:
                            fbit.pickup()
                    foodList = foods.sprites()

        dt = clock.tick(FPS) / 100

        pheroImg = pheroLayer.update(dt)
        pheroLayer.img_array[170:182,0:80] = (50,50,50)  # wall

        workers.update(dt)

        screen.fill(0) # fill MUST be after sensors update, so previous draw is visible to them

        rescaled_img = pg.transform.scale(pheroImg, (cur_w, cur_h))
        pg.Surface.blit(screen, rescaled_img, (0,0))
        
        #workers.update(dt)  # enable here to see debug dots
        foods.draw(screen)

        pg.draw.circle(screen, [40,10,10], (nest[0],nest[1]+6), 6, 3)
        pg.draw.circle(screen, [50,20,20], (nest[0],nest[1]+4), 9, 4)
        pg.draw.circle(screen, [60,30,30], (nest[0],nest[1]+2), 12, 4)
        pg.draw.circle(screen, [70,40,40], nest, 16, 5)

        #pg.draw.rect(screen, (50,50,50), [900, 0, 50, 500]) # test wall

        workers.draw(screen)

        #if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        food_collected_text = font.render(f"Food Collected: {Ant.food_collected_total}", True, [255, 255, 255])
        count_text = font.render(f"Count: {c}", True, [255, 255, 255])
        
        text_rect = food_collected_text.get_rect(topleft=(8, 40))
        text_rect2 =count_text.get_rect(topleft=(8, 15))
        screen.blit(food_collected_text, text_rect)
        screen.blit(count_text,text_rect2)
        pg.display.update()


if __name__ == '__main__':
    main()  
    pg.quit()