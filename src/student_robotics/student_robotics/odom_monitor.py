import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class OdomMonitor(Node):
    def __init__(self):
        super().__init__('odom_monitor')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        self.get_logger().info('OdomMonitor node started')

    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        lin_x = msg.twist.twist.linear.x
        ang_z = msg.twist.twist.angular.z
        self.get_logger().info(
            f'Position: x={x:.3f}, y={y:.3f} | '
            f'Vel: linear.x={lin_x:.3f}, angular.z={ang_z:.3f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = OdomMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()