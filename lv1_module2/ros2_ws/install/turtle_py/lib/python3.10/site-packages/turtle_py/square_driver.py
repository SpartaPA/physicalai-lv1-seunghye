import rclpy
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SquareDriver(Node):
    def __init__(self):
        super().__init__('turtle_square_driver')
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel' ,10)
        self.timer = self.create_timer(0.1, self.timer_callback)

        self.state = 'FORWARD'
        self.step_counter = 0
        self.side_count = 0
        self.get_logger().info('Square Driver 노드가 시작되었습니다.')

    def timer_callback(self):
        msg = Twist()
        if self.side_count >= 4:
            self.cmd_pub.publish(Twist()) # 정지
            return

        #(직진 모드)
        if self.state == 'FORWARD':
            msg.linear.x = 2.0          # 앞으로 가는 속도 (액셀 밟기)
            msg.angular.z = 0.0         # 회전 속도 0 (핸들 똑바로)
            self.step_counter += 1
            if self.step_counter >= 20:  # 0.1초 x 20번 = 2초
                self.state = 'TURN'      # 2초 갔으면 회전 모드로 스위치 변경!
                self.step_counter = 0
        #(회전 모드)
        elif self.state == 'TURN':
            msg.linear.x = 0.0       # 앞속도 0 (브레이크!)     
            msg.angular.z = 1.5708   #np.cos(np.deg2rad(90))# 회전속도:1초간 약 90도 회전
            self.step_counter += 1
            if self.step_counter >= 10: # 0.1초 x 10번 = 1초
                self.state = 'FORWARD'  # 90도 돌았으면 다시 직진 모드로!
                self.step_counter = 0   
                self.side_count += 1    # 변 하나 완성! (변 카운트 +1)

        # 백스페이스로 4칸 당겨서 if/elif 문과 세로줄 위치를 맞춰야
        # 직진할 때도, 회전할 때도 명령 편지가 정상 발송됩니다!
        self.cmd_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SquareDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('KeyboardInterrupt 수신. 노드를 안전하게 종료합니다.')
    finally:
        # 1. 주행 중 Ctrl+C가 눌렸을 때 타이머를 즉시 멈춰 publish 중단
        node.timer.cancel()
        node.destroy_node()
        # 2. 안전하게 노드 파괴 및 셧다운 (에러 무시)
        #try:
        #    node.destroy_node()
        #    if rclpy.ok():
        #        rclpy.shutdown()
        #except Exception:
        #    pass

if __name__ == '__main__':
    main()