#include <memory>       // std::shared_ptr 관리를 위한 스마트 포인터 헤더
#include <cmath>        // sqrt(), pow() 등 수학 계산 함수 사용을 위한 헤더
#include "rclcpp/rclcpp.hpp"              // ROS2 C++ 클라이언트 라이브러리 메인 헤더
#include "turtlesim/msg/pose.hpp"         // turtlesim의 Pose 메시지 타입 헤더
#include "std_msgs/msg/float32.hpp"       // 32비트 부동소수점 Float32 메시지 타입 헤더

//turtlesim의 위치 정보를 받아 거리를 계산하고 /turtle_distance 토픽으로 발행하는 노드

// rclcpp::Node를 상속받아 TurtleDistancePublisher 클래스를 정의합니다.
class TurtleDistancePublisher : public rclcpp::Node
{
public:
    // 생성자: 노드 이름을 "turtle_distance_publisher"로 설정합니다.
    TurtleDistancePublisher()
    : Node("turtle_distance_publisher"), is_first_pose_(true), last_x_(0.0), last_y_(0.0), total_distance_(0.0)
    {
        // 1. 구독자 생성: /turtle1/pose 토픽을 구독하며 10개까지 버퍼링, pose_callback 함수 지정
        pose_subscriber_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose",
            10,
            std::bind(&TurtleDistancePublisher::pose_callback, this, std::placeholders::_1)
        );

        // 2. 발행자 생성: /turtle_distance 토픽으로 Float32 메시지를 발행하며 10개까지 버퍼링
        distance_publisher_ = this->create_publisher<std_msgs::msg::Float32>(
            "/turtle_distance",
            10
        );

        // 3. 타이머 생성: 100ms(10Hz) 마다 timer_callback 함수를 실행
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&TurtleDistancePublisher::timer_callback, this)
        );

        RCLCPP_INFO(this->get_logger(), "Turtle Distance Publisher 노드가 시작되었습니다.");
    }

private:
    // Pose 토픽이 수신될 때마다 호출되는 콜백 함수
    void pose_callback(const turtlesim::msg::Pose::SharedPtr msg)
    {
        if (is_first_pose_) {
            // 첫 위치를 받으면 기준점으로 저장만 하고 이동 거리 계산은 건너뜁니다.
            last_x_ = msg->x;
            last_y_ = msg->y;
            is_first_pose_ = false;
            return;
        }

        // 이전 위치와 현재 위치 사이의 유클리드 거리(피타고라스 정리) 계산
        double dx = msg->x - last_x_;
        double dy = msg->y - last_y_;
        double distance = std::sqrt(dx * dx + dy * dy);

        // 누적 이동 거리 갱신
        total_distance_ += distance;

        // 현재 위치를 다음 계산을 위한 이전 위치로 저장
        last_x_ = msg->x;
        last_y_ = msg->y;
    }

    // 타이머 주기(10Hz)마다 호출되어 이동 거리를 발행하는 콜백 함수
    void timer_callback()
    {
        auto message = std_msgs::msg::Float32(); // 발행할 메시지 객체 생성
        message.data = total_distance_;           // 누적 이동 거리 데이터 할당

        // 토픽 발행 및 터미널 로그 출력
        distance_publisher_->publish(message);
        RCLCPP_INFO(this->get_logger(), "발행 중인 누적 거리: %.2f m", message.data);
    }

    // 멤버 변수 선언
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr pose_subscriber_;  // 구독자 객체
    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr distance_publisher_;// 발행자 객체
    rclcpp::TimerBase::SharedPtr timer_;                                     // 타이머 객체
    
    bool is_first_pose_;   // 첫 수신 여부 플래그
    double last_x_;        // 이전 x 좌표
    double last_y_;        // 이전 y 좌표
    float total_distance_; // 총 누적 이동 거리
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv); // ROS2 C++ 시스템 초기화
    // 노드를 생성하고 이벤트를 처리하도록 spin(대기) 상태로 전환
    rclcpp::spin(std::make_shared<TurtleDistancePublisher>());
    rclcpp::shutdown();       // 노드 종료 및 자원 해제
    return 0;
}