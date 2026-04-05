# Übungsblatt 06 — ROS2 Fundamentals: Topics, Nodes & Communication

**Name:** Aleksandr Zheleznov  
**Student ID:** 25-110-818  
**ROS2 Version:** Humble  
**Repository:** https://github.com/Aleks4920/lecture6-ros2demo

---

## Task 1a — Package Creation & Circle Motion Publisher

### Package Structure

```
/workspace/turtlebot3_ws/src/student_robotics:
package.xml  resource  setup.cfg  setup.py  student_robotics  test

/workspace/turtlebot3_ws/src/student_robotics/resource:
student_robotics

/workspace/turtlebot3_ws/src/student_robotics/student_robotics:
__init__.py  circle_motion.py  odom_monitor.py

/workspace/turtlebot3_ws/src/student_robotics/test:
test_copyright.py  test_flake8.py  test_pep257.py
```

![Package Structure](screenshots/Screenshot%202026-04-05%20221232.png)

### circle_motion.py

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CircleMotion(Node):
    def __init__(self):
        super().__init__('circle_motion')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10 Hz
        self.get_logger().info('CircleMotion node started')

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.3   # m/s
        msg.angular.z = 0.5  # rad/s
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CircleMotion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Robot in Gazebo

![TurtleBot3 in Gazebo](screenshots/Screenshot%202026-04-05%20220827.png)

### Why use create_timer()?

`create_timer()` decouples message publishing from blocking loops, allowing the ROS2 executor to handle callbacks efficiently without occupying the main thread.

---

## Task 1b — Odometry Subscriber

### odom_monitor.py

```python
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
```

### Both Nodes Running & ros2 node list

![ros2 node list showing both nodes](screenshots/Screenshot%202026-04-05%20213729.png)

### How does pub-sub decoupling work?

Publishers and subscribers have no direct knowledge of each other — they communicate only through named topics managed by the ROS2 middleware. Nodes can be started, stopped, or replaced independently without affecting other nodes in the system. Middleware handles all message routing, buffering via QoS

---

## Task 2a — ROS2 CLI Topic Commands

### ros2 topic list

![ros2 topic list](screenshots/Screenshot%202026-04-05%20213607.png)

### ros2 topic info /cmd_vel

![ros2 topic info /cmd_vel](screenshots/Screenshot%202026-04-05%20213619.png)

### ros2 topic info /odom

![ros2 topic info /odom](screenshots/Screenshot%202026-04-05%20213634.png)

### ros2 topic hz /odom

![ros2 topic hz /odom](screenshots/Screenshot%202026-04-05%20213717.png)

### ros2 topic bw /odom

![ros2 topic bw /odom](screenshots/Screenshot%202026-04-05%20213654.png)

### ros2 node list

![ros2 node list](screenshots/Screenshot%202026-04-05%20213729.png)

### ros2 node info /circle_motion

![ros2 node info /circle_motion](screenshots/Screenshot%202026-04-05%20213754.png)

---

### What is /odom frequency? Why does it matter?

The `/odom` topic publishes at approximately **29 Hz** as shown in the `ros2 topic hz` output. Frequency matters for robot control because the control loop depends on fresh pose estimates to compute correct velocity commands — too low a frequency introduces delays that cause unstable or inaccurate motion, particularly during fast maneuvers or tight feedback loops.

### How many publishers and subscribers does /cmd_vel have?

- **Publisher count: 1** — `/circle_motion` node publishes velocity commands
- **Subscription count: 1** — `/turtlebot3_diff_drive` (Gazebo differential drive controller) subscribes

### What is the difference between ros2 topic hz and ros2 topic bw?

`ros2 topic hz` measures the message publish rate in messages per second, showing how often data arrives on a topic. `ros2 topic bw` measures data throughput in kilobytes per second.

---

## Task 2b — Communication Graph (rqt_graph)

![rqt_graph node communication](screenshots/Screenshot%202026-04-05%20221009.png)

### What does the graph show?

The graph shows `/circle_motion` publishing `Twist` messages to `/cmd_vel`, which is consumed by `/turtlebot3_diff_drive` — the Gazebo physics controller. That controller then publishes odometry data on `/odom`, which is subscribed to by `/odom_monitor`. Additional Gazebo nodes (`/turtlebot3_imu`, `/turtlebot3_laserscan`, `/turtlebot3_joint_state`) publish their respective sensor topics independently.

### What happens if you stop circle_motion? Does odom_monitor still work?

Yes, `odom_monitor` continues running because it only subscribes to `/odom`, which is published by the Gazebo simulation independently of any student nodes. The robot stops moving however.

---

## Commands Used

```bash
# Environment setup
export DISPLAY=host.docker.internal:0
export LIBGL_ALWAYS_SOFTWARE=1
export TURTLEBOT3_MODEL=burger
source /opt/ros/humble/setup.bash
source /workspace/turtlebot3_ws/install/setup.bash

# Build
cd /workspace/turtlebot3_ws
colcon build --packages-select student_robotics

# Launch simulation
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
gzclient --verbose  # needed separately due to container display setup

# Run nodes
ros2 run student_robotics circle_motion
ros2 run student_robotics odom_monitor

# CLI inspection
ros2 topic list
ros2 topic info /cmd_vel
ros2 topic info /odom
ros2 topic hz /odom
ros2 topic bw /odom
ros2 node list
ros2 node info /circle_motion
rqt_graph
```

## Issues Encountered

- **GPU error on container start**: `devcontainer.json` required `--gpus all` but WSL had no NVIDIA adapter exposed. Fixed by removing the GPU flag from the devcontainer config.
- **Gazebo display not opening**: `DISPLAY` was set to `192.168.65.7:0` (Docker internal gateway) with nothing listening. Fixed by setting `export DISPLAY=host.docker.internal:0` and running VcXsrv on Windows with access control disabled.
- **gzserver crashing (exit code 255)**: Required `LIBGL_ALWAYS_SOFTWARE=1` and `MESA_GL_VERSION_OVERRIDE=3.3` for software rendering in the container.
- **gzclient not launching with ros2 launch**: Launched `gzclient --verbose` separately in a dedicated terminal as a workaround.