进程与系统管理手册
==================

本文档是 Linux 进程与系统管理的全面参考手册，涵盖进程查看、控制、资源监控、
线程管理、Core Dump 调试、服务管理和系统日志等核心主题。

.. contents:: 目录
   :depth: 2
   :local:


查看进程
--------

进程是 Linux 系统中正在运行的程序的实例。每个进程都有唯一的 PID（Process ID），
就像每个人都有唯一的身份证号一样。理解如何查看和分析进程，是系统管理的第一步。


ps —— 进程快照
^^^^^^^^^^^^^^

``ps`` 是最基础的进程查看工具，它拍下当前系统进程的一张"照片"。

**比喻**：``ps`` 就像医院的值班表——它显示某个时刻谁在工作、状态如何、占用了多少资源。

.. code-block:: bash

   # 查看所有进程（BSD 风格，最常用）
   ps aux

   # 查看所有进程（System V 风格，显示完整命令行）
   ps -ef

   # 按名称过滤
   ps aux | grep process_name

   # 只看某个用户的进程
   ps -u username

   # 按 CPU 使用率排序（找出 CPU 杀手）
   ps aux --sort=-%cpu | head -20

   # 按内存使用率排序（找出内存大户）
   ps aux --sort=-%mem | head -20

   # 查看进程的线程
   ps -T -p PID

**输出字段解读**：

- ``USER``：进程所属用户
- ``PID``：进程 ID
- ``%CPU``：CPU 使用率
- ``%MEM``：内存使用率
- ``VSZ``：虚拟内存大小（Virtual Memory Size）
- ``RSS``：实际使用的物理内存（Resident Set Size）
- ``STAT``：进程状态（R=运行, S=睡眠, D=不可中断睡眠, Z=僵尸, T=停止）
- ``COMMAND``：启动命令

**踩坑经验**：``ps aux`` 和 ``ps -ef`` 看到的结果一样，但列名不同。
``aux`` 用 ``%CPU``，``-ef`` 用 ``C``。


pstree —— 进程树
^^^^^^^^^^^^^^^^

``pstree`` 以树状结构展示进程之间的父子关系。

**比喻**：如果 ``ps`` 是一张平面的值班表，``pstree`` 就是一张组织架构图，
能清楚看到谁是谁的上级（父进程）。

.. code-block:: bash

   # 显示进程树（带 PID）
   pstree -p

   # 显示某个进程的子树
   pstree -p PID

   # 显示用户名
   pstree -u

   # 高亮显示当前进程的祖先链
   pstree -hp $$


top / htop —— 实时监控
^^^^^^^^^^^^^^^^^^^^^^

``top`` 是系统管理员的"仪表盘"，实时显示系统资源使用情况。
``htop`` 是 ``top`` 的增强版，界面更友好，支持鼠标操作。

**比喻**：``top`` 就像汽车的仪表盘——你能实时看到引擎转速（CPU）、
油量（内存）和速度（进程活动）。

.. code-block:: bash

   # 启动 top
   top

   # 启动 htop（推荐，更易用）
   htop

**top 交互快捷键**：

- ``P``：按 CPU 排序
- ``M``：按内存排序
- ``k``：杀死进程（输入 PID）
- ``r``：renice 调整优先级
- ``1``：显示每个 CPU 核心的使用率
- ``q``：退出

**top 输出头部解读**：

- ``load average: 0.50, 0.80, 1.20``：1分钟、5分钟、15分钟的平均负载。
  如果值超过 CPU 核心数，说明系统过载。
- ``Tasks``：总进程数、运行中、睡眠中、僵尸进程数
- ``%Cpu(s)``：CPU 使用分布（用户态、内核态、空闲、等待I/O）
- ``KiB Mem``：物理内存使用情况

**踩坑经验**：如果看到 ``僵尸进程（Zombie）`` 数量不为零，
说明有子进程退出后父进程没有回收它。少量僵尸无害，大量僵尸需要排查父进程。


pgrep / pidof —— 按名称查找进程
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``grep`` 配合 ``ps`` 虽然能查找进程，但 ``pgrep`` 和 ``pidof`` 更直接。

**比喻**：``pgrep`` 是按姓名查电话号码，``pidof`` 是按全名精确查号。

.. code-block:: bash

   # 按名称查找进程 PID（模糊匹配）
   pgrep nginx

   # 显示进程名和 PID
   pgrep -l nginx

   # 显示完整命令行
   pgrep -a nginx

   # 精确匹配（不会匹配 nginx-worker）
   pgrep -x nginx

   # pidof：精确查找（必须完全匹配进程名）
   pidof nginx
   # 输出: 1234 5678 9012（所有 nginx 进程的 PID）

   # pidof 只返回一个（最老的）
   pidof -s nginx

**区别**：

- ``pgrep`` 支持正则，更灵活，但可能匹配到 grep 自身
- ``pidof`` 只做精确匹配，不会误匹配


/proc 文件系统 —— 进程的"病历本"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``/proc`` 是一个虚拟文件系统，不占用磁盘空间，是内核向用户空间暴露信息的窗口。
每个进程在 ``/proc/[pid]/`` 下都有一个目录，包含该进程的所有"病历"。

**比喻**：``/proc`` 就像医院的电子病历系统——你不需要打开病人（进程），
就能查看他的各项指标。

.. code-block:: bash

   # 查看进程状态（基本信息、线程数、内存等）
   cat /proc/1234/status

   # 查看进程的启动命令
   cat /proc/1234/cmdline | tr '\0' ' '
   # 注意：cmdline 中参数用 \0 分隔，需要 tr 转换

   # 查看进程的环境变量
   cat /proc/1234/environ | tr '\0' '\n'
   # 同样用 \0 分隔

   # 查看进程打开的文件描述符
   ls -la /proc/1234/fd/

   # 查看进程的内存映射
   cat /proc/1234/maps

   # 查看进程的当前工作目录
   ls -la /proc/1234/cwd

   # 查看进程的可执行文件路径
   ls -la /proc/1234/exe

