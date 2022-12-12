'''
File: setup.py
Created Date: Friday, July 5th 2020, 10:11:51 pm
Author: Zentetsu

----

Last Modified: Sat Nov 27 2021
Modified By: Zentetsu

----

Project: SharedMemory
Copyright (c) 2020 Zentetsu

----

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

----

HISTORY:
2020-07-03	Zen	Creating file
2021-10-20	Zen	updating required lib
'''


from setuptools import setup, find_packages

setup(
    name='SharedMemory',
    version='1.1.2',
    author='Zentetsu',
    packages=find_packages(exclude=['tests*']),
    license='GPLv3',
    description='SharedMemory',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=['posix-ipc'],
    url='https://github.com/Zentetsu/SharedMemory',
    python_requires='>=3.6',
)