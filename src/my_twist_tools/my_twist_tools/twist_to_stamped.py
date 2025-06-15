import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped

class TwistToStamped(Node):
    def __init__(self):
        super().__init__('twist_to_stamped')
        self.sub = self.create_subscription(Twist, '/cmd_vel_nav', self.callback, 10)
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)

    def callback(self, msg):
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.header.frame_id = 'base_link'
        scale = 10.0
        stamped.twist.linear.x = msg.linear.x * scale
        stamped.twist.linear.y = msg.linear.y * scale
        stamped.twist.linear.z = msg.linear.z * scale
        stamped.twist.angular.x = msg.angular.x * scale
        stamped.twist.angular.y = msg.angular.y * scale
        stamped.twist.angular.z = msg.angular.z * scale
        self.pub.publish(stamped)


def main(args=None):
    rclpy.init(args=args)
    node = TwistToStamped()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()