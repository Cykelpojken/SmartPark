from car_controller.car_controller_ import CarController
from roboviz import MapVisualizer
import config as cfg
import time
import numpy as np
import cv2
from matplotlib import pyplot as plt
import threading
'''Conclusion: Might need to scale down. Then we do threshold where we just make a distinction between white and black. 
Then we use erosion to make the lines thicker. Finally we blur the image to make it less "pixely" and then print corners.'''
class test():

    MAP_SIZE_PIXELS         = cfg.MAP_SIZE_PIXELS
    MAP_SIZE_METERS         = cfg.MAP_SIZE_METERS
    SCALE_PERCENT           = 50
    ALPHA_CONTRAST          = 1.5
    BETA_BRIGHTNESS         = 0

    THRESHOLD               = 50 #less means more stricts
    EROSION                 = 3 #Iteration. More means thicker
    DILATION                = 2 #Iteration. More means more is removed

    viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')
    c = CarController("localhost")


    def __init__(self):
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
        #plt.imshow(img),plt.show()
        #print(self.t2 - self.t1)      

    def contrast(self, img = None):
        if img == None:
            img = self.original_img

        new_image = np.zeros(img.shape, img.dtype)
       
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                #for c in range(image.shape[2]):
                new_image[y,x] = np.clip(self.ALPHA_CONTRAST * img[y,x] + self.BETA_BRIGHTNESS, 0, 255)

        self.images["contrast"] = new_image
        return new_image

    def scale(self):
        width = int(self.original_img.shape[1] * self.SCALE_PERCENT / 100)
        height = int(self.original_img.shape[0] * self.SCALE_PERCENT / 100)
        dim = (width, height)
        resized = cv2.resize(self.original_img, dim, interpolation = cv2.INTER_AREA) 
        self.original_img = resized
        #self.images["Scaled"] = resized 

    def thresholding(self, img = None):
        if img is None:
            img = self.original_img
            ret,thresh1 = cv2.threshold(img,self.THRESHOLD,255,cv2.THRESH_BINARY)
            self.images["Thresholding"] = thresh1
            cv2.imwrite('threshold_map_127.jpg', thresh1)

        else:
            ret,thresh1 = cv2.threshold(img,1,255,cv2.THRESH_BINARY)
            cv2.imwrite('threshold_map_127.jpg', thresh1)

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
            img = self.original_img
            edges = cv2.Canny(img,100,150)
            self.images["Canny"] = edges
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
        cv2.imwrite("erosion.jpg", img_erosion)
        self.images["Erosion"] = img_erosion
        return img_erosion
    
    def dilation(self, img = None):
        kernel = np.ones((2,2), np.uint8) 
        if img is None:
            img = self.original_img
        img_dilation = cv2.dilate(img, kernel, iterations=self.DILATION) 
        cv2.imwrite("dilation.jpg", img_dilation)
        self.images["Erosion"] = img_dilation
        return img_dilation
    
    def blur(self, img = None):
        if img is None:
            img = cv2.imread("erosion.jpg", 0)
        
        blur = cv2.GaussianBlur(img,(5,5),0)
        cv2.imwrite("blurred and done.jpg", blur)
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



############################################################################################################################
############################################################################################################################
############################################################################################################################

    def image_processing(self):
        
        mapimg = np.reshape(np.frombuffer(self.c.slam_data_model.mapbytes, dtype=np.uint8), (self.MAP_SIZE_PIXELS, self.MAP_SIZE_PIXELS))
        cv2.imwrite('map.jpg', mapimg)
    
        img = cv2.imread('map.jpg', 0)
        self.original_img = img
        self.images = {"Original" : self.original_img}
        #a = self.remove_isolated_pixels(img)
        
        t_map = self.thresholding()
        d_map = self.dilation(t_map)
        t_e_map = self.erosion(d_map)
        #c_map = self.canny(t_e_map)
        blur = self.blur(t_e_map)

        #self.images = {"Blurred" : blur}
        print("---------------------------------------------------------------------")
        self.draw_corners(t_map)
        print("---------------------------------------------------------------------")
        #time.sleep(123)

        #self.show_image()

    def start_SLAM(self):
        #threading.Thread(target=self.image_processing, daemon=False).start()
        while True:
            if self.c.slam_data_model.x is not None:
                print("X: {}, Y: {}".format(int(self.c.slam_data_model.x/100), int(self.c.slam_data_model.y/100)))
                if not self.viz.display(self.c.slam_data_model.x/1000., self.c.slam_data_model.y/1000., 1, self.c.slam_data_model.mapbytes):
                    self.image_processing()
                    exit(0)
                    
            else:
                time.sleep(1)

if __name__ == '__main__':
    t = test()