文件操作
========

Linux 的核心哲学之一是"一切皆文件"。文件操作是日常使用中最频繁的任务，
掌握高效的文件查找、内容搜索、文本处理和文件管理技巧，能大幅提升工作效率。

.. note::

   **关于管道的比喻**

   Linux 命令行的管道（``|``）就像工厂的流水线：原材料（数据）从一端进入，
   经过一道道工序（命令），最终产出成品（结果）。每个命令只做一件事，
   但通过组合就能完成复杂任务——这就是 Unix 哲学。


查找文件
--------

在庞大的文件系统中找到目标文件，是最基本也最常见的需求。
Linux 提供了多种查找工具，适用于不同场景。


find：最强大的文件查找工具
^^^^^^^^^^^^^^^^^^^^^^^^^^

``find`` 是 Linux 中功能最全面的文件搜索命令。它会**实时遍历**目录树，
根据各种条件筛选文件。可以把它想象成一个认真负责的档案管理员，
逐个抽屉翻找符合条件的文件。

**基本语法：**

.. code-block:: bash

   find [搜索路径] [匹配条件] [操作]

**按名称查找：**

.. code-block:: bash

   # 在当前目录及子目录中查找所有 .c 文件
   find . -name "*.c"

   # 忽略大小写查找（如 README、readme、ReadMe 都能匹配）
   find . -iname "readme*"

   # 限制搜索深度：只在当前目录的直接子目录中查找（不递归）
   find . -maxdepth 2 -name "*.txt"

.. tip::

   ``-name`` 使用的是 shell 通配符（glob），不是正则表达式。
   ``*`` 匹配任意字符，``?`` 匹配单个字符。
   如果需要正则表达式，请用 ``-regex``。

**按类型查找：**

.. code-block:: bash

   # 只查找普通文件（排除目录、链接等）
   find /path -type f -name "*.h"

   # 只查找目录
   find /path -type d -name "src"

   # 常见类型标识：
   #   f = 普通文件
   #   d = 目录
   #   l = 符号链接
   #   b = 块设备（如硬盘）
   #   c = 字符设备（如终端）

**按大小查找：**

.. code-block:: bash

   # 查找大于 1MB 的文件
   find /path -size +1M

   # 查找小于 100KB 的文件
   find /path -size -100k

   # 查找恰好 512 字节的文件
   find /path -size 512c

   # 大小单位：c=字节, k=KB, M=MB, G=GB
   # + 表示大于，- 表示小于，无符号表示恰好

**按时间查找：**

``find`` 的时间查找功能非常实用，尤其是在排查"最近改坏了什么"的时候。

.. code-block:: bash

   # 查找最近 7 天内修改过的文件
   find /path -mtime -7

   # 查找超过 30 天未修改的文件（可用于清理旧文件）
   find /path -mtime +30

   # 查找恰好 3 天前修改的文件
   find /path -mtime 3

   # -mtime 按"天"计算，还有更精确的选项：
   # -mmin  按分钟（如 -mmin -60 表示最近 60 分钟内修改过）
   # -atime 访问时间（最后一次读取）
   # -ctime 变更时间（最后一次 inode 元数据变更）

   # 查找比某个文件更新的文件（非常实用！）
   find /path -newer /tmp/checkpoint.txt

   # 查找比某个文件更旧的文件
   find /path ! -newer /tmp/checkpoint.txt

.. tip::

   **-mtime 的"陷阱"**

   ``-mtime -7`` 表示"修改时间在 **7天以内**"（最近7天），``+7`` 表示"超过7天前"。
   记忆技巧：``-`` 像"减号"→ 时间更少 → 更新；``+`` 像"加号"→ 时间更多 → 更旧。

**执行操作（-exec）：**

``find`` 最强大的特性之一是 ``-exec``，它让你对查找到的每个文件执行任意命令。

.. code-block:: bash

   # 查找并删除所有 .tmp 文件
   find /path -name "*.tmp" -exec rm {} \;

   # 查找并列出详细信息
   find /path -name "*.log" -exec ls -lh {} \;

   # {} 是占位符，代表 find 找到的每个文件
   # \; 表示命令结束（反斜杠转义分号，防止 shell 解释）

   # 使用 + 代替 \; 可以批量传参，效率更高
   find /path -name "*.log" -exec ls -lh {} +

   # \;  每找到一个文件就执行一次命令（慢）
   # +   把多个文件名作为参数一次性传给命令（快）
   # 类比：\; 像逐个搬运包裹，+ 像用推车一次搬一车

   # 实用示例：查找并修改权限
   find /path -type f -name "*.sh" -exec chmod 755 {} \;

   # 实用示例：查找并压缩
   find /path -name "*.log" -exec gzip {} \;

