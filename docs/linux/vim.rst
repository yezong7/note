.. meta::
   :description: Vim 编辑器完整参考手册
   :keywords: vim, 编辑器, 文本编辑, 终端, Linux

============================
Vim 编辑器完整参考手册
============================

.. contents:: 目录
   :depth: 3
   :local:

概述
====

Vim（Vi IMproved）是一款高度可配置的文本编辑器，被誉为"编辑器之神"。它继承了经典 Vi 编辑器的核心思想，同时增加了大量现代功能。Vim 的设计理念是**让双手始终停留在主键盘区**，通过模式切换和组合命令实现高效的文本编辑。

**为什么学习 Vim？**

- **效率极高**：熟练后编辑速度远超普通编辑器
- **无处不在**：几乎所有 Linux/Unix 系统都预装了 Vi/Vim
- **可扩展性强**：通过插件可以变成 IDE
- **减少鼠标依赖**：减少手部移动，降低 RSI（重复性劳损）风险

**比喻理解**：如果把普通编辑器比作"用筷子吃饭"（直接、直观），那么 Vim 就像"用刀叉西餐"——每种工具各司其职，配合使用效率极高，但需要先学习正确的握法。

.. code-block:: bash

   # 启动 Vim
   vim                    # 打开空白缓冲区
   vim file.txt           # 打开指定文件
   vim +10 file.txt       # 打开文件并跳转到第 10 行
   vim +/pattern file.txt # 打开文件并跳转到第一个匹配处
   vim -R file.txt        # 只读模式打开
   vim -d file1 file2     # 比较模式（diff）


模式系统
========

Vim 最独特的设计就是**模式系统**。普通编辑器只有一个模式——打字就是输入，Vim 则把"移动光标"和"输入文字"分成了不同的模式。

**为什么需要模式？**

想象你在写文章时，有时需要打字（输入模式），有时需要移动到某个位置修改（导航模式），有时需要选中一段文字操作（选择模式）。普通编辑器通过鼠标和方向键切换这些状态，而 Vim 用键盘模式切换，双手不需要离开主键盘区。

**核心比喻**：

- **Normal 模式** = 开车：控制车辆（光标）移动
- **Insert 模式** = 加油：往油箱（文件）里加东西
- **Visual 模式** = 圈地：选中一块地（文本）进行操作
- **Command-line 模式** = 导航设定：设置目的地（执行命令）

模式切换总览
------------

