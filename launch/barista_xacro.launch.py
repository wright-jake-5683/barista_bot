import os
import random
from launch.actions import TimerAction
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_prefix

# this is the function launch  system will look for
def generate_launch_description():

    ####### DATA INPUT ##########
    xacro_file = 'barista_robot_model.urdf.xacro'
    package_description = "barista_robot_description"
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_barista_bot_gazebo = get_package_share_directory('barista_robot_description')

     # Position and orientation
    # [X, Y, Z]
    position = [0.0, 0.0, 0.2]
    # [Roll, Pitch, Yaw]
    orientation = [0.0, 0.0, 0.0]
    # Base Name or robot
    robot_base_name = "barista_bot"


    entity_name = robot_base_name+"-"+str(int(random.random()*100000))

    ####### DATA INPUT END ##########
    print("Fetching XACRO File ==>")
    robot_model_path = os.path.join(
        get_package_share_directory('barista_robot_description'))

    xacro_path = os.path.join(robot_model_path, 'xacro', xacro_file)

    # convert XACRO file into URDF
    doc = xacro.parse(open(xacro_path))
    xacro.process_doc(doc)
    params = {'robot_description': doc.toxml()}

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[params],
        output="screen"
    )


    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(package_description), 'rviz', 'urdf_vis.rviz')
    
    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            name='rviz_node',
            parameters=[{'use_sim_time': True}],
            arguments=['-d', rviz_config_dir])


    jsp_node = Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui'
    )

    # Spawn ROBOT Set Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=['-entity',
                   entity_name,
                   '-x', str(position[0]), '-y', str(position[1]), '-z', str(position[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]), '-Y', str(orientation[2]),
                   '-topic', '/robot_description'
                   ]
    )


    install_dir = get_package_prefix(package_description)

    # Set the path to the WORLD model files. Is to find the models inside the models folder in my_box_bot_gazebo package
    gazebo_models_path = os.path.join(pkg_barista_bot_gazebo, 'models')
    # os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] =  os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] =  install_dir + "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))


    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )

    delayed_spawn = TimerAction(
        period=5.0,   # wait 5 seconds
        actions=[spawn_robot]
    )    

    # create and return launch description object
    return LaunchDescription(
        [            
            robot_state_publisher_node,
            rviz_node,
            jsp_node,
            DeclareLaunchArgument(
                'world',
                default_value=[os.path.join(pkg_barista_bot_gazebo, 'worlds', 'barista_bot_empty.world'), ''],
                description='SDF world file'
            ),
            gazebo,
            delayed_spawn
        ]
    )