快速入门
========

环境要求
--------

- Python 3.8+
- Git

安装依赖
--------

.. code-block:: bash

   pip install -r requirements.txt

本地构建
--------

.. code-block:: bash

   cd docs
   make html

构建完成后，打开 ``_build/html/index.html`` 即可预览。

自动部署
--------

本项目已配置 Read the Docs 自动构建：

1. 每次推送到 ``main`` 分支
2. Read the Docs 自动触发构建
3. 文档实时更新到 https://note.readthedocs.io
