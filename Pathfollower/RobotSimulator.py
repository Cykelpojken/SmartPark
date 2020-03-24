import configparser
import math
import numpy as np
import cv2
import time
#import statistics

distances = []

def Average(lst): 
    return sum(lst) / len(lst) 

def closest():
    global path, pos
    
    mindist = (0, math.sqrt((path[0][0] - pos[0]) ** 2 + (path[0][1] - pos[1]) ** 2))
    for i, p in enumerate(path):
        dist = math.sqrt((p[0]-pos[0])**2 + (p[1]-pos[1])**2)
        distances.append(dist)
        if dist < mindist[1]:
            mindist = (i, dist)

    return mindist[0]
def lookahead():
    global path, t, t_i, pos

    for i, p in enumerate(reversed(path[:-1])):
        i_ = len(path)-2 - i
        d = (path[i_+1][0]-p[0], path[i_+1][1]-p[1])
        f = (p[0]-pos[0], p[1]-pos[1])

        a = sum(j**2 for j in d)
        b = 2*sum(j*k for j,k in zip(d,f))
        c = sum(j**2 for j in f) - float(config["PATH"]["LOOKAHEAD"])**2
        disc = b**2 - 4*a*c
        if disc >= 0:
            disc = math.sqrt(disc)
            t1 = (-b + disc)/(2*a)
            t2 = (-b - disc)/(2*a)
            # print("t1=" + str(t1) + ", t2=" + str(t2))
            if 0<=t1<=1:
                # if (t1 >= t and i == t_i) or i > t_i:
                    t = t1
                    t_i = i_
                    # print("hit")
                    return p[0]+t*d[0], p[1]+t*d[1]
            if 0<=t2<=1:
                # if (t2 >= t and i == t_i) or i > t_i:
                    t = t2
                    t_i = i_
                    # print("hit")
                    return p[0]+t*d[0], p[1]+t*d[1]
    t = 0
    t_i = 0
    return path[closest()][0:2]
def curvature(lookahead):
    global path, pos, angle
    side = np.sign(math.sin(3.1415/2 - angle)*(lookahead[0]-pos[0]) - math.cos(3.1415/2 - angle)*(lookahead[1]-pos[1]))
    a = -math.tan(3.1415/2 - angle)
    c = math.tan(3.1415/2 - angle)*pos[0] - pos[1]
    # x = abs(-math.tan(3.1415/2 - angle) * lookahead[0] + lookahead[1] + math.tan(3.1415/2 - angle)*pos[0] - pos[1]) / math.sqrt((math.tan(3.1415/2 - angle))**2 + 1)
    x = abs(a*lookahead[0] + lookahead[1] + c) / math.sqrt(a**2 + 1)
    return side * (2*x/(float(config["PATH"]["LOOKAHEAD"])**2))
def turn(curv, vel, trackwidth):
    return  [vel*(2+curv*trackwidth)/2, vel*(2-curv*trackwidth)/2]

def draw_path(img):
    global path, start_pos
    cv2.circle(img, (int(path[0][0]*scaler), int(path[0][1]*scaler)), 2,
               (255*(1-path[0][2]/float(config["VELOCITY"]["MAX_VEL"])), 0, 255*path[0][2]/float(config["VELOCITY"]["MAX_VEL"])), -1)
    for i in range(1, len(path)):
        cv2.circle(img, (int(path[i][0]*scaler), int(path[i][1]*scaler)), 2,
                   (255*(1-path[i-1][2]/float(config["VELOCITY"]["MAX_VEL"])), 0, 255*path[i-1][2]/float(config["VELOCITY"]["MAX_VEL"])), -1)
        cv2.line(img, (int(path[i][0]*scaler), int(path[i][1]*scaler)),
                 (int(path[i-1][0]*scaler), int(path[i-1][1]*scaler)),
                 (255*(1-path[i-1][2]/float(config["VELOCITY"]["MAX_VEL"])), 0, 255*path[i-1][2]/float(config["VELOCITY"]["MAX_VEL"])), 1)

