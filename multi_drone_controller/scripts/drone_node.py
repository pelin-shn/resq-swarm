#!/usr/bin/env python3

import rospy
import math
from mavros_msgs.msg import State, BatteryStatus
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String

class DroneController:
    active_drones = [1, 2, 3]

    def __init__(self):
        self.drone_id = rospy.get_param("~drone_id", 1)
        self.state = State()
        self.battery = 100.0 if self.drone_id != 2 else 50.0
        self.target_found = False

        # Tarama alanı parametreleri
        self.zone_xmin = None
        self.zone_xmax = None
        self.zone_ymin = 0
        self.zone_ymax = 10
        self.current_x = 0
        self.current_y = 0
        self.step = 2.0
        self.altitude = 5.0

        # Başlangıç noktası (şarj ünitesi)
        self.start_x = 0
        self.start_y = 0

        # ROS Subscribers
        rospy.Subscriber("/drone_%d/mavros/state" % self.drone_id, State, self.state_callback)
        rospy.Subscriber("/drone_%d/mavros/battery" % self.drone_id, BatteryStatus, self.battery_callback)
        rospy.Subscriber("/drones/p2p_comm", String, self.p2p_callback)

        # ROS Publishers
        self.pose_pub = rospy.Publisher("/drone_%d/mavros/setpoint_position/local" % self.drone_id, PoseStamped, queue_size=10)
        self.p2p_pub = rospy.Publisher("/drones/p2p_comm", String, queue_size=10)

        # Alanı yükle
        self.load_mission()
        rospy.loginfo("Drone %d aktif, tarama alanı: %.1f -> %.1f" % (self.drone_id, self.zone_xmin, self.zone_xmax))

    def load_mission(self):
        xmin = rospy.get_param("/search_area/xmin", 0)
        xmax = rospy.get_param("/search_area/xmax", 30)
        total = xmax - xmin
        share = total / len(DroneController.active_drones)
        idx = DroneController.active_drones.index(self.drone_id)
        self.zone_xmin = xmin + idx * share
        self.zone_xmax = self.zone_xmin + share
        self.current_x = self.zone_xmin
        self.current_y = self.zone_ymin
        self.start_x = self.current_x
        self.start_y = self.current_y

    def state_callback(self, msg):
        self.state = msg

    def battery_callback(self, msg):
        self.battery = msg.remaining * 100
        if self.battery < 20.0:
            self.broadcast_message("BATTERY_LOW:{}".format(self.drone_id))
            if self.drone_id in DroneController.active_drones:
                DroneController.active_drones.remove(self.drone_id)
                rospy.logwarn("Drone %d şarj bitti, alan devredildi!" % self.drone_id)
                self.current_x = self.start_x
                self.current_y = self.start_y

    def p2p_callback(self, msg):
        data = msg.data.split(':')
        msg_type = data[0]
        sender_id = int(data[1])
        if sender_id == self.drone_id:
            return
        if msg_type == "BATTERY_LOW":
            rospy.logwarn("Drone %d alan devralıyor!" % sender_id)
        elif msg_type == "TARGET_FOUND":
            rospy.loginfo("Drone %d insan buldu!" % sender_id)
            self.target_found = True

    def broadcast_message(self, message):
        self.p2p_pub.publish(message)

    def move(self):
        self.current_x += self.step
        if self.current_x > self.zone_xmax or self.current_x < self.zone_xmin:
            self.step *= -1
            self.current_y += 1.0
            if self.current_y > self.zone_ymax:
                self.current_y = self.zone_ymin

    def send_pose(self):
        pose = PoseStamped()
        pose.header.stamp = rospy.Time.now()
        pose.pose.position.x = self.current_x
        pose.pose.position.y = self.current_y
        pose.pose.position.z = self.altitude
        pose.pose.orientation.w = 1.0
        self.pose_pub.publish(pose)

    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            if self.battery < 20.0:
                self.current_x = self.start_x
                self.current_y = self.start_y
            else:
                self.move()
            self.send_pose()
            rate.sleep()


if __name__ == "__main__":
    rospy.init_node('drone_controller', anonymous=True)
    controller = DroneController()
    controller.run()
