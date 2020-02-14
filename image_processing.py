from car_controller.car_controller_ import CarController
from roboviz import MapVisualizer
import config as cfg
import time
import numpy as np
import cv2
from matplotlib import pyplot as plt
import threading
import image_slicer
from PIL import ImageDraw, ImageFont 

c = CarController("localhost")


THRESHOLD               = 100 #less means more stricts
EROSION                 = 2 #Iteration. More means thicker
DILATION                = 2 #Iteration. More means more is removed


SAVE_PICTURES = False
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
    
def blur(img = None):
    blur = cv2.GaussianBlur(img,(7,7),cv2.BORDER_DEFAULT)
    if SAVE_PICTURES:
        cv2.imwrite("blurredjpg", blur)
    return blur

def find_spot(img): #Working well ish
        MIN_MATCH_COUNT = 4

        box = cv2.imread('box.png',0)          # queryImage
       
        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(box,None)
        kp2, des2 = sift.detectAndCompute(img,None)

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
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()

            h,w = box.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            pts2 = np.float32([[15,50],[40,50], [40,70], [15,70]]).reshape(-1,1,2)

            if M is not None and pts is not None:
                dst = cv2.perspectiveTransform(pts,M)
                dst2 = cv2.perspectiveTransform(pts2,M)
                img = cv2.polylines(img,[np.int32(dst)],True,50,3, cv2.LINE_AA)
                img = cv2.polylines(img,[np.int32(dst2)],True,50,2, cv2.LINE_AA)
                cv2.imwrite("asd.jpg", img)
            else:
                print("got a bad frame")
            



        else:
            #print("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
            matchesMask = None

        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)

        img3 = cv2.drawMatches(box,kp1,img,kp2,good,None,**draw_params)

        img3 = img3[:,:,0]

        if SAVE_PICTURES:
            cv2.imwrite("identifiedjpg", img3)
        cv2.imwrite("identified.jpg", img3)

        return img3
 