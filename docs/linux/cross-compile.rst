交叉编译与构建参考手册
======================

本手册系统介绍交叉编译的核心概念、GCC 编译流程、CMake 工程组织、库的创建与链接，
以及实际项目中的常见问题排查方法。

.. contents:: 目录
   :depth: 3
   :local:


工具链设置
----------

交叉编译的"交叉"是什么意思？
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

想象你是一名翻译，你精通中文（宿主机），但需要把一本英文书（源代码）翻译成法文（目标架构的可执行文件）。
你不可能用中文去写法文——你需要一套"中→法"的翻译工具链。

- **宿主机（Host）**：你正在使用的电脑，比如 x86_64 的 Linux 开发机。
- **目标机（Target）**：最终运行程序的设备，比如 ARM 架构的嵌入式板子。
- **交叉编译器**：在宿主机上运行、但生成目标机机器码的编译器。

交叉编译工具链命名规则
^^^^^^^^^^^^^^^^^^^^^^

工具链的名称不是随便起的，它遵循 ``<arch>-<vendor>-<os>-<abi>`` 的命名约定。
理解命名规则能帮你快速判断一个工具链是给什么平台用的：

.. code-block:: text

   arm-linux-gnueabihf-gcc
   │    │     │      │    └── 工具名称 (gcc)
   │    │     │      └────── ABI: gnueabihf = GNU EABI + 硬件浮点
   │    │     └───────────── OS: linux
   │    └─────────────────── vendor: (此处省略，常见为 "none", "unknown")
   └──────────────────────── 目标架构: arm

常见工具链示例：

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - 工具链名称
     - 用途说明
   * - ``arm-linux-gnueabihf-gcc``
     - ARM 32 位，Linux，硬件浮点（树莓派等）
   * - ``aarch64-linux-gnu-gcc``
     - ARM 64 位（AArch64），Linux（RK3588 等）
   * - ``arm-linux-gnueabi-gcc``
     - ARM 32 位，软件浮点（老式嵌入式设备）
   * - ``arm-none-eabi-gcc``
     - ARM 裸机（无操作系统），用于 STM32 等 MCU
   * - ``x86_64-w64-mingw32-gcc``
     - 在 Linux 上交叉编译 Windows 可执行文件
   * - ``mipsel-linux-gnu-gcc``
     - MIPS 小端序，Linux（路由器等）


基础设置
^^^^^^^^

最直接的方式是通过环境变量告诉构建系统使用哪个编译器：

.. code-block:: bash

   # 设置交叉编译工具链
   export CC=arm-linux-gnueabihf-gcc
   export CXX=arm-linux-gnueabihf-g++

   # 验证工具链是否可用
   arm-linux-gnueabihf-gcc --version

   # 查看工具链支持的目标架构
   arm-linux-gnueabihf-gcc -dumpmachine
   # 输出: arm-linux-gnueabihf

**易错点：** 只设置了 ``CC`` 而忘了 ``CXX``，导致 C++ 代码回退到宿主机的 g++ 编译，
链接时报架构不匹配的错误。


Android NDK 工具链设置
^^^^^^^^^^^^^^^^^^^^^^

Android NDK 从 r19 开始默认使用 LLVM/Clang 工具链，不再提供独立的 GCC。
其工具链路径结构与传统 Linux 交叉工具链不同：

.. code-block:: bash

   # 1. 设置 NDK 根目录
   export ANDROID_NDK=/path/to/android-ndk-r27c

   # 2. 工具链预构建目录（NDK 已经为你编译好了交叉编译器）
   export TOOLCHAIN=$ANDROID_NDK/toolchains/llvm/prebuilt/linux-x86_64

   # 3. 目标三元组（aarch64 = ARM 64 位）
   export TARGET=aarch64-linux-android

   # 4. 最低 API 级别（低于此版本的 Android 设备无法运行）
   export API=21

   # 5. 编译器——注意命名格式: <target><api>-clang
   #    这是 NDK 特有的命名方式，将目标架构和 API 级别编码进编译器名
   export CC=$TOOLCHAIN/bin/$TARGET$API-clang
   export CXX=$TOOLCHAIN/bin/$TARGET$API-clang++

   # 6. 归档工具和随机化库工具（使用 LLVM 版本而非 GNU 版本）
   export AR=$TOOLCHAIN/bin/llvm-ar
   export RANLIB=$TOOLCHAIN/bin/llvm-ranlib

   # 7. 验证
   $CC --version

**为什么 API 级别在编译器名里？** Android NDK 把 API 级别编进了编译器路径
（如 ``aarch64-linux-android21-clang``），这样编译器在预处理阶段就能自动过滤掉
该 API 级别不存在的系统函数声明，防止你在编译时调用了一个低版本设备上不存在的函数。

**常见坑：**

- ``armv7a-linux-androideabi``（注意是 ``androdieabi`` 不是 ``gnueabihf``）
  用于 32 位 ARM Android。
- API 级别 21 对应 Android 5.0，是目前比较通用的最低支持版本。
- 如果用 ``gcc`` 而非 ``clang`` 编译 Android 代码，NDK r19+ 已经移除了 GCC。


GCC 编译流程详解
----------------

GCC 编译一个 C 程序并不是一步到位的，它实际分为四个阶段。
理解这四个阶段，就像理解"把一块木头做成桌子"需要经过伐木、切割、打磨、组装四个步骤。

