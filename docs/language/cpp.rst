C++ 语言参考手册
================

这是一份全面的 C++ 语言参考手册，涵盖从基础初始化到现代高级特性的核心知识。
每个知识点都配有原理解释、代码示例和实际应用场景。

.. contents:: 目录
   :depth: 3
   :local:

初始化
------

初始化是 C++ 中最容易出错、也最值得深入理解的领域之一。
类比来说：**构造**是"造一个盒子"，**初始化**是"往盒子里放东西"。
C++ 对这两件事的处理方式比大多数语言都更精细。

默认初始化 vs 值初始化 vs 列表初始化
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**默认初始化 (Default Initialization)**

当声明一个变量而不提供任何初始值时，发生默认初始化。
对于内置类型（int, float, 指针等），默认初始化**不会**给变量赋值，其值是未定义的（垃圾值）。
对于类类型，编译器会调用默认构造函数。

.. code-block:: cpp

   int x;              // 默认初始化：x 的值未定义（垃圾值）
   std::string s;      // 默认初始化：调用 string 的默认构造函数，s 为空字符串

   class Foo {
   public:
       Foo() { std::cout << "Foo constructed\n"; }  // 默认构造函数
   };
   Foo f;  // 默认初始化：调用 Foo()

**值初始化 (Value Initialization)**

使用空括号 ``()`` 或空花括号 ``{}`` 进行初始化。
对于内置类型，值初始化会将变量**零初始化**（int 变为 0，指针变为 nullptr）。
对于类类型，值初始化会调用默认构造函数。

.. code-block:: cpp

   int x{};       // 值初始化：x = 0
   int y = int(); // 值初始化：y = 0
   std::string s{}; // 值初始化：调用默认构造函数

**比喻**：默认初始化是"造了盒子但没放东西（里面是随机垃圾）"，
值初始化是"造了盒子并放进零值（盒子干净但内容为零）"。

列表初始化 (C++11)
^^^^^^^^^^^^^^^^^^

C++11 引入了统一的列表初始化语法，使用花括号 ``{}`` 进行初始化。
这是**推荐的现代写法**，因为它有一个杀手级特性：**防止窄化转换**。

.. code-block:: cpp

   int a{1};         // 直接列表初始化
   int b = {2};      // 拷贝列表初始化（效果相同）
   std::string s{"hello"}; // 列表初始化

   // 防止窄化——以下代码会编译失败！
   int x = {3.14};   // 错误：double 转 int 是窄化，编译器拒绝
   char c = {1000};  // 错误：1000 超出 char 范围，编译器拒绝

**为什么需要列表初始化？** 传统写法 ``int x = 3.14;`` 会悄悄丢掉小数部分，
程序运行时产生难以察觉的 bug。列表初始化将这类隐患在**编译期**就掐灭。

**易错点**：``int x(1)`` 和 ``int x{1}`` 在简单场景下效果相同，
但涉及类型转换时，花括号版本更安全。建议统一使用花括号初始化。

初始化列表 (Member Initializer List)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

初始化列表发生在构造函数的大括号 ``{}`` **之前**，
是告诉编译器："用括号里的参数，唤醒对应类型成员变量的构造函数"。

.. code-block:: cpp

   class Holder {
       int& _ref;       // 引用成员——必须在初始化列表中绑定
       const int _id;   // const 成员——必须在初始化列表中初始化
       std::string _name;
   public:
       // 初始化列表：在进入 {} 之前完成所有成员的初始化
       Holder(int& r, int id, std::string name)
           : _ref(r)       // 绑定引用（赋值做不到这件事）
           , _id(id)       // 初始化 const 成员
           , _name(name)   // 初始化 string 成员
       {
           // 此处 {} 内部是"赋值"，不是"初始化"
           // 对于引用和 const，到这里再赋值就太晚了
       }
   };

**铁律**：以下成员**必须**使用初始化列表：

- **引用类型成员**：引用天生必须在诞生时绑定，无法事后赋值
- **``const`` 成员**：const 变量一旦初始化就不能修改，不能先默认构造再赋值
- **没有默认构造函数的类成员**：编译器无法自动创建，必须显式提供参数

**比喻**：初始化列表就像"出生证明"——在对象诞生的那一刻就确定身份。
构造函数体内的赋值更像是"改名手续"——对象已经存在了，只是修改它的状态。

两段式初始化 (Two-Phase Initialization)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

在大型项目中，构造和初始化需要拆分。原因很简单：**构造对象是安全、快速、不能失败的，
而初始化涉及申请资源（声卡、网络连接等），可能失败**。

.. code-block:: cpp

   class PlayerManager {
       bool initialized_ = false;

   public:
       // 第一段：获取单例（安全、快速、永不失败）
       static PlayerManager& Instance() {
           static PlayerManager inst;
           return inst;
       }

       // 第二段：初始化资源（可能失败，用 bool 返回值保护）
       bool Init(const Config& cfg) {
           if (initialized_) return true;  // 防止重复初始化
           // 申请声卡、加载配置等可能失败的操作
           if (!AcquireAudioDevice(cfg)) {
               return false;  // 初始化失败，但对象本身完好
           }
           initialized_ = true;
           return true;
       }

       bool IsInitialized() const { return initialized_; }
   };

