网络调试手册
============

本手册涵盖 Linux 下网络调试的核心工具与技术，从基础连通性测试到深层 TCP 调优，
适合嵌入式开发、服务器运维和物联网场景的日常排查。

.. contents:: 目录
   :depth: 2
   :local:


连接测试
--------

排查网络问题的第一步：确认"能不能通"。就像检查水管有没有水，先拧开龙头看看。


ping —— 基础连通性
^^^^^^^^^^^^^^^^^^

**是什么：** ping 使用 ICMP 协议发送回声请求（Echo Request），目标主机收到后返回回声应答（Echo Reply）。
它是最基本的网络诊断工具，告诉你"对方在不在线"以及"来回要多久"。

**为什么需要：** 任何网络问题排查都从 ping 开始。如果 ping 不通，说明物理链路、路由或防火墙有问题，
继续排查上层协议（HTTP、MQTT 等）毫无意义。

.. code-block:: bash

   # 基本测试 —— 发送 4 个 ICMP 包
   ping -c 4 8.8.8.8

   # 指定网卡（多网卡设备很有用）
   ping -I eth0 -c 4 192.168.1.1

   # 指定包大小（测试 MTU 问题）
   ping -s 1472 -c 4 192.168.1.1

   # 快速 ping（0.2 秒间隔，适合监控脚本）
   ping -i 0.2 -c 10 192.168.1.1

   # 仅显示统计结果（不逐行打印）
   ping -c 100 -q 8.8.8.8

输出解读：

- **rtt min/avg/max/mdev**：往返时延的最小/平均/最大/标准差，mdev 越大说明网络越不稳定
- **丢包率**：如果 > 0%，说明链路有问题

**比喻：** ping 就像在山谷里喊一声"喂"，然后听回声。如果听不到回声，要么山太远（路由问题），
要么中间有堵墙（防火墙拦截）。回声回来得慢，说明距离远或中间堵车（网络拥塞）。


traceroute —— 路由路径追踪
^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** traceroute 通过逐步增大 IP 包的 TTL（Time To Live）值，让路径上每个路由器
返回"超时"消息，从而揭示数据包经过的每一跳。

**为什么需要：** 当 ping 不通或延迟异常时，traceroute 告诉你问题出在哪一跳。
是运营商骨干网拥塞？还是某个中间节点故障？

.. code-block:: bash

   # 基本用法
   traceroute 8.8.8.8

   # 使用 TCP 探测（有些防火墙会拦截 ICMP，但放行 TCP）
   traceroute -T -p 80 8.8.8.8

   # 使用 UDP（默认方式，某些系统需要 root 权限用 TCP）
   traceroute -U 8.8.8.8

   # 指定最大跳数
   traceroute -m 15 8.8.8.8

输出解读：

- 每一行代表一跳，显示该跳的 IP 和三次探测的延迟
- 星号 ``*`` 表示该节点未响应（可能防火墙丢弃了探测包，不一定代表不通）
- 如果在某一跳之后全是星号，说明问题可能就在那一跳

**比喻：** traceroute 就像寄快递时追踪包裹。你能看到包裹从发货地出发，经过了哪些中转站，
每站花了多长时间。如果到了某个中转站就没了记录，问题就出在那里。


mtr —— 持续路径监控
^^^^^^^^^^^^^^^^^^^^

**是什么：** mtr 结合了 ping 和 traceroute 的功能，持续监控到目标的每一跳质量。
它是 traceroute 的"实时版"，不只是看一次快照，而是持续观察每一跳的延迟和丢包。

**为什么需要：** traceroute 只显示一次结果，但网络问题是间歇性的。mtr 持续运行，
能捕捉到偶发的丢包和延迟抖动，这在排查"偶尔断一下"的问题时特别有用。

.. code-block:: bash

   # 交互模式（实时刷新）
   mtr 8.8.8.8

   # 报告模式（跑 100 次后输出统计，适合脚本）
   mtr -r -c 100 8.8.8.8

   # 指定网卡
   mtr -I eth0 192.168.1.1

   # 使用 TCP 模式（绕过 ICMP 过滤）
   mtr -T -P 80 8.8.8.8

输出关键列：

- **Loss%**：该跳的丢包率，持续 > 0% 说明该节点有问题
- **Snt**：已发送的探测包数量
- **Avg**：平均延迟
- **Best/Wrst**：最好和最差延迟，差距大说明抖动严重

**实际踩坑经验：** 某些中间节点会限制 ICMP 响应速率，导致显示 80% 丢包，但实际业务完全正常。
判断方法：如果某一跳丢包率高，但后续跳的丢包率恢复正常，则该跳只是限速而非真的丢包。


telnet / nc —— 端口连通性
^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** telnet 和 nc（netcat）可以测试 TCP 端口是否可达。ping 测的是 IP 层连通性，
而端口测试测的是传输层——服务是否真的在监听。

**为什么需要：** 服务明明启动了却连不上？90% 的情况是防火墙拦截或服务没监听在预期地址。
telnet/nc 能快速排除连接层的问题。

.. code-block:: bash

   # telnet 测试端口
   telnet 192.168.1.100 1883

   # nc 测试端口（推荐，输出更清晰）
   nc -zv 192.168.1.100 1883

   # nc 测试端口范围
   nc -zv 192.168.1.100 80-443

   # nc 超时设置（默认容易卡住）
   nc -zv -w 3 192.168.1.100 1883

   # nc 发送数据测试（调试 HTTP/MQTT 握手）
   echo -e "GET / HTTP/1.0\r\n\r\n" | nc example.com 80

**输出解读：**

- ``Connection refused`` —— 端口没有服务在监听（不是防火墙问题，是服务没启动）
- ``Connection timed out`` —— 被防火墙丢包了（中间有东西在拦截）
- ``Connected`` —— 端口可达，TCP 三次握手成功

**比喻：** ping 是检查"这栋楼在不在"，telnet/nc 是检查"这扇门开不开"。
楼在但门锁着（Connection refused），说明服务没启动；走到门口发现人不见了（timeout），
说明保安（防火墙）把你拦住了。


