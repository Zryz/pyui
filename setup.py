from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as req:
        return req.readlines()

setup(
    name='pyui',
    version='0.1.0',
    packages=find_packages(),
    install_requires=read_requirements(),
    author='Stuart Yeadon',
    author_email='stuartyeadon@gmail.com',
    description='A simple Python UI library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/pyui',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)