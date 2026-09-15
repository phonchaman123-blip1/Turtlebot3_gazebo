cmake_minimum_required(VERSION 3.8)
project(turtlebot3_midterm_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Rotate.action"
)

ament_package()
