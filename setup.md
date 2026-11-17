# Hoverboard-Roboter: SLAM + Nav2 starten (ROS 2 Jazzy)

Jeden Schritt in einem **eigenen Terminal** starten, in dieser Reihenfolge.
In jedem Terminal zuerst sourcen:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash   # Pfad zu deinem Workspace anpassen
```

## Einmalig: bauen

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

Nach jeder Änderung an Launch- oder YAML-Dateien im Paket neu bauen.

## 1. Hoverboard (Controller, robot_state_publisher, Joystick, RViz)

```bash
ros2 launch hoverboard_demo_bringup hoverboard.launch.py
```

Test: Mit dem Joystick fahren.

```bash
ros2 topic info /cmd_vel -v   # Typ TwistStamped, Controller als Subscriber
```

## 2. Lidar

```bash
ros2 launch rplidar_ros <modell>_launch.py serial_port:=/dev/ttyUSB0
# z.B. rplidar_a1_launch.py, rplidar_a2m8_launch.py, rplidar_c1_launch.py
```

Test:

```bash
ros2 topic hz /scan
```

Der `frame_id` des Lidars (Standard `laser`) ist im URDF als Link `laser` angelegt. Die Position steht in `hoverboard_description.xacro` (`base_link_laser_joint`) und muss nachgemessen werden.

## 3. SLAM Toolbox

```bash
ros2 launch slam_toolbox online_async_launch.py \
  use_sim_time:=false \
  slam_params_file:=$(ros2 pkg prefix hoverboard_demo_bringup)/share/hoverboard_demo_bringup/config/mapper_params_online_async.yaml
```

Die Datei liegt im Paket (`config/mapper_params_online_async.yaml`) und enthält bereits `base_frame: base_link`, `odom_frame: odom` und `scan_topic: /scan`.

Test:

```bash
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_tools view_frames   # Kette: map -> odom -> base_link -> laser
```

## 4. Nav2

```bash
ros2 launch nav2_bringup navigation_launch.py \
  use_sim_time:=false \
  params_file:=$(ros2 pkg prefix hoverboard_demo_bringup)/share/hoverboard_demo_bringup/config/nav2_params.yaml
```

Warten bis im Terminal steht: `Managed nodes are active`.

## 5. Ziel setzen in RViz

1. Fixed Frame auf `map` stellen.
2. Displays hinzufügen: `Map` (`/map`), `Map` (`/global_costmap/costmap`), `Map` (`/local_costmap/costmap`).
3. Oben in der Toolbar **2D Goal Pose** wählen und ein Ziel auf die Karte klicken.
4. Erstes Ziel nah am Roboter (~1 m), Hand am Joystick bzw. Not-Aus.

## Fehlersuche

| Problem | Prüfen |
|---|---|
| Pfad geplant, Roboter steht | `ros2 topic echo /cmd_vel` – kommt etwas an? |
| Fährt Kreise / Schlangenlinien | `wheel_separation` / `wheel_radius`, Motorrichtung |
| Kein Pfad / "out of bounds" | `robot_radius` / `inflation_radius` verkleinern |
| "Control loop missed its desired rate" | MPPI `batch_size` senken |
| TF-Fehler | `ros2 run tf2_tools view_frames`, `use_sim_time:=false` überall |

## Karte speichern (optional)

```bash
ros2 run nav2_map_server map_saver_cli -f ~/maps/meine_karte
```