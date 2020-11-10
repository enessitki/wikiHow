#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

rospy.init_node("topic_publisher")
pub = rospy.Publisher("phrases", String, queue_size=10)

rate = rospy.Rate(2)  # Hz
msg_str = "Hello"

while not rospy.is_shutdown():
    pub.publish(msg_str)
    rate.sleep()
