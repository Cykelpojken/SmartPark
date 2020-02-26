from car_controller.car_controller_ import CarController
import time
import numpy as np
import cv2
from matplotlib import pyplot as plt
THRESHOLD               = 100 #less means more stricts
EROSION                 = 2 #Iteration. More means thicker
DILATION                = 2 #Iteration. More means more is removed
MIN_MATCH_COUNT         = 2
SURF                    = True
SAVE_PICTURES           = False
def thresholding(img):

        ret,thresh1 = cv2.threshold(img,THRESHOLD,255,cv2.THRESH_BINARY)
        if SAVE_PICTURES: 
            cv2.imwrite('threshold.jpg', thresh1)

        return thresh1

def erosion(img):
        kernel = np.ones((2,2), np.uint8) 
        img_erosion = cv2.erode(img, kernel, iterations=EROSION) 
        if SAVE_PICTURES:
            cv2.imwrite("erosion.jpg", img_erosion)
        return img_erosion

def dilation(img):
        kernel = np.ones((2,2), np.uint8) 
        img_dilation = cv2.dilate(img, kernel, iterations=DILATION) 
        if SAVE_PICTURES:
            cv2.imwrite("dilation.jpg", img_dilation)
        return img_dilation
    
def blur(img = None, threshold = 3, t = cv2.BORDER_DEFAULT):
    blur = cv2.GaussianBlur(img,(threshold,threshold),t)
    if SAVE_PICTURES:
        cv2.imwrite("blurred.jpg", blur)
    return blur

def find_spot(img=None): #Working well ish
    #print(img)
    
    parking_coordinates = None

    img = cv2.imread('erosion.jpg', 0)
    img = blur(img, 3, 0)

    box = cv2.imread('erosion_box.png',0) # queryImage
    box = blur(box, 3, 0) #5 here 5 other both 0 works ok

    # Initiate surf detector
    surf = cv2.xfeatures2d.SURF_create(2000*1.3) if SURF else cv2.xfeatures2d.SIFT_create()

    # find the keypoints and descriptors with surf
    kp1, des1 = surf.detectAndCompute(box,None)
    kp2, des2 = surf.detectAndCompute(img,None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(des1,des2,k=2)

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    if len(good)>MIN_MATCH_COUNT:
        print(len(good))
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        #print(dst_pts)
        #print(src_pts, dst_pts)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        #print(M)
        matchesMask = mask.ravel().tolist()
        h,w = box.shape
        #print(box.shape)
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        pts2 = np.float32([[15,50],[40,50], [40,70], [15,70]]).reshape(-1,1,2)

        if M is not None and pts is not None:
            dst = cv2.perspectiveTransform(pts,M)
            dst2 = cv2.perspectiveTransform(pts2,M)
            img = cv2.polylines(img,[np.int32(dst)],True,50,3, cv2.LINE_AA)
            img = cv2.polylines(img,[np.int32(dst2)],True,50,2, cv2.LINE_AA)
            cv2.imwrite("asd.jpg", img)

            x = (dst2[0][0][0] + dst2[1][0][0]) / 2 
            y = (dst2[2][0][0] + dst2[3][0][0]) / 2 
            parking_coordinates = (x,y)

        else:
            print("M: " + str(M))
            #print("pts: " + str(pts))
            print("got a bad frame")

    else:
        matchesMask = None

    draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                singlePointColor = None,
                matchesMask = matchesMask, # draw only inliers
                flags = 2)

    img3 = cv2.drawMatches(box,kp1,img,kp2,good,None,**draw_params)
    #plt.imshow(img3),plt.show()

    img3 = img3[:,:,0]

    if SAVE_PICTURES:
        cv2.imwrite("identified.jpg", img3)
        #plt.imshow(img3),plt.show()
    cv2.imwrite("identified.jpg", img3)

    return img3, parking_coordinates
