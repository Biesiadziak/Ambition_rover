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
        self.odom_vo_sub = self.create_subscription(Odometry, '/vo_odom', self.odom_vo_callback, 10)

        self.fused_odom_pub = self.create_publisher(Odometry, '/fused/odom', 10)

        self.timer_ = self.create_timer(0.5, self.update_graph)

        # Pos Guess
        self.initial_pose_sub_ = self.create_subscription(PoseWithCovarianceStamped, '/initialpose', self.initial_pose_callback, 10)  # Get initial pose from user's guess
        self.got_initial_pose = False

        # GTSAM
        self.graph_ = None
        self.initial_estimate_ = None

        self.prev_pose_ = Pose3()  # Previous pose
        self.prev_pose_vo = Pose3()

        self.prev_velocity_ = self.Vector3(0, 0, 0) # Previous velocity 
        self.prev_bias_ = gtsam.imuBias.ConstantBias()

        self.prev_time_ = self.get_clock().now()
        self.pim = None
        self.is_pim_set = False
        self.last_imu_time = None

        self.keyframe_index = 1

        self.imu_ = None
        self.odom_ = None
        self.odom_vo = None

    def Vector3(self, x, y, z):
        return np.array([x, y, z], dtype=np.float64)
    
    def initial_pose_callback(self, msg):
        self.got_initial_pose = False

        self.graph_ = gtsam.NonlinearFactorGraph()  # Reset the graph

        prior_noise = noiseModel.Diagonal.Sigmas([0.1] * 6)
        bias_prior_noise = noiseModel.Isotropic.Sigma(6, 0.1)

        self.initial_estimate_ = gtsam.Values()  # Reset Initial state

        self.initial_estimate_.insert(X(0), self.prev_pose_)
        self.initial_estimate_.insert(V(0), self.prev_velocity_)
        self.initial_estimate_.insert(B(0), self.prev_bias_)

        self.graph_.add(PriorFactorPose3(X(0), Pose3(), prior_noise))  # Add prior factor to the graph
        self.graph_.add(gtsam.PriorFactorConstantBias(B(0), self.prev_bias_, bias_prior_noise))
        
        self.got_initial_pose = True
        self.keyframe_index = 1

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

    def imu_callback(self, msg: Imu):
        self.imu_ = msg
        if not self.is_pim_set:
            self.imu_init(msg)

    def odom_wheels_callback(self, msg: Odometry):
        self.odom_ = msg

    def odom_vo_callback(self, msg: Odometry):
        self.odom_vo = msg

    def update_imu_graph(self, msg: Imu):
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        if self.last_imu_time is None:
            self.last_imu_time = current_time

        dt = current_time - self.last_imu_time
        self.last_imu_time = current_time

        if dt <= 0:
            dt = 0.01

        measured_acceleration = self.Vector3(msg.linear_acceleration.x,
                                            msg.linear_acceleration.y,
                                            msg.linear_acceleration.z)
        measured_omega = self.Vector3(msg.angular_velocity.x,
                                    msg.angular_velocity.y,
                                    msg.angular_velocity.z)

        self.pim.integrateMeasurement(measured_acceleration, measured_omega, dt)

        imufactor=gtsam.ImuFactor(X(self.keyframe_index -1), V(self.keyframe_index -1), X(self.keyframe_index), V(self.keyframe_index), B(0), self.pim)
        self.graph_.push_back(imufactor)

        self.pim.resetIntegration()

        prev_state = gtsam.NavState(self.prev_pose_, self.prev_velocity_)
        predicted_navstate = self.pim.predict(prev_state, self.prev_bias_)

        predicted_velocity = gtsam.Point3(predicted_navstate.velocity())

        # Dodajemy te zmienne do initial_estimate
        self.initial_estimate_.insert(V(self.keyframe_index), predicted_velocity)

        dt = 0.0
        
    def update_odom_graph(self, msg):
        # pos_x = msg.pose.pose.position.x + np.random.normal(0, 0.1)
        # pos_y = msg.pose.pose.position.y + np.random.normal(0, 0.1)
        pos_x = msg.pose.pose.position.x
        pos_y = msg.pose.pose.position.y
        pos_z = msg.pose.pose.position.z

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

        relative_pose = self.prev_pose_.between(odom_pose)
        self.graph_.add(BetweenFactorPose3(X(self.keyframe_index - 1), X(self.keyframe_index), relative_pose, odom_noise))

        self.initial_estimate_.insert(X(self.keyframe_index), odom_pose)

        self.prev_pose_ = odom_pose

    def update_vo_graph(self, msg):
        # pos_x = msg.pose.pose.position.x + np.random.normal(0, 0.1)
        # pos_y = msg.pose.pose.position.y + np.random.normal(0, 0.1)
        pos_x = msg.pose.pose.position.x
        pos_y = msg.pose.pose.position.y
        pos_z = msg.pose.pose.position.z

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

        relative_pose = self.prev_pose_vo.between(odom_pose)
        self.graph_.add(BetweenFactorPose3(X(self.keyframe_index - 1), X(self.keyframe_index), relative_pose, odom_noise))

        # self.initial_estimate_.insert(X(self.keyframe_index), odom_pose)

        self.prev_pose_vo = odom_pose

    def update_graph(self):
        if not self.got_initial_pose:
            self.get_logger().warn("Waiting for initial pose...")
            return

        if not self.is_pim_set:
            self.get_logger().warn("Waiting for IMU initialization...")
            return

        if self.imu_ is not None and self.odom_ is not None and self.odom_vo is not None:
            self.update_imu_graph(self.imu_)
            self.update_odom_graph(self.odom_)
            self.update_vo_graph(self.odom_vo)

            self.optimize_graph()
            self.keyframe_index += 1

    def optimize_graph(self):
        lm_params = gtsam.LevenbergMarquardtParams()
        lm_params.setMaxIterations(100)
        lm_params.setRelativeErrorTol(1e-5)

        optimizer = gtsam.LevenbergMarquardtOptimizer(self.graph_, self.initial_estimate_, lm_params)

        self.optimized_estimate_ = optimizer.optimize()
        optimized_pose = self.optimized_estimate_.atPose3(X(self.keyframe_index - 1))
        optimized_position = optimized_pose.translation()
        optimized_orientation = optimized_pose.rotation().toQuaternion()
        
        # Create a message with estimate state and publish it
        estimated_state = Odometry()
        estimated_state.header.stamp = self.get_clock().now().to_msg()
        estimated_state.header.frame_id = "map"
        estimated_state.pose.pose.position.x = optimized_position[0]
        estimated_state.pose.pose.position.y = optimized_position[1]
        estimated_state.pose.pose.position.z = optimized_position[2]
        estimated_state.pose.pose.orientation.w = optimized_orientation.w()
        estimated_state.pose.pose.orientation.x = optimized_orientation.x()
        estimated_state.pose.pose.orientation.y = optimized_orientation.y()
        estimated_state.pose.pose.orientation.z = optimized_orientation.z()

        self.fused_odom_pub.publish(estimated_state)


def main(args=None):
    rclpy.init(args=args)
    node = GtsamExampleNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
