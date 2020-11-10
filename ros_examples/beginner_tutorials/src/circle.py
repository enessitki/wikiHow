#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist


def main():
    pub = rospy.Publisher('my_diff_drive/cmd_vel', Twist, queue_size=10)
    rospy.init_node('circler', anonymous=True)

    rate = rospy.Rate(2) # 2hz
    msg = Twist()
    msg.linear.x = 10
    msg.angular.z = 0

    while not rospy.is_shutdown():
        msg.linear.x += .02
        pub.publish(msg)
        rate.sleep()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass