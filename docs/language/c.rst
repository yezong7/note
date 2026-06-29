C 语言
======

C 语言学习笔记。

基础语法
--------

- 数据类型与变量
- 指针与数组
- 结构体与联合体
- 函数指针

内存管理
--------

- 栈与堆
- malloc / free
- 内存对齐

常用技巧
--------

.. code-block:: c

   // 函数指针回调
   typedef void (*callback_t)(int);

   void register_cb(callback_t cb) {
       cb(42);
   }

.. note::

   持续更新中...
