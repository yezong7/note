.. Personal Notes documentation master file

欢迎来到 Personal Notes 文档
================================

这是一个基于 **Read the Docs** 自动构建的个人笔记文档。

每次推送到 GitHub 仓库，文档会自动更新。

.. toctree::
   :maxdepth: 2
   :caption: 目录

   profile/index
   english/index
   algorithm/index
   language/index
   linux/index

快速开始
--------

1. 克隆仓库：

   .. code-block:: bash

      git clone https://github.com/yezong7/note.git

2. 本地构建文档：

   .. code-block:: bash

      cd note
      pip install -r requirements.txt
      cd docs && make html

3. 打开 ``docs/_build/html/index.html`` 查看文档。
