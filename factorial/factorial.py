import pandas as pd
import cv2
import image_processing as ip
import time
no_iterations = 1
blur_map = 1
blur_box = 1

blur_max = 35

imgset1 = [cv2.imread('testmaps/map1.png', 0), cv2.imread('testmaps/box1_big.png', 0), cv2.imread('testmaps/box1_small.png', 0)]
imgset2 = [cv2.imread('testmaps/map2.png', 0), cv2.imread('testmaps/box2_huge.png', 0), cv2.imread('testmaps/box2_small.png', 0)]
imgset3 = [cv2.imread('testmaps/map3.png', 0), cv2.imread('testmaps/box3_huge.png', 0), cv2.imread('testmaps/box3_small.png', 0)]
imgset4 = [cv2.imread('testmaps/map4.png', 0), cv2.imread('testmaps/box4_big.png', 0), cv2.imread('testmaps/box4_small.png', 0)]
imgsets = [imgset1, imgset2, imgset3, imgset4]

data = {
    'Blur Map'          : [], 
    'Blur Box'          : [],
    'Average Matches'   : [],
    'Max Matches'       : [],
    'Average Time'      : []
}
data_frame = pd.DataFrame(data)
max_matches         = 0
while blur_map <= blur_max:
    total_matches       = 0 
    total_time          = 0

    i = no_iterations
    while (i > 0):
        i -= 1
        
        t1 = time.time()

        img_map = ip.blur(imgset3[0], blur_map, 0)
        img_box_big = ip.blur(imgset3[1], blur_box, 0)
        img_box_small = ip.blur(imgset3[2], blur_box, 0)
        cv2.imwrite("test1.png", img_map)
        cv2.imwrite("test2.png", img_box_big)
        img, coordinates, matches = ip.find_spot(img_map, img_box_big)

        total_time += time.time() - t1

        total_matches += matches


        if matches >= max_matches:
            print(matches, max_matches)
            max_matches = matches
            cv2.imwrite("max_matches.png", img)
            
        data['Blur Map'] = [blur_map]
        data['Blur Box'] = [blur_box]
        data['Average Matches'] = [total_matches / no_iterations]
        data['Max Matches'] = [max_matches]
        data['Average Time'] = [total_time / no_iterations]

        pd_data = pd.DataFrame(data)
        temp = pd_data
        data_frame = data_frame.append(pd_data)  
        #time.sleep(0.1) 

    if blur_box < blur_max:
        blur_box += 2
    else:
        blur_box = 1
        blur_map += 2

data_frame.to_csv('test.csv')
        
        



