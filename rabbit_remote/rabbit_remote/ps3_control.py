import rclpy

from rclpy.node import Node
from std_msgs.msg import Bool, Int8
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

from rabbit_remote.rabbit_omni import RabbitModel


class PS3Remote(Node):

    def __init__(self):

        super().__init__('PS4_Node')

        self.rabbit_model = RabbitModel()

        self.subscribe_joy = self.create_subscription(
            Joy, "joy", self.subscribe_callback, 10
        )

        self.publisher_twist = self.create_publisher(
            Twist, "cmd_vel", 10
        )

        self.shooter_cmd = self.create_publisher(Int8, 'shooter_command', 10)
        
        self.twist_callback = self.create_timer(
            1/120, self.twist_teleop
        )

        self.axes_list = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.button_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.coef_vx = 0.0
        self.coef_vy = 0.0
        self.coef_vth = 0.0

        self.a = 0.0
        self.b = 0.0
        self.c = 0.0


    def subscribe_callback(self, joy):
        
        shooter_msg = Int8()

        self.axes_list = joy.axes
        self.button_list = joy.buttons

        if self.button_list[11] == 1:
            shooter_msg.data = 1
            self.shooter_cmd.publish(shooter_msg)

        else:
            shooter_msg.data = 0
            self.shooter_cmd.publish(shooter_msg)

    def twist_teleop(self):
        twist_msg = Twist()

        self.coef_vx = -self.axes_list[1]
        self.coef_vy = -self.axes_list[2]
        if self.axes_list[4] > 0 :
            self.coef_vth = self.axes_list[4]
        elif self.axes_list[5] > 0:
            self.coef_vth = -self.axes_list[5]
        # if (self.axes_list[4] > 0) and (self.axes_list[5] == 0):
        #     self.coef_vth = self.axes_list[4]
        # if (self.axes_list[4] == 0) and (self.axes_list[5] > 0):
        #     self.coef_vth = -self.axes_list[5]
        else:
            self.coef_vth = 0.0

        # self.coef_vx = self.axes_list[0]
        # self.coef_vy = self.axes_list[1]
        # self.coef_vth = self.axes_list[2]

        if self.button_list[1] == 1:
            self.a += 0.01
            self.b += 0.01
            self.c += 0.01
        elif self.button_list[3] == 1:
            self.a -= 0.01
            self.b -= 0.01
            self.c -= 0.01

        elif self.button_list[2] == 1:
            self.coef_vx = 0.0
            self.coef_vy = 0.0
            self.coef_vth = 0.0
            self.a = 0.0
            self.b = 0.0
            self.c = 0.0

        twist_msg.linear.x = self.coef_vx*self.a
        twist_msg.linear.y = self.coef_vy*self.b
        twist_msg.angular.z = self.coef_vth*self.c

        self.publisher_twist.publish(twist_msg)


    



def main(args=None):

    rclpy.init(args=args)

    node = PS3Remote()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()

if __name__ == "__main__":
    main()

