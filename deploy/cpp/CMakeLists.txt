cmake_minimum_required(VERSION 3.18)
project(uavrm_infer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Point CMAKE_PREFIX_PATH at your LibTorch unzip dir, e.g.:
#   cmake -DCMAKE_PREFIX_PATH="/opt/libtorch" ..
find_package(Torch REQUIRED)
find_package(OpenCV REQUIRED)

add_executable(uavrm_infer src/infer.cpp)
target_link_libraries(uavrm_infer "${TORCH_LIBRARIES}" "${OpenCV_LIBS}")
target_include_directories(uavrm_infer PRIVATE "${OpenCV_INCLUDE_DIRS}")
set_property(TARGET uavrm_infer PROPERTY CXX_STANDARD 17)

if (MSVC)
  file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
  add_custom_command(TARGET uavrm_infer POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${TORCH_DLLS} $<TARGET_FILE_DIR:uavrm_infer>)
endif()
