import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CirclePublisher(Node):
    """
    Task A1: publishes Twist commands so the TurtleBot3 drives
    continuously in a circle of radius ~0.5 m.

    For a circle: angular_speed = linear_speed / radius
    """

    def __init__(self):
        super().__init__('circle_publisher')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        self.linear_speed = 0.2   # m/s
        self.radius = 0.5         # m  (required by the exam)
        self.angular_speed = self.linear_speed / self.radius  # rad/s

        timer_period = 0.1  # seconds -> 10 Hz publish rate
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.get_logger().info(
            f'circle_publisher started: v={self.linear_speed} m/s, '
            f'r={self.radius} m, w={self.angular_speed:.3f} rad/s'
        )

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = self.linear_speed
        msg.angular.z = self.angular_speed
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CirclePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # stop the robot cleanly on shutdown (Ctrl+C).
        # rclpy's own SIGINT handler may already have shut the context
        # down by the time we get here, so publishing/destroying without
        # checking rclpy.ok() first raises "publisher's context is
        # invalid". Guard every context-dependent call.
        if rclpy.ok():
            node.publisher_.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
