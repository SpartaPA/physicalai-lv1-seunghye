import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/pa21/seunghye/physicalai-lv1-seunghye/lv1_module2/ros2_ws/install/turtle_py'