/proc/[pid]/status —— 进程状态摘要
"""""""""""""""""""""""""""""""""""

.. code-block:: bash

   $ cat /proc/1234/status
   Name:   nginx
   State:  S (sleeping)
   Pid:    1234
   PPid:   1         # 父进程 PID
   Threads: 4        # 线程数
   VmSize:  123456 kB  # 虚拟内存
   VmRSS:    12345 kB  # 物理内存
   FDSize:   256       # 文件描述符表大小

**实用场景**：排查内存泄漏时，定期记录 ``VmRSS`` 看是否有持续增长。

/proc/[pid]/fd —— 打开的文件描述符
"""""""""""""""""""""""""""""""""""

.. code-block:: bash

   # 列出进程打开的所有文件
   ls -la /proc/1234/fd/

   # 输出示例：
   # lrwx------ 1 root root 64 Jun 29 10:00 0 -> /dev/null
   # lrwx------ 1 root root 64 Jun 29 10:00 1 -> /dev/null
   # lrwx------ 1 root root 64 Jun 29 10:00 2 -> /dev/null
   # lrwx------ 1 root root 64 Jun 29 10:00 3 -> socket:[12345]
   # lrwx------ 1 root root 64 Jun 29 10:00 4 -> /var/log/nginx/access.log

   # 统计打开的文件数
   ls /proc/1234/fd/ | wc -l

**实用场景**：程序报 "Too many open files" 错误时，用这个命令查看进程到底打开了多少文件。

/proc/[pid]/maps —— 内存映射
"""""""""""""""""""""""""""""

.. code-block:: bash

   # 查看进程的内存布局
   cat /proc/1234/maps

   # 输出示例：
   # 地址范围              权限  偏移    设备  inode  路径
   # 00400000-00452000 r-xp 00000000 08:02 131074  /usr/bin/nginx
   # 00651000-00652000 r--p 00051000 08:02 131074  /usr/bin/nginx
   # 00652000-0066f000 rw-p 00052000 08:02 131074  /usr/bin/nginx
   # 7f1234567000-7f1234789000 r-xp 00000000 08:02 262145  /lib/x86_64-linux-gnu/libc.so.6

**权限字段**：``r``=读, ``w``=写, ``x``=执行, ``p``=私有, ``s``=共享

/proc/[pid]/environ —— 环境变量
""""""""""""""""""""""""""""""""

.. code-block:: bash

   # 查看进程的环境变量
   cat /proc/1234/environ | tr '\0' '\n'

   # 输出示例：
   # PATH=/usr/local/bin:/usr/bin:/bin
   # HOME=/home/user
   # LANG=en_US.UTF-8

**实用场景**：程序行为异常时，检查它读取的环境变量是否正确。

/proc 系统级信息
""""""""""""""""

.. code-block:: bash

   # 查看 CPU 信息
   cat /proc/cpuinfo

   # 查看内存详情
   cat /proc/meminfo

   # 查看内核版本
   cat /proc/version

   # 查看系统启动时间
   cat /proc/uptime

   # 查看磁盘分区
   cat /proc/partitions


lsof —— 列出打开的文件
^^^^^^^^^^^^^^^^^^^^^^^

``lsof``（List Open Files）是排查文件和网络问题的利器。
在 Linux 中，"一切皆文件"，所以 ``lsof`` 能查看文件、目录、网络连接、设备等。

**比喻**：``lsof`` 就像一个侦探——它能告诉你"这个文件被谁打开了"、
"这个端口被谁占用了"。

.. code-block:: bash

   # 列出某个进程打开的所有文件
   lsof -p PID

   # 列出某个用户打开的文件
   lsof -u username

   # 查看某个文件被谁打开
   lsof /var/log/syslog

   # 查看某个端口被谁占用（最常用！）
   lsof -i :80
   lsof -i :8080

   # 查看所有网络连接
   lsof -i

   # 只看 TCP 连接
   lsof -i tcp

   # 只看 LISTEN 状态
   lsof -i -sTCP:LISTEN

   # 查看某个进程打开的所有网络连接
   lsof -i -p PID

   # 查看被删除但仍被占用的文件（磁盘空间未释放的元凶）
   lsof | grep deleted

**踩坑经验**：磁盘空间满了但找不到大文件？
很可能是有进程打开文件后删除了它，但进程还在运行，文件句柄未释放。
用 ``lsof | grep deleted`` 找到它，重启对应进程即可释放空间。


strace —— 系统调用追踪
^^^^^^^^^^^^^^^^^^^^^^^^

``strace`` 能追踪进程的每一次系统调用（读文件、写网络、申请内存等），
是调试程序行为的"X光机"。

**比喻**：``strace`` 就像给程序装了一个窃听器——你能看到它和内核之间的所有对话。

.. code-block:: bash

   # 追踪一个新程序
   strace ./myprogram

   # 追踪已运行的进程
   strace -p PID

   # 只追踪文件相关的系统调用
   strace -e trace=file ./myprogram

   # 只追踪网络相关的系统调用
   strace -e trace=network ./myprogram

   # 只追踪进程管理相关
   strace -e trace=process ./myprogram

   # 统计每个系统调用的耗时
   strace -c ./myprogram

   # 显示时间戳
   strace -t ./myprogram

   # 显示微秒级时间
   strace -tt ./myprogram

   # 输出到文件（避免刷屏）
   strace -o trace.log ./myprogram

   # 追踪子进程
   strace -f ./myprogram

**输出解读**：

.. code-block:: text

   open("/etc/nginx/nginx.conf", O_RDONLY) = 3
   ^^^^  ^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^  ^
   系统调用  参数                    标志      返回的文件描述符

   read(3, "worker_processes auto;\n...", 4096) = 1234
   ^^^^  ^  ^^^^^^^^^^^^^^^^^^^^^^  ^^^^  ^^^^
   调用  fd  读到的内容              缓冲区大小 实际读取字节数

**实际调试场景**：

1. **程序卡住不动**：``strace -p PID`` 看它卡在哪个系统调用
2. **找不到配置文件**：``strace -e trace=open,openat`` 看程序尝试打开哪些路径
3. **程序启动慢**：``strace -T`` 看哪个系统调用耗时最长
4. **权限问题**：看 ``open()`` 返回 ``-1 EACCES``


进程控制
--------

信号机制 —— 进程间的"喊话"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

信号是 Linux 中进程间通信（IPC）的最简单形式。就像给进程"喊话"，
进程可以选择"听到并处理"或"装作没听到"（除了 SIGKILL）。