四步编译流程图
^^^^^^^^^^^^^^

.. code-block:: text

   源代码 (.c)
       │
       ▼  ① 预处理 (-E)        展开宏、头文件、条件编译
   预处理后的代码 (.i)
       │
       ▼  ② 编译   (-S)        将 C 代码翻译为汇编语言
   汇编代码 (.s / .S)
       │
       ▼  ③ 汇编   (-c)        将汇编翻译为机器码（目标文件）
   目标文件 (.o)
       │
       ▼  ④ 链接              合并目标文件和库，生成最终可执行文件
   可执行文件 (a.out / demo)


第一步：预处理（-E）
^^^^^^^^^^^^^^^^^^^^^

**是什么：** 预处理器处理所有以 ``#`` 开头的指令——``#include``、``#define``、``#ifdef`` 等。

**为什么需要：** 编译器看不懂 ``#include <stdio.h>``，它需要先把头文件的完整内容复制粘贴过来，
把宏定义替换为实际值，然后才开始真正的编译。

**类比：** 就像你做菜前，先把所有食材从冰箱里拿出来、洗好、切好放在案板上（预处理），
然后才开始炒菜（编译）。

.. code-block:: bash

   # -E: 只做预处理，然后停止
   # -o: 指定输出文件名
   gcc -E demo.c -o demo.i

查看预处理结果，你会看到 ``#include`` 被替换为成千上万行的头文件内容：

.. code-block:: bash

   # 查看预处理后文件的行数（可能有几十万行）
   wc -l demo.i

   # 查看预处理后某个宏是否被正确定义
   grep "MY_DEFINE" demo.i

**易错点：** 预处理阶段不会检查语法错误，所以即使你的宏展开后语法有问题，
预处理阶段也不会报错——错误会在下一步编译阶段才暴露。


第二步：编译（-S）
^^^^^^^^^^^^^^^^^

**是什么：** 编译器将预处理后的 C 代码翻译成目标架构的汇编语言。

**为什么需要：** CPU 不认识 C 语言，它只认识机器指令。汇编语言是机器指令的可读表示，
是 C 和机器码之间的中间层。

.. code-block:: bash

   # -S: 只编译到汇编阶段，然后停止
   gcc -S demo.i -o demo.S

查看生成的汇编代码：

.. code-block:: bash

   # 查看汇编代码（AT&T 语法风格，默认）
   cat demo.S

   # 如果你想看 Intel 语法风格（更易读）
   gcc -S -masm=intel demo.i -o demo.S

**实用技巧：** 想知道编译器对某段 C 代码做了什么优化？用 ``-S`` 看汇编是最直接的方式。
很多性能调优和底层调试都依赖这一步。


第三步：汇编（-c）
^^^^^^^^^^^^^^^^^

**是什么：** 汇编器将人类可读的汇编代码翻译成 CPU 可以直接执行的机器码，存入目标文件（.o）。

**类比：** .o 文件就像建筑的一块预制件——它本身已经做好了（机器码），
但还不能独立使用，需要和其他预制件组装成完整的建筑。

.. code-block:: bash

   # -c: 只做汇编，生成目标文件，不做链接
   gcc -c demo.S -o demo.o

   # 查看目标文件的节（section）信息
   readelf -S demo.o

**关键概念——符号（Symbol）：** .o 文件中包含"符号表"，记录了这个文件定义了哪些函数和变量，
以及引用了哪些外部函数和变量。链接阶段就是根据符号表把多个 .o 文件"缝合"在一起。


第四步：链接
^^^^^^^^^^^^

**是什么：** 链接器将多个目标文件和库文件合并，解析所有外部符号引用，
生成最终的可执行文件。

**类比：** 你写了一个函数调用 ``printf()``，但 ``printf`` 的实现在 libc.so 里。
链接器的工作就是：找到 ``printf`` 的实现地址，把它填到你的调用指令里。

.. code-block:: bash

   # 完整的链接示例
   # -I: 头文件搜索路径 (Include)
   # -L: 库文件搜索路径 (Library)
   # -l: 要链接的库名 (去掉 lib 前缀和 .so/.a 后缀)
   gcc demo.o -I ./includeA -L ./libB -lcommon -o demo

**链接又分两种：**

- **静态链接（-static）：** 把库的代码直接复制到可执行文件中。文件更大，但不依赖外部 .so 文件。
- **动态链接（默认）：** 可执行文件只记录需要哪些 .so 文件，运行时才加载。文件更小，多程序可共享同一份库。


一步到位编译 vs 分步编译
^^^^^^^^^^^^^^^^^^^^^^^^^

日常开发中通常一步到位：

.. code-block:: bash

   # 一步到位（GCC 内部自动走完四步）
   gcc demo.c -o demo

但排查问题时，分步编译非常有用：

.. code-block:: bash

   # 分步编译——每步都可以检查中间产物
   gcc -E demo.c -o demo.i          # 检查头文件是否正确展开
   gcc -S demo.i -o demo.S          # 检查生成的汇编是否合理
   gcc -c demo.S -o demo.o          # 检查目标文件的符号表
   gcc demo.o -o demo               # 检查链接是否成功


常用 GCC 参数详解
^^^^^^^^^^^^^^^^^

优化级别
""""""""

