网络调试
========

连接测试
--------

.. code-block:: bash

   # 测试连通性
   ping host

   # 端口测试
   telnet host port
   nc -zv host port

   # DNS 查询
   nslookup domain
   dig domain

端口与连接
----------

.. code-block:: bash

   # 查看端口占用
   netstat -tlnp | grep port
   ss -tlnp | grep port

   # 查看所有连接
   netstat -an

   # 查看路由表
   route -n
   ip route

抓包分析
--------

.. code-block:: bash

   # 抓取指定端口
   tcpdump -i eth0 port 1883

   # 抓取指定主机
   tcpdump -i eth0 host 192.168.1.100

   # 保存到文件
   tcpdump -i eth0 -w capture.pcap

   # 读取抓包文件
   tcpdump -r capture.pcap
