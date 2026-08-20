cmake_minimum_required(VERSION 3.0.2)
project(multi_drone_controller)

find_package(catkin REQUIRED COMPONENTS
  rospy
  geometry_msgs
  sensor_msgs
  mavros_msgs
  std_msgs
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/drone_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