**find + xargs 组合：**

``xargs`` 是另一个强大的工具，它从标准输入读取数据，转化为命令参数。
与 ``find`` 配合使用，比 ``-exec`` 更灵活。

.. code-block:: bash

   # 基本用法：find 的输出作为 xargs 的参数
   find /path -name "*.log" | xargs rm

   # 处理文件名含空格的情况（-print0 + -0）
   find /path -name "*.log" -print0 | xargs -0 rm

   # -print0 用 NULL 字符分隔文件名（而非换行符）
   # -0 告诉 xargs 用 NULL 字符作为分隔符
   # 这样即使文件名包含空格、引号等特殊字符也不会出错

   # 限制每次传给命令的参数数量（-n）
   find /path -name "*.txt" | xargs -n 10 grep "pattern"
   # 每次给 grep 传 10 个文件，而不是一次传所有文件

   # 交互模式：执行前确认（-p）
   find /path -name "*.tmp" | xargs -p rm

.. warning::

   **find + xargs 的安全用法**

   默认情况下，``xargs`` 用空格和换行符分隔输入。如果文件名包含空格，
   会导致参数被错误拆分。**始终使用** ``-print0`` 和 ``-0`` 的组合
   来避免这个问题。


locate：基于数据库的快速查找
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``locate`` 与 ``find`` 的最大区别是：``find`` 实时遍历文件系统（慢但准确），
``locate`` 查预先建好的数据库（快但可能不是最新）。

.. code-block:: bash

   # 快速查找文件（模糊匹配路径名）
   locate "*.conf"

   # 忽略大小写
   locate -i "readme"

   # 限制结果数量
   locate -n 10 "*.log"

   # 更新数据库（通常由 cron 定时任务自动执行）
   sudo updatedb

.. tip::

   **何时用 find，何时用 locate？**

   - ``find``：需要实时结果、需要按复杂条件筛选时使用
   - ``locate``：快速查找已知文件名、不确定文件在哪个目录时使用
   - 类比：``find`` 像现场搜查，``locate`` 像查档案索引


which / whereis / type：查找命令位置
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

当你想知道某个命令到底在哪里、是什么类型时，这三个工具各有用途：

.. code-block:: bash

   # which：显示命令的可执行文件路径（只搜索 PATH）
   which python
   # 输出：/usr/bin/python

   # whereis：显示命令的二进制文件、源码和手册页路径
   whereis python
   # 输出：python: /usr/bin/python3 /usr/lib/python3 /usr/share/man/man1/python.1.gz

   # type：显示命令的类型（内置命令、别名、外部程序等）
   type cd
   # 输出：cd is a shell builtin

   type ls
   # 输出：ls is aliased to 'ls --color=auto'

   type grep
   # 输出：grep is /usr/bin/grep

   # type -a 显示所有匹配（包括别名和外部命令）
   type -a python

.. tip::

   **实用场景**

   - ``which``：确认你用的是哪个版本的命令（如多个 Python 版本时）
   - ``whereis``：查找命令的完整安装位置（包括文档和源码）
   - ``type``：判断命令是 shell 内置还是外部程序（排查"为什么这个命令不工作"时很有用）


搜索内容
--------

找到文件之后，下一步往往是在文件内容中搜索特定信息。
Linux 提供了强大的文本搜索工具。


grep：文本搜索的瑞士军刀
^^^^^^^^^^^^^^^^^^^^^^^^^

``grep`` 是 Linux 中使用频率最高的命令之一。它在文件或输入流中搜索匹配指定模式的行。
可以把它想象成一个高效的过滤器：水流（文本）经过它，只有符合条件的才能通过。

**基本用法：**

.. code-block:: bash

   # 在文件中搜索字符串
   grep "error" logfile.txt

   # 递归搜索目录下所有文件
   grep -rn "pattern" /path

   # 忽略大小写
   grep -rni "error" /path

   # 只显示匹配的文件名（不显示具体内容）
   grep -rl "pattern" /path

   # 反向匹配：显示不包含模式的行
   grep -v "debug" logfile.txt

**上下文显示：**

默认情况下，grep 只显示匹配的行。但很多时候你需要看上下文才能理解含义。