.. code-block:: bash

   # -O0: 不优化（默认），编译最快，调试最方便
   gcc -O0 demo.c -o demo_debug

   # -O1: 基础优化，编译时间和代码质量的平衡
   gcc -O1 demo.c -o demo

   # -O2: 推荐的生产优化级别，不会显著增加编译时间
   gcc -O2 demo.c -o demo_release

   # -O3: 激进优化（循环展开、向量化等），可能增加代码体积
   gcc -O3 demo.c -o demo_fast

   # -Os: 优化代码体积（嵌入式设备常用）
   gcc -Os demo.c -o demo_small

**经验法则：** 开发调试用 ``-O0``，发布用 ``-O2``，嵌入式空间受限用 ``-Os``。
``-O3`` 不一定比 ``-O2`` 快，有时反而因为代码膨胀导致缓存命中率下降而变慢。

警告与调试
""""""""""

.. code-block:: bash

   # -Wall: 开启所有常见警告（强烈建议始终使用）
   gcc -Wall demo.c -o demo

   # -Wextra: 开启额外警告（比 -Wall 更严格）
   gcc -Wall -Wextra demo.c -o demo

   # -Werror: 把警告当作错误处理（CI/CD 中推荐）
   gcc -Wall -Werror demo.c -o demo

   # -g: 生成调试信息（供 gdb 使用）
   gcc -g demo.c -o demo

   # 开发时的推荐组合
   gcc -Wall -Wextra -g -O0 demo.c -o demo

标准与宏定义
""""""""""""

.. code-block:: bash

   # -std=c11: 使用 C11 标准（默认因 GCC 版本而异）
   gcc -std=c11 demo.c -o demo

   # -std=gnu11: C11 + GNU 扩展（比 c11 多一些 GCC 特有的语法）
   gcc -std=gnu11 demo.c -o demo

   # -D: 定义宏（等价于在代码里写 #define DEBUG 1）
   gcc -DDEBUG=1 demo.c -o demo

   # -D 常见用法：条件编译开关
   gcc -DENABLE_LOGGING -DVERSION=\"1.0\" demo.c -o demo

数学库链接
""""""""""

.. code-block:: bash

   # -lm: 链接数学库 libm（使用 sin, cos, sqrt 等函数时需要）
   # 为什么需要手动指定？因为数学库从 libc 中分离出来是历史原因
   gcc demo.c -lm -o demo

   # 易错点: -lm 必须放在源文件之后（GCC 从左到右解析依赖）
   # 正确:
   gcc demo.c -lm -o demo
   # 可能失败:
   gcc -lm demo.c -o demo


CMake 交叉编译
--------------

CMake 工具链文件
^^^^^^^^^^^^^^^^

CMake 本身不了解交叉编译——你需要一个"工具链文件"告诉它：
"别用宿主机的编译器，用我指定的这个。"

**类比：** 工具链文件就像一份"采购清单"，你告诉 CMake："去这个地址拿编译器（CC），
去那个地址找头文件和库（CMAKE_FIND_ROOT_PATH），别在宿主机上找程序（NEVER）。"

.. code-block:: cmake

   # toolchain.cmake -- ARM Linux 交叉编译工具链文件

   # 告诉 CMake 目标系统的信息
   set(CMAKE_SYSTEM_NAME Linux)           # 目标操作系统
   set(CMAKE_SYSTEM_PROCESSOR arm)        # 目标处理器架构

   # 指定交叉编译器
   set(CMAKE_C_COMPILER arm-linux-gnueabihf-gcc)
   set(CMAKE_CXX_COMPILER arm-linux-gnueabihf-g++)

   # sysroot: 目标系统的根文件系统路径（包含 /usr/lib, /usr/include 等）
   set(CMAKE_FIND_ROOT_PATH /usr/arm-linux-gnueabihf)

   # 搜索策略：
   # NEVER  -- 程序（如 cmake 本身）在宿主机上找
   # ONLY   -- 库和头文件只在 sysroot 中找（目标系统的）
   set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
   set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
   set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

使用工具链文件：

.. code-block:: bash

   # -DCMAKE_TOOLCHAIN_FILE 告诉 CMake 使用你的工具链文件
   cmake -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake ..
   make

   # 常用组合：指定构建目录 + 工具链 + 构建类型
   mkdir build && cd build
   cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain.cmake \
         -DCMAKE_BUILD_TYPE=Release ..
   make -j$(nproc)


Android NDK 的 CMake 工具链文件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Android NDK 自带了 CMake 工具链文件，通常不需要自己写：

.. code-block:: bash

   # NDK 自带的工具链文件路径
   cmake -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake \
         -DANDROID_ABI=arm64-v8a \
         -DANDROID_PLATFORM=android-21 \
         -DANDROID_STL=c++_shared \
         ..


CMake 项目结构
^^^^^^^^^^^^^^

一个成熟的 CMake 交叉编译项目通常采用如下结构。
这个结构的核心思想是**把平台差异隔离到独立文件中**，主代码无需关心目标平台：

