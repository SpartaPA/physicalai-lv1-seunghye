cmake_minimum_required(VERSION 3.10)
project(cpp_basics)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

#모든 빌드 대상에 g++ -Wall 경고 옵션 자동 적용
add_compile_options(-Wall -Wextra)

#1. 단일 파일 프로그램 빌드 설정
add_executable(stop_distance stop_distance.cpp)

#2. 다중 파일 프로그램 빌드 설정(main과 motor을 함께 묶음)
add_executable(motor_app main.cpp motor.cpp)

#sensors 파일 빌드 설정 :: 경로가 sensors/ 폴더 안에 있어서.
add_executable(sensors sensors/sensors.cpp)

# (선택 사항) sensors 실행 파일에 메모리 누수 검출기(ASan) 적용하고 싶을 때 주석 해제
# target_compile_options(sensors PRIVATE -fsanitize=address)
# target_link_options(sensors PRIVATE -fsanitize=address)