.. code-block:: bash

   # 显示匹配行及其后 3 行（After）
   grep -A 3 "error" logfile.txt

   # 显示匹配行及其前 3 行（Before）
   grep -B 3 "error" logfile.txt

   # 显示匹配行及其前后各 3 行（Context）
   grep -C 3 "error" logfile.txt

   # 实际场景：查看报错的上下文
   grep -C 5 "Exception" app.log

.. tip::

   **记忆技巧**：``-A`` = After（之后），``-B`` = Before（之前），``-C`` = Context（上下文）。

**扩展正则表达式（-E）：**

默认情况下，``grep`` 使用基本正则表达式，许多元字符需要转义。
使用 ``-E``（或 ``egrep``）可以使用扩展正则表达式，语法更简洁。

.. code-block:: bash

   # 基本正则：需要转义 + ? | 等字符
   grep "error\|warning" logfile.txt

   # 扩展正则：无需转义，更直观
   grep -E "error|warning" logfile.txt

   # 匹配一个或多个数字
   grep -E "[0-9]+" data.txt

   # 匹配 IP 地址的简单模式
   grep -E "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" access.log

   # 匹配邮箱地址
   grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" data.txt

**只输出匹配部分（-o）：**

.. code-block:: bash

   # 只输出匹配的字符串（而非整行）
   grep -o "error [0-9]*" logfile.txt

   # 提取所有 IP 地址
   grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" access.log

   # 配合 -c 统计匹配次数
   grep -co "error" logfile.txt

**文件类型过滤：**

.. code-block:: bash

   # 只在特定类型的文件中搜索
   grep -rn --include="*.py" "import os" /project

   # 排除特定类型的文件
   grep -rn --exclude="*.log" "TODO" /project

   # 排除指定目录
   grep -rn --exclude-dir=".git" "TODO" /project

   # 多个 include/exclude
   grep -rn --include="*.py" --include="*.js" "function" /project

   # 使用 .gitignore 风格的排除文件
   grep -rn --exclude-from=".grepignore" "pattern" /project


ripgrep (rg)：现代替代品
^^^^^^^^^^^^^^^^^^^^^^^^^

``ripgrep`` 是 grep 的现代替代品，由 Rust 编写。它更快、默认更智能，
在大型代码库中优势明显。

.. code-block:: bash

   # 安装（Ubuntu/Debian）
   sudo apt install ripgrep

   # 基本搜索（默认递归、忽略 .gitignore 中的文件、彩色输出）
   rg "pattern" /path

   # 指定文件类型
   rg -t py "import" /project

   # 按文件名过滤
   rg -g "*.txt" "pattern" /path

   # 显示上下文
   rg -C 3 "error" logfile.txt

   # 只输出匹配部分
   rg -o "[0-9]+" data.txt

.. tip::

   **grep vs ripgrep**

   - ``grep``：无处不在，无需安装，功能成熟
   - ``rg``：速度快数倍，默认忽略二进制文件和 .gitignore 中的文件
   - 日常简单搜索用 ``grep``，大型项目搜索推荐 ``rg``


流编辑器 sed
------------

``sed``（Stream Editor，流编辑器）是 Linux 中最强大的文本处理工具之一。
它逐行读取输入，根据指定的规则进行编辑，然后输出结果。
可以把它想象成一条文本处理流水线：文本流进去，经过加工，变成新文本流出来。

**为什么需要 sed？**

- 批量修改配置文件中的某个值
- 自动化脚本中的文本替换
- 不打开编辑器就能修改文件
- 处理日志文件中的特定内容


基本语法
^^^^^^^^

.. code-block:: bash

   # 基本格式
   sed [选项] '命令' 文件

   # 最常用的操作：替换（substitute）
   sed 's/old/new/' file        # 替换每行第一个匹配
   sed 's/old/new/g' file       # 替换所有匹配（g = global）
   sed 's/old/new/2' file       # 只替换每行第 2 个匹配

   # s 是"替换"命令，g 是"全局"标志
   # 没有 g 时，每行只替换第一个匹配
   # 有了 g，一行中的所有匹配都会被替换

.. code-block:: bash

   # 示例：替换文件中的字符串
   echo "hello world hello" | sed 's/hello/hi/'
   # 输出：hi world hello

   echo "hello world hello" | sed 's/hello/hi/g'
   # 输出：hi world hi


原地编辑（-i）
^^^^^^^^^^^^^^

默认情况下，``sed`` 只输出到标准输出，不修改原文件。
使用 ``-i``（in-place）可以直接修改文件。

