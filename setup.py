from setuptools import find_packages, setup

setup(
    name='nsrtf',
    packages=find_packages(),
    version='0.1.0',
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'nsrtf = nsrtf:cli',
        ],
    },
    description='No se rinda tan facil" CV trainer',
    author='Vera Sativa',
    license='',
)
