import math
import time

import rclpy
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

from turtlebot3_midterm_interfaces.action import Rotate


def quaternion_to_yaw(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def normalize_angle(angle):
    """Wrap an angle to the range [-pi, pi]."""
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


class RotateActionServer(Node):
    """
    Task C1: action server "rotate_action_server" using the custom
    Rotate.action interface. Rotates the robot in place by the
    requested angle using a simple proportional (P) controller,
    publishing feedback (remaining angle) at 10 Hz.
    """

    def __init__(self):
        super().__init__('rotate_action_server')
        self.cb_group = ReentrantCallbackGroup()

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_cb, 10, callback_group=self.cb_group
        )

        self.current_yaw = 0.0
        self.have_odom = False

        # --- P controller tuning ---
        # Kp = 1.0 was chosen empirically: it turns the robot briskly
        # without overshoot/oscillation on the TurtleBot3 Burger in
        # Gazebo. Explain in your report how you tuned this value.
        self.Kp = 2
        self.max_ang_vel = 1.0            # rad/s, TurtleBot3 Burger limit
        self.tolerance = math.radians(2.0)  # stop once within 2 degrees

        self._action_server = ActionServer(
            self,
            Rotate,
            'rotate',
            execute_callback=self.execute_callback,
            callback_group=self.cb_group,
        )
        self.get_logger().info('rotate_action_server ready.')

    def odom_cb(self, msg: Odometry):
        self.current_yaw = quaternion_to_yaw(msg.pose.pose.orientation)
        self.have_odom = True

    def execute_callback(self, goal_handle):
        angle = goal_handle.request.angle
        self.get_logger().info(f'Received goal: rotate {angle:.3f} rad')

        while rclpy.ok() and not self.have_odom:
            time.sleep(0.05)

        start_yaw = self.current_yaw
        target_yaw = normalize_angle(start_yaw + angle)

        feedback_msg = Rotate.Feedback()
        result = Rotate.Result()

        feedback_period = 0.1  # seconds -> 10 Hz, required by the exam
        last_feedback_time = time.time()

        while rclpy.ok():
            error = normalize_angle(target_yaw - self.current_yaw)

            if abs(error) <= self.tolerance:
                break

            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.stop_robot()
                result.success = False
                return result

            ang_vel = self.Kp * error
            ang_vel = max(-self.max_ang_vel, min(self.max_ang_vel, ang_vel))
            twist = Twist()
            twist.angular.z = ang_vel
            self.cmd_pub.publish(twist)

            now = time.time()
            if now - last_feedback_time >= feedback_period:
                feedback_msg.remaining_angle = error
                goal_handle.publish_feedback(feedback_msg)
                last_feedback_time = now

            time.sleep(0.02)

        self.stop_robot()
        goal_handle.succeed()
        result.success = True
        self.get_logger().info('Rotation goal succeeded.')
        return result

    def stop_robot(self):
        self.cmd_pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = RotateActionServer()
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