.. code-block:: bash

   # 直接修改文件（危险！建议先备份）
   sed -i 's/old_value/new_value/g' config.conf

   # 修改前创建备份（推荐做法）
   sed -i.bak 's/old_value/new_value/g' config.conf
   # 原文件被修改，原内容保存在 config.conf.bak

   # macOS 的 sed 语法略有不同（-i 后必须跟参数）
   sed -i '' 's/old/new/g' file          # macOS：不创建备份
   sed -i '.bak' 's/old/new/g' file      # macOS：创建 .bak 备份

.. warning::

   **-i 的危险性**

   ``sed -i`` 会直接修改原文件，且无法撤销。在重要文件上使用前，
   务必先用 ``sed 's/old/new/' file`` 预览结果，确认无误后再加 ``-i``。


地址范围
^^^^^^^^

你可以指定 sed 命令作用于哪些行：

.. code-block:: bash

   # 指定行号
   sed '3s/old/new/' file          # 只处理第 3 行
   sed '3,10s/old/new/g' file      # 处理第 3 到第 10 行
   sed '3,$s/old/new/g' file       # 处理第 3 行到最后一行

   # 按模式匹配
   sed '/pattern/s/old/new/g' file  # 只处理包含 pattern 的行

   # 实际示例：只在 [database] 段落中替换
   sed '/^\[database\]/,/^\[/s/host=.*/host=127.0.0.1/' config.ini

   # 范围取反（处理不匹配的行）
   sed '/pattern/!s/old/new/g' file  # 不包含 pattern 的行才替换


常用操作
^^^^^^^^

**替换（s）：**

.. code-block:: bash

   # 替换字符串
   sed 's/old/new/g' file

   # 使用不同的分隔符（当路径中有 / 时特别有用）
   sed 's|/usr/local|/opt|g' file
   sed 's#/usr/local#/opt#g' file

   # & 代表匹配到的内容
   sed 's/[0-9]+/&px/g' file      # 在数字后加 px

**删除（d）：**

.. code-block:: bash

   # 删除特定行
   sed '3d' file           # 删除第 3 行
   sed '3,10d' file        # 删除第 3 到第 10 行

   # 删除空行
   sed '/^$/d' file

   # 删除以 # 开头的注释行
   sed '/^#/d' file

   # 删除包含特定模式的行
   sed '/pattern/d' file

**插入和追加：**

.. code-block:: bash

   # 在指定行前插入（i = insert）
   sed '3i\新插入的行' file

   # 在指定行后追加（a = append）
   sed '3a\新追加的行' file

   # 在匹配行后追加
   sed '/pattern/a\新追加的行' file

   # 实际示例：在配置文件的 [section] 后添加配置
   sed '/^\[mysqld\]/a\max_connections=200' my.cnf

**打印（p）：**

.. code-block:: bash

   # 只打印匹配的行（类似 grep）
   sed -n '/pattern/p' file

   # 打印特定行
   sed -n '3p' file           # 只打印第 3 行
   sed -n '3,10p' file        # 只打印第 3 到第 10 行


实用示例
^^^^^^^^

.. code-block:: bash

   # 替换配置文件中的值
   sed -i 's/old_value/new_value/' config.conf

   # 删除空行
   sed -i '/^$/d' file.txt

   # 在第 3 行后插入
   sed -i '3a\new line' file.txt

   # 删除行首和行尾的空白字符
   sed 's/^[[:space:]]*//;s/[[:space:]]*$//' file

   # 将多个空格压缩为一个
   sed 's/  */ /g' file

   # 批量注释：在第 5 到第 10 行前加 #
   sed -i '5,10s/^/#/' file

   # 批量取消注释
   sed -i '5,10s/^#//' file

   # 提取两个标记之间的内容
   sed -n '/START/,/END/p' file

   # 将 Windows 换行符转为 Unix 换行符
   sed -i 's/\r$//' file


字段处理 awk
------------

``awk`` 是 Linux 中最强大的文本处理语言之一，尤其擅长处理结构化文本
（如 CSV、日志文件、配置文件）。它逐行读取输入，按字段分割，
然后对每个字段进行处理。可以把它想象成一个能理解"列"的过滤器。

**为什么需要 awk？**

``grep`` 和 ``sed`` 擅长处理"行"，但当你需要处理"列"时（如提取第 3 列、
按某列排序），``awk`` 才是真正的利器。


基本语法
^^^^^^^^

.. code-block:: bash

   # 基本格式
   awk 'pattern {action}' file

   # pattern 是匹配条件（可省略，默认匹配所有行）
   # action 是要执行的操作

   # 最简单的用法：打印所有内容
   awk '{print}' file

   # 等价于
   cat file

**内置变量：**

