import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from std_msgs.msg import Header
from geometry_msgs.msg import PoseWithCovarianceStamped

import gtsam
from gtsam.symbol_shorthand import X, V, B
from gtsam import PriorFactorPose3, BetweenFactorPose3, Pose3, Rot3, Point3, noiseModel
from gtsam import PreintegratedImuMeasurements, PreintegrationParams

import numpy as np
class GtsamExampleNode(Node):

    def __init__(self):
        super().__init__('gtsam_fusion_node')
        # TOPICS
        self.imu_sub = self.create_subscription(Imu, '/imu/data', self.imu_callback, 10)
        self.odom_wheels_sub = self.create_subscription(Odometry, '/odometry/wheels', self.odom_wheels_callback, 10)
        self.odom_vo_sub = self.create_subscription(Odometry, '/vo_odom', self.odom2_callback, 10)

        self.fused_odom_pub = self.create_publisher(Odometry, '/fused/odom', 10)

        # Pos Guess
        self.initial_pose_sub_ = self.create_subscription(PoseWithCovarianceStamped, '/initialpose', self.initial_pose_callback, 10)  # Get initial pose from user's guess
        self.got_initial_pose = False

        # GTSAM
        self.graph_ = None
        self.initial_estimate_ = None

        self.prev_pose_ = Pose3()  # Previous pose
        self.prev_velocity_ = Point3()  # Previous velocity 
        self.prev_bias_ = gtsam.imuBias.ConstantBias()

        self.prev_time_ = self.get_clock().now()
        self.pim = None
        self.is_pim_set = False
        self.last_imu_time = 0.000

        self.keyframe_index = 1
    
    def Vector3(self, x, y, z):
        return np.array([x, y, z])
    
    def initial_pose_callback(self, msg):
        self.got_initial_pose = False

        self.graph_ = gtsam.NonlinearFactorGraph()  # Reset the graph

        prior_noise = noiseModel.Diagonal.Sigmas([0.1] * 6)  # Prior noise for initial position

        self.graph_.add(PriorFactorPose3(X(0), Pose3(), prior_noise))  # Add prior factor to the graph

        self.initial_estimate_ = gtsam.Values()  # Reset Initial state

        self.initial_estimate_.insert(X(0), self.prev_pose_)
        self.initial_estimate_.insert(V(0), self.prev_velocity_)
        self.initial_estimate_.insert(B(0), self.prev_bias_)

        self.get_logger().info(f"X, V i B dodane do {0}")
        self.get_logger().info(f"previous pose: {self.prev_pose_}, previous velocity: {self.prev_velocity_}, previous bias: {self.prev_bias_}")
        
        self.got_initial_pose = True
        self.keyframe_index = 1
        self.imu_ = None

    def imu_init(self, msg: Imu):
        # IMU params
        gravity=9.81
        params=PreintegrationParams.MakeSharedU(gravity)
        I=np.eye(3)
        params.setAccelerometerCovariance(np.array(msg.linear_acceleration_covariance).reshape((3, 3)))  # Set accelerometer covariance
        params.setGyroscopeCovariance(np.array(msg.angular_velocity_covariance).reshape((3, 3)))  # Set gyroscope covariance
        params.setIntegrationCovariance(I*1e-7)
        params.setUse2ndOrderCoriolis(False) # Disable 2nd order Coriolis effect
        params.setOmegaCoriolis(np.zeros((3,1))) # Zero out 

        accBias = np.array([0.1, 0.1, 0.1])
        gyroBias = np.array([0.0000075, 0.0000075, 0.0000075])
        bias_covariance=noiseModel.Isotropic.Sigma(6,0.1)
        actualBias = gtsam.imuBias.ConstantBias(accBias, gyroBias)
        # Calculate PIM
        self.pim = PreintegratedImuMeasurements(params, actualBias)
        self.is_pim_set = True

    def imu_callback(self, msg):
        self.imu_ = msg
        if not self.is_pim_set:
            self.imu_init(msg)

    def imu(self, msg: Imu):
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        if msg is None:
            return
        if self.last_imu_time is None:
            self.last_imu_time = current_time
            return
        self.get_logger().info(f"IMU data received at time: {current_time}")
        self.get_logger().info(f"Last IMU time: {self.last_imu_time}")
        if self.got_initial_pose:
            dt = current_time - self.last_imu_time
            self.last_imu_time = current_time
            if dt <= 0:
                dt = 0.01  # Ensure dt is positive to avoid division by zero

            measured_acceleration = self.Vector3(msg.linear_acceleration.x,
                                                msg.linear_acceleration.y,
                                                msg.linear_acceleration.z)
            measured_omega = self.Vector3(msg.angular_velocity.x,
                                        msg.angular_velocity.y,
                                        msg.angular_velocity.z)

            self.pim.integrateMeasurement(measured_acceleration, measured_omega, dt)

            imufactor=gtsam.ImuFactor(X(self.keyframe_index -1), V(self.keyframe_index -1), X(self.keyframe_index), V(self.keyframe_index), B(0), self.pim)
            self.graph_.add(imufactor)

            prev_state = gtsam.NavState(self.prev_pose_, gtsam.Point3(*self.prev_velocity_))
            predicted_navstate = self.pim.predict(prev_state, self.prev_bias_)

            predicted_velocity = predicted_navstate.velocity()
            predicted_bias = self.prev_bias_  # Zakładamy, że bias się nie zmienił

            # Dodajemy te zmienne do initial_estimate
            self.initial_estimate_.insert(V(self.keyframe_index), predicted_velocity)
            self.initial_estimate_.insert(B(self.keyframe_index), predicted_bias)
            self.get_logger().info(f"V i B dodane do {self.keyframe_index}")
            self.get_logger().info(f"previous velocity: {predicted_velocity}, previous bias: {predicted_bias}")
            dt = 0.0
            self.pim.resetIntegration()


    def odom_wheels_callback(self, msg):
        if not msg:
            self.get_logger().error("Problem with odometry data")
            return
        if self.got_initial_pose:
            pos_x = msg.pose.pose.position.x + np.random.normal(0, 0.1)
            pos_y = msg.pose.pose.position.y + np.random.normal(0, 0.1)
            # pos_x = msg.pose.pose.position.x
            # pos_y = msg.pose.pose.position.y
            pos_z = msg.pose.pose.position.z
            t = msg.header.stamp.sec + msg.header.stamp.nanosec/1e9

            odom_pose = Pose3(Rot3.Quaternion(
                msg.pose.pose.orientation.w,
                msg.pose.pose.orientation.x,
                msg.pose.pose.orientation.y,
                msg.pose.pose.orientation.z),
                Point3(
                    pos_x,
                    pos_y,
                    pos_z))

            # Implement factor graph for odometry data
            odom_noise = gtsam.noiseModel.Diagonal.Sigmas([msg.pose.covariance[0] + 0.01,
                                                            msg.pose.covariance[7] + 0.01,
                                                            msg.pose.covariance[14],
                                                            msg.pose.covariance[21],
                                                            msg.pose.covariance[28],
                                                            msg.pose.covariance[35]])
            # if self.keyframe_index == 0:
            #     self.graph_.add(PriorFactorPose3(X(self.keyframe_index), odom_pose, odom_noise))
            #     self.initial_estimate_.insert(X(self.keyframe_index), odom_pose)
            # else:
            # Ensure both previous and current poses are in initial_estimate_
            self.initial_estimate_.insert(X(self.keyframe_index), odom_pose)
            self.get_logger().info(f"X dodane do {self.keyframe_index}")
            self.get_logger().info(f"odom pose: {odom_pose}")
            self.imu(self.imu_)

            relative_pose = self.prev_pose_.between(odom_pose)
            self.graph_.add(BetweenFactorPose3(X(self.keyframe_index - 1), X(self.keyframe_index), relative_pose, odom_noise))

            self.prev_pose_ = odom_pose

            self.optimize_graph()
            self.keyframe_index += 1

    def optimize_graph(self):
        lm_params = gtsam.LevenbergMarquardtParams()
        lm_params.setMaxIterations(100)
        lm_params.setRelativeErrorTol(1e-5)

        optimizer = gtsam.LevenbergMarquardtOptimizer(self.graph_, self.initial_estimate_, lm_params)

        self.optimized_estimate_ = optimizer.optimize()
        optimized_pose = self.optimized_estimate_.atPose3(X(self.keyframe_index-1))
        optimized_position = optimized_pose.translation()
        optimized_orientation = optimized_pose.rotation().toQuaternion()
        
        # Create a message with estimate state and publish it
        estimated_state = Odometry()
        estimated_state.header.stamp = self.get_clock().now().to_msg()
        estimated_state.header.frame_id = "odom"
        estimated_state.pose.pose.position.x = optimized_position[0]
        estimated_state.pose.pose.position.y = optimized_position[1]
        estimated_state.pose.pose.position.z = optimized_position[2]
        estimated_state.pose.pose.orientation.w = optimized_orientation.w()
        estimated_state.pose.pose.orientation.x = optimized_orientation.x()
        estimated_state.pose.pose.orientation.y = optimized_orientation.y()
        estimated_state.pose.pose.orientation.z = optimized_orientation.z()

        self.fused_odom_pub.publish(estimated_state)

    def odom2_callback(self, msg: Odometry):
        # You can add vision odometry factors here
        pass


def main(args=None):
    rclpy.init(args=args)
    node = GtsamExampleNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
