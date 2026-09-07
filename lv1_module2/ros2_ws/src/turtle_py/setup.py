from setuptools import find_packages, setup

package_name = 'turtle_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pa21',
    maintainer_email='ivory0130@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    #=============================
        #"실행 단축키"를 등록하는 핵심 부분
        # A = B . C : D" 라는 공식
        # distance_pub    =  turtle_py.distance_publisher  :  main
        # 실행할 단축키 이름 ->   폴더이름 내의 파이썬 파일 이름   내의 실행할 함수 이름
    entry_points={
        'console_scripts': [
            'distance_pub = turtle_py.distance_publisher:main',
            'distance_sub = turtle_py.distance_monitor:main',
            'square_driver = turtle_py.square_driver:main',
            'turtle_tf_marker_broadcaster = turtle_py.turtle_tf_marker_broadcaster:main',
        ],
    },
)
