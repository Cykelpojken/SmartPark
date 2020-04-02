from car_controller.car_controller_ import CarController
import time

c = car_controller("localhost")

def allign(target_theta):
    while c.slam_data_model.theta != target_theta:
        c.set_turnrate(5)

def phase1(target_theta):
    pass
    # turn 45 degrees away from the parking spot

def phase2(theta, target_coordinates):
    pass
    # Drive straight backwards to target location

def phase3(theta):
    pass
    # turn back to original theta

def phase4(theta):
    pass
    # slight forward


# tråd som kollar att vi alltid är en viss offset från väggarna?
