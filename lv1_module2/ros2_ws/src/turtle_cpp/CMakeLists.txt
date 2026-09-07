cmake_minimum_required(VERSION 3.8)
project(turtle_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies 의존성 패키지 검색
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(turtlesim REQUIRED)

# 1. 거리 발행 노드 실행 파일 생성 및 빌드 설정
add_executable(turtle_distance_publisher src/turtle_distance_publisher.cpp)
ament_target_dependencies(turtle_distance_publisher rclcpp std_msgs turtlesim)

# 2. 거리 구독 노드 실행 파일 생성 및 빌드 설정
add_executable(turtle_distance_subscriber src/turtle_distance_subscriber.cpp)
ament_target_dependencies(turtle_distance_subscriber rclcpp std_msgs)

# 3. ros2 run 사용을 위한 설치(Install) 타겟 지정
install(TARGETS
  turtle_distance_publisher
  turtle_distance_subscriber
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
