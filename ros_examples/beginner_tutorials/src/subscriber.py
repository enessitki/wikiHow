#!/usr/bin/env python3
import rospy
from std_msgs.msg import String


def callback(msg):
    print(msg.data, type(msg.data))


rospy.init_node("topic_subscriber")
sub = rospy.Subscriber("/phrases", String, callback=callback)
rospy.spin()