.. code-block:: text

   项目根目录/
   ├── CMakeLists.txt              # 顶层 CMake，负责添加子模块
   ├── Makefile                    # 便捷入口，指向 cmake 的 project.mk
   ├── cmake/
   │   ├── config/                 # 不同产品的配置（开关、宏定义等）
   │   ├── platform/               # 主机差异化配置（如 0010.cmake, 0027.cmake）
   │   ├── toolchain/              # 不同平台的编译工具链文件
   │   │   ├── arm-linux.cmake
   │   │   ├── aarch64-linux.cmake
   │   │   └── android-arm64.cmake
   │   ├── project.cmake           # 依据 productCode 选择对应的工具链
   │   └── project.mk              # 主 Makefile，设置 productCode 并调用 cmake
   ├── common/                     # 公共库（跨项目复用）
   │   ├── common.c
   │   ├── common.h
   │   └── CMakeLists.txt          # 编译为动态库和静态库
   └── project/                    # 各子项目/模块
       ├── UI/
       ├── voice/
       └── gateway/

顶层 ``CMakeLists.txt`` 示例：

.. code-block:: cmake

   cmake_minimum_required(VERSION 3.10)
   project(MyProject C)

   # 添加公共库子目录
   add_subdirectory(common)

   # 添加各业务模块
   add_subdirectory(project/UI)
   add_subdirectory(project/voice)
   add_subdirectory(project/gateway)

``project.mk`` 示例（通过 Make 传入产品代码来选择不同平台）：

.. code-block:: makefile

   # 用法: make PRODUCT=0010
   # 或: make PRODUCT=0027

   PRODUCT ?= 0010

   # 根据产品代码选择不同的 cmake 配置
   include cmake/platform/$(PRODUCT).cmake
   include cmake/project.cmake

   .PHONY: all clean

   all:
       mkdir -p build && cd build && \
       cmake -DCMAKE_TOOLCHAIN_FILE=$(TOOLCHAIN_FILE) \
             -DPRODUCT=$(PRODUCT) .. && \
       make -j$(nproc)

   clean:
       rm -rf build

**设计要点：**

- ``productCode``（如 0010、0027）对应不同的硬件平台，每个平台有自己的工具链文件。
- 切换平台只需改一个变量，无需修改业务代码。
- 公共库独立编译，子项目通过 ``target_link_libraries`` 引用。


库的创建与使用
--------------

为什么需要理解库？
^^^^^^^^^^^^^^^^^^

想象你写了一组工具函数（比如字符串处理、日志打印），多个项目都要用。
你有两个选择：

1. **每次复制源代码**——改了 bug 要在所有项目里同步修改（噩梦）。
2. **编译成库**——其他项目只需链接这个库，改了 bug 重新编译库即可。

库就是"打包好的可复用代码"。


静态库（.a）
^^^^^^^^^^^^

**是什么：** 静态库是一组 .o 目标文件的打包集合（用 ``ar`` 工具创建）。
链接时，链接器把用到的代码**复制**到可执行文件中。

**类比：** 静态库就像把整本字典复印一份塞进你的书包——你的书包变重了，
但你不再需要随身带原版字典。

.. code-block:: bash

   # 第一步：编译源文件为目标文件（注意 -c 只编译不链接）
   gcc -c common_utils.c -o common_utils.o

   # 第二步：用 ar 工具打包成静态库
   # r: 替换已有的 .o 文件（如果存在）
   # c: 创建库（如果不存在）
   # s: 创建索引（加速链接时的符号查找）
   ar rcs libcommon.a common_utils.o

   # 验证静态库内容
   ar t libcommon.a            # 列出包含的 .o 文件
   nm libcommon.a              # 查看符号表

使用静态库：

.. code-block:: bash

   # 链接静态库
   gcc main.o -L ./lib -lcommon -o demo

   # 强制静态链接（即使有同名 .so 也用 .a）
   gcc main.o -L ./lib -lcommon -static -o demo


动态库（.so）
^^^^^^^^^^^^^

**是什么：** 动态库在编译时只记录"我需要这个库"，不复制代码。
运行时，操作系统的动态链接器（ld-linux.so）才把库加载到内存。

**类比：** 动态库就像你书包里放了一张图书馆借书卡——你的书包很轻，
但运行时你需要去图书馆（系统库路径）把书借出来。

.. code-block:: bash

   # -fpic: 生成位置无关代码（Position Independent Code）
   #        动态库必须用 PIC，因为库加载到内存的地址不固定
   # -shared: 告诉链接器生成共享库而不是可执行文件
   gcc -fpic -shared -o libcommon.so common_utils.c

   # 验证动态库
   readelf -d libcommon.so     # 查看动态段信息
   nm -D libcommon.so          # 查看动态符号表

使用动态库：

.. code-block:: bash

   # 编译时链接
   gcc main.o -L ./lib -lcommon -o demo

   # 运行时——系统需要能找到 .so 文件
   # 方法一：设置环境变量（临时，当前会话有效）
   export LD_LIBRARY_PATH=./lib:$LD_LIBRARY_PATH
   ./demo

   # 方法二：用 -rpath 把库路径写进可执行文件（永久）
   gcc main.o -L ./lib -lcommon -Wl,-rpath,./lib -o demo


动态库 vs 静态库对比
^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - 特性
     - 静态库 (.a)
     - 动态库 (.so)
   * - 文件大小
     - 可执行文件更大（库代码被复制）
     - 可执行文件更小
   * - 运行时依赖
     - 无（所有代码已内嵌）
     - 需要 .so 文件存在于运行环境中
   * - 更新库
     - 需要重新编译可执行文件
     - 替换 .so 文件即可（接口不变的情况下）
   * - 内存占用
     - 每个进程独立一份库代码
     - 多进程共享同一份库代码（节省内存）
   * - 适用场景
     - 嵌入式、单文件分发、避免依赖
     - 通用 Linux 系统、插件架构