nslookup / dig —— DNS 查询
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** nslookup 和 dig 用于查询 DNS 解析。域名到 IP 的映射关系由 DNS 服务器管理，
解析失败意味着"找不到门牌号"。

**为什么需要：** "网站打不开"但 ping IP 能通？大概率是 DNS 问题。DNS 是网络的"电话簿"，
电话簿查不到号码，自然打不了电话。

.. code-block:: bash

   # nslookup 基本查询
   nslookup example.com

   # 指定 DNS 服务器（排除本地 DNS 问题）
   nslookup example.com 8.8.8.8

   # dig 详细查询（推荐，信息更全）
   dig example.com

   # dig 仅看答案
   dig +short example.com

   # 查询特定记录类型
   dig MX example.com        # 邮件服务器
   dig CNAME www.example.com  # 别名
   dig NS example.com         # 域名服务器
   dig TXT example.com        # TXT 记录（SPF、DKIM 等）

   # 反向解析（IP 查域名）
   dig -x 8.8.8.8

   # 追踪完整解析路径
   dig +trace example.com

**踩坑经验：**

- Linux 的 DNS 缓存可能让你看到旧的解析结果。如果刚改了 DNS 记录但没生效，
  试试 ``systemd-resolve --flush-caches``（systemd 系统）
- ``/etc/resolv.conf`` 是 DNS 配置文件，但有些系统用 NetworkManager 管理它，
  直接编辑会被覆盖。用 ``resolvectl status`` 查看当前配置


curl / wget —— HTTP 层测试
^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** curl 和 wget 是 HTTP 客户端工具。当端口通了但服务"不好用"时，
需要用 curl 模拟真实请求来排查应用层问题。

**为什么需要：** TCP 连接建立成功不代表应用层正常。服务可能返回 500 错误、证书过期、
重定向异常等问题，只有发送真实 HTTP 请求才能发现。

.. code-block:: bash

   # 基本 GET 请求
   curl http://example.com

   # 详细模式（显示请求头、响应头、TLS 握手等）
   curl -v https://example.com

   # 仅获取 HTTP 状态码（快速检查服务是否正常）
   curl -s -o /dev/null -w "%{http_code}" https://example.com

   # 保存响应到文件
   curl -o output.html https://example.com

   # 跟随重定向
   curl -L http://example.com

   # 指定 HTTP 方法
   curl -X POST https://api.example.com/data
   curl -X PUT https://api.example.com/resource/1
   curl -X DELETE https://api.example.com/resource/1

   # 发送 JSON 数据
   curl -X POST https://api.example.com/data \
     -H "Content-Type: application/json" \
     -d '{"key": "value", "name": "test"}'

   # 发送表单数据
   curl -X POST https://api.example.com/login \
     -d "username=admin&password=secret"

   # 自定义请求头
   curl -H "Authorization: Bearer TOKEN123" \
     -H "X-Custom-Header: myvalue" \
     https://api.example.com/protected

   # 忽略 SSL 证书验证（调试自签名证书）
   curl -k https://self-signed.example.com

   # 查看 TLS 证书信息
   curl -vI https://example.com 2>&1 | grep -i "expire\|subject\|issuer"

   # 超时设置（脚本中很重要，避免永远卡住）
   curl --connect-timeout 5 --max-time 10 https://example.com

   # 使用代理
   curl -x http://proxy:8080 https://example.com

   # wget 下载文件
   wget https://example.com/file.tar.gz

   # wget 断点续传
   wget -c https://example.com/large-file.iso

   # wget 递归下载（镜像网站）
   wget -r -l 2 https://example.com/

**比喻：** telnet/nc 是"敲门确认有人"，curl 是"推门进去说话"。
curl -v 就像带了个录音笔，把整个对话过程（请求头、响应头、TLS 握手）全部记录下来，
事后可以逐字逐句分析。


端口与连接
----------

确认网络能通之后，下一步是看"谁在连谁"、"哪些端口在用"。


netstat / ss —— 连接状态查看
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** netstat 和 ss 都用于查看当前系统的网络连接、监听端口和 socket 状态。
ss 是 netstat 的现代替代品，速度更快（直接读 /proc，不走 netlink）。

**为什么需要：** 服务启动了但连不上？用 ss 确认它是否真的在监听。
连接数异常增长？用 ss 看看有多少连接、处于什么状态。

.. code-block:: bash

   # 查看 TCP 监听端口（最常用）
   ss -tlnp

   # 查看所有 TCP 连接
   ss -tnp

   # 查看 UDP 监听
   ss -ulnp

   # 按端口过滤
   ss -tlnp | grep :1883

   # 按状态过滤
   ss -tn state established
   ss -tn state time-wait

   # 查看 socket 统计摘要
   ss -s

   # netstat 等价写法（老系统兼容）
   netstat -tlnp
   netstat -an | grep :1883


ss 状态详解
^^^^^^^^^^^

TCP 连接有多种状态，理解它们是排查连接问题的关键。

.. code-block:: bash

   # 按状态分组统计（一看就知道哪里有问题）
   ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c | sort -rn

常见状态说明：

- **LISTEN** —— 服务端正在等待客户端连接。就像商店开门营业，等着客人进来。
- **ESTABLISHED** —— 连接已建立，双方正在通信。客人已经进店，正在交易。
- **TIME_WAIT** —— 主动关闭方等待 2MSL（通常 60 秒）后才释放端口。
  就像客人走后店家还要等一会儿才收拾桌子，防止客人忘了东西回来拿。
  高并发场景下 TIME_WAIT 堆积是常见问题。
- **CLOSE_WAIT** —— 被动关闭方收到 FIN 但还没发自己的 FIN。
  这通常是**应用代码 bug**——没有正确关闭 socket。就像对方挂了电话但你没挂。
- **SYN_SENT** —— 客户端发送了 SYN，等待服务端回应。如果大量堆积，说明服务端响应慢或不可达。
- **FIN_WAIT_1 / FIN_WAIT_2** —— 主动关闭方的不同阶段。
- **CLOSING** —— 双方同时关闭，比较少见。