.. code-block:: bash

   # 从 Normal 模式进入其他模式
   i                    # 进入 Insert 模式（当前位置）
   v                    # 进入 Visual 模式（字符选择）
   :                    # 进入 Command-line 模式

   # 从任何模式返回 Normal 模式
   Esc                  # 标准方式
   Ctrl+[               # 等效 Esc（更不容易误触）
   Ctrl+c               # 也可以返回，但可能有副作用

**实用技巧**：在键盘上按 Caps Lock 键不方便，很多人把 Caps Lock 映射为 Esc 或 Ctrl，这是提升 Vim 效率的第一步。


Normal 模式（普通模式）
-----------------------

**是什么**：Normal 模式是 Vim 的默认模式，也是最常用的模式。在这个模式下，键盘输入被解释为命令（移动、删除、复制等），而不是文本内容。

**为什么需要它**：在普通编辑器中，你必须用鼠标选中文字再操作，或者用 Ctrl+X 等组合键。在 Vim 的 Normal 模式下，简单的按键就能完成复杂的编辑操作。

**比喻**：Normal 模式就像驾驶座——你可以控制车辆的行驶方向（移动光标）、按喇叭（执行命令）、打开雨刷（搜索替换），但你不会在驾驶座上写东西。

.. code-block:: bash

   # 进入 Normal 模式
   Esc                  # 从任何模式返回 Normal 模式
   Ctrl+[               # 等效替代

   # Normal 模式下的典型操作
   dd                   # 删除当前行
   yy                   # 复制当前行
   p                    # 粘贴
   u                    # 撤销
   /pattern             # 搜索


Insert 模式（插入模式）
-----------------------

**是什么**：Insert 模式是 Vim 中唯一可以输入文本的模式。在这个模式下，键盘输入就像普通编辑器一样，直接插入到文件中。

**为什么需要它**：当然需要输入文字！但 Vim 的设计哲学是——你大部分时间应该在 Normal 模式下导航和操作，只在需要输入时才进入 Insert 模式，输入完立即返回 Normal 模式。

**比喻**：Insert 模式就像打开水龙头——只有在需要注水（输入文字）时才打开，用完就关上（返回 Normal），否则水（光标操作）会浪费。

**多种进入方式**：

.. code-block:: bash

   # 进入 Insert 模式的各种方式
   i                    # 在光标前插入（insert）
   a                    # 在光标后插入（append）
   I                    # 在行首插入（Insert at beginning）
   A                    # 在行尾插入（Append at end）
   o                    # 在下方新开一行并插入（open below）
   O                    # 在上方新开一行并插入（Open above）

**选择哪种进入方式？**

- ``i`` 最常用，在光标位置开始输入
- ``a`` 适合在字符后补充内容（比如在括号后加内容）
- ``I`` 适合在行首添加内容（比如添加注释符号 ``//``）
- ``A`` 适合在行尾添加内容（比如添加分号 ``;``）
- ``o`` 适合在当前行下方新增一行
- ``O`` 适合在当前行上方新增一行

**实用技巧**：

.. code-block:: bash

   # 快速从 Insert 返回 Normal
   jj                   # 如果在 .vimrc 中设置了 imap jj <Esc>
   Ctrl+[               # 标准替代 Esc

   # 快速输入单个字符再返回 Normal
   gi                   # 在上次插入的位置重新进入 Insert 模式


Visual 模式（可视模式）
-----------------------

**是什么**：Visual 模式用于选择文本块。选中后可以对选中区域执行各种操作（删除、复制、缩进等）。

**为什么需要它**：Normal 模式下的操作对象通常是"一个单词""一行""到某个位置"，而 Visual 模式让你自由选择任意范围的文本。

**比喻**：Visual 模式就像用荧光笔在书上画线——先选定范围，再决定怎么处理这个范围。

**三种子模式**：

.. code-block:: bash

   v                    # 字符选择（Characterwise Visual）
   V                    # 行选择（Linewise Visual）
   Ctrl+v               # 块选择（Blockwise Visual）——矩形区域

   # 在 Visual 模式下选择后执行操作
   d                    # 删除选中内容
   y                    # 复制选中内容
   c                    # 修改选中内容（删除并进入 Insert）
   >                    # 右缩进
   <                    # 左缩进
   =                    # 自动缩进
   ~                    # 切换大小写
   u                    # 转小写
   U                    # 转大写

**字符选择 vs 行选择 vs 块选择**：

- **字符选择 (v)**：精确到字符，适合选择不规则的文本片段
- **行选择 (V)**：以行为单位，适合操作整行或多行
- **块选择 (Ctrl+v)**：矩形区域，适合对齐的列操作（比如批量添加注释）

.. code-block:: bash

   # 示例：块选择批量添加注释
   # 1. Ctrl+v 进入块选择
   # 2. 用 j/k 选择多行
   # 3. I 输入 "// "（注意空格）
   # 4. 按 Esc 应用到所有选中行


Command-line 模式（命令行模式）
------------------------------

**是什么**：Command-line 模式允许你输入更复杂的命令，包括保存、退出、搜索替换、设置选项等。

**为什么需要它**：简单的按键操作不足以覆盖所有需求。比如"将全文的 foo 替换为 bar"需要一个命令来表达。

**比喻**：Command-line 模式就像给汽车输入导航地址——你告诉它去哪里，它带你去。

.. code-block:: bash

   # 进入 Command-line 模式
   :                    # 执行 Ex 命令
   /                    # 向下搜索
   ?                    # 向上搜索

   # 常用命令行命令
   :w                   # 保存（write）
   :q                   # 退出（quit）
   :wq                  # 保存并退出
   :q!                  # 强制退出不保存
   :w filename          # 另存为
   :e filename          # 打开另一个文件
   :!command            # 执行外部命令
   :set option          # 设置选项
   :help topic          # 查看帮助


模式切换最佳实践
-----------------

**Vim 的黄金法则**：在 Normal 模式下停留尽可能长的时间，只在需要输入时短暂进入 Insert 模式。

.. code-block:: bash

   # 不好的习惯：长时间停留在 Insert 模式
   # 输入一大堆文字 -> 用方向键移动 -> 继续输入

   # 好的习惯：频繁切换模式
   i                    # 进入 Insert
   Hello World          # 输入内容
   Esc                  # 返回 Normal
   w                    # 移动到下一个单词
   cw                   # 修改这个单词（自动进入 Insert）
   New Text             # 输入新内容
   Esc                  # 返回 Normal


光标移动
========

光标移动是 Vim 操作的基础。在 Normal 模式下，你可以用各种按键快速移动光标，双手始终停留在主键盘区。

**核心理念**：Vim 的移动命令可以与操作命令组合。比如 ``d`` 是删除，``w`` 是移动到下一个单词，``dw`` 就是"删除到下一个单词"。这种**动词+名词**的组合是 Vim 的核心语法。


基础移动
--------

.. code-block:: bash

   h                    # 左移一个字符（记忆：最左边的键）
   j                    # 下移一行（记忆：向下箭头形状）
   k                    # 上移一行（记忆：向上箭头形状）
   l                    # 右移一个字符（记忆：最右边的键）

**为什么用 hjkl 而不是方向键？**

方向键需要右手离开主键盘区，而 hjkl 就在右手下方，手指不需要移动。这看起来微不足道，但当你每分钟执行上百次移动时，节省的时间非常可观。

**记忆技巧**：``h`` 和 ``l`` 分别在左右两侧（left/right），``j`` 像向下的钩子，``k`` 像向上伸的手。

**实用技巧**：

.. code-block:: bash

   5j                   # 向下移动 5 行（数字前缀 = 重复次数）
   10l                  # 向右移动 10 个字符
   3k                   # 向上移动 3 行


单词移动
--------

**是什么**：单词移动让你按"词"为单位移动光标，比逐字符移动快得多。

**为什么需要它**：编辑代码时，大部分操作都以单词为单位（变量名、函数名、关键字），单词移动正好匹配这种需求。

.. code-block:: bash

   w                    # 移动到下一个单词的开头（word）
   b                    # 移动到上一个单词的开头（back）
   e                    # 移动到当前/下一个单词的末尾（end）
   W                    # 以空格为分隔的大单词开头
   B                    # 以空格为分隔的大单词末尾
   E                    # 以空格为分隔的大单词末尾

**小写 vs 大写的区别**：

- 小写 ``w/b/e``：以标点符号为分隔（``foo-bar`` 算 3 个单词：``foo``、``-``、``bar``）
- 大写 ``W/B/E``：仅以空白为分隔（``foo-bar`` 算 1 个单词）

**比喻**：小写单词移动像"跨步走"，遇到标点就停；大写单词移动像"大跨步"，只在空格处停。

.. code-block:: bash

   # 示例文本：hello-world vim-editor
   # w 会在 hello, -, world, vim, -, editor 之间跳转
   # W 会在 hello-world, vim-editor 之间跳转

   3w                   # 向前移动 3 个单词
   2b                   # 向后移动 2 个单词


行内跳转
--------

.. code-block:: bash

   0                    # 跳到行首（第 0 列）
   $                    # 跳到行尾
   ^                    # 跳到行内第一个非空字符（首字母）
   g_                   # 跳到行内最后一个非空字符

**实用技巧**：

.. code-block:: bash

   # 快速选中一行内容（不含换行符）
   ^v$                  # 跳到首字母 -> 进入 Visual -> 跳到行尾

   # 快速在行首行尾之间跳转
   0$                   # 跳到行首再到行尾（用于确认行内容）


行内字符搜索
------------

**是什么**：``f/F/t/T`` 命令可以在当前行内快速跳转到指定字符。

**为什么需要它**：编辑代码时经常需要跳到某个符号（括号、引号、等号等），字符搜索比反复按 ``l`` 快得多。

.. code-block:: bash

   f{char}              # 跳到当前行下一个 char 字符（find）
   F{char}              # 跳到当前行上一个 char 字符（Find 反向）
   t{char}              # 跳到 char 前一个字符（to）
   T{char}              # 跳到 char 后一个字符（To 反向）
   ;                    # 重复上次 f/F/t/T（同方向）
   ,                    # 反向重复上次 f/F/t/T

**f 和 t 的区别**：

- ``f`` 跳到字符**上面**
- ``t`` 跳到字符**前面**（差一个字符）

**比喻**：``f`` 像"走到门口"，``t`` 像"走到门口前面一点"。

.. code-block:: bash

   # 示例：快速移动到等号
   # 文本：const name = "hello"
   f=                   # 光标跳到 = 上面
   t=                   # 光标跳到 = 前面（空格上）

   # 连续使用 ; 重复
   f.                   # 跳到下一个句号
   ;                    # 再跳到下一个
   ,                    # 反向跳回上一个


屏幕移动
--------

.. code-block:: bash

   Ctrl+d               # 向下翻半屏（down）
   Ctrl+u               # 向上翻半屏（up）
   Ctrl+f               # 向下翻一屏（forward）
   Ctrl+b               # 向上翻一屏（backward）
   Ctrl+e               # 屏幕向下滚一行（不移动光标）
   Ctrl+y               # 屏幕向上滚一行（不移动光标）

**光标不动 vs 光标跟随**：

- ``Ctrl+d/u/f/b``：屏幕和光标一起移动
- ``Ctrl+e/y``：只滚动屏幕，光标保持在原位

**实用技巧**：

.. code-block:: bash

   # 快速回到原来的位置
   Ctrl+o               # 跳回上一个位置（jump list）
   Ctrl+i               # 跳到下一个位置（反向 jump list）


屏幕定位
--------

.. code-block:: bash

   H                    # 移动到屏幕顶部（High）
   M                    # 移动到屏幕中部（Middle）
   L                    # 移动到屏幕底部（Low）
   zt                   # 将当前行滚动到屏幕顶部（top）
   zz                   # 将当前行滚动到屏幕中部（center）
   zb                   # 将当前行滚动到屏幕底部（bottom）

**实用技巧**：

.. code-block:: bash

   # 查看当前行的上下文
   zz                   # 将当前行居中，方便查看上下文
   zt                   # 将当前行移到顶部，查看下方内容
   zb                   # 将当前行移到底部，查看上方内容


文件跳转
--------

.. code-block:: bash

   gg                   # 跳到文件第一行
   G                    # 跳到文件最后一行
   {n}G                 # 跳到第 n 行（如 42G 跳到第 42 行）
   :{n}                 # 也可以用命令跳到第 n 行（如 :42）
   %                    # 跳到文件百分比位置（如 50% 跳到中间）

**实用技巧**：

.. code-block:: bash

   # 快速查看文件有多少行
   Ctrl+g               # 在状态栏显示文件信息（行数、百分比）

   # 跳到上次编辑的位置
   '.                   # 跳到上次修改的行
   `.                   # 跳到上次修改的精确位置

   # 跳到上次打开文件的位置
   `"                   # 打开文件后自动跳到上次光标位置（需 viminfo 支持）


标记系统
--------

**是什么**：标记就像在书页上夹书签——你可以在文件的任意位置设置标记，然后随时跳回。

**为什么需要它**：当你在文件中多处编辑时，标记让你在不同位置之间快速切换。

.. code-block:: bash

   m{a-z}               # 在当前光标位置设置标记 a-z（小写：文件内标记）
   '{a-z}               # 跳到标记所在行的首字母
   `{a-z}               # 跳到标记的精确位置（行+列）

   m{A-Z}               # 设置全局标记 A-Z（跨文件标记）
   '{A-Z}               # 跳到全局标记所在文件的行
   `{A-Z}               # 跳到全局标记的精确位置

**小写 vs 大写标记**：

- **小写 (a-z)**：文件内标记，只在当前文件有效
- **大写 (A-Z)**：全局标记，可以在不同文件间跳转

**比喻**：小写标记像"在当前页夹书签"，大写标记像"在另一本书里夹书签"。

.. code-block:: bash

   # 使用示例
   ma                   # 在当前位置设置标记 a
   # ... 移动到其他位置编辑 ...
   `a                   # 跳回标记 a 的精确位置
   'a                   # 跳回标记 a 所在行的开头

   # 查看所有标记
   :marks               # 列出所有标记

   # 特殊标记
   `.                   # 上次修改的位置
   `^                   # 上次插入的位置
   ``                   # 上次跳转前的位置


括号匹配
--------

.. code-block:: bash

   %                    # 跳到匹配的括号/花括号/方括号

**适用的括号类型**：``()``、``[]``、``{}``、``/* */``（C 风格注释）

**实用技巧**：

.. code-block:: bash

   # 快速选中括号内容
   # 光标在 ( 上时：
   v%                   # 选中从 ( 到匹配的 ) 之间的内容

   # 快速修改括号内容
   ci(                  # 修改括号内的内容（change inner paren）
   ci[                  # 修改方括号内的内容
   ci{                  # 修改花括号内的内容
   ci"                  # 修改引号内的内容


数字前缀
--------

几乎所有 Vim 命令都可以加数字前缀表示重复次数：

.. code-block:: bash

   5j                   # 向下移动 5 行
   3w                   # 向前移动 3 个单词
   10dd                 # 删除 10 行
   5yy                  # 复制 5 行
   3x                   # 删除 3 个字符
   2dw                  # 删除 2 个单词


编辑操作
========

Vim 的编辑操作遵循一个强大的语法：**动词 + 名词/范围**。

**核心语法**：

- **动词**：要执行的操作（d=删除, c=修改, y=复制）
- **名词/范围**：操作的对象（w=单词, $=到行尾, G=到文件末尾）

这种组合可以产生大量命令，而不需要逐一记忆。


删除操作
--------

**动词**：``d``（delete）

.. code-block:: bash

   x                    # 删除光标下的字符
   X                    # 删除光标前的字符
   dd                   # 删除整行
   D                    # 删除到行尾（等效 d$）
   d$                   # 删除到行尾
   d0                   # 删除到行首
   d^                   # 删除到行首第一个非空字符
   dw                   # 删除到下一个单词开头
   de                   # 删除到当前单词末尾
   db                   # 删除到上一个单词开头
   dG                   # 删除到文件末尾
   dgg                  # 删除到文件开头
   d%                   # 删除到匹配的括号
   df{char}             # 删除到指定字符（含字符）
   dt{char}             # 删除到指定字符（不含字符）

**数字前缀**：

.. code-block:: bash

   3dd                  # 删除 3 行
   2dw                  # 删除 2 个单词
   5x                   # 删除 5 个字符

**实用技巧**：

.. code-block:: bash

   # 删除空行
   dd                   # 光标在空行上直接 dd

   # 删除多行空行
   :g/^$/d              # 删除所有空行

   # 删除行尾空格
   :%s/\s\+$//g         # 删除所有行尾空格


修改操作
--------

**动词**：``c``（change）—— 删除并进入 Insert 模式

.. code-block:: bash

   cw                   # 修改到单词末尾
   cb                   # 修改到单词开头
   c$                   # 修改到行尾（等效 C）
   c0                   # 修改到行首
   cc                   # 修改整行（删除内容但保留空行）
   C                    # 修改到行尾
   ciw                  # 修改整个单词（change inner word）
   ci"                  # 修改引号内的内容
   ci(                  # 修改圆括号内的内容
   ci[                  # 修改方括号内的内容
   ci{                  # 修改花括号内的内容
   cit                  # 修改标签内的内容（HTML/XML）
   cf{char}             # 修改到指定字符（含字符）
   ct{char}             # 修改到指定字符（不含字符）

**c 和 d 的区别**：

- ``d`` 只删除
- ``c`` 删除后自动进入 Insert 模式（方便输入新内容）

**实用技巧**：

.. code-block:: bash

   # 快速修改引号内的字符串
   ci"                  # 删除引号内容并进入 Insert 模式
   # 输入新字符串
   Esc                  # 返回 Normal 模式

   # 快速修改函数参数
   ci(                  # 修改圆括号内的内容

   # 快速修改 HTML 标签内容
   cit                  # 修改标签内的内容


复制粘贴
--------

.. code-block:: bash

   yy                   # 复制整行（yank）
   Y                    # 复制整行（等效 yy）
   y$                   # 复制到行尾
   y0                   # 复制到行首
   yw                   # 复制一个单词
   ye                   # 复制到单词末尾
   yG                   # 复制到文件末尾
   ygg                  # 复制到文件开头
   p                    # 在光标后粘贴（put）
   P                    # 在光标前粘贴

**数字前缀**：

.. code-block:: bash

   5yy                  # 复制 5 行
   3yw                  # 复制 3 个单词

**粘贴行为**：

- ``p`` 在光标后粘贴（行操作时在下方粘贴）
- ``P`` 在光标前粘贴（行操作时在上方粘贴）

**实用技巧**：

.. code-block:: bash

   # 快速复制一行并粘贴到下方
   yyp                  # 复制当前行并在下方粘贴

   # 交换两行
   ddp                  # 删除当前行并在下方粘贴

   # 复制到系统剪贴板（需 +clipboard 支持）
   "+yy                 # 复制到系统剪贴板
   "+p                  # 从系统剪贴板粘贴


撤销与重做
----------

.. code-block:: bash

   u                    # 撤销（undo）
   Ctrl+r               # 重做（redo）
   U                    # 撤销对整行的所有修改

**撤销树**：

Vim 的撤销不是线性的，而是一棵树。你可以撤销多次，然后在某个分支上做新操作，之前的分支仍然保留。

.. code-block:: bash

   # 查看撤销树
   :undolist            # 显示撤销列表

   # 在撤销树中导航
   g+                   # 在撤销树中向前（更新的状态）
   g-                   # 在撤销树中向后（更旧的状态）


替换操作
--------

.. code-block:: bash

   r{char}              # 替换光标下的单个字符（不进入 Insert）
   R                    # 进入替换模式（覆盖输入，直到按 Esc）

**r 和 R 的区别**：

- ``r`` 只替换一个字符，然后自动返回 Normal 模式
- ``R`` 进入持续覆盖模式，像按下了 Insert 键的覆盖版本

.. code-block:: bash

   # 示例
   rX                   # 将光标下的字符替换为 X
   R                    # 进入替换模式
   ABCDE                # 逐个覆盖字符
   Esc                  # 返回 Normal 模式


缩进操作
--------

.. code-block:: bash

   >>                   # 当前行右缩进
   <<                   # 当前行左缩进
   >{motion}            # 对范围右缩进（如 >G 右缩进到文件末尾）
   <{motion}            # 对范围左缩进
   =                    # 自动缩进当前行
   ={motion}            # 对范围自动缩进
   ==                   # 自动缩进当前行

**在 Visual 模式下**：

.. code-block:: bash

   # 先选中多行，然后缩进
   Vjj                  # 选择 3 行
   >                    # 右缩进
   <                    # 左缩进
   =                    # 自动缩进

**实用技巧**：

.. code-block:: bash

   # 自动缩进整个文件
   gg=G                 # 跳到开头 -> 自动缩进到末尾

   # 缩进选中的代码块
   =i{                  # 自动缩进花括号内的内容
   =ip                  # 自动缩进段落


点命令（.）
-----------

**是什么**：点命令 ``.`` 重复上一次的修改操作。这是 Vim 最强大的功能之一。

**为什么需要它**：很多编辑操作是重复性的——在多处执行相同的修改。点命令让你执行一次，然后重复多次。

**比喻**：点命令就像"复制上一步操作"——你做了一步，然后按 ``.`` 就能重复它。

.. code-block:: bash

   # 示例 1：在多行末尾添加分号
   A;                   # 在行尾添加分号（进入 Insert，输入 ;，返回 Normal）
   j                    # 移动到下一行
   .                    # 重复"在行尾添加分号"
   j
   .
   # ... 重复

   # 示例 2：删除多行中的某个单词
   dw                   # 删除一个单词
   j                    # 移动到下一行
   .                    # 重复删除单词
   j
   .

   # 示例 3：配合搜索批量操作
   /TODO                # 搜索 TODO
   cwDONE               # 修改为 DONE
   n                    # 跳到下一个 TODO
   .                    # 重复修改
   n
   .

**为什么点命令如此强大**：

点命令的关键在于"如何定义一个可重复的操作"。好的做法是用 ``c`` 而不是 ``d``+``i``，因为 ``c`` 是一个原子操作，点命令会完整重复它。


大小写切换
----------

.. code-block:: bash

   ~                    # 切换光标下字符的大小写
   g~{motion}           # 切换范围内的大小写
   gU{motion}           # 将范围转为大写
   gu{motion}           # 将范围转为小写

**实用技巧**：

.. code-block:: bash

   gUiw                 # 将当前单词转为大写
   guiw                 # 将当前单词转为小写
   gUU                  # 将整行转为大写
   guu                  # 将整行转为小写
   g~$                  # 切换到行尾的大小写

**在 Visual 模式下**：

.. code-block:: bash

   v                    # 进入 Visual 模式
   # 选择文本
   U                    # 转为大写
   u                    # 转为小写
   ~                    # 切换大小写


组合操作（动词+名词）
---------------------

Vim 的操作命令遵循 **动词 + 名词/范围** 的语法，可以自由组合：

**动词**：

- ``d`` 删除（delete）
- ``c`` 修改（change）
- ``y`` 复制（yank）
- ``>`` 右缩进
- ``<`` 左缩进
- ``=`` 自动缩进
- ``gU`` 转大写
- ``gu`` 转小写
- ``g~`` 切换大小写

**名词/范围**：

- ``w`` 单词（word）
- ``W`` 大单词（WORD）
- ``$`` 到行尾
- ``0`` 到行首
- ``^`` 到首字母
- ``e`` 单词末尾
- ``b`` 单词开头
- ``G`` 到文件末尾
- ``gg`` 到文件开头
- ``%`` 到匹配括号
- ``iw`` 内部单词（inner word）
- ``aw`` 包含空格的单词（a word）
- ``i"`` 引号内部
- ``a"`` 包含引号
- ``i(`` 圆括号内部
- ``a(`` 包含圆括号
- ``i{`` 花括号内部
- ``a{`` 包含花括号
- ``it`` 标签内部（inner tag）
- ``at`` 包含标签（a tag）
- ``ip`` 段落内部
- ``ap`` 包含段落

**组合示例**：

.. code-block:: bash

   # 删除操作
   dw                   # 删除一个单词
   daw                  # 删除一个单词（含空格）
   diw                  # 删除单词内容（不含空格）
   d$                   # 删除到行尾
   dG                   # 删除到文件末尾
   d%                   # 删除到匹配括号

   # 修改操作
   cw                   # 修改一个单词
   ciw                  # 修改单词内容
   ci"                  # 修改引号内容
   ci(                  # 修改圆括号内容
   ci{                  # 修改花括号内容
   ci`                  # 修改反引号内容
   cit                  # 修改 HTML 标签内容

   # 复制操作
   yw                   # 复制一个单词
   yiw                  # 复制单词内容
   y$                   # 复制到行尾

   # 缩进操作
   >ip                  # 缩进段落
   =i{                  # 自动缩进花括号内容


搜索与替换
==========

搜索与替换是文本编辑的核心功能，Vim 在这方面提供了强大的正则表达式支持。


基础搜索
--------

.. code-block:: bash

   /pattern             # 向下搜索 pattern
   ?pattern             # 向上搜索 pattern
   n                    # 跳到下一个匹配（同方向）
   N                    # 跳到上一个匹配（反方向）
   *                    # 搜索光标下的单词（向下）
   #                    # 搜索光标下的单词（向上）

**搜索选项**：

.. code-block:: bash

   # 在 .vimrc 中设置
   set hlsearch         # 搜索结果高亮
   set incsearch        # 增量搜索（边输入边搜索）
   set ignorecase       # 忽略大小写
   set smartcase        # 智能大小写（包含大写字母时区分大小写）

**实用技巧**：

.. code-block:: bash

   # 取消搜索高亮
   :noh                 # 取消高亮（no highlight）

   # 使用 very magic 模式搜索（减少转义）
   /\vpattern           # very magic 模式

   # 搜索当前单词
   *                    # 向下搜索光标下的单词
   #                    # 向上搜索光标下的单词
   g*                   # 向下搜索（部分匹配）
   g#                   # 向上搜索（部分匹配）


搜索历史
--------

.. code-block:: bash

   # 在搜索模式下
   /                    # 进入搜索模式
   Ctrl+p               # 上一个搜索历史
   Ctrl+n               # 下一个搜索历史

   # 查看搜索历史
   :history /           # 显示搜索历史


替换命令
--------

**基本语法**：``:[range]s/old/new/[flags]``

.. code-block:: bash

   # 当前行替换
   :s/old/new/          # 当前行第一个匹配
   :s/old/new/g         # 当前行所有匹配（g = global）

   # 全文替换
   :%s/old/new/g        # 全文所有匹配（% = 全文范围）
   :%s/old/new/gc       # 全文替换，逐个确认（c = confirm）

   # 范围替换
   :10,20s/old/new/g    # 第 10-20 行替换
   :.,.+5s/old/new/g    # 当前行到下 5 行
   :'<,'>s/old/new/g    # Visual 选中范围替换

   # 使用正则
   :%s/\d\+/NUMBER/g    # 将所有数字替换为 NUMBER

**范围表示法**：

.. code-block:: bash

   :%                   # 全文
   :1,10                # 第 1 到 10 行
   :.,$                 # 当前行到文件末尾
   :.,.+5               # 当前行到下 5 行
   :'<,'>               # Visual 选中范围
   :/start/,/end/       # 从匹配 start 到匹配 end

**替换标志**：

.. code-block:: bash

   g                    # 全局替换（一行内所有匹配）
   c                    # 逐个确认
   i                    # 忽略大小写
   I                    # 区分大小写
   n                    # 只计数不替换

**确认选项**（使用 c 标志时）：

- ``y`` 替换当前匹配
- ``n`` 跳过当前匹配
- ``a`` 替换所有剩余匹配
- ``q`` 退出替换
- ``l`` 替换当前匹配并退出

**实用示例**：

.. code-block:: bash

   # 将所有 foo 替换为 bar
   :%s/foo/bar/g

   # 将所有 foo 替换为 bar（逐个确认）
   :%s/foo/bar/gc

   # 删除行尾空格
   :%s/\s\+$//g

   # 将多个空格替换为一个
   :%s/  \+/ /g

   # 删除所有空行
   :g/^$/d

   # 将 Windows 换行符转为 Unix
   :%s/\r//g


正则表达式
----------

Vim 支持强大的正则表达式，但默认模式需要大量转义。使用 ``\v``（very magic）模式可以减少转义。

**模式比较**：

.. code-block:: bash

   # 默认模式（magic）- 需要转义很多字符
   /\(foo\|bar\)

   # very magic 模式 - 更像标准正则
   /\v(foo|bar)

**常用元字符**：

.. code-block:: bash

   # 字符类
   .                    # 任意字符
   \d                   # 数字 [0-9]
   \D                   # 非数字
   \w                   # 单词字符 [a-zA-Z0-9_]
   \W                   # 非单词字符
   \s                   # 空白字符
   \S                   # 非空白字符
   \a                   # 字母 [a-zA-Z]
   \l                   # 小写字母
   \u                   # 大写字母

   # 量词
   *                    # 0 次或多次
   \+                   # 1 次或多次（very magic 中用 +）
   \?                   # 0 次或 1 次（very magic 中用 ?）
   \{n,m}               # n 到 m 次（very magic 中用 {n,m}）

   # 位置
   ^                    # 行首
   $                    # 行尾
   \<                   # 单词开头
   \>                   # 单词结尾

   # 分组与引用
   \(pattern\)          # 捕获组（very magic 中用 (pattern)）
   \1 \2 \9             # 引用捕获组

   # Vim 特有
   \zs                  # 匹配开始（标记匹配起点）
   \ze                  # 匹配结束（标记匹配终点）

**实用正则示例**：

.. code-block:: bash

   # 匹配邮箱地址
   /\v\w+@\w+\.\w+

   # 匹配 IP 地址
   /\v\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}

   # 匹配 HTML 标签
   /\v<\w+>.*</\w+>

   # 匹配引号内的内容（非贪婪）
   /\v"[^"]*"

   # 使用 \zs 和 \ze 精确控制匹配范围
   # 匹配引号内的内容但不包含引号
   /\v"\zs[^"]*\ze"

   # 匹配函数名
   /\v\w+\ze\(

   # 使用捕获组交换两个单词
   :%s/\v(\w+) (\w+)/\2 \1/g

   # 匹配重复的单词
   /\v(\w+) \1


增量搜索
--------

.. code-block:: bash

   # 启用增量搜索
   set incsearch        # 输入时实时显示匹配

   # 增量搜索时的快捷键
   # 输入搜索模式时：
   Ctrl+e               # 停止搜索，恢复原内容
   Ctrl+y               # 停止搜索，接受当前匹配


多文件与窗口
============

Vim 可以同时编辑多个文件，通过缓冲区、窗口和标签页来组织。


缓冲区（Buffers）
-----------------

**是什么**：缓冲区是文件在内存中的表示。打开一个文件就创建一个缓冲区，但屏幕上不一定显示它。

**为什么需要它**：你可以同时打开多个文件，在它们之间快速切换，无需关闭再打开。

**比喻**：缓冲区就像桌上的多份文件——你一次只能看一份，但其他的都在手边。

.. code-block:: bash

   # 打开文件
   :e filename          # 打开文件（edit）
   :e .                 # 打开文件浏览器

   # 缓冲区操作
   :ls                  # 列出所有缓冲区
   :buffers             # 同上
   :bn                  # 下一个缓冲区（buffer next）
   :bp                  # 上一个缓冲区（buffer previous）
   :b{n}                # 切换到第 n 个缓冲区
   :b filename          # 切换到指定文件名的缓冲区
   :bf                  # 切换到第一个缓冲区
   :bl                  # 切换到最后一个缓冲区

   # 关闭缓冲区
   :bd                  # 关闭当前缓冲区（buffer delete）
   :bdelete filename    # 关闭指定缓冲区

**缓冲区状态标记**：

.. code-block:: bash

   # :ls 输出中的状态标记
   # %    当前缓冲区
   # #    上一个缓冲区
   # a    活动缓冲区（已加载）
   # h    隐藏缓冲区（已修改但未显示）
   # +    已修改的缓冲区

**实用技巧**：

.. code-block:: bash

   # 快速在最近两个缓冲区之间切换
   Ctrl+^               # 切换到上一个缓冲区

   # 使用模糊搜索切换缓冲区（需插件支持）
   :Buffer              # 使用 fzf.vim 的 :Buffers 命令


窗口（Windows）
---------------

**是什么**：窗口是缓冲区的视口。你可以把屏幕分割成多个窗口，同时查看不同的文件或同一文件的不同部分。

**为什么需要它**：对比代码、参考文档、查看函数定义等场景需要同时看到多个位置。

**比喻**：窗口就像房间里的多扇窗户——每扇窗看到不同的风景（缓冲区），但都在同一个房间（Vim 会话）里。

.. code-block:: bash

   # 窗口分割
   :sp                  # 水平分割（split）
   :vsp                 # 垂直分割（vertical split）
   :sp filename         # 水平分割并打开文件
   :vsp filename        # 垂直分割并打开文件
   Ctrl+w s             # 水平分割当前缓冲区
   Ctrl+w v             # 垂直分割当前缓冲区

   # 窗口导航
   Ctrl+w h             # 切换到左边窗口
   Ctrl+w j             # 切换到下方窗口
   Ctrl+w k             # 切换到上方窗口
   Ctrl+w l             # 切换到右边窗口
   Ctrl+w w             # 切换到下一个窗口
   Ctrl+w p             # 切换到上一个窗口

   # 窗口大小调整
   Ctrl+w =             # 均分所有窗口
   Ctrl+w _             # 最大化当前窗口高度
   Ctrl+w |             # 最大化当前窗口宽度
   Ctrl+w +             # 增加窗口高度
   Ctrl+w -             # 减少窗口高度
   Ctrl+w >             # 增加窗口宽度
   Ctrl+w <             # 减少窗口宽度

   # 窗口操作
   Ctrl+w c             # 关闭当前窗口（close）
   Ctrl+w o             # 关闭其他窗口（only）
   Ctrl+w q             # 退出当前窗口

   # 窗口移动
   Ctrl+w H             # 将当前窗口移到最左边
   Ctrl+w J             # 将当前窗口移到最下方
   Ctrl+w K             # 将当前窗口移到最上方
   Ctrl+w L             # 将当前窗口移到最右边

**实用技巧**：

.. code-block:: bash

   # 快速打开文件在新窗口
   :sf filename         # 水平分割打开文件
   :vert sf filename    # 垂直分割打开文件

   # 在新窗口中打开光标下的文件
   Ctrl+w f             # 水平分割打开文件
   Ctrl+w gf            # 垂直分割打开文件

   # 窗口布局
   Ctrl+w H             # 将窗口移到左边（适合宽屏）
   Ctrl+w K             # 将窗口移到上方


标签页（Tabs）
--------------

**是什么**：标签页是窗口的集合。每个标签页可以有自己的窗口布局。

**为什么需要它**：当你需要在不同的"工作空间"之间切换时——比如一个标签页写代码，一个标签页看文档。

**比喻**：标签页就像浏览器的标签——每个标签是一个独立的工作空间。

.. code-block:: bash

   # 标签页操作
   :tabnew filename     # 在新标签页打开文件
   :tabe filename       # 同上
   :tabclose            # 关闭当前标签页
   :tabonly             # 关闭其他标签页

   # 标签页导航
   gt                   # 下一个标签页
   gT                   # 上一个标签页
   {n}gt                # 切换到第 n 个标签页
   :tabn                # 下一个标签页
   :tabp                # 上一个标签页
   :tabfirst            # 切换到第一个标签页
   :tablast             # 切换到最后一个标签页

   # 标签页移动
   :tabm {n}            # 将当前标签页移到第 n 个位置
   :tabm 0              # 移到最前面
   :tabm                # 移到最后面

**实用技巧**：

.. code-block:: bash

   # 在所有标签页中搜索
   :tabdo %s/old/new/g  # 在所有标签页中执行替换

   # 将当前缓冲区移到新标签页
   Ctrl+w T             # 将当前窗口移到新标签页


文件浏览器
----------

.. code-block:: bash

   # 内置文件浏览器
   :Ex                  # 打开文件浏览器（Explore）
   :Sex                 # 水平分割打开文件浏览器
   :Vex                 # 垂直分割打开文件浏览器
   :Tex                 # 在新标签页打开文件浏览器

   # Netrw 文件浏览器快捷键（在 :Ex 中）
   -                    # 返回上级目录
   Enter                # 进入目录或打开文件
   d                    # 创建目录
   %                    # 创建新文件
   D                    # 删除文件
   R                    # 重命名文件
   i                    # 切换列表/网格视图


宏录制
======

**是什么**：宏录制让你记录一系列操作，然后回放。这是批量处理重复任务的利器。

**为什么需要它**：当你需要对多行执行相同的操作时，手动一行行操作太慢，宏可以一次录制，多次执行。

**比喻**：宏就像"录屏"——你录下一段操作，然后让它自动"重播"。


基础宏操作
----------

.. code-block:: bash

   q{a-z}               # 开始录制宏到寄存器 a-z
   # ... 执行操作 ...
   q                    # 停止录制

   @{a-z}               # 执行寄存器 a-z 中的宏
   @@                   # 重复执行上次的宏
   {n}@{a-z}            # 执行宏 n 次

**录制流程**：

1. 按 ``q{a-z}`` 开始录制
2. 状态栏会显示"recording @{register}"
3. 执行你的操作
4. 按 ``q`` 停止录制
5. 按 ``@{a-z}`` 执行宏
6. 按 ``@@`` 重复执行

**实用技巧**：

.. code-block:: bash

   # 查看宏内容
   :reg {a-z}           # 查看指定寄存器内容

   # 编辑宏（将宏内容粘贴出来编辑，再录回去）
   "ap                  # 粘贴宏内容
   # 编辑后
   "ay$                 # 复制回寄存器 a


宏录制最佳实践
--------------

**录制技巧**：

1. **确保从一致的位置开始**：录制前将光标移到行首（``0``）或某个固定位置
2. **确保以一致的位置结束**：录制结束时移到下一行（``j``）或下个位置
3. **使用相对移动**：尽量用 ``w``、``e`` 等相对移动，而不是 ``f{char}``（后者依赖字符位置）

.. code-block:: bash

   # 示例 1：批量注释代码行
   # 目标：在每行开头添加 "// "
   qa                   # 开始录制到寄存器 a
   I//                  # 在行首进入 Insert 并输入 "// "
   Esc                  # 返回 Normal
   j                    # 移到下一行
   q                    # 停止录制
   9@a                  # 对接下来 9 行执行宏

   # 示例 2：批量在行尾添加分号
   qa                   # 开始录制
   A;                   # 在行尾添加分号
   Esc                  # 返回 Normal
   j                    # 移到下一行
   q                    # 停止录制
   9@a                  # 对接下来 9 行执行宏

   # 示例 3：将 CSS 属性转为驼峰命名
   # 如：background-color -> backgroundColor
   qa                   # 开始录制
   f-                   # 跳到连字符
   x                    # 删除连字符
   ~                    # 切换下一个字符大小写
   q                    # 停止录制


宏的高级用法
------------

.. code-block:: bash

   # 在所有行上执行宏
   :%normal @a          # 对所有行执行宏 a

   # 在匹配行上执行宏
   :g/pattern/normal @a # 对匹配 pattern 的行执行宏 a

   # 递归宏（宏自己调用自己）
   qa                   # 开始录制
   # ... 操作 ...
   @a                   # 在宏内调用自己（递归）
   q                    # 停止录制
   @a                   # 执行（会一直执行直到出错）


可视块编辑
==========

**是什么**：可视块编辑是 Visual 模式的块选择（``Ctrl+v``）功能，让你选择矩形区域并批量编辑。

**为什么需要它**：代码中有很多对齐的结构（列数据、注释、前缀等），块选择可以同时修改多行的同一列位置。

**比喻**：可视块编辑就像用矩形框选 Excel 中的一片单元格——选中的区域是一个矩形。


基础块操作
----------

.. code-block:: bash

   Ctrl+v               # 进入块选择模式
   # 使用 h/j/k/l 或其他移动命令选择区域
   # 选择后执行操作：
   d                    # 删除块
   c                    # 修改块（删除并进入 Insert）
   y                    # 复制块
   r{char}              # 将块中每个字符替换为 char
   >                    # 右缩进
   <                    # 左缩进
   =                    # 自动缩进
   ~                    # 切换大小写
   U                    # 转大写
   u                    # 转小写

**I 和 A 操作**：

.. code-block:: bash

   # I 操作：在块前面插入
   Ctrl+v               # 进入块选择
   # 选择多行
   I                    # 进入 Insert 模式（在块左侧）
   //                   # 输入要插入的内容
   Esc                  # 应用到所有选中行

   # A 操作：在块后面追加
   Ctrl+v               # 进入块选择
   # 选择多行
   A                    # 进入 Insert 模式（在块右侧）
   ;                    # 输入要追加的内容
   Esc                  # 应用到所有选中行


实用场景
--------

.. code-block:: bash

   # 场景 1：批量添加注释
   # 选择代码行
   Ctrl+v               # 进入块选择
   5j                   # 选择 5 行
   I//                  # 在行首输入 //
   Esc                  # 应用

   # 场景 2：批量添加分号
   Ctrl+v
   5j                   # 选择 5 行
   A;                   # 在行尾添加分号
   Esc

   # 场景 3：批量修改前缀
   # 将 var_ 改为 let_
   Ctrl+v
   # 选择 var_ 区域
   c                    # 修改
   let_                 # 输入新内容
   Esc

   # 场景 4：对齐等号
   # 假设有多行赋值语句
   # foo = 1
   # barbaz = 2
   Ctrl+v
   # 选择等号列
   I                    # 在等号前插入空格
   Esc                  # 应用

   # 场景 5：在每行末尾添加内容
   Ctrl+v
   $                    # 选择到行尾（块选择会扩展到最长行）
   A                    # 在行尾追加
   ,                    # 输入逗号
   Esc


寄存器
======

**是什么**：寄存器是 Vim 中的剪贴板。Vim 不只有一个剪贴板，而是有多个命名寄存器，可以分别存储不同的内容。

**为什么需要它**：普通编辑器只有一个剪贴板，复制新内容会覆盖旧内容。Vim 的多寄存器让你同时保存多段文本。

**比喻**：寄存器就像有多个口袋——你可以把不同的东西放在不同的口袋里，需要时从特定口袋取出。


寄存器类型
----------

.. code-block:: bash

   # 无名寄存器（默认）
   "                    # 默认寄存器，dd、cc 等操作使用

   # 命名寄存器
   "a - "z              # 26 个命名寄存器

   # 只读寄存器
   "%                   # 当前文件名
   "#                   # 交替文件名
   ".                   # 上次插入的文本
   ":                   # 上次执行的命令
   "/                   # 上次搜索的模式

   # 复制专用寄存器
   "0                   # y（复制）操作使用的寄存器

   # 系统剪贴板
   "+                   # 系统剪贴板（需 +clipboard 支持）
   "*                   # 选择寄存器（X11 选择）

   # 表达式寄存器
   "=                   # 用于计算表达式

   # 黑洞寄存器
   "_                   # 删除到黑洞（不保存内容）


使用寄存器
----------

.. code-block:: bash

   # 复制到指定寄存器
   "ayy                 # 复制当前行到寄存器 a
   "ayw                 # 复制单词到寄存器 a
   "ay                  # 复制 Visual 选中内容到寄存器 a

   # 从指定寄存器粘贴
   "ap                  # 从寄存器 a 粘贴
   "aP                  # 从寄存器 a 粘贴到光标前

   # 删除到指定寄存器
   "add                 # 删除当前行到寄存器 a

   # 追加到寄存器
   "Ayy                 # 追加复制到寄存器 a（大写字母 = 追加）

   # 使用系统剪贴板
   "+yy                 # 复制到系统剪贴板
   "+p                  # 从系统剪贴板粘贴

   # 使用黑洞寄存器（删除不覆盖默认寄存器）
   "_dd                 # 删除到黑洞

   # 查看寄存器内容
   :reg                 # 查看所有寄存器
   :reg a b c           # 查看指定寄存器


寄存器实用技巧
--------------

.. code-block:: bash

   # 技巧 1：复制后不覆盖默认寄存器
   # 问题：dd 会覆盖默认寄存器，导致之前 yy 的内容丢失
   # 解决：使用命名寄存器
   "ayy                 # 复制到寄存器 a
   # ... dd 删除某行 ...
   "ap                  # 从寄存器 a 粘贴

   # 技巧 2：交换两行
   # 方法 1：使用 ddp
   # 方法 2：使用寄存器
   "ayy                 # 复制第一行
   ddp                  # 删除并粘贴到下方
   "aP                  # 粘贴第一行到上方

   # 技巧 3：在插入模式下使用寄存器
   Ctrl+r a             # 在 Insert 模式下插入寄存器 a 的内容
   Ctrl+r "             # 插入默认寄存器内容
   Ctrl+r +             # 插入系统剪贴板内容

   # 技巧 4：使用表达式寄存器计算
   "=2+3                # 计算表达式
   p                    # 粘贴结果 5

   # 技巧 5：录制宏到寄存器后编辑
   qa                   # 录制宏到 a
   # ... 操作 ...
   q
   "ap                  # 粘贴宏内容（可以编辑）
   # 编辑后重新录回
   "ay$                 # 复制回寄存器 a


配置文件 (.vimrc)
=================

**是什么**：``.vimrc`` 是 Vim 的配置文件，位于用户主目录下。它定义了 Vim 的行为、外观和快捷键。

**为什么需要它**：Vim 的默认配置比较保守，通过配置文件可以大幅提升使用体验。


基础配置
--------

.. code-block:: vim

   " ~/.vimrc - Vim 配置文件

   " ========================================
   " 基础设置
   " ========================================

   set nocompatible       " 关闭 Vi 兼容模式
   set encoding=utf-8     " 设置编码
   set fileencoding=utf-8 " 文件编码

   " 行号
   set number             " 显示行号
   set relativenumber     " 显示相对行号（方便跳转）

   " 缩进
   set tabstop=4          " Tab 显示宽度
   set shiftwidth=4       " 缩进宽度
   set expandtab          " Tab 转空格
   set autoindent         " 自动缩进
   set smartindent        " 智能缩进
   set softtabstop=4      " 退格键可以删除 4 个空格

   " 语法高亮
   syntax on              " 启用语法高亮
   filetype on            " 文件类型检测
   filetype plugin on     " 文件类型插件
   filetype indent on     " 文件类型缩进


搜索配置
--------

.. code-block:: vim

   " 搜索
   set hlsearch           " 搜索结果高亮
   set incsearch          " 增量搜索
   set ignorecase         " 忽略大小写
   set smartcase          " 智能大小写（有大写时区分）


界面配置
--------

.. code-block:: vim

   " 界面
   set laststatus=2       " 始终显示状态栏
   set ruler              " 显示光标位置
   set showcmd            " 显示输入的命令
   set showmode           " 显示当前模式
   set cursorline         " 高亮当前行
   set showmatch          " 括号匹配高亮
   set wildmenu           " 命令行补全菜单
   set wildmode=longest:full,complete " 补全模式
   set scrolloff=5        " 光标距屏幕顶/底保持 5 行
   set sidescrolloff=5    " 光标距屏幕左/右保持 5 列
   set wrap               " 自动换行
   set linebreak          " 按单词换行


实用配置
--------

.. code-block:: vim

   " 实用
   set backspace=indent,eol,start  " 退格键行为
   set mouse=a            " 启用鼠标
   set clipboard=unnamedplus " 共享系统剪贴板
   set hidden             " 允许切换未保存的缓冲区
   set autoread           " 文件变化时自动重新加载
   set autowrite          " 切换缓冲区时自动保存
   set confirm            " 退出未保存文件时确认
   set history=1000       " 命令历史数量
   set undolevels=1000    " 撤销次数
   set undofile           " 持久化撤销历史
   set backup=no          " 不创建备份文件
   set swapfile=no        " 不创建交换文件


键位映射
--------

.. code-block:: vim

   " Leader 键
   let mapleader = ","    " 设置 Leader 键为逗号（默认是 \）

   " 快捷键映射
   " 格式：{mode}{命令} {lhs} {rhs}
   " mode: n=Normal, v=Visual, i=Insert, c=Command

   " 快速保存
   nnoremap <leader>w :w<CR>
   nnoremap <leader>q :q<CR>

   " 取消搜索高亮
   nnoremap <leader>/ :noh<CR>

   " 快速移动
   nnoremap j gj         " 按显示行移动
   nnoremap k gk

   " 窗口导航
   nnoremap <C-h> <C-w>h
   nnoremap <C-j> <C-w>j
   nnoremap <C-k> <C-w>k
   nnoremap <C-l> <C-w>l

   " 快速切换缓冲区
   nnoremap <leader>bn :bn<CR>
   nnoremap <leader>bp :bp<CR>

   " 在 Insert 模式下用 jj 退出
   inoremap jj <Esc>


常用插件
========

Vim 的强大之处在于其丰富的插件生态系统。


插件管理器
----------

**vim-plug**（推荐）
^^^^^^^^^^^^^^^^^^^^

.. code-block:: vim

   " 安装 vim-plug
   " Unix
   curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
     https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

   " 在 .vimrc 中配置
   call plug#begin('~/.vim/plugged')

   " 插件列表
   Plug 'preservim/nerdtree'           " 文件树
   Plug 'vim-airline/vim-airline'       " 状态栏
   Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }  " 模糊搜索
   Plug 'junegunn/fzf.vim'             " fzf Vim 集成
   Plug 'neoclide/coc.nvim', {'branch': 'release'}  " 代码补全
   Plug 'tpope/vim-surround'           " 包围操作
   Plug 'tpope/vim-commentary'         " 注释操作
   Plug 'airblade/vim-gitgutter'       " Git 状态显示

   call plug#end()

   " vim-plug 命令
   " :PlugInstall    安装插件
   " :PlugUpdate     更新插件
   " :PlugClean      清理未使用的插件
   " :PlugStatus     查看插件状态
   " :PlugUpgrade    升级 vim-plug


常用插件详解
------------

**NERDTree**（文件树）
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: vim

   " 安装
   Plug 'preservim/nerdtree'

   " 常用命令
   :NERDTreeToggle     " 切换文件树显示
   :NERDTreeFind       " 在文件树中定位当前文件
   :NERDTreeFocus      " 聚焦到文件树窗口

   " 快捷键映射示例
   nnoremap <leader>n :NERDTreeToggle<CR>

   " NERDTree 内快捷键
   " o       打开/关闭目录或文件
   " t       在新标签页打开
   " i       水平分割打开
   " s       垂直分割打开
   " p       跳到上级目录
   " P       跳到根目录
   " r       刷新当前目录
   " m       显示文件操作菜单（添加、删除、重命名）
   " ?       显示帮助


**vim-airline**（状态栏）
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: vim

   " 安装
   Plug 'vim-airline/vim-airline'
   Plug 'vim-airline/vim-airline-themes'  " 主题

   " 配置
   let g:airline_theme='dark'             " 设置主题
   let g:airline#extensions#tabline#enabled = 1  " 显示标签页
   let g:airline_powerline_fonts = 1      " 使用 Powerline 字体


**coc.nvim**（代码补全）
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: vim

   " 安装（需要 Node.js）
   Plug 'neoclide/coc.nvim', {'branch': 'release'}

   " 常用命令
   :CocInstall coc-json       " 安装 JSON 语言支持
   :CocInstall coc-tsserver   " 安装 TypeScript 语言支持
   :CocInstall coc-python     " 安装 Python 语言支持

   " 快捷键配置
   " Tab 键触发补全
   inoremap <silent><expr> <TAB>
     \ pumvisible() ? "\<C-n>" :
     \ <SID>check_back_space() ? "\<TAB>" :
     \ coc#refresh()
   inoremap <expr><S-TAB> pumvisible() ? "\<C-p>" : "\<C-h>"

   " 跳转定义
   nmap <silent> gd <Plug>(coc-definition)
   nmap <silent> gy <Plug>(coc-type-definition)
   nmap <silent> gi <Plug>(coc-implementation)
   nmap <silent> gr <Plug>(coc-references)

   " 显示文档
   nnoremap <silent> K :call <SID>show_documentation()<CR>

   " 重命名
   nmap <leader>rn <Plug>(coc-rename)


**fzf.vim**（模糊搜索）
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: vim

   " 安装
   Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
   Plug 'junegunn/fzf.vim'

   " 常用命令
   :Files              " 搜索文件
   :Buffers            " 搜索缓冲区
   :Lines              " 搜索当前文件的行
   :BLines             " 搜索当前缓冲区的行
   :Tags               " 搜索标签
   :BTags              " 搜索当前缓冲区的标签
   :Rg                 " 使用 ripgrep 搜索内容
   :History            " 搜索文件历史
   :Commands           " 搜索命令

   " 快捷键映射
   nnoremap <leader>f :Files<CR>
   nnoremap <leader>b :Buffers<CR>
   nnoremap <leader>g :Rg<CR>


**vim-surround**（包围操作）
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: vim

   " 安装
   Plug 'tpope/vim-surround'

   " 操作
   cs"'               " 将双引号改为单引号 (change surround)
   ds"                " 删除双引号 (delete surround)
   ysiw"              " 给单词添加双引号 (you surround inner word)
   yss"               " 给整行添加双引号
   cst<html>          " 将包围改为 HTML 标签

   " Visual 模式
   S"                 " 给选中文本添加双引号
   S<p>               " 给选中文本添加 <p> 标签


**vim-commentary**（注释操作）
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: vim

   " 安装
   Plug 'tpope/vim-commentary'

   " 操作
   gcc                " 切换当前行注释
   gc{motion}         " 切换注释（如 gcip 注释段落）
   gcgc               " 取消相邻注释
   :5,10Commentary    " 注释 5-10 行


实用技巧集合
============

快速操作
--------

.. code-block:: bash

   # 取消搜索高亮
   :noh

   # 粘贴模式（避免自动缩进干扰）
   :set paste           # 进入粘贴模式
   # 粘贴内容
   :set nopaste         # 退出粘贴模式

   # 数字增减
   Ctrl+a               # 将光标下的数字加 1
   Ctrl+x               # 将光标下的数字减 1
   5Ctrl+a              # 加 5

   # 跳转
   gd                   # 跳到局部定义（go to definition）
   gD                   # 跳到全局定义
   gf                   # 打开光标下的文件名
   Ctrl+]               # 跳到标签定义
   Ctrl+t               # 跳回标签栈

   # 自动补全
   Ctrl+n               # 下一个补全选项
   Ctrl+p               # 上一个补全选项
   Ctrl+x Ctrl+f        # 文件名补全
   Ctrl+x Ctrl+l        # 整行补全
   Ctrl+x Ctrl+o        # Omni 补全（代码补全）

   # 查看信息
   :marks               # 查看所有标记
   :changes             # 查看修改历史
   :jumps               # 查看跳转历史
   :reg                 # 查看寄存器内容
   :set all             # 查看所有选项
   :version             # 查看 Vim 版本和编译信息


