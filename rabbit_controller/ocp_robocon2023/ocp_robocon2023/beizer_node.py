import rclpy
import numpy as np

from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from sensor_msgs.msg import Imu
from .library.bezier_path import calc_bezier_path, calc_4points_bezier_path
from tf_transformations import euler_from_quaternion


class TrajectoryGenerator(Node):

    def __init__(self):

        super().__init__('beizer_node')

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0

        self.n_points = 200

        self.current_states = np.array([self.current_x, self.current_y, self.current_yaw])
        self.startX = [self.current_x, self.current_y, self.current_yaw]

        self.goal_x = 0.0
        self.goal_y = 0.0
        self.goal_yaw = 0.0

        self.endX = [self.goal_x, self.goal_y, self.goal_yaw]

        self.path = np.zeros((self.n_points, 2))
        self.offset = 20.0

        self.goal_states = np.zeros((3, self.n_points))

        self.path_x = np.zeros((self.n_points, 1))
        self.path_y = np.zeros((self.n_points, 1))
        self.path_yaw = np.zeros((self.n_points, 1))

        self.index = 0

        self.odom_subscriber = self.create_subscription(Float32MultiArray, 'state_est', self.odom_callback, 10)
        self.imu_subscriber = self.create_subscription(Imu, 'imu/data2', self.imu_callback, 10)
        self.goal_subscriber = self.create_subscription(Float32MultiArray, 'path_gen', self.goal_callback, 10)

        self.path_publisher = self.create_publisher(Float32MultiArray, 'beizer_path', 10)

        self.path_timer = self.create_timer(1/20, self.path_callback)


    def calc_planner(self, start_X, end_X, n_points, offset):
        dist = np.hypot(start_X[0] - end_X[0], start_X[1]-end_X[1]) / offset
        control_points =  np.array([
            [start_X[0], start_X[1]],
            [start_X[0] + dist * np.cos(start_X[2]), start_X[1] + dist * np.sin(start_X[2])],
            [end_X[0] - dist * np.cos(end_X[2]), end_X[1] - dist * np.sin(end_X[2])],
            [end_X[0], end_X[1]]
        ])

        path = calc_bezier_path(control_points, n_points)

        return path, control_points


    def odom_callback(self, odom_msg):
        self.current_x = odom_msg.data[0]
        self.current_y = odom_msg.data[1]

        self.current_states = np.array([
            self.current_x,
            self.current_y,
            self.current_yaw
        ])

    
    def imu_callback(self, quat_msg):
        q1 = quat_msg.orientation.x
        q2 = quat_msg.orientation.y
        q3 = quat_msg.orientation.z
        q4 = quat_msg.orientation.w

        orient_list = [q1, q2, q3, q4]

        roll, pitch, yaw = euler_from_quaternion(orient_list)

        self.current_yaw = yaw

        self.current_states = np.array([
            self.current_x,
            self.current_y,
            self.current_yaw
        ])

        self.startX = [self.current_x, self.current_y, self.current_yaw]

    def goal_callback(self, goal_msg):
        self.goal_x = goal_msg.data[0]
        self.goal_y = goal_msg.data[1]
        self.goal_yaw = goal_msg.data[2]

        self.endX = [self.goal_x, self.goal_y, self.goal_yaw]


        self.path, _ = self.calc_planner(
             self.startX, self.endX, self.n_points, self.offset
        )

        #self.path, _ = calc_4points_bezier_path(
        #    self.current_x, self.current_y, self.current_yaw,
        #    self.goal_x, self.goal_y, self.goal_yaw, self.offset
        #)

        self.path_x = self.path[:, 0]
        self.path_y = self.path[:, 1]
        self.path_yaw = np.append(np.arctan2(np.diff(self.path_y), np.diff((self.path_x))), self.goal_yaw)

        self.goal_states = np.vstack([self.path_x, self.path_y, self.path_yaw])

        # print(self.goal_states[:, 2])
    
    def path_callback(self):
        path_msg = Float32MultiArray()

        if np.linalg.norm(self.current_states-self.goal_states[:, -1], 2) > 0.2:
            self.index += 4
            if self.index >= self.n_points:
                self.index = self.n_points - 1
        if np.linalg.norm(self.current_states-self.goal_states[:, -1], 2) < 0.001:
            self.index = 0 

        # if self.index >= self.n_points:
        #     self.index = self.n_points - 1

        path_msg.data = [float(self.path_x[self.index]), float(self.path_y[self.index]), float(self.path_yaw[self.index])]
        self.path_publisher.publish(path_msg)

        # self.index += 1
        print(self.index)



def main(args=None):
    rclpy.init(args=args)

    node = TrajectoryGenerator()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()

if __name__== "__main__":
    main()