.. code-block:: bash

   # 只看 CLOSE_WAIT（排查应用泄漏 socket）
   ss -tn state close-wait

   # 只看 TIME_WAIT（排查端口耗尽）
   ss -tn state time-wait | wc -l

   # 查看连接的进程信息
   ss -tnp | grep :1883

   # 查看连接的详细 timer 信息
   ss -tni | grep -A1 :1883

**实际踩坑经验：** 如果 CLOSE_WAIT 数量持续增长不释放，99% 是程序没有关闭 socket。
在嵌入式 MQTT 客户端中，断线重连时忘记 close() 旧 socket 是最常见的原因。


ip 命令族 —— 网络配置查看
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** ``ip`` 是现代 Linux 的网络配置工具，取代了 ifconfig、route、arp 等老命令。
它是一个统一的命令族，通过子命令管理地址、链路、路由、邻居等。

**为什么需要：** 查看 IP 地址、网卡状态、路由表、ARP 缓存——这些是网络调试的基础信息。

.. code-block:: bash

   # 查看所有网卡的 IP 地址
   ip addr show
   ip a               # 缩写

   # 查看指定网卡
   ip addr show eth0

   # 查看网卡链路状态（是否插网线、速率等）
   ip link show
   ip link show eth0

   # 启用/禁用网卡
   ip link set eth0 up
   ip link set eth0 down

   # 查看路由表
   ip route show
   ip r                # 缩写

   # 添加/删除路由
   ip route add 10.0.0.0/8 via 192.168.1.1
   ip route del 10.0.0.0/8

   # 查看 ARP 表（IP 到 MAC 的映射）
   ip neigh show
   ip n                # 缩写

   # 手动添加 ARP 条目
   ip neigh add 192.168.1.200 lladdr aa:bb:cc:dd:ee:ff dev eth0

   # 清除 ARP 缓存（切换网关后需要）
   ip neigh flush dev eth0

**比喻：**

- ``ip addr`` —— 查看"我家地址是什么"
- ``ip route`` —— 查看"去某个地方该走哪条路"
- ``ip neigh`` —— 查看"邻居们的门牌号和长相（MAC 地址）"。ARP 就是"先喊一声谁是 192.168.1.1，
  然后记住它的 MAC 地址"的过程。


iptables —— 包过滤防火墙
^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** iptables 是 Linux 内核的包过滤防火墙，通过规则链决定每个数据包的命运——
放行（ACCEPT）、丢弃（DROP）、拒绝（REJECT）或转发（NAT）。

**为什么需要：** "ping 能通但端口连不上"很可能是 iptables 规则在拦截。
理解 iptables 是排查防火墙问题的基础。

.. code-block:: bash

   # 查看所有规则（数字格式，不解析域名和服务名）
   iptables -L -n -v

   # 查看指定链
   iptables -L INPUT -n -v

   # 允许已建立的连接（必须有这条，否则回程包被丢弃）
   iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

   # 允许 SSH（端口 22）
   iptables -A INPUT -p tcp --dport 22 -j ACCEPT

   # 允许 MQTT（端口 1883）
   iptables -A INPUT -p tcp --dport 1883 -j ACCEPT

   # 允许来自特定 IP 的访问
   iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT

   # 拒绝其他所有入站连接
   iptables -A INPUT -j DROP

   # 删除规则（按行号）
   iptables -L INPUT --line-numbers
   iptables -D INPUT 3

   # 清空所有规则（谨慎！会断开远程连接）
   iptables -F

   # 保存规则（重启后生效取决于发行版）
   iptables-save > /etc/iptables/rules.v4

**比喻：** iptables 就像大楼的保安系统。每个来访者（数据包）都要经过一系列检查点（规则链），
保安根据规则决定放行还是拦下。``-L`` 是查看保安手册，``-A`` 是给保安加一条新规则。

**踩坑经验：** 远程服务器上修改 iptables 一定要先加允许 SSH 的规则，再加 DROP 规则。
否则你会把自己锁在外面。经验之谈：先加允许规则，测试 SSH 能连，再加拒绝规则。

详细的防火墙配置参见后面的 :ref:`防火墙与安全` 章节。


nftables —— iptables 的继任者
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** nftables 是 iptables 的替代品，从 Linux 内核 3.13 开始引入。
它使用统一的框架，语法更简洁，性能更好。

**为什么需要：** 新发行版（Debian 10+、RHEL 8+、Ubuntu 20.04+）逐步用 nftables 取代 iptables。
了解 nftables 能让你在新系统上也能操作防火墙。

.. code-block:: bash

   # 查看当前规则
   nft list ruleset

   # 创建表和链
   nft add table inet myfilter
   nft add chain inet myfilter input '{ type filter hook input priority 0; policy drop; }'

   # 添加允许规则
   nft add rule inet myfilter input tcp dport 22 accept
   nft add rule inet myfilter input tcp dport 1883 accept
   nft add rule inet myfilter input ct state established,related accept

   # 列出规则
   nft list chain inet myfilter input

   # 删除规则（先用 --handle 查看句柄号）
   nft list chain inet myfilter input -a
   nft delete rule inet myfilter input handle 5

   # 清空所有规则
   nft flush ruleset

**iptables vs nftables 对比：**

- nftables 用统一的 ``nft`` 命令，不再需要 iptables、ip6tables、arptables 等多个命令
- nftables 支持原子规则更新（不会出现加载一半的中间状态）
- nftables 的规则集更大时性能更好
- iptables 的 ``iptables-translate`` 工具可以将旧规则转为 nftables 格式


抓包分析
--------

当"能不能通"和"谁在连谁"都查完还是找不到问题时，就需要抓包——
直接看线缆里流动的每一个字节。这是网络调试的终极手段。


tcpdump —— 命令行抓包
^^^^^^^^^^^^^^^^^^^^^^

**是什么：** tcpdump 是最经典的网络抓包工具，直接捕获网卡上流过的原始数据包。
它在任何 Linux 系统上都能用，不需要图形界面，是嵌入式设备和服务器的首选。