def draw_robot(img):
    tmp = img.copy()
    cv2.drawContours(tmp, [np.array([((pos[0]+length/2*math.sin(angle)-width/2*math.cos(angle))*scaler,
                                      (pos[1]+length/2*math.cos(angle)+width/2*math.sin(angle))*scaler),
                                     ((pos[0]+length/2*math.sin(angle)+width/2*math.cos(angle))*scaler,
                                      (pos[1]+length/2*math.cos(angle)-width/2*math.sin(angle))*scaler),
                                     ((pos[0]-length/2*math.sin(angle)+width/2*math.cos(angle))*scaler,
                                      (pos[1]-length/2*math.cos(angle)-width/2*math.sin(angle))*scaler),
                                     ((pos[0]-length/2*math.sin(angle)-width/2*math.cos(angle))*scaler,
                                      (pos[1]-length/2*math.cos(angle)+width/2*math.sin(angle))*scaler)])
                     .reshape((-1,1,2)).astype(np.int32)], 0, (0, 255, 255), 2)
    cv2.circle(tmp, (int(pos[0]*scaler), int(pos[1]*scaler)), int(config["PATH"]["LOOKAHEAD"]), (0, 255, 0), 1)
    cv2.circle(tmp, (int(path[close][0]*scaler), int(path[close][1]*scaler)), 4,
               (255*(1-path[close][2]/float(config["VELOCITY"]["MAX_VEL"])), 0, 255*path[close][2]/float(config["VELOCITY"]["MAX_VEL"])), -1)
    cv2.circle(tmp, (int(look[0]*scaler), int(look[1]*scaler)), 4, (0,255,0), -1)

    try:
        x3 = (pos[0]+look[0])/2
        y3 = -(pos[1]+look[1])/2
        q = math.sqrt((pos[0]-look[0])**2 + (pos[1]-look[1])**2)
        x = x3 - math.sqrt(1/curv**2 - (q/2)**2) * (pos[1]-look[1])/q * np.sign(curv)
        y = y3 - math.sqrt(1/curv**2 - (q/2)**2) * (pos[0]-look[0])/q * np.sign(curv)
        cv2.circle(tmp, (int(x*scaler), int(y*scaler)), int(abs(1/curv*scaler)), (0,255,255), 1) #This doesn't draw at the right positions atm
    except:
        pass

    cv2.line(tmp,
             (int((pos[0]+length/2*math.sin(angle)-width/2*math.cos(angle))*scaler),
              int((pos[1]+length/2*math.cos(angle)+width/2*math.sin(angle))*scaler)),
             (int((pos[0]+(length/2+wheels[0]/5)*math.sin(angle)-width/2*math.cos(angle))*scaler),
              int((pos[1]+(length/2+wheels[0]/5)*math.cos(angle)+width/2*math.sin(angle))*scaler)),
             (0,0,255), 2)
    cv2.line(tmp,
             (int((pos[0]+length/2*math.sin(angle)+width/2*math.cos(angle))*scaler),
              int((pos[1]+length/2*math.cos(angle)-width/2*math.sin(angle))*scaler)),
             (int((pos[0]+(length/2+wheels[1]/5)*math.sin(angle)+width/2*math.cos(angle))*scaler),
              int((pos[1]+(length/2+wheels[1]/5)*math.cos(angle)-width/2*math.sin(angle))*scaler)),
             (0,0,255), 2)

    cv2.imshow("img", tmp)
    # if itt%6==0:
    #     cv2.imwrite("images/" + str(itt) + ".png", tmp)
    #     print(itt)
    cv2.waitKey(5)

def click(event, x, y, flags, param):
    global pos, angle, t, t_i, wheels
    if event == cv2.EVENT_LBUTTONDOWN:
        pos = (x/scaler,y/scaler)
        angle = 0
        t = 0
        t_i = 0
        wheels = [0, 0]


config = configparser.ConfigParser()
config.read("config.ini")

with open(config["PATH"]["FILE_LOCATION"]) as file:
    path = [([float(x) for x in line.split(",")]) for line in file.readlines()]


scaler = float(config["FIELD_IMAGE"]["PIXELS_PER_UNIT"])
width = float(config["ROBOT"]["TRACKWIDTH"])
length = float(config["ROBOT"]["LENGTH"])

pos = path[0]
angle = math.atan2(path[1][0], path[1][1])
t = 0
t_i = 0
wheels = [0,0]

dt=0.005

field = cv2.imread(config["FIELD_IMAGE"]["FILE_LOCATION"])
scale_multiplier = 2
width2 = int(field.shape[1] * scale_multiplier)
height2 = int(field.shape[0] * scale_multiplier)
dim = (width2, height2)
resized = cv2.resize(field, dim, interpolation = cv2.INTER_AREA)
img = resized
#img = np.zeros((resized.shape[0], resized.shape[1], 3), np.uint8)
start_pos = (path[0][0], path[0][1]) #(resized.shape[0]/2, resized.shape[1]/2)
draw_path(img)
#print(start_pos)
#print(scaler)
cv2.imshow("img", img)
cv2.setMouseCallback('img', click)
cv2.waitKey(5)

itt = 0
t1= time.time()
while closest() != len(path)-1:

    look = lookahead()
    close = closest()
    curv = curvature(look) if t_i>close else 0.00001 
    vel = path[close][2]
    last_wheels = wheels
    wheels = turn(curv, vel, width)

    for i, w in enumerate(wheels):
        wheels[i] = last_wheels[i] + min(float(config["ROBOT"]["MAX_VEL_CHANGE"])*dt, max(-float(config["ROBOT"]["MAX_VEL_CHANGE"])*dt, w-last_wheels[i]))

    pos = (pos[0] + (wheels[0]+wheels[1])/2*dt * math.sin(angle), pos[1] + (wheels[0]+wheels[1])/2*dt * math.cos(angle))
    angle += math.atan((wheels[0]-wheels[1])/width*dt)
    #print(str(wheels) + ", " + str(angle))
    #time.sleep(0.05)
    draw_robot(img)
    itt += 1
t2= time.time()
print("done")
#print(t2 - t1)
#print(statistics.mean(distances))
print(scaler)
#print(distances)
cv2.waitKey()