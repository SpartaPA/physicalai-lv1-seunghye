import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class DistanceMonitor(Node):
    def __init__(self):
        super().__init__('turtle_distance_monitor')

        # 파라미터 선언 (기본값: 2.5 m)
        # 안전선 그리기 원점에서 2.5미터보다 멀어지면 경고울리도록 기준선 잡음.
        self.declare_parameter('warn_distance', 0.8)

        #distance_publisher.py에서 /turtle_distance로 값을 넣어주면
        # distance_callback으로 실행함.
        self.sub_dist = self.create_subscription(
            Float32, '/turtle_distance',self.distance_callback,10
        )
        self.get_logger().info('Distance Monitor 노드가 시작되었습니다.')

    #현재 거리 확인하기
    def distance_callback(self, msg:Float32):
        warn_dist = self.get_parameter('warn_distance').get_parameter_value().double_value
        current_dist = msg.data

        #warn_dist - 기준선 2.5m
        if current_dist > warn_dist:
            self.get_logger().warn(
                f'경고: 원점 거리 한계 초과! 현재 거리: {current_dist:.2f} m (임계값: {warn_dist:.2f} m)'
            )

def main(args=None):
    rclpy.init(args=args)
    node = DistanceMonitor()
    try: 
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()