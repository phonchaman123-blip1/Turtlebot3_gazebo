import math
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from turtlebot3_midterm_interfaces.action import Rotate


class RotateActionClient(Node):
    """
    Task C2: client node "rotate_action_client" that sends a goal
    angle to rotate_action_server, prints feedback (remaining angle)
    as it arrives, and prints the final result.
    """

    def __init__(self):
        super().__init__('rotate_action_client')
        self._action_client = ActionClient(self, Rotate, 'rotate')

    def send_goal(self, angle):
        self._action_client.wait_for_server()
        goal_msg = Rotate.Goal()
        goal_msg.angle = angle

        self.get_logger().info(
            f'Sending goal: rotate {angle:.3f} rad ({math.degrees(angle):.1f} deg)'
        )
        send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return
        self.get_logger().info('Goal accepted')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        remaining = feedback_msg.feedback.remaining_angle
        self.get_logger().info(
            f'Feedback: remaining angle = {math.degrees(remaining):.1f} deg'
        )

    def get_result_callback(self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info('Goal reached successfully')
        else:
            self.get_logger().info('Goal aborted')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    # default goal: +180 degrees (pi radians); override with a CLI arg, e.g.:
    #   ros2 run turtlebot3_midterm rotate_action_client 1.57
    angle = math.pi
    if len(sys.argv) > 1:
        angle = float(sys.argv[1])

    node = RotateActionClient()
    node.send_goal(angle)
    rclpy.spin(node)


if __name__ == '__main__':
    main()
