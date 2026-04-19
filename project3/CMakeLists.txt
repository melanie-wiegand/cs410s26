# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(proj3)

set(CMAKE_CXX_STANDARD 17)

find_package(VTK REQUIRED)

add_executable(proj3 proj3.cxx)
target_link_libraries(proj3 PRIVATE ${VTK_LIBRARIES})
vtk_module_autoinit(
  TARGETS proj3
  MODULES ${VTK_LIBRARIES}
)
configure_file(${CMAKE_SOURCE_DIR}/noise.vtk ${CMAKE_BINARY_DIR}/noise.vtk COPYONLY)
