#!/usr/bin/env python3
import matplotlib.pyplot as plt
import math
import rospy
from nav_msgs.msg import Odometry


# count = 0
LIMIT = 300


def callback(msg):
    # global count
    t = msg.header.stamp.secs + msg.header.stamp.nsecs / 1e9
    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y
    z = msg.pose.pose.position.z

    a = msg.pose.pose.orientation.x
    b = msg.pose.pose.orientation.y
    c = msg.pose.pose.orientation.z
    d = msg.pose.pose.orientation.w

    plt.xlim(t - 100, t + 1)
    plt.scatter(t, x)
    plt.pause(0.001)


rospy.init_node("vehicle-subscriber")
sub = rospy.Subscriber("/vehicle/odom", Odometry, callback=callback)
rospy.spin()
