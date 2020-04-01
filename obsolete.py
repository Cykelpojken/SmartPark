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
'''Conclusion: Might need to scale down. Then we do threshold where we just make a distinction between white and black. 
Then we use erosion to make the lines thicker. Finally we blur the image to make it less "pixely".'''
class test():

    MAP_SIZE_PIXELS         = cfg.MAP_SIZE_PIXELS
    MAP_SIZE_METERS         = cfg.MAP_SIZE_METERS
    MAP_SIZE_PIXELS_1       = 1118
    SCALE_PERCENT           = 50
    ALPHA_CONTRAST          = 1.5
    BETA_BRIGHTNESS         = 0

    THRESHOLD               = 100 #less means more stricts
    EROSION                 = 2 #Iteration. More means thicker
    DILATION                = 2 #Iteration. More means more is removed

    SAVE_PICTURES           = False
    DEFAULT_SLAM_MAP        = True

    c = CarController("localhost")


    def __init__(self):
        self.viz = MapVisualizer(self.MAP_SIZE_PIXELS, self.MAP_SIZE_PIXELS, self.MAP_SIZE_METERS, 'SLAM') if self.DEFAULT_SLAM_MAP else MapVisualizer(self.MAP_SIZE_PIXELS, self.MAP_SIZE_PIXELS_1, self.MAP_SIZE_METERS, 'SLAM')
        self.start_SLAM()
    
    def draw_corners(self, img = None):
        if img is None:
            img = cv2.imread('erosion.jpg', cv2.COLOR_BGR2GRAY)
            #plt.imshow(img),plt.show()
        
        img = cv2.cvtColor(img,1)           
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        corners = cv2.goodFeaturesToTrack(gray,1,0.1,10)
        corners = np.int0(corners)

        for i in corners:
            x,y = i.ravel()
            cv2.circle(img,(x,y),3,(0, 0, 255),-1)
            print("X: {} Y: {}".format(int(x),int(y)))
        cv2.imwrite("asd.jpg", img)
        plt.imshow(img),plt.show()
        #print(self.t2 - self.t1)      

    def contrast(self, img = None):
        if img == None:
            img = self.original_img

        new_image = np.zeros(img.shape, img.dtype)
       
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                #for c in range(image.shape[2]):
                new_image[y,x] = np.clip(self.ALPHA_CONTRAST * img[y,x] + self.BETA_BRIGHTNESS, 0, 255)

        return new_image

    def scale(self):
        width = int(self.original_img.shape[1] * self.SCALE_PERCENT / 100)
        height = int(self.original_img.shape[0] * self.SCALE_PERCENT / 100)
        dim = (width, height)
        resized = cv2.resize(self.original_img, dim, interpolation = cv2.INTER_AREA) 
        self.original_img = resized

    def thresholding(self, img = None):
        if img is None:
            img = cv2.imread("map_{}.jpg".format(self.time))
        ret,thresh1 = cv2.threshold(img,self.THRESHOLD,255,cv2.THRESH_BINARY)
        if self.SAVE_PICTURES: 
            cv2.imwrite('threshold_{}.jpg'.format(self.time), thresh1)

        return thresh1
            
    def show_image(self):
        print("asd")
        nrows = 1
        ncols = 3
        fig, axeslist = plt.subplots(ncols=ncols, nrows=nrows)
        for ind,title in enumerate(self.images):
            axeslist.ravel()[ind].imshow(self.images[title], cmap=plt.gray())
            axeslist.ravel()[ind].set_title(title)
            axeslist.ravel()[ind].set_axis_off()
        plt.tight_layout()
        plt.show()
    
    def canny(self, img = None):
        if img is None:
            img = cv2.imread("erosion.jpg", 0)
            edges = cv2.Canny(img,100,150)
            cv2.imwrite('Canny.jpg', edges)
        else:
            edges = cv2.Canny(img,100,150)
            cv2.imwrite('Canny.jpg', edges)
            
        

        
        return edges

    def erosion(self, img = None):
        kernel = np.ones((2,2), np.uint8) 
        if img is None:
            img = self.original_img
        img_erosion = cv2.erode(img, kernel, iterations=self.EROSION) 
        if self.SAVE_PICTURES:
            cv2.imwrite("erosion_{}.jpg".format(self.time), img_erosion)
        return img_erosion
    
    def dilation(self, img = None):
        kernel = np.ones((2,2), np.uint8) 
        if img is None:
            img = self.original_img
        img_dilation = cv2.dilate(img, kernel, iterations=self.DILATION) 
        if self.SAVE_PICTURES:
            cv2.imwrite("dilation_{}.jpg".format(self.time), img_dilation)
        return img_dilation
    
    def blur(self, img = None):
        if img is None:
            img = cv2.imread("erosion.jpg", 0)
        
        blur = cv2.GaussianBlur(img,(7,7),cv2.BORDER_DEFAULT)
        if self.SAVE_PICTURES:
            cv2.imwrite("blurred_{}.jpg".format(self.time), blur)
        return blur

    def remove_isolated_pixels(self, image):
        connectivity = 8

        output = cv2.connectedComponentsWithStats(image, connectivity, cv2.CV_32S)

        num_stats = output[0]
        labels = output[1]
        stats = output[2]

        new_image = image.copy()

        for label in range(num_stats):
            if stats[label,cv2.CC_STAT_AREA] == 1:
                new_image[labels == label] = 0

        return new_image

    def feature_detection(self, image = None): #Works Decent with edgethreshold on orb =10
        img1 = cv2.imread('blurred and done.jpg',0)          # queryImage
        img2 = cv2.imread('box.png',0) # trainImage
        plt.imshow(img2),plt.show()
        # Initiate SIFT detector
        orb = cv2.ORB_create()
        orb.setEdgeThreshold(10) #10 working pretty good
        print([method_name for method_name in dir(orb)
                  if callable(getattr(orb, method_name))])
        # find the keypoints and descriptors with SIFT
        kp1, des1 = orb.detectAndCompute(img1,None)
        kp2, des2 = orb.detectAndCompute(img2,None)
        # create BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck=True)

        # Match descriptors.
        matches = bf.match(des1,des2)
        # Sort them in the order of their distance.
        matches = sorted(matches, key = lambda x:x.distance)

        # Draw first 10 matches.
        img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:5],None, flags=2)

        plt.imshow(img3),plt.show()

    def find_spot(self, img = None): #Working well ish
        MIN_MATCH_COUNT = 4

        img1 = cv2.imread('box.png',0)          # queryImage
        #if img is None:
            #img = cv2.imread('blurred_{}.jpg'.format(self.time),0) # trainImage
        img = cv2.imread('blurred.jpg',0) # trainImage
        img2 = img
       

        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        # if(des2.type()!=CV_32F):
        #     des2.convertTo(des2, CV_32F)

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
            h,w = img1.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            pts2 = np.float32([[15,50],[40,50], [40,70], [15,70]]).reshape(-1,1,2)
            #pts = np.float32([pts])
            if M is not None and pts is not None:
                dst = cv2.perspectiveTransform(pts,M)
                dst2 = cv2.perspectiveTransform(pts2,M)
                #print(np.int32(dst))
                print(np.int32(dst2))
                img2 = cv2.polylines(img2,[np.int32(dst)],True,50,3, cv2.LINE_AA)
                img2 = cv2.polylines(img2,[np.int32(dst2)],True,50,2, cv2.LINE_AA)
                cv2.imwrite("asd.jpg", img2)
            else:
                print("got a bad frame")
            
            #plt.imshow(img2, 'gray'),plt.show()


        else:
            #print("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
            matchesMask = None

        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)

        img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)

        img3 = img3[:,:,0]

        if self.SAVE_PICTURES:
            cv2.imwrite("identified_{}.jpg".format(self.time), img3)
        #plt.imshow(img3, 'gray'),plt.show()
        cv2.imwrite("identified.jpg", img3)

        return img3
                                                  
    def find_spot_surf_bf(self, img = None):
        MIN_MATCH_COUNT = 1

        img1 = cv2.imread('box.png',0)          # queryImage
        #if img is None:
            #img = cv2.imread('blurred_{}.jpg'.format(self.time),0) # trainImage
        img = cv2.imread('blurred.jpg',0) # trainImage
        img2 = img
       

        # Initiate SIFT detector
        sift = cv2.xfeatures2d.SURF_create()

        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)

        # create BFMatcher object
        bf = cv2.BFMatcher()

        # Match descriptors.
        matches = bf.knnMatch(des1,des2, k=2)

        # Sort them in the order of their distance.
        #matches = sorted(matches, key = lambda x:x.distance)

        # store all the good matches as per Lowe's ratio test.
        good = []
        for m,n in matches:
            if m.distance < 0.70*n.distance:
                good.append(m)


        if len(good)>MIN_MATCH_COUNT:
            print("asd")
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

            M, mask = cv2.findHomography(src_pts, dst_pts) #cv2.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()
            h,w = img1.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            #pts = np.float32([pts])
            if M is not None and pts is not None:
                dst = cv2.perspectiveTransform(pts,M)
                img2 = cv2.polylines(img2,[np.int32(dst)],True,50,3, cv2.LINE_AA)
            else:
                print("got a bad frame")
            
            #plt.imshow(img2, 'gray'),plt.show()


        else:
            #print("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
            matchesMask = None

        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)

        img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,None,flags=2)

        img3 = img3[:,:,0]

        if self.SAVE_PICTURES:
            cv2.imwrite("identified_{}.jpg".format(self.time), img3)
        #plt.imshow(img3, 'gray'),plt.show()
        cv2.imwrite("identified.jpg", img3)

        return img3
  
    def hough_transform(self, img = None): 
        img = cv2.imread('box.png')
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray,50,150,apertureSize = 3)

        lines = cv2.HoughLines(image = edges,
                               rho = 4,
                               theta = np.pi/180,
                               threshold = 1)
        for rho,theta in lines[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

        cv2.imwrite('houghlines3.jpg',img)
    
    def contours(self, image = None):
        im = cv2.imread('threshold_map_127.jpg')
        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        ret, thresh = cv2.threshold(imgray, 1, 255, 0)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, 
        cv2.CHAIN_APPROX_SIMPLE)

        img = cv2.drawContours(im, contours, -1, (0, 255, 0), 3)

        cv2.imwrite("contours.jpg", img)
        # cv2.imshow('Output', img)
        # wk = cv2.waitKey(0) & 0xFF
        # if wk == 27:
        #     cv2.destroyAllWindows()

    def template(self):
        img_rgb = cv2.imread('blurred and done.jpg')
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread('box.png',0)
        w, h = template.shape[::-1]
        
        res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where( res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)

        cv2.imwrite('res.png',img_rgb)

    def orb_test(self):
        img = cv2.imread('box_erosion.png',0)
        orb = cv2.ORB_create()
        print([method_name for method_name in dir(orb)
                  if callable(getattr(orb, method_name))])
        orb.setEdgeThreshold(10)
        #orb.setScoreType(1)
        #print(orb.getScoreType)
        kp = orb.detect(img,None)

        # compute the descriptors with ORB
        kp, des = orb.compute(img, kp)

        # draw only keypoints location,not size and orientation
        img2 = cv2.drawKeypoints(img,kp,None ,color=(0,255,0), flags=0)
        plt.imshow(img2),plt.show()
#################################################################################
############################################################################################################################
############################################################################################################################

    def image_processing(self):
        mapimg = np.reshape(np.frombuffer(self.c.slam_data_model.mapbytes, dtype=np.uint8), (self.MAP_SIZE_PIXELS, self.MAP_SIZE_PIXELS))
        cv2.imwrite('map_{}.jpg'.format(self.time), mapimg)
        # self.original_img = mapimg

        # t_map = self.thresholding()
        # d_map = self.dilation(t_map)
        # t_e_map = self.erosion(d_map)
        # blur = self.blur(t_e_map)
        # identified = self.find_spot(blur)



    def start_SLAM(self):
        self.time = 0
        t1 = time.time()
        self.find_spot()
        t2 = time.time()
        print(t2-t1)
if __name__ == '__main__':
    t = test()