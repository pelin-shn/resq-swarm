## 🚁 ResQ-SWARM (Search and Rescue Drone Swarm)

A simulation-based project focused on autonomous UAV communication, swarm coordination, and dynamic response in Search-and-Rescue (SAR) operations.

## 🏗️ System Architecture

* The system features a fully decentralized architecture that operates without a central controller.
* Drones communicate via ROS topics for continuous data broadcasting, such as position and energy levels.
* ROS services are utilized for request-response interactions, including task assignments and confirmations.
* Core software components include a Communication Manager, Task Management Component, and Swarm Coordination Component.

## ✨ Key Capabilities & Simulation Results

* **Fault Tolerance:** During failure recovery tests, if a drone becomes inactive, the system successfully reassigns unfinished tasks to available active drones.
* **Environment Detection:** The Gazebo simulation supports basic object scanning and real-time coordinate monitoring.
* **Task Distribution:** Preliminary tests proved that tasks are distributed correctly among drones under normal operating conditions.
* **Flight Stack Integration:** The system uses Ardupilot SITL for virtual flight control and QGroundControl for real-time telemetry monitoring.
