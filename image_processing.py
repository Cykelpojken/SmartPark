from car_controller.car_controller_ import CarController  # pragma: no cover
import time
import numpy as np
import cv2
from matplotlib import pyplot as plt
THRESHOLD = 100  # less means more stricts
EROSION = 2  # Iteration. More means thicker
DILATION = 2  # Iteration. More means more is removed
MIN_MATCH_COUNT = 8
BOXBLUR = 7
SURF = True
SAVE_PICTURES = False

def thresholding(img):
    ret, thresh1 = cv2.threshold(img, THRESHOLD, 255, cv2.THRESH_BINARY)
    if SAVE_PICTURES:
        cv2.imwrite('threshold.jpg', thresh1)
    return thresh1

def erosion(img):
    kernel = np.ones((2, 2), np.uint8)
    img_erosion = cv2.erode(img, kernel, iterations=EROSION)
    if SAVE_PICTURES:
        cv2.imwrite("erosion.jpg", img_erosion)
    return img_erosion

def dilation(img):
    kernel = np.ones((2, 2), np.uint8)
    img_dilation = cv2.dilate(img, kernel, iterations=DILATION)
    if SAVE_PICTURES:
        cv2.imwrite("dilation.jpg", img_dilation)
    return img_dilation

def blur(img=None, threshold=BOXBLUR, t=cv2.BORDER_DEFAULT):
    blur = cv2.GaussianBlur(img, (threshold, threshold), t)
    if SAVE_PICTURES:
        cv2.imwrite("blurred.jpg", blur)
    return blur

def find_spot(img=None):  # Working well ish
    parking_coordinates = None

    box = cv2.imread('box.png', 0)  # queryImage
    box = blur(box, 3, 0)  # 5 here 5 other both 0 works ok

    # Initiate surf detector
    surf = cv2.xfeatures2d.SURF_create(2000*2) if SURF else cv2.xfeatures2d.SIFT_create()

    # find the keypoints and descriptors with surf
    kp1, des1 = surf.detectAndCompute(box, None)
    kp2, des2 = surf.detectAndCompute(img, None)

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    # Apply ratio test
    good = []
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m, n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts,
                                     dst_pts,
                                     method=cv2.RANSAC,
                                     ransacReprojThreshold=5,
                                     maxIters=2000,
                                     confidence=0.999)

        matchesmask = mask.ravel().tolist()
        h, w = box.shape

        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        pts2 = np.float32([[20, 12.5]]).reshape(-1, 1, 2)

        if M is not None and pts is not None:
            dst = cv2.perspectiveTransform(pts, M)
            dst2 = cv2.perspectiveTransform(pts2, M)
            img = cv2.polylines(img, [np.int32(dst)], True, 50, 3, cv2.LINE_AA)
            img = cv2.circle(img, (dst2[0][0][0], dst2[0][0][1]), 5, (127, 0, 0), 3)
            parking_coordinates = (dst2[0][0][0], dst2[0][0][1])
            cv2.imwrite("coordinates.png", img)
        else:
            print("Got a bad frame")

    else:
        matchesmask = None

    draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                       singlePointColor=None,
                       matchesMas=matchesmask,  # draw only inliers
                       flags=2)

    img3 = cv2.drawMatches(box, kp1, img, kp2, good, None, **draw_params)

    if SAVE_PICTURES:
        cv2.imwrite("identified.jpg", img3)

    return img3, parking_coordinates
