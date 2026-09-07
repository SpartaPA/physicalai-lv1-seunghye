import math
import rclpy   #ROS 2 로봇 세상과 대화하기 위한 필수 도구 상자
from rclpy.node import Node  #로봇 일을 처리할 '일꾼(노드)'을 만드는 기본 틀
from turtlesim.msg import Pose #거북이가 보내는 "x, y 좌표 위치 편지" 양식
from std_msgs.msg import Float32 #소수점 숫자를 담아서 보낼 "숫자 전용 편지 봉투"

class DistancePublisher(Node):
    def __init__(self):
        super().__init__('turtle_distance_publisher')

        # 파라미터 선언(기본값 10.0 Hz)
        #"declare_parameter(...) 1초에 몇 번 말할까?" 조절 스위치를 만들고 기본값을 10.0(10번)으로 설정
        self.declare_parameter('publish_rate', 10.0)
        rate = self.get_parameter('publish_rate').get_parameter_value().double_value

        #거북이의 최신 위치를 적어둘 비어있는 메모장을 하나 준비
        self.latest_pose = None

        # /turtle1/pose 구독자 생성
        # pose_callback행동을 하라고 지시
        self.sub_pose = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )

        # /turtle_distance 발행자 생성
        #계산한 거리를 /turtle_distance 로 보낼 준비
        self.pub_dist = self.create_publisher(Float32, '/turtle_distance', 10)

        # 타이머 설정 (구독 콜백과 분리)
        #1초에 10번씩 째깍거리는 알람 시계를 켜고, 시계가 울릴 때마다 timer_callback 행동을 하게 함.
        timer_period = 1.0 / rate if rate > 0 else 0.1
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info(f'Distance Publisher 노드가 시작되었습니다. (주기: {rate} Hz)')

    #위치 편지(X, Y 좌표)를 보내오면, 계산은 하지 않고 메모장에 위치만 쏙 받아 적어둠.
    def pose_callback(self, msg: Pose):
        # 최신 자세 데이터 수신 및 보관만 수행
        self.latest_pose = msg

    def timer_callback(self):
        if self.latest_pose is None:
            return

        # 원점(0,0)과의 거리 계산: sqrt(x^2 + y^2)
        dist = math.sqrt(self.latest_pose.x ** 2 + self.latest_pose.y ** 2)

        msg = Float32()
        #계산한 거리 담기
        msg.data = float(dist)
        #담아 둔 계산거리를 발행
        self.pub_dist.publish(msg)

def main(args=None):
    rclpy.init(args=args)       # 1. ROS2 세상 시동 걸기
    node = DistancePublisher()  # 2. 거리 계산 일꾼 생성하기

    try:
        rclpy.spin(node)        # 3. 멈추라고 할 때까지 계속 일해라!
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()     # 4. 일꾼 퇴근시키기
        rclpy.shutdown()        # 5. ROS2 세상 끄기

if __name__ == '__main__':
    main()