**为什么需要：** 应用层日志说"连接超时"，但到底是没收到 SYN？还是收到了但没回？
还是 TCP 握手成功但应用层数据不对？只有抓包才能看到真相。

.. code-block:: bash

   # 抓取指定端口的所有流量
   tcpdump -i eth0 port 1883

   # 抓取指定主机的流量
   tcpdump -i eth0 host 192.168.1.100

   # 保存到文件（可用 Wireshark 打开分析）
   tcpdump -i eth0 -w capture.pcap

   # 读取抓包文件
   tcpdump -r capture.pcap

   # 限制抓包数量
   tcpdump -i eth0 -c 100 port 1883

   # 显示 ASCII 内容（看明文协议内容）
   tcpdump -i eth0 -A port 1883

   # 显示十六进制 + ASCII
   tcpdump -i eth0 -X port 80

   # 不解析主机名和端口名（加快速度）
   tcpdump -i eth0 -nn port 1883

   # 显示绝对序列号（分析 TCP 重传时需要）
   tcpdump -i eth0 -S port 1883


tcpdump 高级过滤
^^^^^^^^^^^^^^^^^

tcpdump 使用 BPF（Berkeley Packet Filter）语法进行过滤，支持 and、or、not 组合。

.. code-block:: bash

   # 组合条件：指定主机 AND 指定端口
   tcpdump -i eth0 host 192.168.1.100 and port 1883

   # OR 条件：抓两个端口
   tcpdump -i eth0 port 1883 or port 8883

   # NOT 条件：排除某个主机
   tcpdump -i eth0 not host 192.168.1.1

   # 只抓 TCP SYN 包（看连接建立过程）
   tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'

   # 只抓 TCP RST 包（看异常断开）
   tcpdump -i eth0 'tcp[tcpflags] & tcp-rst != 0'

   # 只抓 TCP FIN 包（看正常关闭）
   tcpdump -i eth0 'tcp[tcpflags] & tcp-fin != 0'

   # 只抓入站流量
   tcpdump -i eth0 inbound

   # 只抓出站流量
   tcpdump -i eth0 outbound

   # 按网段过滤
   tcpdump -i eth0 net 192.168.1.0/24

   # 按包大小过滤（大于 1000 字节的包）
   tcpdump -i eth0 'greater 1000'

   # 抓取 MQTT 流量（端口 1883，不解析，显示内容）
   tcpdump -i eth0 -nn -A port 1883

   # 抓取 MQTT over TLS（端口 8883，只能看握手，内容加密）
   tcpdump -i eth0 -nn port 8883

   # 按时间范围过滤（抓最近 60 秒的数据）
   tcpdump -i eth0 -G 60 -W 1 -w /tmp/capture.pcap port 1883

   # 每 10MB 切分文件（长时间抓包不撑爆磁盘）
   tcpdump -i eth0 -C 10 -w /tmp/capture.pcap port 1883

**实际踩坑经验：**

- 在高流量服务器上抓包，一定要加过滤条件，否则磁盘瞬间写满
- ``-w`` 写文件比直接打印到终端快得多，事后用 Wireshark 分析更方便
- MQTT 明文（1883）可以抓到内容，MQTT over TLS（8883）只能看到 TLS 握手，
  应用层数据是加密的


wireshark / tshark —— 图形化与命令行分析
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** Wireshark 是最强大的网络协议分析工具，tshark 是它的命令行版本。
tcpdump 只能抓包和简单过滤，Wireshark 能解析上千种协议，逐层展示每个字段。

**为什么需要：** 复杂的协议问题（TCP 重传、窗口缩小、TLS 握手失败等）用 tcpdump 看起来
是一堆十六进制，Wireshark 能把它们翻译成人能读懂的格式。

.. code-block:: bash

   # tshark 抓包（类似 tcpdump，但协议解析更强大）
   tshark -i eth0 -f "port 1883"

   # 保存到文件（Wireshark 兼容格式）
   tshark -i eth0 -f "port 1883" -w /tmp/mqtt.pcap

   # 读取并过滤
   tshark -r capture.pcap -Y "tcp.analysis.retransmission"

   # 统计 TCP 会话
   tshark -r capture.pcap -z conv,tcp

   # 查看 HTTP 请求
   tshark -r capture.pcap -Y "http.request" -T fields -e http.host -e http.request.uri

   # 统计协议分布
   tshark -r capture.pcap -z io,phs

**何时用哪个：**

- 快速抓包、脚本中使用 → tcpdump
- 深度协议分析、图形界面 → Wireshark
- 服务器上无图形界面但需要 Wireshark 级别的分析 → tshark

**比喻：** tcpdump 是"照 X 光"，能看到骨头（数据包）但细节有限。
Wireshark 是"做 CT"，能逐层切片，看清每根血管（协议字段）。


ngrep —— 网络 grep
^^^^^^^^^^^^^^^^^^^^

**是什么：** ngrep 是网络流量的 grep 工具，能在抓包的同时按正则表达式搜索内容。
它把网络数据当作"文本流"来搜索，就像 grep 搜索日志文件一样。

**为什么需要：** tcpdump 能抓包但不方便搜索内容。想在大量 MQTT 流量中找到包含
特定 Topic 的包？ngrep 一行搞定。

.. code-block:: bash

   # 搜索 HTTP 请求中的特定 URL
   ngrep -q -d eth0 "GET /api" port 80

   # 搜索 MQTT 中的特定 topic（明文 MQTT）
   ngrep -q -d eth0 "sensor/temperature" port 1883

   # 搜索包含特定字符串的所有 TCP 流量
   ngrep -q -d eth0 "error" tcp

   # 不指定接口（自动选择）
   ngrep -q "password" port 80

   # 忽略大小写
   ngrep -qi "error" port 80

   # 同时显示时间戳
   ngrep -q -t "keyword" port 1883

   # 保存到 pcap 文件
   ngrep -q -O /tmp/ngrep.pcap "keyword" port 1883

