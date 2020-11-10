#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist


def main():
    pub = rospy.Publisher('vehicle/cmd_vel', Twist, queue_size=10)
    rospy.init_node('vehicle-publisher', anonymous=True)

    rate = rospy.Rate(20) # 2hz
    msg = Twist()
    a = 0.0001
    # msg.linear.x = 0.1
    msg.angular.z = 0

    t0 = rospy.get_time()
    while not rospy.is_shutdown():
        msg.linear.x += a * (rospy.get_time() - t0)
        pub.publish(msg)
        rate.sleep()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass