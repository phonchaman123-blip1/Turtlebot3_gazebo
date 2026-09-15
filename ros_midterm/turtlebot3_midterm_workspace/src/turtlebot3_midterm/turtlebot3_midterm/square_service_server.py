import math
import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_srvs.srv import Empty


def quaternion_to_yaw(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def angle_diff(a, b):
    """Smallest signed difference a-b, wrapped to [-pi, pi]."""
    d = a - b
    return math.atan2(math.sin(d), math.cos(d))


class SquareServiceServer(Node):
    """
    Task B1: service server "square_service_server" using
    std_srvs/srv/Empty. When called, drives the robot in a
    0.5 m per side square, then stops.

    Uses /odom feedback (distance travelled, yaw turned) rather
    than pure timing, so the square is accurate even if speeds vary.
    """

    def __init__(self):
        super().__init__('square_service_server')
        # A ReentrantCallbackGroup lets the odom subscription keep
        # updating self.current_x/y/yaw on its own executor thread
        # while the service callback below is busy running the square
        # sequence on another thread. This replaces the earlier design
        # that called rclpy.spin_once() *inside* handle_square() while
        # the node was already being spun by rclpy.spin() in main() --
        # that nested-spin pattern is fragile and can stall.
        self.cb_group = ReentrantCallbackGroup()

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_cb, 10, callback_group=self.cb_group
        )
        self.srv = self.create_service(
            Empty, 'draw_square', self.handle_square, callback_group=self.cb_group
        )

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.have_odom = False

        self.linear_speed = 0.2   # m/s
        self.angular_speed = 0.5  # rad/s
        self.side_length = 0.5    # m, required by the exam

        self.get_logger().info('square_service_server ready: call "draw_square"')

    def odom_cb(self, msg: Odometry):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.current_yaw = quaternion_to_yaw(msg.pose.pose.orientation)
        self.have_odom = True

    def _wait_for_odom(self):
        # odom_cb runs concurrently on its own executor thread (see
        # ReentrantCallbackGroup above), so we just wait -- no need to
        # spin this node ourselves from inside a service callback.
        while rclpy.ok() and not self.have_odom:
            time.sleep(0.05)

    def move_straight(self, distance):
        self._wait_for_odom()
        x0, y0 = self.current_x, self.current_y
        twist = Twist()
        twist.linear.x = self.linear_speed

        while rclpy.ok():
            self.cmd_pub.publish(twist)
            travelled = math.hypot(self.current_x - x0, self.current_y - y0)
            if travelled >= distance:
                break
            time.sleep(0.05)
        self.stop()

    def turn_angle(self, angle):
        """angle > 0 turns left (CCW), angle < 0 turns right (CW)."""
        self._wait_for_odom()
        yaw0 = self.current_yaw
        twist = Twist()
        twist.angular.z = self.angular_speed if angle > 0 else -self.angular_speed

        while rclpy.ok():
            self.cmd_pub.publish(twist)
            turned = abs(angle_diff(self.current_yaw, yaw0))
            if turned >= abs(angle):
                break
            time.sleep(0.05)
        self.stop()

    def stop(self):
        self.cmd_pub.publish(Twist())
        time.sleep(0.1)

    def handle_square(self, request, response):
        self.get_logger().info('Service called: drawing 0.5 m square...')
        for i in range(4):
            self.move_straight(self.side_length)
            self.turn_angle(math.pi / 2.0)  # 90 degrees
        self.stop()
        self.get_logger().info('Square finished, robot stopped.')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = SquareServiceServer()
    executor = MultiThreadedExecutor()
    try:
        rclpy.spin(node, executor=executor)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.cmd_pub.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