.. code-block:: bash

   # $1, $2, $3... 表示第 1、2、3 个字段
   # $0 表示整行
   # NR = 当前行号（Number of Records）
   # NF = 当前行的字段数（Number of Fields）
   # FS = 输入字段分隔符（Field Separator，默认为空格或制表符）
   # OFS = 输出字段分隔符

   # 打印第 1 和第 3 列
   awk '{print $1, $3}' file

   # 打印行号和整行内容
   awk '{print NR, $0}' file

   # 打印每行的字段数
   awk '{print NF}' file

   # 打印最后一列
   awk '{print $NF}' file

   # 打印倒数第二列
   awk '{print $(NF-1)}' file


字段分隔符
^^^^^^^^^^

.. code-block:: bash

   # 使用 -F 指定分隔符
   awk -F: '{print $1}' /etc/passwd
   # 从 /etc/passwd 中提取用户名（第 1 列）

   # 也可以在 BEGIN 块中设置
   awk 'BEGIN {FS=":"} {print $1}' /etc/passwd

   # 多个分隔符
   awk -F'[,;: ]' '{print $1}' file
   # 用逗号、分号、冒号或空格作为分隔符

   # 使用正则表达式作为分隔符
   awk -F'[,;]+' '{print $1}' file


BEGIN / END 块
^^^^^^^^^^^^^^^

.. code-block:: bash

   # BEGIN 块在处理任何输入之前执行
   # END 块在处理完所有输入之后执行

   # 打印表头 + 内容 + 统计
   awk 'BEGIN {print "Name\tAge"} {print $1"\t"$2} END {print "--- Total:", NR, "rows ---"}' data.txt

   # 计算总和
   awk '{sum += $3} END {print "Total:", sum}' data.txt

   # 计算平均值
   awk '{sum += $3; count++} END {print "Average:", sum/count}' data.txt


模式匹配
^^^^^^^^

.. code-block:: bash

   # 使用正则表达式匹配（~ 是匹配运算符）
   awk '/error/ {print}' logfile.txt
   # 等价于 grep "error" logfile.txt

   # 匹配特定字段
   awk '$1 ~ /admin/ {print}' data.txt

   # 取反匹配
   awk '$1 !~ /admin/ {print}' data.txt

   # 比较运算
   awk '$3 > 100 {print $0}' data.txt

   # 多条件（AND）
   awk '$1 == "admin" && $3 > 100 {print}' data.txt

   # 多条件（OR）
   awk '$1 == "admin" || $1 == "root" {print}' data.txt


实用示例
^^^^^^^^

.. code-block:: bash

   # 打印第 1 和第 3 列
   awk '{print $1, $3}' file

   # 按分隔符切割并打印第 1 列
   awk -F: '{print $1}' /etc/passwd

   # 统计行数
   awk 'END {print NR}' file

   # 条件过滤：只打印第 3 列大于 100 的行
   awk '$3 > 100 {print $0}' data.txt

   # 统计每个用户的进程数
   ps aux | awk 'NR>1 {print $1}' | sort | uniq -c | sort -rn

   # 格式化输出（printf）
   awk '{printf "%-20s %10d\n", $1, $3}' data.txt

   # 计算某列的总和
   awk '{sum += $5} END {printf "Total: %.2f\n", sum}' data.txt

   # 去重（类似 sort | uniq，但保持原始顺序）
   awk '!seen[$0]++' file

   # 将多行合并为一行
   awk '{printf "%s, ", $0} END {print ""}' file

   # 每 N 行添加分隔符（如每 3 行加一条横线）
   awk 'NR%3==0 {print; print "---"; next} {print}' file


文本处理工具集
--------------

Linux 提供了一系列小巧但强大的文本处理工具。它们各自只做一件事，
但通过管道组合起来，就能完成非常复杂的文本处理任务。
这就像乐高积木：每块积木很简单，但组合起来能造出城堡。


wc：统计行数、字数、字节数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``wc``（Word Count）用于统计文本的基本信息。

.. code-block:: bash

   # 统计行数、字数、字节数
   wc file.txt
   # 输出：  10  50  300 file.txt
   # 含义：  行数  字数  字节数  文件名

   # 只统计行数
   wc -l file.txt

   # 只统计字数
   wc -w file.txt

   # 只统计字节数
   wc -c file.txt

   # 统计字符数（多字节字符算一个）
   wc -m file.txt

   # 统计多个文件
   wc -l *.txt

   # 配合管道统计命令输出的行数
   ls -1 | wc -l


cut：按列提取
^^^^^^^^^^^^^^

