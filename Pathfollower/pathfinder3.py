import cv2
import numpy as np
import threading
import colorsys
import time
import math  

class Point(object):

    

    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.f = 0
        self.dir = 0
        #self.parent = parent
        #self.position = position
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

rw = 3
p = 0
start = Point()
end = Point()
startpos = (start.x, start.y)
endpos = (end.x, end.y)
dir4 = [Point(0, -1), Point(0, 1), Point(1, 0), Point(-1, 0), Point(-1, -1), Point(-1, 1), Point(1, -1), Point(1, 1)]


def BFS(start_point, end_point):

    global img, h, w
    const = w*h/50

    found = False

    #---------------Start-2-end--------------------------
    q = []
    visited = [[0 for j in range(w)] for i in range(h)]
    parent = [[Point() for j in range(w)] for i in range(h)]

    q.append(start_point)
    visited[start_point.y][start_point.x] = 1
    while len(q) > 0:
        p = q.pop(0)
        for d in dir4:
            child = p + d
            if (child.x >= 0 and child.x < w and child.y >= 0 and child.y < h and visited[child.y][child.x] == 0 and
                    (img[child.y][child.x][0] != 0 or img[child.y][child.x][1] != 0 or img[child.y][child.x][2] != 0)):
                q.append(child)
                visited[child.y][child.x] = visited[p.y][p.x] + 1  

                img[child.y][child.x] = (
                    [i * 255 for i in colorsys.hsv_to_rgb(visited[child.y][child.x] / const, 1, 1)]
                )
                parent[child.y][child.x] = p
                if child == end_point:
                    found = True
                    del q[:]
                    break

    path = []
    if found:
        p = end_point
        while p != start_point:
            path.append(p)
            p = parent[p.y][p.x]
        path.append(p)
        path.reverse()

        for p in path:
            img[p.y][p.x] = [255, 255, 255]
            img[p.y-1][p.x-1] = [255, 255, 255]
        print("Path Found")
    else:
        print("Path Not Found")
#-------------------------End-2-start-----------------


def astar(maze, start_point, end_point):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end node
    global img, h, w
    start_point.g = start_point.h = start_point.f = 0
    end_point.g = end_point.h = end_point.f = 0
    const = w*h/50
    openset = []
    visited = [[0 for j in range(w)] for i in range(h)]
    parent = [[Point() for j in range(w)] for i in range(h)]
    found = False
    # Add the start node
    openset.append(start_point)

    # Loop until you find the end

    while len(openset) > 0:
        current_node = openset[0]
        #current_node.h = ((current_node.x - end_point.x) ** 2) + ((current_node.y - end_point.y) ** 2)
        #current_node.g = 0
        #current_node.f = current_node.g + current_node.h
    
        current_index = 0
        for index, item in enumerate(openset):
            if item.f < current_node.f:
                current_node = item
                current_index = index
                

        openset.pop(current_index)
        visited.append(current_node)
        for d in dir4:
            child = current_node + d
            child.g = current_node.g + 1
            child.h = ((child.x - end_point.x) ** 2) + ((child.y - end_point.y) ** 2)
            child.f = child.g + child.h
            # Lower F score, not out of bounds, not black check
            if (child.f < current_node.f and child.x >= 0 and child.x < w and child.y >= 0 and child.y < h and visited[child.y][child.x] == 0 and
                    (img[child.y][child.x][0] != 0 or img[child.y][child.x][1] != 0 or img[child.y][child.x][2] != 0)):
                openset.append(child)
                visited[child.y][child.x] = visited[current_node.y][current_node.x] + 1
                img[child.y][child.x] = [i * 255 for i in colorsys.hsv_to_rgb(visited[child.y][child.x] / const, 1, 1)]
                parent[child.y][child.x] = current_node # cameFrom[neighbor] := current
                if child.x == end_point.x and child.y == end_point.y:
                    found = True
                    del openset[:]
                    break
                # Out of bounds, not black check
            elif (child.x >= 0 and child.x < w and child.y >= 0 and child.y < h and visited[child.y][child.x] == 0 and
                    (img[child.y][child.x][0] != 0 or img[child.y][child.x][1] != 0 or img[child.y][child.x][2] != 0)):
                openset.append(child)
                visited[child.y][child.x] = visited[current_node.y][current_node.x] + 1  
                img[child.y][child.x] = [i * 255 for i in colorsys.hsv_to_rgb(visited[child.y][child.x] / const, 1, 1)]
                parent[child.y][child.x] = current_node
                if child.x == end_point.x and child.y == end_point.y:
                    found = True
                    del openset[:]
                    break
            
    path = []
    waypoints = []
    pangle = None
    prevangle = None
    if found:
        p = end_point
        while p != start_point:
            #print("point: ", (p.x, p.y), "parent: ",parent[p.y][p.x].x, parent[p.y][p.x].y)
            path.append(p)
            temp = (p.x, p.y)
            if (parent[p.y][p.x].x - p.x == 0):
                prevangle = pangle
                pangle = 90
            else:
                prevangle = pangle
                pangle = math.degrees(math.atan((parent[p.y][p.x].y - p.y) / (parent[p.y][p.x].x - p.x)))
            if prevangle != pangle:
                waypoints.append(temp)
            p = parent[p.y][p.x]
        print("Path Found")
        temp = (p.x, p.y)
        waypoints.append(temp)
        path.append(p)
        temp = (p.x, p.y)
        waypoints.reverse()
        path.reverse()
        #print(waypoints)
        for p in path:
            img[p.y][p.x] = [255, 255, 255]

        #print("Path Found")
        #print(path)
        
    else:
        print("Path Not Found")
    return waypoints
def mouse_event(event, pX, pY, flags, param):

    global img, start, end, p

    if event == cv2.EVENT_LBUTTONUP:
        if p == 0:
            cv2.rectangle(img, (pX - rw, pY - rw),
                        (pX + rw, pY + rw), (0, 255, 0), -1)
            start = Point(pX, pY)
            print("start = ", start.x, start.y)
            p += 1
        elif p == 1:
            cv2.rectangle(img, (pX - rw, pY - rw),
                        (pX + rw, pY + rw), (0, 0, 255), -1)
            end = Point(pX, pY)
            print("end = ", end.x, end.y)
            p += 1


def disp():
    global img
    cv2.imshow("Image", img)
    cv2.setMouseCallback('Image', mouse_event)
    while True:
        cv2.imshow("Image", img)
        cv2.waitKey(15)

def getpath():
    return path

def getstart():
    return start_point

def getend():
    return end_point


img = cv2.imread("Pathfollower/test2.png", cv2.IMREAD_GRAYSCALE)
_, img = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY)
img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
matrix = img[:,:,0]
#print(matrix)
h, w = img.shape[:2]


print("Select start and end points : ")


t = threading.Thread(target=disp, args=())
t.daemon = True
t.start()



while p < 2:
    pass
t1= time.time()
waypojk = astar(matrix, start, end)
cv2.destroyAllWindows()
time.sleep(2)
t2 = time.time()
#print(t2 - t1)
#waypojk = BFS(start, end)
#astar(matrix, start, end)

#cv2.waitKey(0)
#time.sleep(2)