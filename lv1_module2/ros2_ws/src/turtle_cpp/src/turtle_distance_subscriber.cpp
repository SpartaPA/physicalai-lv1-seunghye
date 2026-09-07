#include <memory>            // std::shared_ptr 스마트 포인터용 헤더
#include "rclcpp/rclcpp.hpp" // ROS2 C++ 시스템 헤더
#include "std_msgs/msg/float32.hpp" //수신할 Float32 메시지 타입 헤더

///turtle_distance 토픽을 수신하여 로그로 출력하는 노드

// rclcpp::Node를 상속받는 구독자 클래스 정의
class TurtleDistanceSubscriber : public rclcpp::Node
{
public:
    //생성자: 노드 이름을 "turtle_distance_subscriber"로 설정
    TurtleDistanceSubscriber()
    :Node("turtle_distance_subscriber")
    {
        // /turtle_distance 토픽을 구독하고 메시지 수신 시 distance_callback 호출 지정
        distance_subscriber_ = this->create_subscription<std_msgs::msg::Float32>(
            "/turtle_distance",
            10,
            std::bind(&TurtleDistanceSubscriber::distance_callback, this, std::placeholders::_1)
        );

        RCLCPP_INFO(this->get_logger(), "Turtle Distance Subscriber 노드가 시작되었습니다.");
    }

private:
    // 메시지를 수신했을 때 호출되는 콜백 함수
    void distance_callback(const std_msgs::msg::Float32::SharedPtr msg) const
    {
        // 수신한 float32 메시지의 data 값을 로그로 출력
        RCLCPP_INFO(this->get_logger(), "수신된 거북이 이동 거리: %.2f m", msg->data);
    }

    // 구독자 스마트 포인터 멤버 변수
    rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr distance_subscriber_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc,argv);// ROS2 C++ 시스템 초기화
    // 구독자 노드 실행 및 메시지 대기
    rclcpp::spin(std::make_shared<TurtleDistanceSubscriber>());
    rclcpp::shutdown();       // 노드 종료
    return 0;
}