文本对象
--------

.. code-block:: bash

   # 文本对象格式：{a/i}{object}
   # a = 包含对象（around）
   # i = 对象内部（inner）

   # 单词
   aw                   # 一个单词（含空格）
   iw                   # 单词内部（不含空格）

   # 句子
   as                   # 一个句子
   is                   # 句子内部

   # 段落
   ap                   # 一个段落
   ip                   # 段落内部

   # 引号
   a"                   # 包含双引号
   i"                   # 双引号内部
   a'                   # 包含单引号
   i'                   # 单引号内部
   a`                   # 包含反引号
   i`                   # 反引号内部

   # 括号
   a(                   # 包含圆括号
   i(                   # 圆括号内部
   a[                   # 包含方括号
   i[                   # 方括号内部
   a{                   # 包含花括号
   i{                   # 花括号内部
   a<                   # 包含尖括号
   i<                   # 尖括号内部

   # 标签（HTML/XML）
   at                   # 包含标签
   it                   # 标签内部

   # 使用示例
   ciw                  # 修改单词
   di"                  # 删除引号内容
   ya(                  # 复制包含括号的内容
   dip                  # 删除段落
   gUi"                 # 将引号内内容转为大写


命令行技巧
----------

.. code-block:: bash

   # 执行外部命令
   :!ls                 # 执行 ls 命令
   :!python %           # 执行当前 Python 文件
   :!gcc % -o %:r && ./%:r  # 编译并运行 C 文件

   # 将命令输出插入文件
   :r !date             # 插入当前日期
   :r !ls               # 插入 ls 输出

   # 范围操作
   :1,10d               # 删除 1-10 行
   :1,10y               # 复制 1-10 行
   :1,10m20             # 移动 1-10 行到第 20 行后
   :1,10t20             # 复制 1-10 行到第 20 行后

   # 全局命令
   :g/pattern/d         # 删除匹配 pattern 的行
   :g/pattern/y         # 复制匹配 pattern 的行
   :g!/pattern/d        # 删除不匹配 pattern 的行
   :g/pattern/normal @a # 对匹配行执行宏 a


折叠
----

.. code-block:: bash

   # 折叠操作
   zf{motion}           # 创建折叠
   zf                   # Visual 模式下创建折叠
   zo                   # 打开折叠（open）
   zc                   # 关闭折叠（close）
   za                   # 切换折叠（toggle）
   zR                   # 打开所有折叠
   zM                   # 关闭所有折叠
   zj                   # 移动到下一个折叠
   zk                   # 移动到上一个折叠

   # 折叠方法
   set foldmethod=manual    # 手动折叠
   set foldmethod=indent    # 按缩进折叠
   set foldmethod=syntax    # 按语法折叠
   set foldmethod=marker    # 按标记折叠
   set foldlevel=99         # 默认打开所有折叠


会话管理
--------

.. code-block:: bash

   # 保存会话
   :mksession ~/session.vim    # 保存当前会话

   # 恢复会话
   vim -S ~/session.vim        # 启动时加载会话
   :source ~/session.vim       # 运行时加载会话

   # 视图（单个窗口的设置）
   :mkview             # 保存当前视图
   :loadview           # 加载视图


快速跳转列表
------------

.. code-block:: bash

   # 跳转列表
   Ctrl+o               # 跳到上一个位置（older）
   Ctrl+i               # 跳到下一个位置（newer）
   :jumps               # 显示跳转列表

   # 修改列表
   g;                   # 跳到上一个修改位置
   g,                   # 跳到下一个修改位置
   :changes             # 显示修改列表

   # 标签栈
   Ctrl+]               # 跳到标签定义
   Ctrl+t               # 跳回标签栈


常见任务示例
============

代码格式化
----------

.. code-block:: bash

   # 自动缩进整个文件
   gg=G

   # 格式化选中的代码块
   =i{                  # 格式化花括号内的内容
   =ip                  # 格式化段落

   # 对齐赋值语句（使用 Tabular 插件）
   :Tabularize /=       # 按等号对齐


批量操作
--------

.. code-block:: bash

   # 批量添加注释
   Ctrl+v               # 块选择
   # 选择行
   I//                  # 在行首输入 //
   Esc                  # 应用

   # 批量删除注释
   Ctrl+v               # 块选择
   # 选择 // 区域
   d                    # 删除

   # 批量添加分号
   :%s/$/;/g            # 在每行末尾添加分号

   # 批量删除空行
   :g/^$/d

   # 批量删除行尾空格
   :%s/\s\+$//g

   # 批量转换大小写
   :%s/.*/\U&/          # 全部转大写
   :%s/.*/\L&/          # 全部转小写


代码导航
--------

.. code-block:: bash

   # 跳转定义
   gd                   # 跳到局部定义
   gD                   # 跳到全局定义
   Ctrl+]               # 跳到标签定义

   # 搜索符号
   :tag function_name   # 跳到标签
   :tselect pattern     # 搜索标签

   # 使用 ctags
   ctags -R .           # 生成标签文件
   :set tags=./tags     # 设置标签文件路径

   # 使用 cscope
   cscope -Rb           # 生成 cscope 数据库
   :cs add cscope.out   # 添加数据库


调试技巧
--------

.. code-block:: bash

   # 查看当前模式
   # 在状态栏显示 -- INSERT --, -- VISUAL -- 等

   # 查看按键映射
   :map                 # 查看所有映射
   :nmap                # 查看 Normal 模式映射
   :imap                # 查看 Insert 模式映射
   :verbose map {key}   # 查看按键的映射来源

   # 查看选项值
   :set {option}?       # 查看选项当前值
   :verbose set {option}?  # 查看选项设置来源

   # 查看运行时路径
   :set runtimepath?    # 查看运行时路径

   # 重置配置
   :source $VIMRUNTIME/vimrc_example.vim  # 加载示例配置


常见问题解答
============

**Q: 如何退出 Vim？**

.. code-block:: bash

   :q                   # 正常退出
   :q!                  # 强制退出不保存
   :wq                  # 保存并退出
   ZZ                   # 保存并退出（Normal 模式）
   ZQ                   # 不保存退出（Normal 模式）

**Q: 如何撤销多步操作？**

.. code-block:: bash

   u                    # 撤销一步
   5u                   # 撤销 5 步
   U                    # 撤销对整行的所有修改

**Q: 如何复制到系统剪贴板？**

.. code-block:: bash

   "+yy                 # 复制到系统剪贴板
   "+p                  # 从系统剪贴板粘贴
   # 或者在 .vimrc 中设置
   set clipboard=unnamedplus

**Q: 如何快速跳转到指定行？**

.. code-block:: bash

   42G                  # 跳到第 42 行
   :42                  # 同上
   gg                   # 跳到第一行
   G                    # 跳到最后一行

**Q: 如何同时编辑多个文件？**

.. code-block:: bash

   vim file1 file2      # 打开多个文件
   :bn                  # 下一个文件
   :bp                  # 上一个文件
   :sp file3            # 水平分割打开新文件
   :vsp file4           # 垂直分割打开新文件

**Q: 如何录制和回放宏？**

.. code-block:: bash

   qa                   # 开始录制到寄存器 a
   # ... 执行操作 ...
   q                    # 停止录制
   @a                   # 执行宏
   @@                   # 重复上次宏
   10@a                 # 执行 10 次

**Q: 如何在 Vim 中执行 Shell 命令？**

.. code-block:: bash

   :!command            # 执行命令
   :shell               # 进入 Shell（exit 返回 Vim）
   :r !command          # 将命令输出插入文件

**Q: 如何比较两个文件？**

.. code-block:: bash

   vim -d file1 file2   # 比较模式
   vimdiff file1 file2  # 同上
   ]c                   # 跳到下一个差异
   [c                   # 跳到上一个差异
   do                   # 获取差异（diff obtain）
   dp                   # 放置差异（diff put）
   :diffupdate          # 更新差异高亮


学习路径建议
============

初级阶段（1-2 周）
------------------

1. 掌握模式切换（Normal/Insert/Visual/Command）
2. 熟练使用 hjkl 移动
3. 学会基本编辑（dd/yy/p/u）
4. 学会保存退出（:wq/:q!）
5. 学会搜索（/pattern）

中级阶段（2-4 周）
------------------

1. 掌握单词移动（w/b/e）
2. 掌握行内跳转（0/$/^/f/t）
3. 学会组合操作（dw/ciw/ci"）
4. 学会宏录制
5. 学会块选择编辑
6. 配置 .vimrc

高级阶段（1-3 月）
------------------

1. 精通正则表达式搜索替换
2. 掌握寄存器系统
3. 学会使用插件管理器
4. 配置 coc.nvim 等 IDE 插件
5. 自定义快捷键和工作流

大师阶段（持续学习）
--------------------

1. 编写 VimScript 函数和插件
2. 深入理解 Vim 的内部机制
3. 优化配置以适应不同语言和项目
4. 分享和贡献 Vim 社区


参考资源
========

- `Vim 官方文档 <https://www.vim.org/docs.php>`_
- `Vim Tips Wiki <https://vim.fandom.com/wiki/Vim_Tips_Wiki>`_
- `Learn Vimscript the Hard Way <https://learnvimscriptthehardway.stevelosh.com/>`_
- `Vim Galore <https://github.com/mhinz/vim-galore>`_
- `Practical Vim (Drew Neil) <https://pragprog.com/titles/dnvim2/practical-vim-second-edition/>`_

.. code-block:: bash

   # 内置帮助
   :help                 # 查看帮助
   :help {topic}         # 查看特定主题帮助
   :helpgrep {pattern}   # 搜索帮助文档
   :helptags ~/.vim/doc  # 生成帮助标签
