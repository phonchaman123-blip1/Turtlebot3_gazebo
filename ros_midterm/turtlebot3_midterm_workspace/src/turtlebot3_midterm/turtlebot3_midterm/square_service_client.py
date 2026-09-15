import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty


class SquareServiceClient(Node):
    """
    Task B2: client node that calls the "draw_square" service
    provided by square_service_server.
    """

    def __init__(self):
        super().__init__('square_service_client')
        self.client = self.create_client(Empty, 'draw_square')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for "draw_square" service...')

    def call_service(self):
        request = Empty.Request()
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result()


def main(args=None):
    rclpy.init(args=args)
    node = SquareServiceClient()
    node.get_logger().info('Calling draw_square service...')
    node.call_service()
    node.get_logger().info('Square drawing complete.')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