**比喻：** 如果 tcpdump 是在河里撒网捕鱼，ngrep 就是在河里只捞红色的鱼。
它不捕获所有流量，只捕获匹配你关键词的那部分。


TCP 调优
--------

默认的 Linux TCP 参数是为通用场景设计的。在嵌入式设备、弱网环境、高并发服务器等场景下，
调优内核参数可以显著提升网络性能和稳定性。


核心内核参数
^^^^^^^^^^^^

**窗口缩放（Window Scaling）**

.. code-block:: bash

   # 开启窗口缩放
   sysctl -w net.ipv4.tcp_window_scaling=1

**是什么：** TCP 头部的窗口字段只有 16 位，最大 65535 字节。窗口缩放选项允许将窗口大小
左移最多 14 位，理论最大可达 1GB。这是 RFC 1323 引入的特性。

**为什么调：** 默认 64KB 的窗口在高延迟链路上严重限制吞吐量。
根据带宽延迟积（BDP = 带宽 x RTT），100Mbps 带宽 + 100ms 延迟的链路需要至少 1.25MB 的窗口。

**比喻：** 窗口就像传送带的长度。传送带太短（窗口小），工人每装满一箱就要等对面清空，
高延迟时等待时间更长。加长传送带（窗口缩放）可以让更多货物在途中。

**缓冲区调优**

.. code-block:: bash

   # 增大 socket 缓冲区默认值
   sysctl -w net.core.rmem_default=262144    # 接收缓冲区默认 256KB
   sysctl -w net.core.wmem_default=262144    # 发送缓冲区默认 256KB

   # 增大 socket 缓冲区最大值
   sysctl -w net.core.rmem_max=16777216      # 接收最大 16MB
   sysctl -w net.core.wmem_max=16777216      # 发送最大 16MB

   # TCP 自动调优缓冲区（min, default, max）
   sysctl -w net.ipv4.tcp_rmem="4096 262144 16777216"
   sysctl -w net.ipv4.tcp_wmem="4096 262144 16777216"

**是什么：** socket 缓冲区是内核为每个 TCP 连接分配的收发数据暂存区。
数据从应用写入发送缓冲区，内核负责从缓冲区取出发送；接收端反过来。

**为什么调：** 默认缓冲区太小（通常几十 KB），在高延迟链路上，数据还没发完窗口就满了，
不得不停下来等 ACK。增大缓冲区让内核可以"提前"把更多数据塞进管道。

**重传参数**

.. code-block:: bash

   # 减少 TCP 最大重传次数（默认 15 次太慢）
   sysctl -w net.ipv4.tcp_retries2=5

   # 设置 SYN 最大重传次数（默认 6 次 = 约 127 秒）
   sysctl -w net.ipv4.tcp_syn_retries=3

   # 设置 SYN+ACK 最大重传次数
   sysctl -w net.ipv4.tcp_synack_retries=3

**是什么：** 当 TCP 发送的数据包没有收到 ACK 时，会进行指数退避重传（1s, 2s, 4s, 8s...）。
``tcp_retries2`` 控制最大重传次数，默认 15 次意味着可能等 13-30 分钟才判定连接断开。

**为什么调：** 嵌入式设备和物联网场景下，网络间歇性断开很常见。
默认 15 次重传等太久，应用层可能已经超时了内核还在傻等。
减少到 5 次（约 25 秒）让连接更快释放，应用层可以更快触发重连。

**比喻：** 就像打电话对方不接，默认要响 15 次才挂（等好几分钟）。
改成响 5 次就挂，虽然可能对方刚好走到电话旁，但至少你不会一直傻等。


BBR 拥塞控制
^^^^^^^^^^^^^

.. code-block:: bash

   # 启用 BBR 拥塞控制算法
   sysctl -w net.core.default_qdisc=fq
   sysctl -w net.ipv4.tcp_congestion_control=bbr

   # 验证当前拥塞控制算法
   sysctl net.ipv4.tcp_congestion_control

   # 查看可用算法
   sysctl net.ipv4.tcp_available_congestion_control

**是什么：** 拥塞控制算法决定 TCP 如何适应网络拥塞。传统算法（如 CUBIC）基于丢包判断拥塞——
看到丢包就减速。BBR（Bottleneck Bandwidth and Round-trip propagation time）是 Google 开发的
算法，基于带宽和延迟来判断拥塞状态。

**为什么调：** 在 4G/Wi-Fi 等弱网环境下，丢包不一定是因为拥塞，可能是无线信号波动。
传统算法看到丢包就减速，导致带宽利用率极低。BBR 不依赖丢包判断，能更好地利用弱网带宽。

**比喻：** 传统算法像一个"看到红灯就停车"的司机，即使是误报也会急刹车。
BBR 像一个"看路宽不宽、车多不多"的司机，更聪明地控制速度。

**场景推荐：**

- 高延迟高带宽链路（跨洋传输）→ BBR 效果显著
- 4G/弱网环境 → BBR 推荐启用
- 低延迟局域网 → 默认 CUBIC 就够了
- 公共云服务器 → BBR 通常能提升 2-5 倍吞吐量

**持久化配置：** sysctl 修改重启后失效，写入配置文件才持久。

.. code-block:: bash

   # 写入 sysctl 配置文件
   cat >> /etc/sysctl.d/99-tcp-tuning.conf << 'EOF'
   net.ipv4.tcp_window_scaling = 1
   net.core.rmem_default = 262144
   net.core.wmem_default = 262144
   net.core.rmem_max = 16777216
   net.core.wmem_max = 16777216
   net.ipv4.tcp_rmem = 4096 262144 16777216
   net.ipv4.tcp_wmem = 4096 262144 16777216
   net.ipv4.tcp_retries2 = 5
   net.core.default_qdisc = fq
   net.ipv4.tcp_congestion_control = bbr
   EOF

   # 加载配置
   sysctl --system


Nagle 算法 vs 延迟 ACK
^^^^^^^^^^^^^^^^^^^^^^^^

这是 TCP 中最经典的"两个好心人互相等"的问题。

