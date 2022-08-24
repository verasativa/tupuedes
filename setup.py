from setuptools import find_packages, setup

setup(
    name='tupuedes',
    packages=find_packages(), 
    version='0.2.0',
    install_requires=[
        'Click', 'mediapipe', 'pandas', 'matplotlib', 'scipy', 'posthog'
    ],
    entry_points={
        'console_scripts': [
            'tupuedes = tupuedes:cli',
        ],
    },
    description='Tú puedes; an opensource smart gym',
    author='Vera Sativa',
    license='',
)
