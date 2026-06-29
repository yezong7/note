进程管理
========

查看进程
--------

.. code-block:: bash

   # 查看所有进程
   ps aux

   # 按名称过滤
   ps aux | grep process_name

   # 查看进程树
   pstree -p

   # 实时监控
   top
   htop

进程控制
--------

.. code-block:: bash

   # 杀死进程
   kill -9 PID
   killall process_name

   # 后台运行
   nohup ./program &

   # 查看后台任务
   jobs -l

   # 切换到前台
   fg %1

系统资源
--------

.. code-block:: bash

   # 内存使用
   free -h

   # 磁盘使用
   df -h

   # CPU 信息
   lscpu
