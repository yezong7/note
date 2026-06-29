交叉编译
========

工具链设置
----------

.. code-block:: bash

   # 设置交叉编译工具链
   export CC=arm-linux-gnueabihf-gcc
   export CXX=arm-linux-gnueabihf-g++

   # 验证工具链
   arm-linux-gnueabihf-gcc --version

CMake 交叉编译
--------------

创建工具链文件 ``toolchain.cmake``：

.. code-block:: cmake

   set(CMAKE_SYSTEM_NAME Linux)
   set(CMAKE_SYSTEM_PROCESSOR arm)

   set(CMAKE_C_COMPILER arm-linux-gnueabihf-gcc)
   set(CMAKE_CXX_COMPILER arm-linux-gnueabihf-g++)

   set(CMAKE_FIND_ROOT_PATH /usr/arm-linux-gnueabihf)
   set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
   set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
   set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

使用：

.. code-block:: bash

   cmake -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake ..
   make

常见问题
--------

- **链接错误**：检查库路径是否正确
- **头文件找不到**：确认 sysroot 配置
- **运行时错误**：确认目标架构与工具链匹配