**为什么分两段？** 如果把资源申请放在构造函数里，一旦失败，
你面对的是一个"半死不活"的对象——构造函数无法返回错误码，
只能抛异常，而异常在嵌入式或性能敏感场景中代价高昂。
两段式初始化让失败可控、可检查。

面向对象
--------

C++ 的面向对象是其最核心的编程范式之一。用一句话概括：
**封装**是"把数据和操作打包"，**继承**是"子承父业"，**多态**是"同一个指令，不同的执行结果"。

访问控制：public 与 private
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   class PlayerManager {
   public:
       // 对外接口——外部业务代码只能调用这些方法
       void Play(const std::string& url);
       void Stop();

   private:
       // 核心资产——外部绝对无法访问
       AudioBackend* backend_;
       std::vector<Track> playlist_;
       PlayerManager() = default;  // 私有构造，禁止外部创建
   };

- **``public``（对外接口）**：暴露给外部系统的"服务窗口"。外部只能通过这里操作。
- **``private``（核心资产）**：存放类的核心数据，防止别人乱改。外部绝对无法访问。

**比喻**：``public`` 是餐厅的菜单，``private`` 是厨房的秘方。顾客只能点菜，
永远看不到秘方。

friend class：打破 private 的唯一手段
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``friend class`` 是打破 ``private`` 防御的**唯一**手段。
它是单向的特权认证："我宣布你是我的好朋友，你能看我的 private 资产。"

.. code-block:: cpp

   class MediaPlayer {
       friend class PlayerManager;  // PlayerManager 可以访问 MediaPlayer 的 private
   private:
       AudioBackend* backend_;
   };

   class PlayerManager {
   public:
       void DebugPrint() {
           MediaPlayer mp;
           // 可以访问 mp.backend_，因为我们是 friend
           std::cout << mp.backend_ << std::endl;
       }
   };

**实战运用**：让"大管家"（PlayerManager）和"小弟"（MediaPlayer）之间
可以互看隐私完成紧密协作，但对外部业务代码坚决屏蔽。

构造函数与析构函数
^^^^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   class Widget {
   public:
       Widget()  { std::cout << "构造：对象诞生\n"; }   // 构造函数
       ~Widget() { std::cout << "析构：对象消亡\n"; }   // 析构函数
   };

   void demo() {
       Widget w;        // 打印 "构造：对象诞生"
   }  // 离开作用域，自动打印 "析构：对象消亡"

构造函数与类同名，**绝对不能写返回值类型**。
析构函数在类名前加 ``~``。两者都由编译器在对象诞生/消亡时**自动调用**。

**比喻**：构造函数是"出生时的接生医生"，析构函数是"去世时的收尾律师"——
你不需要手动呼叫它们，编译器会在正确的时间自动安排。

explicit 关键字
^^^^^^^^^^^^^^^^

单参数构造函数会被 C++ 编译器"自作聪明"地当成类型转换通道。
``explicit`` 的作用是：**禁止隐式类型转换，必须显式调用**。

.. code-block:: cpp

   class MyString {
   public:
       // 没有 explicit 时，编译器允许：MyString s = "hello"; （隐式转换）
       explicit MyString(const char* str) : data_(str) {}
   private:
       std::string data_;
   };

   void process(MyString s) {}

   int main() {
       // MyString s = "hello";   // 错误！explicit 禁止了隐式转换
       MyString s("hello");       // 正确：显式调用
       process(MyString("hello")); // 正确：显式构造
       // process("hello");       // 错误！不能隐式从 const char* 转换为 MyString
   }

**为什么需要 explicit？** 没有它时，编译器可能在你不知情的地方悄悄创建临时对象，
导致难以追踪的性能问题或语义错误。``explicit`` 是一种防御性编程习惯。

虚函数与纯虚函数
^^^^^^^^^^^^^^^^

虚函数是 C++ **运行时多态**的基石。通过 ``virtual`` 关键字，
基类指针调用函数时，实际执行的是派生类的版本。

.. code-block:: cpp

   class Shape {
   public:
       virtual double area() const = 0;  // 纯虚函数：子类必须实现
       virtual ~Shape() = default;        // 虚析构函数：确保正确释放子类资源
   };

   class Circle : public Shape {
       double radius_;
   public:
       Circle(double r) : radius_(r) {}
       double area() const override { return 3.14159 * radius_ * radius_; }
   };

   class Rect : public Shape {
       double w_, h_;
   public:
       Rect(double w, double h) : w_(w), h_(h) {}
       double area() const override { return w_ * h_; }
   };

   int main() {
       Shape* shapes[] = { new Circle(5), new Rect(3, 4) };
       for (auto* s : shapes) {
           std::cout << s->area() << "\n";  // 多态：同一个调用，不同执行
       }
       for (auto* s : shapes) delete s;
   }

**vtable 机制**：每个含虚函数的类都有一个隐藏的虚函数表（vtable），
存储所有虚函数的地址。对象内部有一个隐藏指针（vptr）指向这个表。
调用虚函数时，编译器通过 vptr 找到 vtable，再找到正确的函数地址——
这就是运行时多态的实现原理。