**比喻**：信号就像门铃——大部分时候主人会来开门（处理信号），
但你可以选择拆掉门铃（忽略信号）。唯独 SIGKILL 像是警察踢门，无法回避。

信号表详解
""""""""""

+-------------+------+----------------+------------------------------------------+
| 信号        | 编号 | 含义           | 场景                                     |
+=============+======+================+==========================================+
| ``SIGTERM`` | 15   | 请求终止       | ``kill PID``，可被捕获，优雅关闭         |
+-------------+------+----------------+------------------------------------------+
| ``SIGKILL`` | 9    | 强制终止       | ``kill -9 PID``，不可捕获，立即杀死      |
+-------------+------+----------------+------------------------------------------+
| ``SIGINT``  | 2    | 中断           | 用户按 Ctrl+C                            |
+-------------+------+----------------+------------------------------------------+
| ``SIGHUP``  | 1    | 挂起/重载      | 终端断开；常用于让守护进程重新加载配置    |
+-------------+------+----------------+------------------------------------------+
| ``SIGUSR1`` | 10   | 用户自定义1    | 应用自定义用途（如日志轮转）             |
+-------------+------+----------------+------------------------------------------+
| ``SIGUSR2`` | 12   | 用户自定义2    | 应用自定义用途                           |
+-------------+------+----------------+------------------------------------------+
| ``SIGSEGV`` | 11   | 段错误         | 内存访问违规，通常导致程序崩溃           |
+-------------+------+----------------+------------------------------------------+
| ``SIGCHLD`` | 17   | 子进程退出     | 父进程收到子进程结束通知                 |
+-------------+------+----------------+------------------------------------------+
| ``SIGSTOP`` | 19   | 暂停           | 不可捕获，暂停进程                       |
+-------------+------+----------------+------------------------------------------+
| ``SIGCONT`` | 18   | 继续           | 恢复被暂停的进程                         |
+-------------+------+----------------+------------------------------------------+
| ``SIGPIPE`` | 13   | 管道破裂       | 向已关闭的管道写数据                     |
+-------------+------+----------------+------------------------------------------+
| ``SIGALRM`` | 14   | 定时器到期     | ``alarm()`` 超时                         |
+-------------+------+----------------+------------------------------------------+

**关键理解**：

- SIGTERM（15）：礼貌地请进程退出，进程可以清理资源后退出，也可以忽略
- SIGKILL（9）：最后手段，直接由内核杀死进程，进程没有机会清理
- SIGHUP（1）：常被 nginx、sshd 等守护进程用来重新加载配置文件


kill —— 发送信号
^^^^^^^^^^^^^^^^^

``kill`` 的名字有误导性——它不只是"杀死"进程，而是向进程发送任意信号。

.. code-block:: bash

   # 发送 SIGTERM（默认信号，优雅终止）
   kill PID
   kill -15 PID
   kill -SIGTERM PID

   # 强制杀死（最后手段）
   kill -9 PID
   kill -SIGKILL PID

   # 重新加载配置（nginx、sshd 等支持）
   kill -HUP PID
   kill -1 PID

   # 暂停进程
   kill -STOP PID

   # 恢复进程
   kill -CONT PID

   # 向进程组发送信号（注意负号）
   kill -TERM -PGID

**踩坑经验**：先试 ``kill PID``（SIGTERM），等几秒还没死再用 ``kill -9 PID``。
直接 ``kill -9`` 可能导致数据丢失，因为进程没有机会执行清理代码。


killall / pkill —— 批量杀死
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # 按名称杀死所有同名进程
   killall nginx

   # 按模式匹配杀死
   pkill -f "python server.py"

   # 按用户杀死
   pkill -u username

   # 只发信号不杀死（dry run）
   pkill -SIGTERM -f "python server.py"


nohup —— 终端断开不退出
^^^^^^^^^^^^^^^^^^^^^^^^^

``nohup``（No Hang Up）让进程忽略 SIGHUP 信号，这样即使终端断开，进程也不会退出。

**比喻**：``nohup`` 就像把孩子寄养在别人家——你（终端）走了，
孩子（进程）还能继续生活。

.. code-block:: bash

   # 后台运行，输出写入 nohup.out
   nohup ./program &

   # 后台运行，输出重定向到文件
   nohup ./program > output.log 2>&1 &

   # 配合 disown 更彻底（从 shell 的 job 表中移除）
   nohup ./program > output.log 2>&1 &
   disown

**踩坑经验**：``nohup`` 只保证 SIGHUP 不会杀死进程，
但如果程序本身往 stdout/stderr 写数据且没有重定向，
管道破裂（SIGPIPE）仍然可能杀死它。所以务必重定向输出。


jobs / fg / bg —— 任务控制
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # 查看当前 shell 的后台任务
   jobs -l

   # 将前台任务放到后台（先 Ctrl+Z 暂停）
   # Ctrl+Z
   bg %1

   # 将后台任务调回前台
   fg %1

   # 运行一个新任务在后台
   ./long_running_task &


nice / renice —— 进程优先级
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``nice`` 值范围从 -20（最高优先级）到 19（最低优先级），默认值为 0。

**比喻**：``nice`` 值就像排队的"谦让程度"——越 nice（值越大）的人越谦让，
让别人先用 CPU。值为负就是"霸道"，优先抢占 CPU。

.. code-block:: bash

   # 以低优先级启动程序（nice 值为 10）
   nice -n 10 ./myprogram

   # 以高优先级启动程序（需要 root 权限）
   sudo nice -n -20 ./myprogram

   # 修改已运行进程的优先级
   renice 10 -p PID         # 设置为 10
   renice -5 -p PID         # 设置为 -5（需要 root）
   renice 15 -u username    # 修改用户所有进程

   # 查看进程的 nice 值
   ps -o pid,ni,comm -p PID

**实用场景**：

- 编译大型项目时用 ``nice -n 19 make -j8``，不影响正常工作
- 数据库进程用 ``renice -5`` 提高优先级


trap —— Shell 信号处理
^^^^^^^^^^^^^^^^^^^^^^

``trap`` 让 shell 脚本能够捕获和处理信号，实现优雅退出。

**比喻**：``trap`` 就像给程序装了一个"应急方案"——收到信号时执行清理，
而不是直接崩溃。

.. code-block:: bash

   # 捕获 Ctrl+C，执行清理
   trap 'echo "收到中断信号，正在清理..."; rm -f /tmp/mylock; exit 1' INT

   # 捕获退出信号（脚本结束时执行）
   trap 'echo "脚本退出"; cleanup_function' EXIT

   # 忽略信号
   trap '' HUP

   # 恢复默认行为
   trap - INT

   # 实际使用示例：带锁的脚本
   #!/bin/bash
   LOCKFILE="/tmp/myjob.lock"

   cleanup() {
       rm -f "$LOCKFILE"
       echo "清理完成"
   }
   trap cleanup EXIT

   if [ -f "$LOCKFILE" ]; then
       echo "另一个实例正在运行"
       exit 1
   fi
   touch "$LOCKFILE"

   # ... 主逻辑 ...
   sleep 100


守护进程（Daemon）创建模式
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

守护进程是在后台运行的长期服务进程，不依赖任何终端。

**比喻**：普通进程像商店前台——关门（终端关闭）就下班了。
守护进程像保安——24小时值班，不受商店开关门影响。

.. code-block:: bash

   # 守护进程的典型特征（代码层面）：
   # 1. fork() 两次，让父进程退出
   # 2. setsid() 创建新会话，脱离终端
   # 3. chdir("/") 切换到根目录
   # 4. 关闭 stdin/stdout/stderr
   # 5. 重定向到 /dev/null 或日志文件

   # 简单的守护进程包装（shell 层面）
   #!/bin/bash
   (
     # 子 shell 中运行
     cd /
     exec > /var/log/mydaemon.log 2>&1
     exec < /dev/null
     setsid ./myprogram &
   )

   # 更推荐的方式：使用 systemd 管理（见"服务管理"章节）


系统资源
--------

系统资源监控就像给服务器做体检——定期检查 CPU、内存、磁盘、I/O 等指标，
及早发现问题。


free —— 内存使用
^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # 人类可读的格式
   free -h

   # 每 2 秒刷新一次
   free -h -s 2

   # 以 MB 为单位
   free -m

**输出解读**：

.. code-block:: text

                  total        used        free      shared  buff/cache   available
   Mem:           15Gi       8.0Gi       2.0Gi       512Mi       5.0Gi       6.5Gi
   Swap:         2.0Gi       0.0Gi       2.0Gi

- ``total``：物理内存总量
- ``used``：已使用（不含 buff/cache）
- ``free``：完全空闲
- ``buff/cache``：缓冲区/缓存（可回收）
- ``available``：可用内存（= free + 可回收的 buff/cache）——**看这个！**

**踩坑经验**：``free`` 很小不要慌！Linux 会积极使用空闲内存做缓存，
真正重要的是 ``available`` 列。只有当 ``available`` 持续很低时才需要担心。


df —— 磁盘空间
^^^^^^^^^^^^^^^

.. code-block:: bash

   # 查看磁盘使用（人类可读）
   df -h

   # 只看本地文件系统（排除 tmpfs 等）
   df -h -x tmpfs

   # 查看 inode 使用情况（小文件多时可能 inode 耗尽）
   df -i

   # 查看指定目录所在的文件系统
   df -h /home

**踩坑经验**：磁盘空间没满但报 "No space left on device"？
检查 inode 是否耗尽（``df -i``）。大量小文件（如邮件队列、日志碎片）会耗尽 inode。


lscpu —— CPU 信息
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # 查看 CPU 架构信息
   lscpu

   # 关键字段：
   # Architecture:        x86_64      # 架构
   # CPU(s):              8           # 逻辑核心数
   # Thread(s) per core:  2           # 每核心线程数（超线程）
   # Core(s) per socket:  4           # 每 CPU 核心数
   # Socket(s):           1           # CPU 插槽数
   # Model name:          Intel(R) Core(TM) i7-xxxx

   # 快速查看 CPU 核心数
   nproc
   nproc --all


vmstat —— 虚拟内存统计
^^^^^^^^^^^^^^^^^^^^^^^^

``vmstat`` 显示系统的整体性能概况，包括 CPU、内存、I/O 等。

**比喻**：``vmstat`` 就像医院的综合体检报告——一页纸能看到所有关键指标。

.. code-block:: bash

   # 每 2 秒刷新一次，共显示 10 次
   vmstat 2 10

   # 显示活跃/非活跃内存
   vmstat -a

   # 以 MB 为单位
   vmstat -S M

**输出解读**：

.. code-block:: text

   procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu----
    r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs  us sy id wa
    1  0      0 204800  51200 512000    0    0     5    10  200  400   5  2 92  1

- ``r``：等待运行的进程数（> CPU 核心数说明 CPU 不够用）
- ``b``：不可中断睡眠的进程数（通常在等 I/O）
- ``si/so``：swap in/out（大量换入换出说明内存不足）
- ``bi/bo``：块设备读写（单位 KB/s）
- ``us/sy/id/wa``：CPU 时间分布（用户态/内核态/空闲/等待I/O）

**实用场景**：``wa``（等待 I/O）持续很高，说明磁盘是瓶颈。


iostat —— I/O 统计
^^^^^^^^^^^^^^^^^^^^

``iostat`` 显示磁盘和 CPU 的详细 I/O 统计。

.. code-block:: bash

   # 只看磁盘 I/O（排除 CPU）
   iostat -d

   # 每 2 秒刷新
   iostat -d 2

   # 显示扩展信息（包含 await、%util 等关键指标）
   iostat -dx

   # 以 MB 为单位
   iostat -dm

**关键指标**：

- ``%util``：设备繁忙百分比（> 70% 说明磁盘接近瓶颈）
- ``await``：平均 I/O 等待时间（毫秒，> 10ms 需要关注）
- ``r/s, w/s``：每秒读写次数（IOPS）
- ``rkB/s, wkB/s``：每秒读写吞吐量


sar —— 系统活动报告
^^^^^^^^^^^^^^^^^^^^

``sar``（System Activity Reporter）能查看历史性能数据，是事后分析的利器。

.. code-block:: bash

   # 查看今天的 CPU 使用历史
   sar -u

   # 查看今天的内存使用历史
   sar -r

   # 查看今天的磁盘 I/O 历史
   sar -d

   # 查看今天的网络统计
   sar -n DEV

   # 查看昨天的数据
   sar -u -f /var/log/sysstat/sa$(date -d yesterday +%d)

   # 每 5 秒采样一次，共采样 12 次（1 分钟）
   sar -u 5 12

**踩坑经验**：``sar`` 依赖 ``sysstat`` 包和定时数据采集。
如果命令报错 "No data"，需要安装 ``sysstat`` 并启用定时采集：

.. code-block:: bash

   sudo apt install sysstat
   sudo sed -i 's/ENABLED="false"/ENABLED="true"/' /etc/default/sysstat
   sudo systemctl restart sysstat


ulimit —— 资源限制
^^^^^^^^^^^^^^^^^^^^

``ulimit`` 控制每个用户/进程能使用的系统资源上限。

**比喻**：``ulimit`` 就像给孩子设定零花钱上限——防止某个程序把系统资源花光。

.. code-block:: bash

   # 查看所有限制
   ulimit -a

   # 查看硬限制（只有 root 能修改）
   ulimit -H -a

   # 查看软限制（用户可修改，不能超过硬限制）
   ulimit -S -a

   # 最大打开文件数（最常见的调优项）
   ulimit -n           # 查看当前值
   ulimit -n 65535     # 设置为 65535（当前 shell 生效）

   # 开启 core dump（调试必备）
   ulimit -c unlimited

   # 最大进程数
   ulimit -u           # 查看
   ulimit -u 4096      # 设置

   # 最大文件大小（KB）
   ulimit -f unlimited

   # 最大栈大小
   ulimit -s unlimited

**永久修改**：编辑 ``/etc/security/limits.conf``：

.. code-block:: text

   # <domain>  <type>  <item>  <value>
   *           soft    nofile  65535
   *           hard    nofile  65535
   root        soft    nofile  65535
   root        hard    nofile  65535
   *           soft    nproc   4096
   *           hard    nproc   4096

**踩坑经验**：Web 服务器报 "Too many open files"？默认的 1024 太小了。
修改 ``/etc/security/limits.conf`` 后需要重新登录才生效。
对于 systemd 管理的服务，还需要在 service 文件中设置 ``LimitNOFILE``。


/proc/meminfo —— 内存详情
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # 查看详细内存信息
   cat /proc/meminfo

   # 关键字段：
   # MemTotal:       16384000 kB    # 总物理内存
   # MemFree:         2048000 kB    # 完全空闲
   # MemAvailable:    6553600 kB    # 可用内存（含可回收缓存）
   # Buffers:          512000 kB    # 块设备缓冲
   # Cached:          4096000 kB    # 页面缓存
   # SwapTotal:       2097152 kB    # Swap 总量
   # SwapFree:        2097152 kB    # Swap 空闲
   # Dirty:              1024 kB    # 等待写回磁盘的脏页

   # 快速查看可用内存
   awk '/MemAvailable/ {print $2/1024 " MB"}' /proc/meminfo


/proc/cpuinfo —— CPU 详情
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # 查看所有 CPU 核心信息
   cat /proc/cpuinfo

   # 查看 CPU 核心数
   grep -c processor /proc/cpuinfo

   # 查看 CPU 型号
   grep "model name" /proc/cpuinfo | head -1

   # 查看是否支持虚拟化
   grep -E "vmx|svm" /proc/cpuinfo


线程管理
--------

线程 vs 进程
^^^^^^^^^^^^

**进程**是资源分配的最小单位，**线程**是 CPU 调度的最小单位。

**比喻**：

- 进程像一个独立的办公室——有自己的桌子、文件柜、电话（独立的内存空间）
- 线程像办公室里的员工——共享同一间办公室的资源，但各自做不同的任务

一个进程可以包含多个线程，线程之间共享进程的内存空间（代码段、数据段、堆），
但每个线程有自己的栈和寄存器。

**为什么用线程**：

- 创建和切换线程比进程快（不需要复制地址空间）
- 线程间通信不需要 IPC（共享内存即可）
- 多线程能充分利用多核 CPU


查看线程
^^^^^^^^

.. code-block:: bash

   # ps 查看线程（-T 显示线程，-p 指定进程）
   ps -T -p PID

   # 显示 LWP（Light Weight Process，即线程 ID）和线程名
   ps -T -p PID -o pid,lwp,comm

   # top 的线程视图（-H 显示线程）
   top -H -p PID

   # 查看线程数
   cat /proc/PID/status | grep Threads

   # 查看线程目录
   ls /proc/PID/task/
   # 每个子目录对应一个线程，目录名就是线程 ID（TID）

   # 查看某个线程的状态
   cat /proc/PID/task/TID/status

   # 查看线程的调用栈
   cat /proc/PID/task/TID/stack

   # 使用 htop 查看线程（按 H 键切换线程显示）


线程状态
^^^^^^^^

线程状态与进程状态相同：

- ``R``（Running）：正在运行或等待 CPU
- ``S``（Sleeping）：可中断睡眠（等待事件）
- ``D``（Disk Sleep）：不可中断睡眠（通常在等 I/O，信号无法打断）
- ``Z``（Zombie）：已退出但未被回收
- ``T``（Stopped）：被信号停止

.. code-block:: bash

   # 查看所有线程的状态
   ps -T -p PID -o pid,tid,stat,comm

   # 只看阻塞在 I/O 上的线程（D 状态）
   ps -T -p PID -o pid,tid,stat,comm | grep "^ *D"


pthread 基础
^^^^^^^^^^^^^

POSIX 线程（pthread）是 Linux 上标准的线程编程接口。

.. code-block:: c

   /* pthread 基本用法示例 */
   #include <pthread.h>
   #include <stdio.h>

   void* thread_func(void* arg) {
       printf("线程 %ld 运行中\n", (long)arg);
       return NULL;
   }

   int main() {
       pthread_t threads[3];
       for (long i = 0; i < 3; i++) {
           pthread_create(&threads[i], NULL, thread_func, (void*)i);
       }
       for (int i = 0; i < 3; i++) {
           pthread_join(threads[i], NULL);  // 等待线程结束
       }
       return 0;
   }

编译时需要链接 pthread 库：

.. code-block:: bash

   gcc -pthread thread_example.c -o thread_example


Core Dump 调试
--------------

什么是 Core Dump
^^^^^^^^^^^^^^^^

Core dump 是进程崩溃时操作系统自动生成的内存快照文件。
它记录了崩溃瞬间进程的完整内存状态、寄存器值和调用栈。

**比喻**：Core dump 就像飞机的黑匣子——坠毁后通过它可以还原事故现场，
找到崩溃的原因。

**为什么需要 Core Dump**：

- 某些 bug 只在特定条件下触发，难以复现
- 崩溃瞬间的变量状态对定位问题至关重要
- 比 "Segmentation fault" 这一行错误信息有用一万倍


开启 Core Dump
^^^^^^^^^^^^^^

.. code-block:: bash

   # 查看当前限制
   ulimit -a

   # 开启 core dump（无限大小）
   ulimit -c unlimited

   # 设置 core 文件路径和命名
   sysctl -w kernel.core_pattern=/tmp/core.%e.%p

   # 或者直接写文件
   echo "/tmp/core.%e.%p" > /proc/sys/kernel/core_pattern

   # 查看是否生效
   cat /proc/sys/kernel/core_pattern

**core_pattern 命名参数**：

- ``%e``：可执行文件名
- ``%p``：进程 PID
- ``%t``：崩溃时间戳
- ``%h``：主机名
- ``%u``：用户 ID

**示例**：``kernel.core_pattern=/tmp/core.%e.%p.%t`` 生成类似
``/tmp/core.myapp.12345.1688000000`` 的文件。

**永久配置**：

.. code-block:: bash

   # /etc/security/limits.conf
   *  soft  core  unlimited
   *  hard  core  unlimited

   # /etc/sysctl.d/core.conf
   kernel.core_pattern = /tmp/core.%e.%p
   kernel.core_uses_pid = 1

   # 应用 sysctl 配置
   sudo sysctl --system


生成 Core Dump 的方法
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # 方法 1：程序自然崩溃（段错误、断言失败等）
   ./myprogram    # 如果崩溃且 ulimit -c 已开启，自动生成

   # 方法 2：手动向运行中的进程发送信号
   kill -SIGSEGV PID    # 模拟段错误
   kill -ABRT PID       # 发送 abort 信号

   # 方法 3：使用 gcore 命令（不需要崩溃）
   gcore PID            # 生成 core 文件但不杀死进程

   # 方法 4：systemd 管理的进程
   # 确保 systemd 允许 core dump
   systemctl set-property myservice LimitCORE=infinity
   # 或在 service 文件中添加 LimitCORE=infinity


分析 Core Dump
^^^^^^^^^^^^^^

使用 GDB 分析 core dump 文件是定位崩溃原因的标准方法。

.. code-block:: bash

   # 基本用法：加载可执行文件和 core 文件
   gdb ./program core.12345

   # 进入 GDB 后的常用命令：

   # (gdb) bt          # 查看调用栈（backtrace）—— 最常用！
   # (gdb) bt full     # 查看调用栈 + 每帧的局部变量
   # (gdb) frame 3     # 切换到第 3 帧
   # (gdb) info locals # 查看当前帧的局部变量
   # (gdb) print var   # 打印变量值
   # (gdb) list        # 显示崩溃点附近的源代码
   # (gdb) info threads # 查看所有线程
   # (gdb) thread 2    # 切换到线程 2

   # 查看崩溃时的寄存器状态
   # (gdb) info registers

   # 查看内存内容
   # (gdb) x/20x $rsp  # 查看栈指针附近的 20 个字（十六进制）

**完整调试流程**：

.. code-block:: bash

   # 1. 确保程序带调试信息编译
   gcc -g -O0 myprogram.c -o myprogram

   # 2. 运行程序，等待崩溃
   ./myprogram
   # Segmentation fault (core dumped)

   # 3. 找到 core 文件
   ls -la /tmp/core.*

   # 4. 用 GDB 分析
   gdb ./myprogram /tmp/core.myprogram.12345

   # 5. 在 GDB 中
   # (gdb) bt
   # #0  0x00007f1234567890 in strlen () from /lib/x86_64-linux-gnu/libc.so.6
   # #1  0x0000555555555200 in process_name (name=0x0) at main.c:42
   # #2  0x0000555555555300 in main () at main.c:80

   # 6. 分析：frame 1 显示 name=0x0（空指针），第 42 行传入了空指针


常见 Core Dump 原因
^^^^^^^^^^^^^^^^^^^^

1. **空指针解引用**：访问 ``NULL`` 指针
2. **数组越界**：访问数组外的内存
3. **Use-After-Free**：释放内存后继续使用
4. **Double-Free**：同一块内存释放两次
5. **栈溢出**：递归过深或栈上分配过大
6. **断言失败**：``assert()`` 条件不满足
7. **非法指令**：执行了非法的机器指令

**排查技巧**：

.. code-block:: bash

   # 使用 AddressSanitizer 编译（检测内存错误）
   gcc -fsanitize=address -g myprogram.c -o myprogram

   # 使用 Valgrind（检测内存泄漏和非法访问）
   valgrind --leak-check=full ./myprogram


服务管理
--------

systemd 是现代 Linux 发行版的初始化系统和服务管理器。
它负责系统启动时启动服务、运行时管理服务、以及服务崩溃时重启服务。

**比喻**：systemd 就像公司的行政管理部门——负责开门（启动）、关门（停止）、
员工请假时安排替补（自动重启）。


systemctl 基础
^^^^^^^^^^^^^^

.. code-block:: bash

   # 启动服务
   sudo systemctl start nginx

   # 停止服务
   sudo systemctl stop nginx

   # 重启服务
   sudo systemctl restart nginx

   # 重新加载配置（不中断服务，如果支持的话）
   sudo systemctl reload nginx

   # 查看服务状态
   systemctl status nginx

   # 开机自启
   sudo systemctl enable nginx

   # 取消开机自启
   sudo systemctl disable nginx

   # 查看所有运行中的服务
   systemctl list-units --type=service --state=running

   # 查看所有服务（包括未运行的）
   systemctl list-units --type=service --all

   # 查看服务是否启用（开机自启）
   systemctl is-enabled nginx

   # 查看服务是否活跃（正在运行）
   systemctl is-active nginx


查看服务日志
^^^^^^^^^^^^

``journalctl`` 是 systemd 的日志查看工具，比翻日志文件方便得多。

.. code-block:: bash

   # 查看某个服务的全部日志
   journalctl -u nginx

   # 实时跟踪日志（类似 tail -f）
   journalctl -u nginx -f

   # 只看最近 100 行
   journalctl -u nginx -n 100

   # 看今天的日志
   journalctl -u nginx --since today

   # 看某个时间段
   journalctl -u nginx --since "2026-06-29 10:00" --until "2026-06-29 12:00"

   # 只看错误
   journalctl -u nginx -p err

   # 只看警告及以上
   journalctl -u nginx -p warning

   # 查看上次启动的日志
   journalctl -u nginx -b -1


自定义 systemd Service 文件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Service 文件通常放在 ``/etc/systemd/system/`` 目录下。

.. code-block:: ini

   # /etc/systemd/system/myapp.service

   [Unit]
   Description=My Application
   After=network.target          # 在网络就绪后启动
   Wants=network.target          # 依赖网络

   [Service]
   Type=simple                   # 进程类型
   User=appuser                  # 运行用户
   Group=appgroup                # 运行用户组
   WorkingDirectory=/opt/myapp   # 工作目录
   ExecStart=/opt/myapp/bin/start  # 启动命令
   ExecReload=/bin/kill -HUP $MAINPID  # 重载命令
   ExecStop=/bin/kill -TERM $MAINPID   # 停止命令

   # 重启策略
   Restart=on-failure            # 失败时自动重启
   RestartSec=5                  # 重启间隔 5 秒

   # 资源限制
   LimitNOFILE=65535             # 最大打开文件数
   LimitCORE=infinity            # 允许 core dump

   # 安全加固
   NoNewPrivileges=true          # 禁止提升权限
   ProtectSystem=strict          # 保护系统目录
   PrivateTmp=true               # 独立的 /tmp

   # 日志
   StandardOutput=journal        # stdout 输出到 journal
   StandardError=journal         # stderr 输出到 journal
   SyslogIdentifier=myapp        # syslog 标识符

   [Install]
   WantedBy=multi-user.target    # 多用户模式下启动

.. code-block:: bash

   # 创建 service 文件后，重新加载 systemd
   sudo systemctl daemon-reload

   # 启动并启用
   sudo systemctl start myapp
   sudo systemctl enable myapp

   # 查看状态
   systemctl status myapp

**Service Type 说明**：

- ``simple``：主进程就是服务进程（最常用）
- ``forking``：主进程 fork 出子进程后退出（传统守护进程）
- ``oneshot``：执行一次就结束（如初始化脚本）
- ``notify``：服务启动完成后会通知 systemd


服务状态含义
^^^^^^^^^^^^

``systemctl status`` 输出中的状态含义：

- ``active (running)``：正在运行
- ``active (exited)``：一次性任务已成功完成
- ``active (waiting)``：等待某个事件
- ``inactive (dead)``：未运行
- ``failed``：启动失败或异常退出
- ``activating (start)``：正在启动
- ``deactivating (stop)``：正在停止


系统日志
--------

系统日志是排查问题的第一手资料。Linux 有多个日志来源，了解它们的位置和用途至关重要。


/var/log 目录
^^^^^^^^^^^^^

.. code-block:: bash

   # 常见日志文件
   /var/log/syslog          # Debian/Ubuntu 系统日志（全局）
   /var/log/messages        # CentOS/RHEL 系统日志（全局）
   /var/log/auth.log        # 认证日志（登录、sudo）
   /var/log/kern.log        # 内核日志
   /var/log/dmesg           # 启动时的内核消息
   /var/log/boot.log        # 启动日志
   /var/log/apt/            # 包管理日志（Debian/Ubuntu）
   /var/log/yum.log         # 包管理日志（CentOS/RHEL）
   /var/log/nginx/          # Nginx 日志
   /var/log/mysql/          # MySQL 日志

.. code-block:: bash

   # 实时跟踪系统日志
   tail -f /var/log/syslog

   # 搜索日志
   grep "error" /var/log/syslog
   grep -i "oom" /var/log/syslog    # 搜索 OOM（内存不足）事件

   # 按时间范围查看
   awk '/Jun 29 10:00/,/Jun 29 11:00/' /var/log/syslog


dmesg —— 内核日志
^^^^^^^^^^^^^^^^^^

``dmesg`` 显示内核的环形缓冲区日志，包含硬件检测、驱动加载、内核错误等信息。

**比喻**：``dmesg`` 就像主板的自检报告——告诉你硬件和内核层面发生了什么。

.. code-block:: bash

   # 查看所有内核日志
   dmesg

   # 只看错误和警告
   dmesg -l err,warn

   # 实时跟踪
   dmesg -w

   # 显示时间戳（人类可读）
   dmesg -T

   # 搜索 OOM Killer 事件（内存不足时内核会杀死进程）
   dmesg | grep -i "oom"
   dmesg | grep -i "killed process"

   # 搜索硬件错误
   dmesg | grep -i "error"
   dmesg | grep -i "fail"

   # 搜索磁盘错误
   dmesg | grep -i "i/o error"
   dmesg | grep -i "sector"

**实际场景**：程序莫名消失？检查 ``dmesg`` 看是不是 OOM Killer 杀的。


journalctl —— systemd 日志
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``journalctl`` 是 systemd 的统一日志管理工具，比传统的日志文件更强大。

.. code-block:: bash

   # 查看所有日志
   journalctl

   # 实时跟踪
   journalctl -f

   # 只看本次启动的日志
   journalctl -b

   # 看上次启动的日志
   journalctl -b -1

   # 按优先级过滤
   journalctl -p err           # 只看错误
   journalctl -p warning       # 警告及以上

   # 按时间过滤
   journalctl --since "2026-06-29 10:00"
   journalctl --since "1 hour ago"
   journalctl --since today

   # 按服务过滤
   journalctl -u nginx
   journalctl -u nginx -u mysql    # 多个服务

   # 按进程 ID 过滤
   journalctl _PID=1234

   # 按可执行文件过滤
   journalctl /usr/bin/nginx

   # 查看内核日志（等同 dmesg）
   journalctl -k

   # 输出格式
   journalctl -o json-pretty    # JSON 格式
   journalctl -o verbose        # 详细格式

   # 查看磁盘使用
   journalctl --disk-usage

   # 清理旧日志
   journalctl --vacuum-time=7d      # 保留 7 天
   journalctl --vacuum-size=500M    # 保留 500MB


日志分析技巧
^^^^^^^^^^^^

.. code-block:: bash

   # 统计错误数量
   journalctl -p err --since today | wc -l

   # 统计每个服务的错误数
   journalctl -p err -o json --since today | \
     jq '._SYSTEMD_UNIT' | sort | uniq -c | sort -rn

   # 找出最近重启过的服务
   journalctl -p warning --since today | grep -i "start"

   # 搜索 OOM 事件
   journalctl -k | grep -i "oom"

   # 实时监控多个服务
   journalctl -u nginx -u mysql -f


附录：常用命令速查
------------------

进程查看
^^^^^^^^

+-------------------------+------------------------------------------+
| 命令                    | 用途                                     |
+=========================+==========================================+
| ``ps aux``              | 查看所有进程                             |
+-------------------------+------------------------------------------+
| ``ps -T -p PID``        | 查看进程的线程                           |
+-------------------------+------------------------------------------+
| ``pstree -p``           | 进程树（带 PID）                         |
+-------------------------+------------------------------------------+
| ``top`` / ``htop``      | 实时监控                                 |
+-------------------------+------------------------------------------+
| ``pgrep -l name``       | 按名称查找进程                           |
+-------------------------+------------------------------------------+
| ``pidof name``          | 精确查找进程 PID                         |
+-------------------------+------------------------------------------+
| ``lsof -i :PORT``       | 查看端口占用                             |
+-------------------------+------------------------------------------+
| ``lsof -p PID``         | 查看进程打开的文件                       |
+-------------------------+------------------------------------------+
| ``strace -p PID``       | 追踪系统调用                             |
+-------------------------+------------------------------------------+
| ``cat /proc/PID/status``| 查看进程状态详情                         |
+-------------------------+------------------------------------------+

进程控制
^^^^^^^^

+---------------------------+------------------------------------------+
| 命令                      | 用途                                     |
+===========================+==========================================+
| ``kill PID``              | 优雅终止（SIGTERM）                      |
+---------------------------+------------------------------------------+
| ``kill -9 PID``           | 强制杀死（SIGKILL）                      |
+---------------------------+------------------------------------------+
| ``kill -HUP PID``         | 重载配置                                 |
+---------------------------+------------------------------------------+
| ``killall name``          | 按名称杀死                               |
+---------------------------+------------------------------------------+
| ``pkill -f pattern``      | 按模式匹配杀死                           |
+---------------------------+------------------------------------------+
| ``nice -n N command``     | 以指定优先级启动                         |
+---------------------------+------------------------------------------+
| ``renice N -p PID``       | 修改进程优先级                           |
+---------------------------+------------------------------------------+
| ``nohup command &``       | 终端断开不退出                           |
+---------------------------+------------------------------------------+
| ``trap 'cmd' SIGNAL``     | Shell 信号处理                           |
+---------------------------+------------------------------------------+

系统资源
^^^^^^^^

+---------------------------+------------------------------------------+
| 命令                      | 用途                                     |
+===========================+==========================================+
| ``free -h``               | 内存使用                                 |
+---------------------------+------------------------------------------+
| ``df -h``                 | 磁盘空间                                 |
+---------------------------+------------------------------------------+
| ``df -i``                 | inode 使用                               |
+---------------------------+------------------------------------------+
| ``lscpu``                 | CPU 信息                                 |
+---------------------------+------------------------------------------+
| ``vmstat 2``              | 虚拟内存统计                             |
+---------------------------+------------------------------------------+
| ``iostat -dx``            | I/O 统计                                 |
+---------------------------+------------------------------------------+
| ``sar -u``                | CPU 历史                                 |
+---------------------------+------------------------------------------+
| ``ulimit -a``             | 查看资源限制                             |
+---------------------------+------------------------------------------+
| ``ulimit -c unlimited``   | 开启 core dump                           |
+---------------------------+------------------------------------------+
| ``ulimit -n 65535``       | 最大打开文件数                           |
+---------------------------+------------------------------------------+

服务管理
^^^^^^^^

+-------------------------------------+------------------------------------------+
| 命令                                | 用途                                     |
+=====================================+==========================================+
| ``systemctl start name``            | 启动服务                                 |
+-------------------------------------+------------------------------------------+
| ``systemctl stop name``             | 停止服务                                 |
+-------------------------------------+------------------------------------------+
| ``systemctl restart name``          | 重启服务                                 |
+-------------------------------------+------------------------------------------+
| ``systemctl status name``           | 查看状态                                 |
+-------------------------------------+------------------------------------------+
| ``systemctl enable name``           | 开机自启                                 |
+-------------------------------------+------------------------------------------+
| ``systemctl disable name``          | 取消自启                                 |
+-------------------------------------+------------------------------------------+
| ``journalctl -u name -f``           | 实时跟踪日志                             |
+-------------------------------------+------------------------------------------+
| ``journalctl -u name --since today``| 查看今日日志                             |
+-------------------------------------+------------------------------------------+

Core Dump
^^^^^^^^^

+------------------------------------------+------------------------------------------+
| 命令                                     | 用途                                     |
+==========================================+==========================================+
| ``ulimit -c unlimited``                  | 开启 core dump                           |
+------------------------------------------+------------------------------------------+
| ``sysctl -w kernel.core_pattern=...``    | 设置 core 文件路径                       |
+------------------------------------------+------------------------------------------+
| ``gdb ./program core.xxx``               | 分析 core dump                           |
+------------------------------------------+------------------------------------------+
| ``gcore PID``                            | 不崩溃生成 core                          |
+------------------------------------------+------------------------------------------+
| ``dmesg | grep oom``                     | 检查 OOM 事件                            |
+------------------------------------------+------------------------------------------+
