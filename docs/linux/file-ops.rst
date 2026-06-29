文件操作
========

查找文件
--------

.. code-block:: bash

   # 按名称查找
   find /path -name "*.c"

   # 按类型查找
   find /path -type f -name "*.h"

   # 按大小查找
   find /path -size +1M

搜索内容
--------

.. code-block:: bash

   # 递归搜索
   grep -rn "pattern" /path

   # 忽略大小写
   grep -rni "pattern" /path

   # 只显示文件名
   grep -rl "pattern" /path

文件管理
--------

.. code-block:: bash

   # 查看文件大小
   ls -lh
   du -sh *

   # 批量重命名
   rename 's/\.txt$/\.md/' *.txt

   # 同步文件
   rsync -avz src/ user@host:/dest/