**比喻**：vtable 就像一张"电话簿"，每个子类都有自己的版本。
当你说"打电话给 Shape"时，程序会查当前对象的电话簿，
找到真正对应的"Circle 版"或"Rect 版"的号码。

继承
^^^^

.. code-block:: cpp

   // 单继承：一个基类
   class Animal {
   public:
       virtual void speak() = 0;
   };
   class Dog : public Animal {
   public:
       void speak() override { std::cout << "Woof!\n"; }
   };

   // 多继承：多个基类
   class Flyable {
   public:
       virtual void fly() = 0;
   };
   class Swimmable {
   public:
       virtual void swim() = 0;
   };
   class Duck : public Flyable, public Swimmable {
   public:
       void fly() override { std::cout << "Flying!\n"; }
       void swim() override { std::cout << "Swimming!\n"; }
   };

**虚继承**用于解决多继承中的"菱形继承"问题——当两个基类共享同一个祖先时，
虚继承确保祖先的数据只存在一份拷贝，避免二义性。

.. code-block:: cpp

   class Base { public: int x; };
   class A : virtual public Base {};  // 虚继承
   class B : virtual public Base {};  // 虚继承
   class C : public A, public B {
       // 只有 一份 Base::x，没有二义性
   };

多态：运行时多态 vs 编译时多态
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+------------------+------------------------------------+------------------------------------+
|                  | 运行时多态                           | 编译时多态                          |
+==================+====================================+====================================+
| 机制             | ``virtual`` 函数 + vtable           | 模板 (template)                    |
+------------------+------------------------------------+------------------------------------+
| 绑定时机         | 运行时（动态绑定）                    | 编译时（静态绑定）                   |
+------------------+------------------------------------+------------------------------------+
| 性能             | 有虚函数调用开销（查 vtable）          | 零开销（编译器生成特化代码）           |
+------------------+------------------------------------+------------------------------------+
| 灵活性           | 可以在运行时切换行为                   | 类型在编译时确定                     |
+------------------+------------------------------------+------------------------------------+
| 典型应用         | 接口抽象、插件系统                    | STL 容器、数学库、序列化              |
+------------------+------------------------------------+------------------------------------+

.. code-block:: cpp

   // 运行时多态：通过基类指针调用
   void print_area(Shape* s) { std::cout << s->area() << "\n"; }

   // 编译时多态：模板为每种类型生成专属代码
   template<typename T>
   T max_val(T a, T b) { return (a > b) ? a : b; }