``cut`` 按指定的分隔符切割每行，然后提取指定的字段。
它比 ``awk`` 简单，适合简单的列提取任务。

.. code-block:: bash

   # -d 指定分隔符，-f 指定字段
   cut -d: -f1 /etc/passwd       # 提取第 1 列（用户名）
   cut -d: -f1,3 /etc/passwd     # 提取第 1 和第 3 列
   cut -d: -f3- /etc/passwd      # 提取第 3 列及之后的所有列

   # 按字符位置提取
   cut -c1-10 file               # 提取每行的前 10 个字符
   cut -c5- file                 # 提取从第 5 个字符到行尾

   # 配合其他命令使用
   echo "2026-06-29" | cut -d- -f2   # 提取月份：06


tr：字符翻译和删除
^^^^^^^^^^^^^^^^^^

``tr``（Translate）用于字符级别的转换、删除和压缩。

.. code-block:: bash

   # 大小写转换
   echo "Hello World" | tr 'a-z' 'A-Z'    # 转为大写
   echo "Hello World" | tr 'A-Z' 'a-z'    # 转为小写

   # 字符替换
   echo "hello world" | tr ' ' '\n'       # 空格替换为换行（每词一行）

   # 删除特定字符
   echo "hello 123 world" | tr -d '0-9'   # 删除所有数字
   echo "hello!!" | tr -d '!'             # 删除感叹号

   # 删除重复字符（压缩）
   echo "hello     world" | tr -s ' '     # 多个空格压缩为一个

   # 删除不可见字符
   cat file.txt | tr -d '\r'              # 删除回车符（Windows 转 Unix）


sort：排序
^^^^^^^^^^

``sort`` 对文本行进行排序，是数据处理中最常用的工具之一。

.. code-block:: bash

   # 默认按字典序排序
   sort file.txt

   # 数字排序（-n）
   sort -n numbers.txt
   # 不加 -n 时：1, 10, 2, 20（字典序）
   # 加 -n 后：1, 2, 10, 20（数值序）

   # 反向排序（-r）
   sort -rn numbers.txt           # 数字逆序（从大到小）

   # 按指定列排序（-k）
   sort -t: -k3 -n /etc/passwd    # 按第 3 列（UID）数字排序
   # -t: 指定分隔符为冒号

   # 去重（-u）
   sort -u file.txt               # 排序并去除重复行

   # 忽略大小写排序
   sort -f file.txt

   # 按月份排序
   sort -M months.txt

   # 随机排序（洗牌）
   sort -R file.txt


uniq：去重
^^^^^^^^^^

``uniq`` 用于去除**相邻的**重复行。注意：它只能去除相邻的重复行，
所以通常需要先 ``sort`` 排序。

.. code-block:: bash

   # 去除相邻的重复行
   sort file.txt | uniq

   # 统计每行出现的次数（-c）
   sort file.txt | uniq -c

   # 只显示重复的行（-d）
   sort file.txt | uniq -d

   # 只显示不重复的行（-u）
   sort file.txt | uniq -u

   # 忽略前 N 个字段进行比较
   sort file.txt | uniq -f 2    # 忽略前 2 个字段


diff：文件比较
^^^^^^^^^^^^^^

``diff`` 逐行比较两个文件的差异，是版本控制和代码审查的基础工具。

.. code-block:: bash

   # 基本比较
   diff file1.txt file2.txt

   # 并排显示差异（更直观）
   diff -y file1.txt file2.txt

   # 只显示是否不同（不显示具体差异）
   diff -q file1.txt file2.txt

   # 忽略空白字符差异
   diff -w file1.txt file2.txt

   # 生成补丁文件
   diff -u old.txt new.txt > changes.patch

   # 比较两个目录
   diff -r dir1/ dir2/


patch：应用补丁
^^^^^^^^^^^^^^^

``patch`` 读取 ``diff`` 生成的补丁文件，并将更改应用到原文件。

.. code-block:: bash

   # 应用补丁
   patch < changes.patch

   # 应用补丁并创建备份
   patch -b < changes.patch

   # 反向应用补丁（撤销更改）
   patch -R < changes.patch

   # 预览补丁效果（不实际应用）
   patch --dry-run < changes.patch


管道组合实战
^^^^^^^^^^^^

将上述工具通过管道组合，可以完成复杂的文本处理任务：

