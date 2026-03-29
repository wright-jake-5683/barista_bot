import os
import random
from launch.actions import TimerAction
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument
from ament_index_python.packages import get_package_prefix


# this is the function launch system will look for
def generate_launch_description():
    package_description = "barista_robot_description"
    
    install_dir = get_package_prefix(package_description)
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_barista_bot_gazebo = get_package_share_directory('barista_robot_description')
    

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


##### Robot State Publishers & Spawn Nodes ##############################################################################################################


    ####### DATA INPUT ##########
    xacro_file = 'barista_robot_model.urdf.xacro'

    # Position and orientation
    # [X, Y, Z]
    position_1 = [0.0, 0.0, 0.2]
    position_2 = [1.0, 1.0, 1.2]
    # [Roll, Pitch, Yaw]
    orientation = [0.0, 0.0, 0.0]
    
    # Base Name or robot
    robot_base_name = "barista_bot"
    barista_bot_1_name = robot_base_name+"_"+str(1)
    barista_bot_2_name = robot_base_name+"_"+str(2)

    print("Fetching XACRO File ==>")
    robot_model_path = os.path.join(get_package_share_directory('barista_robot_description'))
    xacro_path = os.path.join(robot_model_path, 'xacro', xacro_file)
    

    # Robot State Publishers
    rsp_barista_bot_1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace="barista_bot_1_ns",
        name='robot_state_publisher_node_barista_bot_1',
        emulate_tty=True,
        parameters=[{
            'use_sim_time': True, 
            'frame_prefix': f"{barista_bot_1_name}/",
            'robot_description': Command([
                f'xacro {xacro_path} robot_name:={barista_bot_1_name}'
            ])
        }],
        output="screen"
    )
    rsp_barista_bot_2 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace="barista_bot_2_ns",
        name='robot_state_publisher_node_barista_bot_2',
        emulate_tty=True,
        parameters=[{
            'use_sim_time': True, 
            'frame_prefix': f"{barista_bot_2_name}/",
            'robot_description': Command([
                f'xacro {xacro_path} robot_name:={barista_bot_2_name}'
            ])
        }],
        output="screen"
    )

    # Spawn Robots in Gazebo
    spawn_robot_barista_bot_1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity_barista_bot_1',
        output='screen',
        arguments=['-entity',
                   barista_bot_1_name,
                   '-x', str(position_1[0]), '-y', str(position_1[1]), '-z', str(position_1[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]), '-Y', str(orientation[2]),
                   '-topic', '/barista_bot_1_ns/robot_description'
                   ]
    )
    spawn_robot_barista_bot_2 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity_barista_bot_2',
        output='screen',
        arguments=['-entity',
                   barista_bot_2_name,
                   '-x', str(position_2[0]), '-y', str(position_2[1]), '-z', str(position_2[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]), '-Y', str(orientation[2]),
                   '-topic', '/barista_bot_2_ns/robot_description'
                   ]
    )

##### Gazebo Launch Config ############################################################################################################################
    
    # Declare a new launch argument for the world file
    world_file_arg = DeclareLaunchArgument(
                'world',
                default_value=[os.path.join(pkg_barista_bot_gazebo, 'worlds', 'barista_bot_empty.world'), ''],
                description='SDF world file'
    )

    # Define the launch arguments for the Gazebo launch file
    gazebo_launch_args = {
        'verbose': 'false',
        'pause': 'false',
        'world': LaunchConfiguration('world')
    }

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments=gazebo_launch_args.items()
        
    )

    delayed_spawn_1 = TimerAction(
        period=5.0,   # wait 5 seconds
        actions=[spawn_robot_barista_bot_1]
    )
    delayed_spawn_2 = TimerAction(
        period=5.0,   # wait 5 seconds
        actions=[spawn_robot_barista_bot_2]
    )  

    # create and return launch description object
    return LaunchDescription(
        [            
            world_file_arg,
            gazebo,
            rsp_barista_bot_1,
            rsp_barista_bot_2,
            delayed_spawn_1,
            delayed_spawn_2
        ]
    )