链接参数详解
^^^^^^^^^^^^

.. code-block:: bash

   # -I <path>: 添加头文件搜索路径
   # 编译器会在 ./include 目录下寻找 #include 的头文件
   gcc -I ./include main.c -o demo

   # -L <path>: 添加库文件搜索路径
   # 链接器会在 ./lib 目录下寻找 .so 和 .a 文件
   gcc main.o -L ./lib -lcommon -o demo

   # -l<name>: 链接名为 lib<name>.so 或 lib<name>.a 的库
   # -lcommon 会自动查找 libcommon.so 或 libcommon.a
   gcc main.o -lcommon -o demo

   # -rpath <path>: 把运行时库搜索路径嵌入可执行文件
   # 这样运行时就不需要设置 LD_LIBRARY_PATH 了
   gcc main.o -L ./lib -lcommon -Wl,-rpath,/opt/myapp/lib -o demo

   # -static: 强制静态链接所有库
   gcc -static main.o -lcommon -o demo

**参数顺序很重要：** GCC 从左到右解析依赖，被依赖的库要放在依赖它的文件右边。

.. code-block:: bash

   # 正确：main.o 依赖 libcommon，所以 -lcommon 放在右边
   gcc main.o -lcommon -o demo

   # 可能失败：链接器处理 -lcommon 时还不知道 main.o 需要什么符号
   gcc -lcommon main.o -o demo


pkg-config 用法
^^^^^^^^^^^^^^^

**是什么：** pkg-config 是一个帮你管理编译和链接参数的工具。
很多库（OpenSSL、libcurl、GTK 等）安装后会注册一个 ``.pc`` 文件，
告诉你使用这个库需要哪些 ``-I``、``-L``、``-l`` 参数。

**类比：** 就像你买了一个电器，包装盒里有一张卡片写着"需要 220V 电源、
三孔插座"——pkg-config 就是这张卡片。

.. code-block:: bash

   # 查看某个库的编译参数
   pkg-config --cflags openssl     # 输出类似: -I/usr/include/openssl
   pkg-config --libs openssl       # 输出类似: -L/usr/lib -lssl -lcrypto

   # 在编译命令中直接使用
   gcc main.c $(pkg-config --cflags --libs openssl) -o demo

   # 在 CMake 中使用
   find_package(PkgConfig REQUIRED)
   pkg_check_modules(OPENSSL REQUIRED openssl)
   target_include_directories(myapp PRIVATE ${OPENSSL_INCLUDE_DIRS})
   target_link_libraries(myapp ${OPENSSL_LIBRARIES})

   # 查看系统中已安装的包
   pkg-config --list-all


CMake 中创建和使用库
^^^^^^^^^^^^^^^^^^^^

