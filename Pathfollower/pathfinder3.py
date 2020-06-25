import cv2
import numpy as np
import threading
import colorsys
import time
import math
import random

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.f = 0
        self.dir = 0

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Pathfinder:
    def __init__(self, image, alg, startp, endp):
        self.start = Point(startp[0], startp[1])
        self.end = Point(endp[0], endp[1])
        self.algorithm = alg
        self.img = image
        #Remove last 4 points in dir4 if you don't want to search diagonally.
        self.dir4 = [Point(0, -1), Point(0, 1), Point(1, 0), Point(-1, 0), Point(-1, -1), Point(-1, 1), Point(1, -1), Point(1, 1)]


    def BFS(self, img, start_point, end_point):

        h, w = img.shape[:2]
        const = w*h/50

        found = False

        q = []
        visited = [[0 for j in range(w)] for i in range(h)]
        parent = [[Point() for j in range(w)] for i in range(h)]

        q.append(start_point)
        visited[start_point.y][start_point.x] = 1
        while len(q) > 0:
            p = q.pop(0)
            for d in self.dir4:
                child = p + d
                if (child.x >= 0 and
                    child.x < w and
                    child.y >= 0 and
                    child.y < h and
                    visited[child.y][child.x] == 0 and
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
<<<<<<< HEAD
            path.reverse()
            print("BFS Path Length: ", len(path))
            for p in path:
                img[p.y][p.x] = [255, 255, 255]
                img[p.y-1][p.x-1] = [255, 255, 255]
            print("Path Found")
        else:
            print("Path Not Found")
        return path


    def astar(self, img, start_point, end_point):
        """Returns a list of tuples as a path from the given start to the given end in the given maze"""

        # Create start and end node
        h, w = img.shape[:2]
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
            current_index = 0
            for index, item in enumerate(openset):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            openset.pop(current_index)
            visited.append(current_node)
            for d in self.dir4:
                child = current_node + d
                child.g = current_node.g + 1
                #child.h styr Heuristic funktionen för A star. Nedan tre exempel är Euclidean, Manhattan och sist 0 = Dijkstra's
                #child.h = ((child.x - end_point.x) ** 2) + ((child.y - end_point.y) ** 2)**0.5 
                child.h = abs(child.x - end_point.x) + abs(child.y - end_point.y)
                #child.h = 0
                child.f = child.g + child.h
                # Lower F score, not out of bounds, not black check
                if (child.f < current_node.f and
                    child.x >= 0 and
                    child.x < w and
                    child.y >= 0 and
                    child.y < h and
                    visited[child.y][child.x] == 0 and
                        (img[child.y][child.x][0] != 0 or img[child.y][child.x][1] != 0 or img[child.y][child.x][2] != 0)):
                    openset.append(child)
                    visited[child.y][child.x] = visited[current_node.y][current_node.x] + 1
                    img[child.y][child.x] = [i * 255 for i in colorsys.hsv_to_rgb(visited[child.y][child.x] / const, 1, 1)]
                    parent[child.y][child.x] = current_node  # cameFrom[neighbor] := current
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

        path = []  #the whole path
        waypoints = [] #Only the waypoints in the path, pick which ever you want
        pangle = None
        prevangle = None
        if found:
            p = end_point
            while p != start_point:
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
            print("A* Path Length: ", len(path))
            for p in path:
                img[p.y][p.x] = [255, 255, 255]

        else:
            print("Path Not Found")
        return waypoints

    def findpath(self):
        if (self.algorithm == 'BFS'):
            waypojk = self.BFS(self.img, self.start, self.end)
            return waypojk
        elif (self.algorithm == 'astar'):
            waypojk = self.astar(self.img, self.start, self.end)
            return waypojk
        else:
            print("Invalid algorithm, rerun the program and choose between BFS or astar")
            waypojk = [(0,0)]
            return waypojk


    #Code for testing (RNG start/end), just remove.
    '''
    lengths = []
    pathA = []
    t1 = time.time()
    for x in range(0, 50):
        startx = random.randint(870, 890)
        starty = random.randint(620, 640)
        endx = random.randint(540, 560)
        endy = random.randint(560, 580)
        start = Point(startx, starty)
        end = Point(endx, endy)
        #path2 = BFS(start, end)
        path2 = astar(matrix, start, end)
        lengths.append(len(path2))
    print(lengths)
    t2 = time.time()
    print(t2-t1)
    '''
=======
            p = parent[p.y][p.x]
        path.append(p)
        path.reverse()

        for p in path:
            img[p.y][p.x] = [255, 255, 255]
            img[p.y-1][p.x-1] = [255, 255, 255]
        print("Path Found")
    else:
        print("Path Not Found")
# -------------------------End-2-start-----------------


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
            child.h = abs(child.x - end_point.x) + abs(child.y - end_point.y)  # ((child.x - end_point.x) ** 2) + ((child.y - end_point.y) ** 2)**0.5
            child.f = child.g + child.h
            # Lower F score, not out of bounds, not black check
            if (child.f < current_node.f and
                child.x >= 0 and
                child.x < w and
                child.y >= 0 and
                child.y < h and
                visited[child.y][child.x] == 0 and
                    (img[child.y][child.x][0] != 0 or img[child.y][child.x][1] != 0 or img[child.y][child.x][2] != 0)):
                openset.append(child)
                visited[child.y][child.x] = visited[current_node.y][current_node.x] + 1
                img[child.y][child.x] = [i * 255 for i in colorsys.hsv_to_rgb(visited[child.y][child.x] / const, 1, 1)]
                parent[child.y][child.x] = current_node  # cameFrom[neighbor] := current
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
        print(len(path))
        for p in path:
            img[p.y][p.x] = [255, 255, 255]

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


img = cv2.imread("Pathfollower/test2.png", cv2.IMREAD_GRAYSCALE)
_, img = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY)
img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
matrix = img[:, :, 0]
h, w = img.shape[:2]

print("Select start and end points : ")

t = threading.Thread(target=disp, args=())
t.daemon = True
t.start()

while p < 2:
    pass
t1 = time.time()
waypojk = astar(matrix, start, end)
t2 = time.time()
>>>>>>> 46674b379bbad32d6867fabb9c29eff690b3b3f6
