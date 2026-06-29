C++ 语言
========

C++ 学习笔记。

面向对象
--------

- 封装、继承、多态
- 构造函数与析构函数
- 虚函数与纯虚函数

设计模式
--------

- **单例模式** (Meyers' Singleton)
- **观察者模式**
- **工厂模式**

现代 C++
--------

- 智能指针 (``unique_ptr``, ``shared_ptr``)
- 移动语义与右值引用
- Lambda 表达式
- ``constexpr`` 与编译期计算

.. code-block:: cpp

   // Meyers' Singleton
   class PlayerManager {
   public:
       static PlayerManager& Instance() {
           static PlayerManager inst;
           return inst;
       }
       PlayerManager(const PlayerManager&) = delete;
       PlayerManager& operator=(const PlayerManager&) = delete;
   private:
       PlayerManager() = default;
   };

.. note::

   持续更新中...