.. code-block:: cmake

   # common/CMakeLists.txt

   # 创建动态库
   add_library(common SHARED common.c common.h)

   # 创建静态库（同一份源码）
   add_library(common_static STATIC common.c common.h)

   # 设置头文件搜索路径（使用此库的 target 自动获得此路径）
   target_include_directories(common PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

   # 项目根目录的 CMakeLists.txt 中使用
   add_executable(demo main.c)
   target_link_libraries(demo common)   # 链接动态库


OpenSSL 交叉编译实战
--------------------

这是一个完整的实战案例：在 x86_64 Linux 开发机上，为 Android ARM64 设备编译 OpenSSL。

整体思路
^^^^^^^^

OpenSSL 使用自己的 ``Configure`` 脚本（不是 CMake 也不是 autotools），
所以你需要通过环境变量告诉它的 Configure 脚本使用你的交叉编译器。

.. code-block:: text

   你需要告诉 OpenSSL 三件事：
   1. 用哪个编译器        → CC 环境变量
   2. 目标平台是什么      → ./Configure android-arm64
   3. 最低 API 级别是多少 → -D__ANDROID_API__=21

完整步骤
^^^^^^^^

.. code-block:: bash

   # ==========================================
   # 第一步：设置 NDK 和工具链环境变量
   # ==========================================
   export ANDROID_NDK=/path/to/android-ndk-r27c
   export TOOLCHAIN=$ANDROID_NDK/toolchains/llvm/prebuilt/linux-x86_64
   export TARGET=aarch64-linux-android
   export API=21

   # 编译器设置
   export CC=$TOOLCHAIN/bin/$TARGET$API-clang
   export CXX=$TOOLCHAIN/bin/$TARGET$API-clang++
   export AR=$TOOLCHAIN/bin/llvm-ar
   export RANLIB=$TOOLCHAIN/bin/llvm-ranlib

   # ==========================================
   # 第二步：配置 OpenSSL
   # ==========================================
   # android-arm64 是 OpenSSL 内置的 target 配置名
   # -D__ANDROID_API__=$API 确保编译时只暴露 API 21 及以下的系统函数
   cd /path/to/openssl-source
   ./Configure android-arm64 -D__ANDROID_API__=$API \
       --prefix=/path/to/install/openssl-android-arm64

   # ==========================================
   # 第三步：编译
   # ==========================================
   # -j$(nproc) 使用所有 CPU 核心并行编译
   make -j$(nproc)

   # ==========================================
   # 第四步：安装到指定目录
   # ==========================================
   make install DESTDIR=/path/to/install

   # ==========================================
   # 第五步：验证产物
   # ==========================================
   file /path/to/install/openssl-android-arm64/lib/libssl.so
   # 应输出: ELF 64-bit LSB shared object, ARM aarch64

常见问题
""""""""

- **``./Configure`` 找不到编译器：** 确认 ``$CC`` 环境变量已设置且路径正确。
- **链接时报 ``undefined reference to __android_log_print``：**
  需要在链接时添加 ``-llog``（Android 日志库）。
- **``make`` 报 ``pod2man`` 错误：** 这是文档生成工具，不影响库本身。
  可以用 ``make build_libs`` 只编译库文件，跳过文档。


调试技巧
--------

调试是交叉编译中不可避免的环节——目标设备上出了问题，你需要在宿主机上分析原因。
以下工具是你的"诊断仪器"。

readelf：查看 ELF 文件信息
^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** ELF（Executable and Linkable Format）是 Linux 上可执行文件和库的标准格式。
``readelf`` 可以解析 ELF 文件的内部结构。

.. code-block:: bash

   # 查看文件头（确认架构、字节序、是否为交叉编译产物）
   readelf -h demo

   # 查看所有节（section）的信息
   readelf -S demo

   # 查看程序头（段信息，运行时需要）
   readelf -l demo

   # 查看动态段（依赖哪些 .so 文件）
   readelf -d demo

   # 查看符号表
   readelf -s demo

**实战用法：** 交叉编译后，第一步用 ``readelf -h`` 确认目标架构是否正确：

.. code-block:: bash

   $ readelf -h demo | grep Machine
   # ARM 32 位应该输出:
   Machine: ARM
   # ARM 64 位应该输出:
   Machine: AArch64

   # 如果输出 "Machine: Advanced Micro Devices X86-64"，
   # 说明你用了宿主机的编译器，没有成功交叉编译！


nm：查看符号表
^^^^^^^^^^^^^^

**是什么：** 符号表记录了目标文件/库中定义和引用的所有函数名、变量名。
排查链接错误时，``nm`` 是最重要的工具。

.. code-block:: bash

   # 查看目标文件的符号
   nm demo.o

   # 符号类型说明:
   # T = 在本文件中定义的函数（Text section）
   # U = 未定义，需要从其他文件/库中找到（Undefined）
   # D = 已初始化的全局变量（Data section）
   # B = 未初始化的全局变量（BSS section）

   # 只看未定义符号（需要链接器解决的外部依赖）
   nm -u demo.o

   # 查看动态库导出了哪些符号
   nm -D libcommon.so

**排查 undefined reference 的经典流程：**

.. code-block:: bash

   # 1. 看报错中缺少什么符号
   # undefined reference to `my_function'

   # 2. 在你的 .o 文件中确认它确实引用了这个符号
   nm -u main.o | grep my_function

   # 3. 在库中确认这个符号是否被导出
   nm -D libcommon.so | grep my_function

   # 如果库中没有这个符号，可能是：
   # - 库编译时没有包含该函数的源文件
   # - 函数名拼写错误或 C++ name mangling 问题


ldd：查看动态库依赖
^^^^^^^^^^^^^^^^^^^^

**是什么：** ``ldd`` 列出一个可执行文件或动态库依赖的所有 .so 文件，
以及系统在当前环境下能否找到它们。

.. code-block:: bash

   # 查看可执行文件依赖哪些动态库
   ldd demo

   # 示例输出:
   # linux-vdso.so.1 (0x00007ffd...)
   # libcommon.so => /usr/lib/libcommon.so (0x00007f...)
   # libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f...)
   # /lib64/ld-linux-x86-64.so.2 (0x00007f...)

   # "not found" 表示某个 .so 文件在系统中找不到

**交叉编译场景注意：** ``ldd`` 是宿主机的工具，它会在宿主机的库路径中搜索。
对于交叉编译产物，应该用交叉工具链版本：

.. code-block:: bash

   # 使用交叉工具链的 readelf 代替（readelf 不需要目标系统的运行环境）
   arm-linux-gnueabihf-readelf -d demo | grep NEEDED

   # 或者用宿主机的 readelf（它只解析文件格式，不运行程序）
   readelf -d demo | grep NEEDED


objdump：反汇编
^^^^^^^^^^^^^^^^

**是什么：** ``objdump`` 可以将二进制文件反汇编成汇编代码，
帮助你理解编译器生成了什么机器指令。

.. code-block:: bash

   # 反汇编整个文件
   objdump -d demo

   # 反汇编指定函数
   objdump -d demo | grep -A 50 '<main>:'

   # 反汇编并显示源代码对照（需要编译时加 -g）
   objdump -S demo

   # 查看特定节的内容
   objdump -s -j .rodata demo

**实战用法：** 怀疑编译器优化掉了某段代码？用 ``objdump -S`` 对照源码和汇编，
看看你写的代码是否真的被编译进去了。


undefined reference 排查方法
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

这是交叉编译中最常见的链接错误。排查思路像侦探破案：

.. code-block:: text

   错误信息: undefined reference to `symbol_name'

   排查步骤:
   ┌─────────────────────────────────────────────────────┐
   │ 1. 符号确实不存在？                                  │
   │    → nm -D libxxx.so | grep symbol_name             │
   │    → 如果没有，检查库版本或编译选项                   │
   ├─────────────────────────────────────────────────────┤
   │ 2. 库没有被链接？                                    │
   │    → 检查 gcc 命令行是否有 -lxxx                     │
   ├─────────────────────────────────────────────────────┤
   │ 3. 链接顺序错误？                                    │
   │    → 被依赖的库放在右边: gcc main.o -lcommon         │
   ├─────────────────────────────────────────────────────┤
   │ 4. C++ name mangling？                               │
   │    → C++ 编译的函数名被修饰了                         │
   │    → 在头文件中用 extern "C" {} 包裹 C 函数声明      │
   ├─────────────────────────────────────────────────────┤
   │ 5. 库路径不在搜索范围内？                            │
   │    → 添加 -L /path/to/lib                           │
   │    → 或设置 LIBRARY_PATH 环境变量                    │
   └─────────────────────────────────────────────────────┘


常见问题
--------

sysroot 配置详解
^^^^^^^^^^^^^^^^

**是什么：** sysroot 是"目标系统的根文件系统"在宿主机上的一个副本。
它包含目标系统的 ``/usr/lib``、``/usr/include`` 等目录。

**为什么需要：** 交叉编译时，编译器需要目标系统的头文件（编译阶段）和库文件（链接阶段）。
但这些文件在目标设备上，不在你的开发机上。sysroot 就是你从目标设备上"拷贝"出来的这些文件。

.. code-block:: bash

   # 方法一：通过环境变量设置 sysroot
   export SYSROOT=/path/to/target-rootfs
   gcc --sysroot=$SYSROOT -I $SYSROOT/usr/include -L $SYSROOT/usr/lib demo.c -o demo

   # 方法二：在工具链文件中设置（CMake）
   set(CMAKE_SYSROOT /path/to/target-rootfs)

   # 方法三：构建 sysroot（从目标设备或发行版获取）
   # 以 Debian ARM 为例，用 debootstrap 创建最小根文件系统
   sudo debootstrap --arch=armhf bullseye /opt/sysroot-armhf http://deb.debian.org/debian

**易错点：** sysroot 中的库版本必须与目标设备上的版本兼容。
如果 sysroot 用了 glibc 2.31 但目标设备是 glibc 2.28，运行时会报
``GLIBC_2.31 not found`` 错误。


LD_LIBRARY_PATH 和 ldconfig
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**是什么：** 运行时，动态链接器（ld-linux.so）需要知道去哪里找 .so 文件。
搜索路径由以下因素决定（按优先级从高到低）：

1. 可执行文件中嵌入的 ``rpath``（编译时用 ``-Wl,-rpath`` 指定）
2. ``LD_LIBRARY_PATH`` 环境变量
3. ``/etc/ld.so.conf`` 及其包含的配置文件
4. 默认路径 ``/lib`` 和 ``/usr/lib``

.. code-block:: bash

   # 临时设置（当前会话有效）
   export LD_LIBRARY_PATH=/opt/myapp/lib:$LD_LIBRARY_PATH
   ./demo

   # 永久方法一：把库路径加入系统配置
   echo "/opt/myapp/lib" | sudo tee /etc/ld.so.conf.d/myapp.conf
   sudo ldconfig              # 重新生成库缓存

   # 永久方法二：编译时嵌入 rpath（推荐，不污染系统配置）
   gcc main.o -lcommon -Wl,-rpath,/opt/myapp/lib -o demo

   # 查看运行时搜索路径
   ldconfig -p | grep libcommon

**踩坑经验：**

- ``LD_LIBRARY_PATH`` 优先级高于系统库路径，如果你设置了一个同名但版本不同的库，
  程序会用你指定的版本——这可能导致意外行为。
- 开发调试时用 ``LD_LIBRARY_PATH`` 比较方便，但生产环境建议用 ``rpath`` 或 ``ldconfig``。


ABI 兼容性问题
^^^^^^^^^^^^^^^

**是什么：** ABI（Application Binary Interface）定义了函数调用约定、数据结构布局、
名称修饰规则等。两个编译单元要链接在一起，它们的 ABI 必须兼容。

**常见 ABI 不兼容场景：**

.. code-block:: text

   场景 1: C 和 C++ 混合编程
   ─────────────────────────
   C++ 编译器会对函数名进行 "name mangling"（名称修饰），
   比如 void foo(int) 可能变成 _Z3fooi。
   如果 C 代码要调用 C++ 的函数，必须用 extern "C" 阻止名称修饰。

   // C++ 头文件中
   #ifdef __cplusplus
   extern "C" {
   #endif
   void foo(int x);    // 告诉 C++ 编译器用 C 的方式命名这个函数
   #ifdef __cplusplus
   }
   #endif

.. code-block:: text

   场景 2: 结构体对齐差异
   ─────────────────────────
   不同编译器或不同平台可能使用不同的结构体对齐规则，
   导致同一个结构体在不同平台上的大小和成员偏移量不同。

   // 确保一致的对齐方式
   #pragma pack(push, 1)
   struct MyData {
       char a;      // 偏移 0
       int b;       // 偏移 1（而不是默认的 4）
   };
   #pragma pack(pop)

.. code-block:: text

   场景 3: 浮点 ABI
   ─────────────────────────
   ARM 平台上，gnueabi（软件浮点）和 gnueabihf（硬件浮点）
   使用不同的寄存器传递浮点参数，两者生成的库不能互换使用。

排查 ABI 问题：

.. code-block:: bash

   # 查看目标文件使用的 ABI 标记
   readelf -A demo.o

   # 对比两个 .o 文件的架构属性
   readelf -A file1.o | grep Tag_ABI
   readelf -A file2.o | grep Tag_ABI


符号冲突处理
^^^^^^^^^^^^

**是什么：** 当两个库导出了同名的函数或变量时，链接器/加载器只会使用其中一个，
这就是符号冲突。表现通常是"调用了 A 库的函数，但实际执行的是 B 库的同名函数"。

**类比：** 你的通讯录里有两个人都叫"张三"，你打电话给"张三"时，
接电话的可能是其中任何一个。

.. code-block:: bash

   # 查看哪些库导出了同名符号
   nm -D libA.so | grep " T " | sort > symbols_A.txt
   nm -D libB.so | grep " T " | sort > symbols_B.txt
   comm -12 symbols_A.txt symbols_B.txt   # 找出两边都有的符号

解决方法：

.. code-block:: text

   方法 1: 使用版本脚本（Version Script）限制导出符号
   ─────────────────────────────────────────────────
   # libA.map
   {
       global:
           api_function_1;
           api_function_2;
       local:
           *;           # 其他符号全部隐藏
   };

   # 编译时使用版本脚本
   gcc -shared -Wl,--version-script=libA.map -o libA.so a.o

.. code-block:: text

   方法 2: 使用 -fvisibility=hidden 默认隐藏所有符号
   ─────────────────────────────────────────────────
   // 编译时加 -fvisibility=hidden，所有符号默认隐藏
   // 然后用 __attribute__((visibility("default"))) 显式导出需要的符号
   __attribute__((visibility("default")))
   void public_api_function(void) { ... }

.. code-block:: text

   方法 3: dlopen + RTLD_LOCAL（动态加载时隔离符号）
   ─────────────────────────────────────────────────
   // 加载 .so 时使用 RTLD_LOCAL 标志，使其符号不暴露给其他库
   void *handle = dlopen("libA.so", RTLD_LAZY | RTLD_LOCAL);


头文件找不到
^^^^^^^^^^^^

.. code-block:: bash

   # 错误: fatal error: xxx.h: No such file or directory

   # 排查步骤:
   # 1. 确认头文件确实存在
   find /path/to/sysroot -name "xxx.h"

   # 2. 检查编译命令是否包含正确的 -I 路径
   echo $CFLAGS
   # 确保 -I /path/to/正确的目录 在其中

   # 3. 检查 CMake 中的 include_directories / target_include_directories
   # 在 CMakeLists.txt 中:
   # target_include_directories(myapp PRIVATE /path/to/headers)

   # 4. 检查 pkg-config 是否能找到该库
   pkg-config --cflags libname


运行时错误
^^^^^^^^^^

.. code-block:: bash

   # 错误: ./demo: cannot execute binary file: Exec format error
   # 原因: 你运行了交叉编译的产物，但当前机器不是目标架构
   file demo
   # 输出: ELF 64-bit LSB executable, ARM aarch64 ...
   # 解决: 把 demo 复制到目标设备上运行

   # 错误: ./demo: error while loading shared libraries: libcommon.so
   # 原因: 运行时找不到动态库
   # 解决: 设置 LD_LIBRARY_PATH 或使用 rpath
   export LD_LIBRARY_PATH=/path/to/lib:$LD_LIBRARY_PATH

   # 错误: /lib/arm-linux-gnueabihf/libc.so.6: version `GLIBC_2.28' not found
   # 原因: 编译时使用的 glibc 版本比目标设备上的高
   # 解决: 用与目标设备相同或更低版本的 sysroot 重新编译


快速参考
--------

常用命令速查
^^^^^^^^^^^^

.. code-block:: bash

   # ---- 编译 ----
   gcc -Wall -Wextra -g -O0 demo.c -o demo_debug    # 开发调试
   gcc -Wall -O2 demo.c -o demo_release               # 发布优化
   gcc -E demo.c -o demo.i                             # 预处理
   gcc -S demo.c -o demo.S                             # 编译到汇编
   gcc -c demo.c -o demo.o                             # 编译到目标文件

   # ---- 创建库 ----
   gcc -fpic -shared -o libfoo.so foo.c               # 动态库
   gcc -c foo.c && ar rcs libfoo.a foo.o               # 静态库

   # ---- 链接 ----
   gcc main.o -L ./lib -lfoo -o demo                  # 链接库
   gcc main.o -L ./lib -lfoo -Wl,-rpath,./lib -o demo # 带 rpath

   # ---- 分析 ----
   readelf -h demo                                     # 文件头
   readelf -d demo                                     # 动态依赖
   nm -D libfoo.so                                     # 动态符号
   ldd demo                                            # 运行时依赖
   objdump -S demo                                     # 反汇编对照源码

   # ---- CMake ----
   cmake -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake ..    # 交叉编译
   cmake -DCMAKE_BUILD_TYPE=Release ..                 # Release 构建
   cmake -DCMAKE_INSTALL_PREFIX=/opt/myapp ..          # 指定安装路径