单例模式 (Meyers' Singleton)
-----------------------------

单例模式保证**全程序只有一个实例**。类比来说，单例就是"大管家"——
整个系统只有一个，所有人都通过同一个入口找它办事。

Meyers' Singleton 是 C++ 中最优雅、最安全的单例实现。
以下代码来自实际项目，逐行解析其防御设计。

完整实现
^^^^^^^^

.. code-block:: cpp

   class PlayerManager {
   public:
       // 第一段：获取单例（安全、快速、永不失败）
       static PlayerManager& Instance() {
           static PlayerManager inst;  // 延迟加载 + 线程安全
           return inst;
       }

       // 彻底封杀克隆：禁止拷贝构造和赋值
       PlayerManager(const PlayerManager&) = delete;
       PlayerManager& operator=(const PlayerManager&) = delete;

   private:
       PlayerManager() = default;  // 私有构造：禁止外部创建
   };

逐行解析
^^^^^^^^

**``static PlayerManager inst;``**

这是整个单例的核心。``static`` 局部变量有三个关键特性：

1. **生命周期**：伴随整个程序寿命（从第一次初始化到程序结束）
2. **作用域**：仅限 ``Instance()`` 函数内部，外部无法直接访问
3. **线程安全**：自 C++11 起，编译器保证 ``static`` 局部变量的初始化是线程安全的

**延迟加载**：``inst`` 只在第一次调用 ``Instance()`` 时才被构造。
如果程序从未调用 ``Instance()``，这个对象就不会被创建，节省了资源。

**``private: PlayerManager() = default;``**

私有构造函数彻底剥夺了外部使用 ``new PlayerManager`` 或定义局部变量来
创建对象的权利。只有 ``Instance()`` 内部的代码能调用这个构造函数。

**``= delete``**

删除编译器默认生成的**拷贝构造函数**和**赋值操作符**。
这阻止了外部写出 ``PlayerManager pm = Instance();`` 这种克隆代码——
如果允许这种行为，就会出现多个"大管家"，单例就被破坏了。

**比喻**：单例模式就像一个国家只有一个总统。
私有构造 = "只有选举程序才能产生总统"，
= delete = "不能通过克隆来制造第二个总统"，
Instance() = "所有人都通过同一个办公室找总统"。

使用方式
^^^^^^^^

.. code-block:: cpp

   // 获取单例并使用
   PlayerManager& pm = PlayerManager::Instance();
   pm.Play("music.mp3");

   // 以下代码全部编译失败——单例防御无死角
   // PlayerManager pm2;                          // 错误：构造函数是 private
   // PlayerManager pm3 = PlayerManager::Instance(); // 错误：拷贝构造被 delete
   // PlayerManager pm4;
   // pm4 = PlayerManager::Instance();               // 错误：赋值操作符被 delete

引用
----

引用是 C++ 最伟大的发明之一——它是一个变量的**别名**，
与原变量共享同一块内存，但语法上更安全、更优雅。

类型旁 ``&`` vs 变量旁 ``&``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``&`` 符号在 C++ 中有两种完全不同的含义，
编译器通过**上下文语法树**瞬间区分：

.. code-block:: cpp

   int x = 42;
   int& ref = x;    // 类型旁的 &：声明引用（别名）
   int* ptr = &x;   // 变量旁的 &：取地址运算

**比喻**：``int& ref = x`` 是"给 x 起了个外号叫 ref"，
``&x`` 是"问 x 住在哪里（获取地址）"。
同一个 ``&`` 符号，就像同一个汉字在不同语境下有不同含义。

引用的三大铁律
^^^^^^^^^^^^^^

**铁律一：不存在空引用**

.. code-block:: cpp

   int& ref = ???;  // 必须绑定到一个已存在的对象，不能是 nullptr
   int* ptr = nullptr; // 指针可以为空——这是指针最常见的 bug 来源

引用天生就必须绑定到一个有效对象，因此比指针**绝对安全**。
你不需要检查 ``if (ref != nullptr)`` 这种代码，因为引用永远不为空。

**铁律二：出生必须绑定**

.. code-block:: cpp

   class Holder {
       int& _ref;
   public:
       // 必须在初始化列表中绑定引用——赋值做不到这件事
       Holder(int& r) : _ref(r) {}
   };

引用在诞生的那一刻就必须绑定到目标，不能先声明后绑定。
这就像一个人出生时就必须有姓氏——你不能先出生、后起名。

**铁律三：一旦绑定，不可更改**

.. code-block:: cpp

   int a = 1, b = 2;
   int& ref = a;  // ref 绑定到 a
   ref = b;       // 这不是"改绑到 b"！这是"把 b 的值赋给 a"
   // 此时 a == 2, ref == 2，但 ref 仍然指向 a

一旦引用绑定到某个变量，它就永远是那个变量的别名。
对引用赋值只是修改目标变量的值，不会改变绑定关系。

函数返回引用
^^^^^^^^^^^^

.. code-block:: cpp

   class PlayerManager {
   public:
       static PlayerManager& Instance() {
           static PlayerManager inst;
           return inst;  // 返回引用：避免复制，直接把本体交出去
       }
   };

返回引用有两个关键好处：

1. **避免复制开销**：如果返回值类型（``PlayerManager``）而非引用，
   每次调用 ``Instance()`` 都会复制整个对象——代价巨大。
2. **比返回指针更安全**：调用者不需要解引用（``->``），不需要担心空指针，
   直接用 ``.`` 操作符就行。

**比喻**：返回引用就像"给你我的名片，上面写着我家地址"——
你直接来我家办事，不需要先拿到我的副本再去找副本的家。

智能指针
--------

智能指针是现代 C++ 管理动态内存的核心工具。
它们的本质是**用对象的生命周期来管理资源**（RAII 思想）——
当智能指针离开作用域时，它管理的内存会自动释放，彻底告别手动 ``delete``。

unique_ptr：独占所有权
^^^^^^^^^^^^^^^^^^^^^^^^

``unique_ptr`` 表示**独占所有权**——同一时刻只有一个 ``unique_ptr`` 拥有某个对象。
不能复制，只能移动。

.. code-block:: cpp

   #include <memory>

   auto ptr = std::make_unique<int>(42);   // 创建：推荐用 make_unique
   // auto ptr2 = ptr;                     // 错误！unique_ptr 不可复制
   auto ptr2 = std::move(ptr);             // 正确：转移所有权
   // 此时 ptr 变为 nullptr，ptr2 拥有对象

**比喻**：``unique_ptr`` 就像一把**唯一的钥匙**——
同一把钥匙不能复制，只能交给下一个人。交出去之后，你就没有了。

shared_ptr：引用计数共享所有权
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``shared_ptr`` 通过**引用计数**实现共享所有权。
多个 ``shared_ptr`` 可以同时拥有同一个对象，当最后一个 ``shared_ptr`` 被销毁时，
对象才会被释放。

.. code-block:: cpp

   auto p1 = std::make_shared<int>(42);  // 引用计数 = 1
   {
       auto p2 = p1;                      // 引用计数 = 2
       std::cout << *p2 << "\n";          // 使用对象
   }  // p2 离开作用域，引用计数 = 1
   // p1 仍然有效，引用计数 = 1
   // 当 p1 也离开作用域时，引用计数 = 0，对象被释放

**比喻**：``shared_ptr`` 就像**合租公寓的钥匙**——
每个室友都有一把钥匙（引用计数 +1），
最后一个搬走的室友（引用计数归零）负责关灯锁门（释放对象）。

**易错点：循环引用**

.. code-block:: cpp

   struct B;  // 前向声明

   struct A {
       std::shared_ptr<B> b_ptr;
   };
   struct B {
       std::shared_ptr<A> a_ptr;  // 循环引用！引用计数永远不会归零
   };

如果 A 指向 B，B 又指向 A，引用计数永远不为零，内存泄漏。
解决方案：一方改用 ``weak_ptr``。

weak_ptr：弱引用，打破循环依赖
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``weak_ptr`` 是一种**弱引用**——它能观察一个 ``shared_ptr`` 管理的对象，
但不会增加引用计数。

.. code-block:: cpp

   auto shared = std::make_shared<int>(42);
   std::weak_ptr<int> weak = shared;     // 弱引用，不增加引用计数

   if (auto locked = weak.lock()) {      // 尝试"锁定"为 shared_ptr
       std::cout << *locked << "\n";     // 对象还活着，可以使用
   } else {
       std::cout << "对象已释放\n";       // 对象已被销毁
   }

**比喻**：``weak_ptr`` 就像"借阅证"——你可以查看图书馆的书（观察对象），
但你借阅不影响书的存亡（不增加引用计数）。
书被销毁后，你的借阅证就失效了（``lock()`` 返回 nullptr）。

**实战：打破循环引用**

.. code-block:: cpp

   struct Child;  // 前向声明

   struct Parent {
       std::vector<std::shared_ptr<Child>> children;
   };

   struct Child {
       std::weak_ptr<Parent> parent;  // 用 weak_ptr 打破循环
   };

移动语义
--------

移动语义是 C++11 引入的核心特性，解决了一个根本问题：
**当我们不再需要一个对象时，如何避免昂贵的深拷贝？**

右值引用 (T&&)
^^^^^^^^^^^^^^^^

C++11 引入了右值引用 ``T&&``，它可以绑定到**临时对象**（右值）。
右值是即将销毁的临时对象，我们可以"偷走"它的资源而不是复制。

.. code-block:: cpp

   void process(std::string&& s) {   // 接受右值引用
       // s 绑定到一个临时 string，我们可以"偷走"它的内部缓冲区
       std::cout << s << "\n";
   }

   process(std::string("hello"));    // OK：临时对象是右值
   // process(some_lvalue);           // 错误：左值不能绑定到右值引用

std::move
^^^^^^^^^

``std::move`` 本身**不做任何移动操作**——它只是一个类型转换，
把左值"标记"为右值，表示"我放弃这个对象的所有权了，你可以偷走它的资源"。

.. code-block:: cpp

   std::string s1 = "hello";
   std::string s2 = std::move(s1);  // 移动：s1 的内部缓冲区被"偷走"给 s2
   // 此时 s1 处于"有效但未指定"的状态——可以销毁，但不应该读取其值

**比喻**：``std::move`` 就像在物品上贴一个"可转让"标签。
贴标签本身不移动任何东西，但它告诉别人："这个东西你可以拿走，
不需要复制一份新的。"

移动构造函数与移动赋值运算符
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   class Buffer {
       int* data_;
       size_t size_;
   public:
       // 移动构造函数："偷走"other 的资源
       Buffer(Buffer&& other) noexcept
           : data_(other.data_)      // 接管指针
           , size_(other.size_)      // 接管大小
       {
           other.data_ = nullptr;    // 置空原对象，防止重复释放
           other.size_ = 0;
       }

       // 移动赋值运算符
       Buffer& operator=(Buffer&& other) noexcept {
           if (this != &other) {
               delete[] data_;        // 释放自己原有的资源
               data_ = other.data_;   // 接管
               size_ = other.size_;
               other.data_ = nullptr; // 置空原对象
               other.size_ = 0;
           }
           return *this;
       }
   };

移动构造函数的核心思想：**转移指针所有权**，而不是复制数据。
这使得移动操作的时间复杂度通常是 O(1)，而复制操作可能是 O(n)。

完美转发 (std::forward)
^^^^^^^^^^^^^^^^^^^^^^^^^

``std::forward`` 用于**模板中保持参数的原始值类别**。
它解决了模板参数传递时值类别被"退化"的问题。

.. code-block:: cpp

   template<typename T>
   void wrapper(T&& arg) {
       // std::forward 保持 arg 的原始值类别
       // 如果传入的是右值，forward 后仍是右值
       // 如果传入的是左值，forward 后仍是左值
       actual_function(std::forward<T>(arg));
   }

**比喻**：``std::forward`` 就像一个**透传包裹**——
不管寄件人寄的是"普通快递"还是"加急件"，
你原封不动地转发给下一站，保持原有的优先级。

Lambda 表达式
-------------

Lambda 是 C++11 引入的**匿名函数**，让你在需要的地方就地定义一个小函数，
无需单独命名和声明。它极大地简化了回调、算法参数等场景。

基本语法
^^^^^^^^

.. code-block:: cpp

   [capture](params) -> return_type { body }

   // 最简形式
   auto greet = []() { std::cout << "Hello!\n"; };
   greet();  // 调用

   // 带参数和返回值
   auto add = [](int a, int b) -> int { return a + b; };
   std::cout << add(3, 4) << "\n";  // 输出 7

**比喻**：Lambda 就像一张**便签纸上的小函数**——
你不需要给它起名字，用完就可以扔掉。

捕获方式
^^^^^^^^

Lambda 的 ``[]`` 部分叫做**捕获列表**，决定 Lambda 能访问外部变量的方式：

.. code-block:: cpp

   int x = 10, y = 20;

   auto f1 = [=]()      { return x + y; };   // 按值捕获所有变量（副本）
   auto f2 = [&]()      { return x + y; };   // 按引用捕获所有变量（直接访问）
   auto f3 = [x, &y]()  { return x + y; };   // x 按值，y 按引用
   auto f4 = [this]()   { return member_; };  // 捕获当前对象的 this 指针

   // C++14：初始化捕获（移动捕获）
   auto ptr = std::make_unique<int>(42);
   auto f5 = [p = std::move(ptr)]() { return *p; };  // 移动 unique_ptr 进 Lambda

+----------+---------------------------------------------+
| 捕获方式  | 含义                                        |
+==========+=============================================+
| ``[=]``  | 按值捕获所有外部变量（创建副本）              |
+----------+---------------------------------------------+
| ``[&]``  | 按引用捕获所有外部变量（直接访问原变量）        |
+----------+---------------------------------------------+
| ``[x]``  | 按值捕获变量 x                              |
+----------+---------------------------------------------+
| ``[&x]`` | 按引用捕获变量 x                            |
+----------+---------------------------------------------+
| ``[this]``| 捕获当前对象指针                             |
+----------+---------------------------------------------+

**易错点**：按值捕获的变量默认是 ``const`` 的——Lambda 内部不能修改它们。
如果需要修改，使用 ``mutable`` 关键字：

.. code-block:: cpp

   int count = 0;
   auto increment = [count]() mutable { count++; };  // mutable 允许修改副本

泛型 Lambda (C++14)
^^^^^^^^^^^^^^^^^^^^

C++14 允许 Lambda 参数使用 ``auto``，使其成为**泛型 Lambda**：

.. code-block:: cpp

   auto print = [](const auto& value) {
       std::cout << value << "\n";
   };
   print(42);          // 输出 42
   print("hello");     // 输出 hello
   print(3.14);        // 输出 3.14

constexpr Lambda (C++17)
^^^^^^^^^^^^^^^^^^^^^^^^

C++17 中 Lambda 默认是 ``constexpr`` 的，可以在编译期求值：

.. code-block:: cpp

   constexpr auto square = [](int x) { return x * x; };
   static_assert(square(5) == 25);  // 编译期计算

模板编程
--------

模板是 C++ 最强大的特性之一——它让你写出**类型无关**的代码，
编译器会为每种类型生成专属的实现。这就是 STL 能同时支持
int、string、自定义类型的秘密。

函数模板
^^^^^^^^

.. code-block:: cpp

   template<typename T>
   T max_val(T a, T b) {
       return (a > b) ? a : b;
   }

   // 编译器自动推导类型
   std::cout << max_val(3, 4) << "\n";        // T = int
   std::cout << max_val(3.14, 2.71) << "\n";  // T = double

类模板
^^^^^^

.. code-block:: cpp

   template<typename T>
   class Stack {
       std::vector<T> data_;
   public:
       void push(const T& val) { data_.push_back(val); }
       T pop() {
           T val = data_.back();
           data_.pop_back();
           return val;
       }
       bool empty() const { return data_.empty(); }
   };

   Stack<int> int_stack;
   int_stack.push(42);
   Stack<std::string> str_stack;
   str_stack.push("hello");

模板特化
^^^^^^^^

**全特化**：为特定类型提供完全不同的实现。

.. code-block:: cpp

   // 通用版本
   template<typename T>
   std::string to_string_custom(T val) { return std::to_string(val); }

   // 全特化：针对 const char* 的特殊处理
   template<>
   std::string to_string_custom<const char*>(const char* val) {
       return std::string(val);
   }

**偏特化**：为部分类型参数提供特殊实现。

.. code-block:: cpp

   // 通用版本
   template<typename T1, typename T2>
   class Pair { /* ... */ };

   // 偏特化：两个类型相同时
   template<typename T>
   class Pair<T, T> {
       T first_, second_;
   public:
       Pair(T a, T b) : first_(a), second_(b) {}
   };

可变参数模板 (Variadic Templates)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

C++11 允许模板接受**任意数量**的参数：

.. code-block:: cpp

   // 递归终止
   void print() {}

   // 递归展开：每次处理一个参数
   template<typename T, typename... Args>
   void print(T first, Args... rest) {
       std::cout << first;
       if constexpr (sizeof...(rest) > 0) {
           std::cout << ", ";
           print(rest...);  // 递归调用
       }
   }

   print(1, "hello", 3.14, 'c');  // 输出: 1, hello, 3.14, c

SFINAE 与 if constexpr
^^^^^^^^^^^^^^^^^^^^^^^^

**SFINAE (Substitution Failure Is Not An Error)**：模板参数替换失败不是错误，
编译器会尝试其他重载。

.. code-block:: cpp

   #include <type_traits>

   // 只对整数类型启用
   template<typename T>
   typename std::enable_if<std::is_integral<T>::value, T>::type
   safe_divide(T a, T b) {
       if (b == 0) throw std::runtime_error("division by zero");
       return a / b;
   }

**``if constexpr`` (C++17)**：在编译期进行条件判断，比 SFINAE 更直观。

.. code-block:: cpp

   template<typename T>
   std::string describe(T val) {
       if constexpr (std::is_integral_v<T>) {
           return "integer: " + std::to_string(val);
       } else if constexpr (std::is_floating_point_v<T>) {
           return "float: " + std::to_string(val);
       } else {
           return "other type";
       }
   }

Concepts (C++20)
^^^^^^^^^^^^^^^^

C++20 的 Concepts 是对 SFINAE 的**彻底革新**——用清晰的约束语法
取代晦涩的模板元编程。

.. code-block:: cpp

   #include <concepts>

   // 定义一个 Concept：要求类型支持加法和流输出
   template<typename T>
   concept Addable = requires(T a, T b) {
       { a + b } -> std::convertible_to<T>;
   };

   // 使用 Concept 约束模板参数
   template<Addable T>
   T add(T a, T b) { return a + b; }

   // 另一种写法：直接在参数列表中约束
   auto multiply(std::integral auto a, std::integral auto b) {
       return a * b;
   }

现代 C++ 特性
--------------

constexpr：编译期计算
^^^^^^^^^^^^^^^^^^^^^^

``constexpr`` 让函数和变量在**编译期**求值，将运行时开销转移到编译期。

.. code-block:: cpp

   constexpr int factorial(int n) {
       return (n <= 1) ? 1 : n * factorial(n - 1);
   }

   constexpr int val = factorial(5);  // 编译期计算：val = 120
   int arr[factorial(3)];             // 编译期计算数组大小：arr[6]

   // C++14：constexpr 函数可以有局部变量和循环
   constexpr int sum(int n) {
       int result = 0;
       for (int i = 1; i <= n; ++i) result += i;
       return result;
   }
   static_assert(sum(100) == 5050);  // 编译期验证

std::optional, std::variant, std::any (C++17)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**``std::optional``**：表示一个"可能有值，可能没有"的变量，替代 nullptr 和哨兵值。

.. code-block:: cpp

   #include <optional>

   std::optional<int> find_value(const std::vector<int>& v, int target) {
       for (int x : v) {
           if (x == target) return x;  // 找到了，返回值
       }
       return std::nullopt;  // 没找到，返回空
   }

   auto result = find_value({1, 2, 3}, 2);
   if (result.has_value()) {
       std::cout << "Found: " << result.value() << "\n";
   }

**``std::variant``**：类型安全的 union，可以存储多种类型中的一种。

.. code-block:: cpp

   #include <variant>

   std::variant<int, std::string, double> v;
   v = 42;                  // 存储 int
   v = "hello";             // 存储 const char*（转为 string）
   v = 3.14;                // 存储 double

   // 安全访问
   if (std::holds_alternative<double>(v)) {
       std::cout << std::get<double>(v) << "\n";
   }

   // 访问者模式（推荐）
   std::visit([](auto&& arg) {
       std::cout << arg << "\n";
   }, v);

**``std::any``**：可以存储**任意类型**的容器，类型擦除的极致。

.. code-block:: cpp

   #include <any>

   std::any a = 42;
   a = std::string("hello");
   a = 3.14;

   // 取出时必须指定正确类型，否则抛异常
   double val = std::any_cast<double>(a);  // OK: 3.14
   // int bad = std::any_cast<int>(a);     // 抛 std::bad_any_cast

**应用场景**：``optional`` 用于可能失败的返回值，
``variant`` 用于有限集合的类型安全联合，
``any`` 用于完全动态的场景（如配置系统、脚本引擎）。

结构化绑定 (C++17)
^^^^^^^^^^^^^^^^^^^^

结构化绑定让你用一行代码解构 tuple、pair、结构体等：

.. code-block:: cpp

   #include <tuple>

   auto [name, age, score] = std::tuple{"Alice", 20, 95.5};
   std::cout << name << " is " << age << " years old\n";

   // 解构 map
   std::map<std::string, int> scores = {{"Alice", 90}, {"Bob", 85}};
   for (const auto& [name, score] : scores) {
       std::cout << name << ": " << score << "\n";
   }

   // 解构结构体
   struct Point { double x, y; };
   auto [x, y] = Point{1.0, 2.0};

ranges (C++20)
^^^^^^^^^^^^^^

Ranges 是 C++20 引入的**函数式数据处理管道**，让数据变换代码
像自然语言一样流畅。

.. code-block:: cpp

   #include <ranges>
   #include <vector>

   std::vector<int> data = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

   // 管道语法：过滤偶数 -> 平方 -> 取前3个
   auto result = data
       | std::views::filter([](int x) { return x % 2 == 0; })
       | std::views::transform([](int x) { return x * x; })
       | std::views::take(3);

   for (int val : result) {
       std::cout << val << " ";  // 输出: 4 16 36
   }

**比喻**：Ranges 就像一条**数据流水线**——
数据从一端进入，经过过滤、转换、截取等工序，
从另一端流出。每个工序都是独立的，可以自由组合。

coroutines (C++20)
^^^^^^^^^^^^^^^^^^^^

协程是 C++20 引入的**协作式并发**机制，让异步代码写起来像同步代码。

.. code-block:: cpp

   #include <coroutine>
   #include <iostream>

   // 简化的 Generator 协程
   template<typename T>
   struct Generator {
       struct promise_type {
           T current_value;
           auto get_return_object() {
               return Generator{
                   std::coroutine_handle<promise_type>::from_promise(*this)};
           }
           auto initial_suspend() { return std::suspend_always{}; }
           auto final_suspend() noexcept { return std::suspend_always{}; }
           auto yield_value(T value) {
               current_value = value;
               return std::suspend_always{};
           }
           void return_void() {}
       };

       std::coroutine_handle<promise_type> handle;
       bool next() { handle.resume(); return !handle.done(); }
       T value() { return handle.promise().current_value; }
       ~Generator() { if (handle) handle.destroy(); }
   };

   Generator<int> fibonacci() {
       int a = 0, b = 1;
       while (true) {
           co_yield a;
           auto temp = a;
           a = b;
           b = temp + b;
       }
   }

   int main() {
       auto gen = fibonacci();
       for (int i = 0; i < 10; ++i) {
           gen.next();
           std::cout << gen.value() << " ";
       }
       // 输出: 0 1 1 2 3 5 8 13 21 34
   }

窄视图模式 (Narrow View)
-------------------------

窄视图模式是一种**架构设计技巧**，解决的问题是：
当一个"大管家"类功能过于庞大时，外部业务代码可以调用任何方法，
容易产生跨域误调用。

问题
^^^^

.. code-block:: cpp

   // 大管家：管理音乐、媒体、音量——功能太多，外部容易乱调
   class PlayerManager {
   public:
       void PlayMusic(const std::string& url);
       void StopMusic();
       void PlayMedia(const std::string& url);
       void StopMedia();
       void SetVolume(int level);
       int  GetVolume();
       // ... 几十个方法
   };

   // 业务代码可能写出这种危险调用：
   PlayerManager& pm = PlayerManager::Instance();
   pm.SetVolume(100);    // 音乐模块不该调音量接口
   pm.PlayMedia("...");  // 音乐模块不该调媒体播放

解决方案
^^^^^^^^

将大管家切分为多个小的**代理对象**，每个代理只暴露特定领域的方法：

.. code-block:: cpp

   // 音乐播放代理——只暴露音乐相关接口
   class MusicPlayer {
       friend class PlayerManager;
       PlayerManager& pm_;
       explicit MusicPlayer(PlayerManager& pm) : pm_(pm) {}
   public:
       void Play(const std::string& url) { pm_.PlayMusic(url); }
       void Stop() { pm_.StopMusic(); }
   };

   // 媒体播放代理——只暴露媒体相关接口
   class MediaPlayer {
       friend class PlayerManager;
       PlayerManager& pm_;
       explicit MediaPlayer(PlayerManager& pm) : pm_(pm) {}
   public:
       void Play(const std::string& url) { pm_.PlayMedia(url); }
       void Stop() { pm_.StopMedia(); }
   };

   // 音量控制代理——只暴露音量相关接口
   class VolumeController {
       friend class PlayerManager;
       PlayerManager& pm_;
       explicit VolumeController(PlayerManager& pm) : pm_(pm) {}
   public:
       void Set(int level) { pm_.SetVolume(level); }
       int  Get() { return pm_.GetVolume(); }
   };

   // 大管家提供窄视图访问
   class PlayerManager {
   public:
       MusicPlayer&     Music()  { static MusicPlayer v(*this); return v; }
       MediaPlayer&     Media()  { static MediaPlayer v(*this); return v; }
       VolumeController& Volume(){ static VolumeController v(*this); return v; }
   };

使用效果
^^^^^^^^

.. code-block:: cpp

   // 音乐业务代码只能拿到 MusicPlayer
   PlayerManager::Instance().Music().Play("song.mp3");   // OK
   // PlayerManager::Instance().Music().SetVolume(100);  // 编译错误！MusicPlayer 没有这个方法

   // 音量业务代码只能拿到 VolumeController
   PlayerManager::Instance().Volume().Set(80);           // OK
   // PlayerManager::Instance().Volume().Play("...");    // 编译错误！

**核心价值**：在**编译期**就杜绝了跨域误调用——不是运行时报错，
而是编译器直接拒绝。这是"让错误在最早期暴露"的工程哲学。

**比喻**：窄视图就像餐厅的**分区管理**——
前台只能操作点餐系统，后厨只能操作出餐系统，仓库管理员只能操作库存系统。
每个岗位只能看到自己需要的功能，不会误操作其他区域。

附录
----

RAII 原则
^^^^^^^^^

**RAII (Resource Acquisition Is Initialization)** 是 C++ 最重要的编程惯用法：
**在构造函数中获取资源，在析构函数中释放资源**。

.. code-block:: cpp

   class FileHandle {
       FILE* fp_;
   public:
       FileHandle(const char* filename) : fp_(fopen(filename, "r")) {
           if (!fp_) throw std::runtime_error("cannot open file");
       }
       ~FileHandle() {
           if (fp_) fclose(fp_);  // 析构时自动释放
       }
       // 禁止复制，防止双重释放
       FileHandle(const FileHandle&) = delete;
       FileHandle& operator=(const FileHandle&) = delete;
   };

   void read_file() {
       FileHandle fh("data.txt");  // 构造时打开文件
       // 使用 fh 读取数据...
   }  // 离开作用域时，析构函数自动关闭文件——无论是否有异常

**RAII 是智能指针、锁守卫等现代 C++ 工具的理论基础。**
它的核心思想：把资源的生命周期绑定到对象的生命周期，
让编译器自动管理资源的释放，彻底告别手动资源管理的噩梦。