**Nagle 算法 —— 发送端的"攒一攒"策略**

Nagle 算法的核心规则：如果已发送的数据还没有收到 ACK，就先把小数据攒起来，
等 ACK 到了再一起发。目的是减少网络上大量的小包（tinygram）。

**延迟 ACK —— 接收端的"等一等"策略**

延迟 ACK 的规则：收到数据后不立即回复 ACK，而是等最多 40ms，希望在这期间能有数据要发送，
这样 ACK 可以"搭便车"附在数据包上一起发，减少纯 ACK 包的数量。

**冲突场景：** 两个好心人的初衷都是"减少小包"，但它们组合在一起就会产生死锁：

1. 发送端发送一个小包
2. 发送端等待 ACK（Nagle 算法：没收到 ACK 就不发下一个包）
3. 接收端收到数据，但不立即回 ACK（延迟 ACK：等 40ms 看有没有数据要搭车）
4. 接收端没有数据要发，40ms 后才发 ACK
5. 发送端收到 ACK，才发下一个小包
6. 每个小包都卡 40ms → 延迟飙升

**比喻：**

- Nagle 像"写信等回执"：寄出一封信后，必须等收到回执才寄下一封。
  好处是不浪费邮票（减少小包），但急性子受不了。
- 延迟 ACK 像"收到信不马上回"：想着"等会儿自己也要写信，回执夹在里面一起寄"。
  好处是省邮票，但如果一直没什么要写的，对方就要干等。

两个策略单独看都很合理，但放在一起：写信的人等回执，收信的人等要写信 → 两人大眼瞪小眼，
每封信都卡 40ms。

**解决方案：**

.. code-block:: bash

   # 在应用层设置 TCP_NODELAY 禁用 Nagle 算法
   # C 语言示例
   int flag = 1;
   setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));

   # Python 示例
   import socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

   # 查看 socket 选项（调试用）
   ss -tni | grep -i nodelay

**何时禁用 Nagle（设置 TCP_NODELAY）：**

- MQTT 心跳包、游戏实时数据、SSH 击键回显等小包高频场景
- 交互式应用（用户输入需要立即响应）
- RPC 调用（请求-响应模式）

**何时保留 Nagle（默认开启）：**

- 大块数据传输（文件下载、批量同步）
- 对延迟不敏感的日志上报

**最佳实践：** 大多数场景下推荐设置 TCP_NODELAY，尤其是 MQTT、HTTP API 等请求-响应模式。
Nagle 的收益在现代网络上已经不明显，但它的延迟副作用仍然存在。


TCP 重传监控
^^^^^^^^^^^^^

**是什么：** TCP 重传是网络质量的核心指标。当发送的数据包没有在预期时间内收到 ACK，
TCP 会重传该包。重传越多，说明网络越不稳定。

**为什么需要：** 应用层可能感觉"偶尔卡一下"，但不知道原因。监控 TCP 重传可以量化
网络质量，判断是网络问题还是应用问题。

.. code-block:: bash

   # 查看 TCP 统计信息
   cat /proc/net/snmp | grep Tcp

   # 使用 netstat 查看重传统计
   netstat -s | grep -i retrans

   # 使用 ss 查看连接级别的重传信息
   ss -tni | grep retrans

   # 持续监控重传（每 1 秒刷新）
   watch -n 1 'cat /proc/net/snmp | grep Tcp'

   # 计算重传率的脚本
   # 重传率 = RetransSegs / OutSegs * 100%
   # 读取两次 /proc/net/snmp 的差值来计算瞬时重传率
   watch -n 5 'cat /proc/net/snmp | grep Tcp | tail -1'

``/proc/net/snmp`` 中 TCP 行的关键字段（按顺序）：

.. code-block:: text

   Tcp: RtoAlgorithm RtoMin RtoMax MaxConn ActiveOpens PassiveOpens
        AttemptFails EstabResets CurrEstab InSegs OutSegs RetransSegs
        InErrs OutRsts

- **OutSegs**：已发送的 TCP 段总数
- **RetransSegs**：重传的 TCP 段总数
- **重传率** = RetransSegs / OutSegs * 100%
- **InErrs**：收到的错误段数
- **OutRsts**：发出的 RST 数（异常断开）

.. code-block:: bash

   # 自动计算重传率的脚本
   #!/bin/bash
   # 读取两次采样，间隔 5 秒
   read_tcp() {
     awk '/^Tcp:/ && /Tcp:/ {print $12, $11}' /proc/net/snmp | tail -1
   }

   echo "采样中，5 秒后计算重传率..."
   set1=$(read_tcp)
   sleep 5
   set2=$(read_tcp)

   retrans1=$(echo $set1 | awk '{print $1}')
   outseg1=$(echo $set1 | awk '{print $2}')
   retrans2=$(echo $set2 | awk '{print $1}')
   outseg2=$(echo $set2 | awk '{print $2}')

   retrans_diff=$((retrans2 - retrans1))
   outseg_diff=$((outseg2 - outseg1))

   if [ $outseg_diff -gt 0 ]; then
     rate=$(echo "scale=2; $retrans_diff * 100 / $outseg_diff" | bc)
     echo "重传率: ${rate}% ($retrans_diff / $outseg_diff)"
     if (( $(echo "$rate > 5" | bc -l) )); then
       echo "警告: 重传率超过 5%，网络质量较差"
     fi
   else
     echo "无出站流量"
   fi


网络诊断指标
------------

在物联网和嵌入式场景中，设备通常通过 4G 或 Wi-Fi 连接，网络质量波动大。
需要一套量化指标来判断"网络到底有多差"。


弱网检测指标
^^^^^^^^^^^^

