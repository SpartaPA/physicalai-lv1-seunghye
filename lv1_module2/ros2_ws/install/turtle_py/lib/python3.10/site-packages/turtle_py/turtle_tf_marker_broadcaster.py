import math
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import TransformStamped
from visualization_msgs.msg import Marker, MarkerArray
from tf2_ros import TransformBroadcaster

# /turtle1/pose를 받아 world -> turtle1 TF를 브로드캐스팅하고, 경유점을 RViz2용 Marker로 내보내는 노드
class TurtleTfMarkerBroadcaster(Node):
    def __init__(self):
        super().__init__('turtle_tf_marker_broadcaster')

        # 1. TF 브로드캐스터 생성 (world -> turtle1 변환 발행용)
        self.tf_broadcaster = TransformBroadcaster(self)

        # 2. RViz2 시각화용 마커 발행자 생성
        self.marker_pub = self.create_publisher(MarkerArray, '/waypoint_markers', 10)

        # 3. /turtle1/pose 구독
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        # 경유점 예시 목록 (x, y)
        self.waypoints = [(2.0, 2.0), (5.0, 8.0), (8.0, 2.0)]

        # 1초 주기로 마커 발행 타이머
        self.create_timer(1.0, self.publish_markers)
        self.get_logger().info('TF Broadcaster & Marker Publisher 노드가 시작되었습니다.')

    def pose_callback(self, msg: Pose):
        # TransformStamped 메시지 생성
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'      # 기준 좌표계
        t.child_frame_id = 'turtle1'     # 대상 좌표계

        # 위치 (x, y, z)
        t.transform.translation.x = msg.x
        t.transform.translation.y = msg.y
        t.transform.translation.z = 0.0

        # 회전 (Euler angle -> Quaternion 변환: Yaw = theta)
        # 2D 평면 회전만 다루므로 z축 회전 sin, cos 이용
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(msg.theta / 2.0)
        t.transform.rotation.w = math.cos(msg.theta / 2.0)

        # TF 변환 정보 브로드캐스팅
        self.tf_broadcaster.sendTransform(t)

    def publish_markers(self):
        marker_array = MarkerArray()
        for i, (wx, wy) in enumerate(self.waypoints):
            marker = Marker()
            marker.header.frame_id = 'world'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'waypoints'
            marker.id = i
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = wx
            marker.pose.position.y = wy
            marker.pose.position.z = 0.0
            marker.scale.x = 0.4
            marker.scale.y = 0.4
            marker.scale.z = 0.4
            marker.color.a = 1.0  # 투명도 (1.0 = 불투명)
            marker.color.r = 1.0  # 빨간색 마커
            marker.color.g = 0.2
            marker.color.b = 0.2
            marker_array.markers.append(marker)

        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    node = TurtleTfMarkerBroadcaster()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()    
