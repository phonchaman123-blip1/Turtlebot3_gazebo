import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


def quaternion_to_yaw(q):
    """
    Convert a geometry_msgs/Quaternion into the yaw (heading) angle,
    in radians, using the standard quaternion-to-Euler formula
    (we only need yaw, so we skip roll/pitch).
    """
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class OdomLogger(Node):
    """
    Task A2: subscribes to /odom and prints the robot's x, y
    position and its yaw (heading) angle.
    """

    def __init__(self):
        super().__init__('odom_logger')
        self.subscription = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )

    def odom_callback(self, msg: Odometry):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        yaw = quaternion_to_yaw(msg.pose.pose.orientation)

        self.get_logger().info(
            f'x={x:.3f} m, y={y:.3f} m, '
            f'yaw={yaw:.3f} rad ({math.degrees(yaw):.1f} deg)'
        )


def main(args=None):
    rclpy.init(args=args)
    node = OdomLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
