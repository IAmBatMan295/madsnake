cmake_minimum_required(VERSION 3.16)

project(MadSnake C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(NCURSESW REQUIRED ncursesw)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

add_executable(madsnake src/madsnake.c)

target_compile_options(madsnake PRIVATE -Wall -Wextra -Wpedantic -O2)
target_include_directories(madsnake PRIVATE ${NCURSESW_INCLUDE_DIRS})
target_link_libraries(madsnake PRIVATE ${NCURSESW_LIBRARIES} m)
