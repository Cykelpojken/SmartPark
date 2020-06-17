from car_controller.car_controller_ import CarController
import time

c = CarController("localhost")

def allign(target_theta):
    if c.slam_data_model.theta < target_theta:
        c.set_turnrate(150)
    else:
        c.set_turnrate(-150)

    while target_theta - 10 <= c.slam_data_model.theta < target_theta + 10: #not sure if necessary to have +-10?
        time.sleep(0.1)
    c.set_turnrate(0)

def phase1(target_theta): # turn 45 degrees away from the parking spot
    theta = c.slam_data_model.theta
    allign(theta + 45)
    

def phase2(theta, target_coordinates): # Drive straight backwards to target location
    #APP
    pass
    

def phase3(theta): # turn back to original theta
    theta = c.slam_data_model.theta
    allign(theta + 45)
    
def phase4(theta): # slight forward
    
    

# tråd som kollar att vi alltid är en viss offset från väggarna?