.. code-block:: bash

   # 统计每个 IP 的访问次数并排序
   cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn

   # 找出最常访问的前 10 个 URL
   awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -10

   # 统计代码行数（按文件类型）
   find . -name "*.py" | xargs wc -l | sort -rn | head -20

   # 提取日志中的时间戳并统计每小时的请求数
   awk '{print $4}' access.log | cut -c2-15 | uniq -c

   # 找出日志中的错误类型分布
   grep "ERROR" app.log | awk -F: '{print $2}' | sort | uniq -c | sort -rn

   # 清理并格式化 CSV 文件
   cat data.csv | tr -d '\r' | sed '/^$/d' | sort -t, -k2 -n

   # 找出目录中最大的 10 个文件
   find . -type f -exec ls -s {} + | sort -n -r | head -10

   # 统计每种文件扩展名的数量
   find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn


文件管理
--------

文件管理是 Linux 系统操作的基础，涵盖文件的查看、压缩、权限控制、
链接管理等方方面面。


查看文件信息
^^^^^^^^^^^^

.. code-block:: bash

   # 查看文件大小
   ls -lh
   du -sh *

   # 查看文件类型（非常实用！）
   file image.png
   # 输出：image.png: PNG image data, 800 x 600, 8-bit/color RGBA

   file document.pdf
   # 输出：document.pdf: PDF document, version 1.7

   file script.sh
   # 输出：script.sh: Bourne-Again shell script, ASCII text executable

   file /dev/sda
   # 输出：/dev/sda: block special

   # 查看文件的详细信息（inode、权限、时间戳等）
   stat file.txt
   # 输出包括：
   #   Size: 文件大小
   #   Blocks: 占用的磁盘块数
   #   Access/Modify/Change: 访问/修改/变更时间
   #   Inode: inode 编号
   #   Links: 硬链接数


批量重命名
^^^^^^^^^^

.. code-block:: bash

   # 使用 rename 命令（Perl 版本，功能更强大）
   rename 's/\.txt$/\.md/' *.txt

   # 使用 rename（util-linux 版本，语法不同）
   rename .txt .md *.txt

   # 使用循环批量重命名
   for f in *.jpeg; do mv "$f" "${f%.jpeg}.jpg"; done

   # 给文件名添加前缀
   for f in *.txt; do mv "$f" "backup_$f"; done

   # 将文件名转为小写
   for f in *; do mv "$f" "$(echo $f | tr 'A-Z' 'a-z')"; done


同步文件
^^^^^^^^

.. code-block:: bash

   # rsync：最强大的文件同步工具
   rsync -avz src/ user@host:/dest/
   # -a 归档模式（保留权限、时间戳等）
   # -v 详细输出
   # -z 压缩传输

   # 本地同步（类似 cp，但支持增量传输）
   rsync -avh /source/ /dest/

   # 删除目标目录中源目录没有的文件（镜像同步）
   rsync -avz --delete src/ user@host:/dest/

   # 排除特定文件
   rsync -avz --exclude='*.log' --exclude='.git' src/ dest/

   # 显示进度
   rsync -avh --progress src/ dest/

   # 试运行（不实际传输）
   rsync -avzn src/ dest/


tar：压缩与解压
^^^^^^^^^^^^^^^^

``tar``（Tape Archive）是 Linux 中最常用的归档工具。
它将多个文件打包成一个文件，通常配合压缩算法使用。

.. code-block:: bash

   # 压缩文件
   tar -czvf filename.tar.gz filename.txt
   # -c 创建归档
   # -z 使用 gzip 压缩
   # -v 显示过程
   # -f 指定文件名

   # 压缩目录
   tar -czvf project.tar.gz /path/to/project

   # 解压文件
   tar -xzvf filename.tar.gz
   # -x 解压归档

   # 解压到指定目录
   tar -xzvf filename.tar.gz -C /target/directory

   # 查看归档内容（不解压）
   tar -tzvf filename.tar.gz

   # 使用 bzip2 压缩（压缩率更高，速度更慢）
   tar -cjvf filename.tar.bz2 file_or_dir
   tar -xjvf filename.tar.bz2

   # 使用 xz 压缩（压缩率最高）
   tar -cJvf filename.tar.xz file_or_dir
   tar -xJvf filename.tar.xz

.. tip::

   **压缩格式速记**

   - ``.tar.gz`` 或 ``.tgz``：gzip 压缩，速度快，最常用
   - ``.tar.bz2``：bzip2 压缩，压缩率更好
   - ``.tar.xz``：xz 压缩，压缩率最高，但速度最慢
   - 记忆：``z`` = gzip, ``j`` = bzip2, ``J`` = xz


权限管理
^^^^^^^^

Linux 的权限系统是安全性的基石。每个文件都有三组权限：所有者（user）、
所属组（group）、其他人（others）。

