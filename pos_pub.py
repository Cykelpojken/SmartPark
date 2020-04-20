#!/usr/bin/env python
import rospy
import time
import queue
import zmq
import threading
from std_msgs.msg import Header
from sensor_msgs.msg import LaserScan
from tf import TransformListener
from geometry_msgs.msg import PointStamped
import tf2_ros

class pos_pub:
    tf_listener = TransformListener()
    x = 0
    y = 0
    rospy.init_node('pos_pub')
    rate = rospy.Rate(5)
    def __init__(self):

        self.server_context = zmq.Context()

        self.publish_socket = self.server_context.socket(zmq.PUB)
        self.publish_socket.setsockopt(zmq.SNDHWM, 1)
        self.publish_socket.setsockopt(zmq.SNDBUF, 2024)
        print(self.publish_socket.bind("tcp://*:5560"))
        threading.Thread(target=self.output).start()


    def output(self):
        while True:
            self.publish_socket.send(bytes(self.x) + ":" + bytes(self.y))
            # 5hz as specified in rate
            print(self.x)
            print(self.y)
            self.rate.sleep()

    def callback(self, data):
        #position = self.tf_listener.transformPoint("scan", data)
        self.x = data.transforms[0].transform.translation.x
        self.y = data.transforms[0].transform.translation.y

    def listener(self):

        rospy.Subscriber("tf", PointStamped, self.callback)
        rospy.spin()

if __name__ == '__main__':
    pos = pos_pub()
    pos.listener()