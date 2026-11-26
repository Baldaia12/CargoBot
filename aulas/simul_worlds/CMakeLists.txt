cmake_minimum_required(VERSION 3.8)
project(simul_worlds)
find_package(ament_cmake REQUIRED)
# Subconjunto de recursos da Aula 2 necessário ao edifício em Gazebo.
install(DIRECTORY launch config gazebo_worlds models DESTINATION share/${PROJECT_NAME})
ament_package()