**理解权限：**

.. code-block:: bash

   # 查看文件权限
   ls -l file.txt
   # 输出：-rw-r--r-- 1 user group 1234 Jun 29 10:00 file.txt
   # 权限部分：rw-r--r--
   #   rw-  = 所有者：读+写
   #   r--  = 所属组：只读
   #   r--  = 其他人：只读

   # 权限字母含义：
   # r = read（读取）= 4
   # w = write（写入）= 2
   # x = execute（执行）= 1
   # - = 无权限 = 0

**数字模式：**

.. code-block:: bash

   # 数字模式：用三位数字表示权限
   chmod 755 file    # rwxr-xr-x（所有者完全控制，其他人可读可执行）
   chmod 644 file    # rw-r--r--（所有者可读写，其他人只读）
   chmod 600 file    # rw-------（只有所有者可读写）
   chmod 777 file    # rwxrwxrwx（所有人完全控制，慎用！）

   # 计算方法：
   # 7 = 4+2+1 = rwx
   # 6 = 4+2+0 = rw-
   # 5 = 4+0+1 = r-x
   # 4 = 4+0+0 = r--
   # 0 = 0+0+0 = ---

   # 常见权限组合：
   # 755：目录和可执行文件的标准权限
   # 644：普通文件的标准权限
   # 600：私密文件（如 SSH 密钥）
   # 700：私密目录

**符号模式：**

.. code-block:: bash

   # 符号模式：用字母表示权限变更
   chmod u+x file    # 给所有者添加执行权限
   chmod g-w file    # 移除所属组的写权限
   chmod o=r file    # 设置其他人为只读

   # u = user（所有者）
   # g = group（所属组）
   # o = others（其他人）
   # a = all（所有人）

   # + 添加权限
   # - 移除权限
   # = 设置权限（覆盖原有）

   # 组合使用
   chmod u=rwx,g=rx,o=r file

**修改所有者和所属组：**

.. code-block:: bash

   # 修改所有者
   chown user file.txt
   sudo chown user:group file.txt

   # 递归修改目录的所有者
   sudo chown -R user:group /path/to/directory

   # 只修改所属组
   chgrp group file.txt

   # 递归修改组
   chgrp -R group /path/to/directory

.. warning::

   **权限安全提示**

   - 永远不要对系统文件使用 ``chmod 777``
   - SSH 密钥文件权限必须是 ``600``（否则 SSH 会拒绝使用）
   - ``-R`` 递归修改权限时要格外小心，避免误改系统目录


ln：硬链接与软链接
^^^^^^^^^^^^^^^^^^

Linux 中的链接分为两种：硬链接（Hard Link）和软链接（Symbolic Link，也叫符号链接）。

.. code-block:: bash

   # 创建软链接（符号链接）—— 最常用
   ln -s target link_name

   # 示例
   ln -s /usr/local/bin/python3 /usr/local/bin/python
   # 创建一个名为 python 的软链接，指向 python3

   # 创建硬链接
   ln target link_name

.. tip::

   **硬链接 vs 软链接**

   - **软链接**（类似 Windows 的快捷方式）：
     - 是一个独立的文件，内容是目标文件的路径
     - 删除原文件后，软链接失效（变成"断链"）
     - 可以跨文件系统
     - 可以链接目录

   - **硬链接**：
     - 与原文件共享同一个 inode（数据块）
     - 删除原文件后，硬链接仍然有效（数据还在）
     - 不能跨文件系统
     - 不能链接目录

   - 类比：软链接像"路标"（指向某个地址），硬链接像"别名"（就是同一个东西）

   # 查看文件的 inode 号
   ls -i file.txt

   # 查看文件的硬链接数
   ls -l file.txt    # 第 2 列就是硬链接数


文件管理实用技巧
^^^^^^^^^^^^^^^^

.. code-block:: bash

   # 查找并删除空文件
   find /path -type f -empty -delete

   # 查找并删除空目录
   find /path -type d -empty -delete

   # 查找超过 100MB 的文件
   find / -type f -size +100M -exec ls -lh {} \;

   # 查找最近 24 小时内修改过的文件
   find /path -type f -mtime -1

   # 批量修改文件权限（目录 755，文件 644）
   find /path -type d -exec chmod 755 {} \;
   find /path -type f -exec chmod 644 {} \;

   # 统计目录下的文件数量
   find /path -type f | wc -l

   # 查找重复文件（基于 MD5）
   find /path -type f -exec md5sum {} + | sort | uniq -w32 -d
