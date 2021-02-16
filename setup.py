from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='mesh_lora',
    description='Mesh LoRa with PubSub meta OS',
    author='Quentin GALLOUÉDEC',
    author_email='gallouedec.quentin@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bsppbep/mesh_lora',
    packages=find_packages(),
    version='0.1.0',
    install_requires=['Adafruit-Blinka', 'adafruit-circuitpython-busdevice', 'adafruit-circuitpython-rfm9x', 'Adafruit-PlatformDetect', 'Adafruit-PureIO', 'pyftdi', 'pyserial', 'pyusb',  'sysv-ipc'] # 'rpi-ws281x' 'RPi.GPIO',
)