.. list-table:: 弱网诊断指标
   :header-rows: 1
   :widths: 20 40 20 20

   * - 指标
     - 获取方式
     - 弱网阈值
     - 说明
   * - 4G RSRP
     - ``AT+CSQ`` 或 ``/sys/class/net/``
     - < -105 dBm
     - 参考信号接收功率，越小越差
   * - Wi-Fi 信号强度
     - ``iwconfig wlan0``
     - < -70 dBm
     - RSSI 值，越小越差
   * - TCP 重传率
     - ``/proc/net/snmp`` 中的 RetransSegs
     - > 5%
     - 重传率高说明链路不可靠
   * - RTT
     - ``ping`` 云端服务器
     - > 200 ms
     - 往返时延，高延迟影响交互体验
   * - MQTT 断连频率
     - on_disconnect 回调计数
     - 连续 3 次以上
     - 频繁断连说明网络极不稳定
   * - DNS 解析时间
     - ``dig`` + 计时
     - > 500 ms
     - DNS 慢会导致连接建立慢

.. code-block:: bash

   # 4G 信号质量（AT 指令，需要串口访问）
   # AT+CSQ 返回 +CSQ: rssi,ber
   # rssi: 0=-113dBm, 1=-111dBm, ..., 31=-51dBm, 99=未知
   echo -e "AT+CSQ\r\n" > /dev/ttyUSB2

   # Wi-Fi 信号强度
   iwconfig wlan0 2>/dev/null | grep "Signal level"

   # 或使用 iw（更现代）
   iw dev wlan0 link | grep signal

   # RTT 测试（ping 云端服务器）
   ping -c 10 -q cloud-server.example.com

   # DNS 解析时间
   # 使用 dig 的 +stats 查看解析耗时
   dig +stats example.com | grep "Query time"


arping —— ARP 层连通性与 IP 冲突检测
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** arping 在 ARP 层面发送请求，用于检测同一网段内某个 IP 是否被占用。
它工作在二层（数据链路层），不经过路由器。

**为什么需要：** 设备刚上电获取了 IP，但这个 IP 可能已经被其他设备占用了（IP 冲突）。
ping 走三层路由，可能因为 ARP 缓存掩盖了冲突。arping 直接问"谁是这个 IP"，
如果收到两个不同的 MAC 地址回应，就是冲突了。

.. code-block:: bash

   # 检测 IP 冲突（发 3 个 ARP 请求）
   arping -c 3 -I eth0 192.168.1.100

   # 如果看到不同的 MAC 地址回应 → IP 冲突
   # 正常情况只有一个 MAC 地址回应

   # 发送 ARP 请求并记录（脚本中使用）
   arping -c 1 -I eth0 192.168.1.100 && echo "IP 被占用" || echo "IP 可用"

   # 指定源 IP（多 IP 网卡场景）
   arping -c 3 -I eth0 -s 192.168.1.50 192.168.1.100

   # 刷新本地 ARP 缓存后再检测（避免缓存干扰）
   ip neigh del 192.168.1.100 dev eth0 2>/dev/null
   arping -c 3 -I eth0 192.168.1.100

**比喻：** ping 是"寄信问你在不在"（走邮局，经过多个中转站），arping 是"站楼下喊你名字"
（只在同一个小区里喊，谁答应就是谁）。如果两个人同时答应，说明重名了（IP 冲突）。


.. _防火墙与安全:

防火墙与安全
------------

Linux 防火墙是网络安全的第一道防线，也是"端口连不上"问题的常见原因。


iptables 四表五链
^^^^^^^^^^^^^^^^^^

**是什么：** iptables 的规则组织结构分为"表"（功能类别）和"链"（检查时机）。
理解表和链的关系是正确配置防火墙的基础。

**四表（按优先级从高到低）：**

- **raw 表** —— 连接跟踪（conntrack）之前的处理。用于标记某些包不走连接跟踪。
- **mangle 表** —— 修改数据包头部（TTL、TOS 等）。一般用不到。
- **nat 表** —— 网络地址转换。端口转发、SNAT、DNAT 都在这里配置。
- **filter 表** —— 包过滤。决定放行还是丢弃，最常用的表。

**五链（数据包经过的检查点）：**

- **PREROUTING** —— 数据包刚进入网络层，还没做路由判断。
  用于 DNAT（目的地址转换，即端口转发）。
- **INPUT** —— 数据包目的地是本机。用于控制哪些流量可以访问本机服务。
- **FORWARD** —— 数据包要转发到其他机器（本机是路由器）。用于控制转发流量。
- **OUTPUT** —— 本机产生的数据包要发出去。用于控制本机的出站访问。
- **POSTROUTING** —— 数据包即将离开本机。用于 SNAT（源地址转换）。

**数据包流向：**

.. code-block:: text

   入站包:  网卡 → PREROUTING → 路由判断 → INPUT → 本机应用
   转发包:  网卡 → PREROUTING → 路由判断 → FORWARD → POSTROUTING → 网卡
   出站包:  本机应用 → OUTPUT → 路由判断 → POSTROUTING → 网卡

**比喻：** 想象一个国际快递流程：

- PREROUTING = 海关入口检查（还没分拣）
- INPUT = 本大楼的收发室（寄给本楼的）
- FORWARD = 转运中心（寄给别的楼的）
- OUTPUT = 本楼寄出的包裹
- POSTROUTING = 海关出口检查


常用防火墙规则
^^^^^^^^^^^^^^

.. code-block:: bash

   # ============ 基础规则 ============

   # 允许回环接口（本机内部通信，必须有）
   iptables -A INPUT -i lo -j ACCEPT

   # 允许已建立和相关连接（必须有，否则回程包被丢弃）
   iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

   # 允许 SSH
   iptables -A INPUT -p tcp --dport 22 -j ACCEPT

   # 允许 HTTP/HTTPS
   iptables -A INPUT -p tcp --dport 80 -j ACCEPT
   iptables -A INPUT -p tcp --dport 443 -j ACCEPT

   # 允许 MQTT
   iptables -A INPUT -p tcp --dport 1883 -j ACCEPT
   iptables -A INPUT -p tcp --dport 8883 -j ACCEPT  # MQTT over TLS

   # 允许 ICMP（ping）
   iptables -A INPUT -p icmp -j ACCEPT

   # 默认拒绝（最后一条）
   iptables -A INPUT -j DROP

   # ============ 限速规则 ============

   # 限制 SSH 连接速率（防暴力破解）
   # 每分钟最多 3 次新连接，超过则丢弃
   iptables -A INPUT -p tcp --dport 22 -m state --state NEW \
     -m recent --set --name SSH
   iptables -A INPUT -p tcp --dport 22 -m state --state NEW \
     -m recent --update --seconds 60 --hitcount 4 --name SSH -j DROP

   # 限制单 IP 并发连接数
   iptables -A INPUT -p tcp --dport 1883 \
     -m connlimit --connlimit-above 100 -j REJECT

   # ============ 日志记录 ============

   # 记录被丢弃的包（用于调试）
   iptables -A INPUT -j LOG --log-prefix "IPT-DROP: " --log-level 4
   iptables -A INPUT -j DROP

   # 查看日志
   tail -f /var/log/syslog | grep IPT-DROP


