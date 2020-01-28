from car_controller.car_controller_ import CarController
from roboviz import MapVisualizer
import time
import numpy as np
import cv2
from matplotlib import pyplot as plt


class test():

    MAP_SIZE_PIXELS         = 500
    MAP_SIZE_METERS         = 10
    SCALE_PERCENT           = 50
    ALPHA_CONTRAST          = 1.5
    BETA_BRIGHTNESS         = 0

    #viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')
    c = CarController("localhost")


    def __init__(self):
        self.start()

    def draw_corners(self, img = None):
        if img == None:
            img = self.original_img
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        corners = cv2.goodFeaturesToTrack(gray,25,0.01,10)
        corners = np.int0(corners)

        for i in corners:
            x,y = i.ravel()
            cv2.circle(img,(x,y),3,255,-1)
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
        if img == None:
            img = self.original_img

        ret,thresh1 = cv2.threshold(img,200,255,cv2.THRESH_BINARY)
        self.images["Thresholding"] = thresh1
        return thresh1
            
    def show_image(self):
        print("asd")
        nrows = 3
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
            i = 0
            img = self.original_img
        else:
            i = 1
            
        edges = cv2.Canny(img,0,200)

        self.images["Canny" + str(i)] = edges
        return edges

    def start(self):
        while True:
            if self.c.slam_data_model.x is not None:
                time.sleep(1)
                img = mapimg = np.reshape(np.frombuffer(self.c.slam_data_model.mapbytes, dtype=np.uint8), (self.MAP_SIZE_PIXELS, self.MAP_SIZE_PIXELS))
                cv2.imwrite('map.jpg', mapimg)

                img = cv2.imread('map.jpg')
                self.original_img = img

                self.images = {"Original" : self.original_img}
                #self.scale()
                #self.contrast()
                cont = self.thresholding()
                self.draw_corners()

                self.canny(cont)
                self.canny()
                self.show_image()
                #print(len(self.images))

                self.t2 = time.time()
                #print(self.t2 - self.t1)

                #if not self.viz.display(self.c.slam_data_model.x/1000., self.c.slam_data_model.y/1000., 1, self.c.slam_data_model.mapbytes):
                    #exit(0)
                
                time.sleep(500)
            else:
                time.sleep(0.1)

if __name__ == '__main__':
    t = test()