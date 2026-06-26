Linux
=====

Linux 常用指令与系统知识。

文件操作
--------

.. code-block:: bash

   # 查找文件
   find /path -name "*.c"

   # 搜索文件内容
   grep -rn "pattern" /path

   # 查看文件大小
   ls -lh
   du -sh *

进程管理
--------

.. code-block:: bash

   # 查看进程
   ps aux | grep process_name

   # 杀死进程
   kill -9 PID

   # 后台运行
   nohup ./program &

网络调试
--------

.. code-block:: bash

   # 查看端口占用
   netstat -tlnp | grep port

   # 测试连通性
   ping host
   telnet host port

   # 抓包
   tcpdump -i eth0 port 1883

交叉编译
--------

.. code-block:: bash

   # 设置交叉编译工具链
   export CC=arm-linux-gnueabihf-gcc
   export CXX=arm-linux-gnueabihf-g++

   # CMake 交叉编译
   cmake -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake ..

.. note::

   持续更新中...
