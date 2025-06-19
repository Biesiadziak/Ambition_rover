import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from std_msgs.msg import Header

import gtsam
from gtsam import symbol

import numpy as np

class GtsamExampleNode(Node):

    def __init__(self):
        super().__init__('gtsam_fusion_node')

        # IMU params
        self.imu_params = gtsam.PreintegrationParams.MakeSharedU(9.81)
        self.imu_params.setAccelerometerCovariance(np.identity(3) * 0.1)
        self.imu_params.setGyroscopeCovariance(np.identity(3) * 0.1)
        self.imu_params.setIntegrationCovariance(np.identity(3) * 0.01)


        self.bias = gtsam.imuBias.ConstantBias()
        self.imu_preintegrated = gtsam.PreintegratedImuMeasurements(self.imu_params, self.bias)

        self.graph = gtsam.NonlinearFactorGraph()
        self.initialEstimate = gtsam.Values()

        prior_noise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.1]*6))
        odom_noise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.2, 0.2, 0.2, 0.1, 0.1, 0.1]))

        prior_mean = gtsam.Pose3()

        self.current_key = 1

        # Add prior factor
        self.graph.add(gtsam.PriorFactorPose3(self.current_key, prior_mean, prior_noise))
        self.initialEstimate.insert(self.current_key, prior_mean)

        bias_key_0 = symbol('b', self.current_key)
        self.graph.add(gtsam.PriorFactorConstantBias(bias_key_0, self.bias, gtsam.noiseModel.Isotropic.Sigma(6, 1e-3)))
        self.initialEstimate.insert(bias_key_0, self.bias)

        self.odom_noise = odom_noise

        self.last_imu_time = None

        self.imu_sub = self.create_subscription(Imu, '/imu/data', self.imu_callback, 10)
        self.odom1_sub = self.create_subscription(Odometry, '/odometry/wheels', self.odom1_callback, 10)
        self.odom2_sub = self.create_subscription(Odometry, '/vo_odom', self.odom2_callback, 10)

        self.fused_odom_pub = self.create_publisher(Odometry, '/fused/odom', 10)

    def imu_callback(self, msg: Imu):
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        if self.last_imu_time is None:
            self.last_imu_time = current_time
            return

        dt = current_time - self.last_imu_time
        self.last_imu_time = current_time

        measured_acceleration = gtsam.Vector3(msg.linear_acceleration.x,
                                              msg.linear_acceleration.y,
                                              msg.linear_acceleration.z)
        measured_omega = gtsam.Vector3(msg.angular_velocity.x,
                                      msg.angular_velocity.y,
                                      msg.angular_velocity.z)

        self.imu_preintegrated.integrateMeasurement(measured_acceleration, measured_omega, dt)

    def odom1_callback(self, msg: Odometry):
        q = msg.pose.pose.orientation
        rot = gtsam.Rot3.Quaternion(q.w, q.x, q.y, q.z)
        trans = gtsam.Point3(msg.pose.pose.position.x,
                            msg.pose.pose.position.y,
                            msg.pose.pose.position.z)
        odom_pose = gtsam.Pose3(rot, trans)

        self.add_imu_and_odometry_factor(odom_pose)
        self.optimize_and_publish(msg.header)

    def add_imu_and_odometry_factor(self, odom: gtsam.Pose3):
        prev_key = self.current_key
        next_key = self.current_key + 1

        pose_key_prev = symbol('x', prev_key)
        vel_key_prev = symbol('v', prev_key)
        bias_key_prev = symbol('b', prev_key)

        pose_key_next = symbol('x', next_key)
        vel_key_next = symbol('v', next_key)
        bias_key_next = symbol('b', next_key)

        if self.imu_preintegrated.deltaTij() > 0:
            imu_factor = gtsam.ImuFactor(pose_key_prev, vel_key_prev,
                                        pose_key_next, vel_key_next,
                                        bias_key_prev, self.imu_preintegrated)
            self.graph.add(imu_factor)

        bias_noise = gtsam.noiseModel.Isotropic.Sigma(6, 1e-3)
        self.graph.add(gtsam.BetweenFactorConstantBias(bias_key_prev, bias_key_next, self.bias, bias_noise))

        self.graph.add(gtsam.BetweenFactorPose3(pose_key_prev, pose_key_next, odom, self.odom_noise))

        prev_pose = self.initialEstimate.atPose3(prev_key)
        predicted_pose = prev_pose.compose(odom)

        self.initialEstimate.insert(next_key, predicted_pose)
        self.initialEstimate.insert(bias_key_next, self.bias)

        self.current_key = next_key

        self.imu_preintegrated.resetIntegrationAndSetBias(self.bias)

    def optimize_and_publish(self, header: Header):
        optimizer = gtsam.LevenbergMarquardtOptimizer(self.graph, self.initialEstimate)
        result = optimizer.optimize()

        bias_key = symbol('b', self.current_key)
        self.bias = result.atConstantBias(bias_key)

        pose_key = self.current_key
        optimized_pose = result.atPose3(pose_key)

        self.publish_odom(optimized_pose, header)

    def publish_odom(self, pose: gtsam.Pose3, header: Header):
        odom_msg = Odometry()
        odom_msg.header = header
        odom_msg.header.frame_id = "map"
        odom_msg.child_frame_id = "base_link"

        odom_msg.pose.pose.position.x = pose.x()
        odom_msg.pose.pose.position.y = pose.y()
        odom_msg.pose.pose.position.z = pose.z()

        q = pose.rotation().toQuaternion()  # returns gtsam.Quaternion

        odom_msg.pose.pose.orientation.w = q.w()
        odom_msg.pose.pose.orientation.x = q.x()
        odom_msg.pose.pose.orientation.y = q.y()
        odom_msg.pose.pose.orientation.z = q.z()

        self.fused_odom_pub.publish(odom_msg)

        self.get_logger().info(
            f"Published fused odometry - Position: [{odom_msg.pose.pose.position.x:.2f}, "
            f"{odom_msg.pose.pose.position.y:.2f}, {odom_msg.pose.pose.position.z:.2f}], "
            f"Orientation (w,x,y,z): [{q.w():.2f}, {q.x():.2f}, {q.y():.2f}, {q.z():.2f}]"
        )

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