NAT 与端口转发
^^^^^^^^^^^^^^^

**是什么：** NAT（Network Address Translation）将私有 IP 转换为公有 IP，
让内网设备能访问互联网。端口转发将外部请求映射到内部服务器。

**为什么需要：** 物联网网关通常只有一个公网 IP，但背后有多个设备。
NAT 和端口转发让外部能访问内网的 MQTT Broker、Web 服务等。

.. code-block:: bash

   # ============ 开启 IP 转发 ============

   # 临时开启
   echo 1 > /proc/sys/net/ipv4/ip_forward

   # 持久化
   echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.d/99-forward.conf
   sysctl --system

   # ============ SNAT（源地址转换）============
   # 内网设备访问互联网时，把源地址改成网关的公网 IP

   # 假设 eth0 是外网接口，192.168.1.0/24 是内网网段
   iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth0 -j MASQUERADE

   # 如果公网 IP 是固定的，用 SNAT 性能更好
   iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth0 \
     -j SNAT --to-source 203.0.113.1

   # ============ DNAT（目的地址转换 / 端口转发）============

   # 把外部的 1883 端口转发到内网 MQTT Broker
   iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 1883 \
     -j DNAT --to-destination 192.168.1.100:1883

   # 把外部的 80 端口转发到内网 Web 服务器
   iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 \
     -j DNAT --to-destination 192.168.1.200:80

   # 端口映射（外部 8080 → 内部 80）
   iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 8080 \
     -j DNAT --to-destination 192.168.1.200:80

   # 别忘了 FORWARD 链也要允许
   iptables -A FORWARD -i eth0 -o eth1 -p tcp --dport 1883 \
     -d 192.168.1.100 -j ACCEPT
   iptables -A FORWARD -i eth1 -o eth0 -p tcp --sport 1883 \
     -s 192.168.1.100 -j ACCEPT

   # ============ 查看 NAT 规则 ============

   # 查看 NAT 表
   iptables -t nat -L -n -v

   # 查看连接跟踪表（NAT 依赖连接跟踪）
   conntrack -L
   conntrack -L | grep 1883

**比喻：** NAT 就像公司的总机。外面打进来一个电话（数据包），
总机根据分机号（端口）转接到对应的工位（内网服务器）。
SNAT 是员工用总机号码往外打电话（隐藏内部分机号），
DNAT 是外面的电话转接到内部分机（端口转发）。


安全最佳实践
^^^^^^^^^^^^

.. code-block:: bash

   # 1. 默认拒绝，按需开放（白名单模式）
   iptables -P INPUT DROP       # 设置默认策略为丢弃
   iptables -P FORWARD DROP
   iptables -P OUTPUT ACCEPT    # 出站默认放行

   # 2. 防 SYN Flood 攻击
   iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT
   iptables -A INPUT -p tcp --syn -j DROP

   # 3. 防端口扫描
   iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP           # NULL 包
   iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP            # XMAS 包
   iptables -A INPUT -p tcp --tcp-flags SYN,FIN SYN,FIN -j DROP   # SYN+FIN

   # 4. 禁止 ping（可选，防 ICMP 洪泛）
   iptables -A INPUT -p icmp --icmp-type echo-request -j DROP

   # 5. 记录并丢弃无效包
   iptables -A INPUT -m state --state INVALID -j LOG --log-prefix "IPT-INVALID: "
   iptables -A INPUT -m state --state INVALID -j DROP

   # 6. 保护 SSH：只允许特定 IP 段
   iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
   iptables -A INPUT -p tcp --dport 22 -j DROP

   # 7. 保存规则（Debian/Ubuntu）
   apt install iptables-persistent
   netfilter-persistent save

   # 7. 保存规则（CentOS/RHEL）
   service iptables save


常见问题速查
------------

.. list-table:: 网络问题速查表
   :header-rows: 1
   :widths: 30 35 35

   * - 现象
     - 可能原因
     - 排查命令
   * - ping 不通
     - 物理链路断 / IP 配置错 / 路由缺失
     - ``ip link show`` → ``ip addr`` → ``ip route``
   * - ping IP 通但域名不通
     - DNS 配置错误
     - ``dig @8.8.8.8 domain`` → 检查 ``/etc/resolv.conf``
   * - 端口 Connection refused
     - 服务未启动 / 监听地址不对
     - ``ss -tlnp | grep port``
   * - 端口 Connection timed out
     - 防火墙拦截 / 路由不通
     - ``iptables -L -n`` → ``traceroute``
   * - TCP 连接慢
     - DNS 慢 / SYN 重传 / 拥塞控制不当
     - ``dig +stats`` → ``ss -tni`` → ``sysctl tcp_congestion_control``
   * - CLOSE_WAIT 堆积
     - 应用层未关闭 socket
     - ``ss -tn state close-wait | wc -l`` → 检查代码
   * - TIME_WAIT 堆积
     - 短连接过多
     - ``ss -tn state time-wait | wc -l`` → 启用连接池
   * - 高重传率
     - 链路质量差 / 缓冲区太小
     - ``cat /proc/net/snmp | grep Tcp`` → 调优缓冲区
   * - 间歇性断连
     - 弱网信号 / IP 冲突
     - ``mtr`` → ``arping`` → 检查信号强度
