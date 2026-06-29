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

值类别 (Value Categories)
-------------------------

理解值类别是掌握移动语义、引用绑定和完美转发的**前置知识**。
C++ 将所有表达式分为五种类别，它们决定了表达式能否被移动、能否被绑定到引用。

五种值类别
^^^^^^^^^^

.. code-block:: text

                    表达式 (expression)
                   /                    \
              泛左值 (glvalue)          右值 (rvalue)
             /           \             /           \
          左值 (lvalue)  亡值 (xvalue)  亡值 (xvalue)  纯右值 (prvalue)

- **左值 (lvalue)**：有持久身份的表达式，可以取地址。如变量名、解引用 ``*p``、前置 ``++x``
- **纯右值 (prvalue)**：没有持久身份的临时值。如字面量 ``42``、后置 ``x++``、lambda 表达式
- **亡值 (xvalue)**：即将被"掠夺"资源的值。如 ``std::move(x)``、返回右值引用的函数调用
- **泛左值 (glvalue)**：左值 + 亡值（有身份的表达式）
- **右值 (rvalue)**：亡值 + 纯右值（可以被移动的表达式）

**比喻**：左值就像"有门牌号的房子"——你知道它在哪里，可以反复访问。
右值就像"路边的临时摊位"——用完就撤，没有固定地址。

引用绑定规则
^^^^^^^^^^^^

.. code-block:: cpp

   int x = 42;

   int& ref1 = x;              // OK：左值引用绑定到左值
   // int& ref2 = 42;          // 错误：左值引用不能绑定到右值
   const int& ref3 = 42;       // OK：const 左值引用可以绑定到右值
   int&& ref4 = 42;            // OK：右值引用绑定到右值
   int&& ref5 = std::move(x);  // OK：右值引用绑定到亡值
   // int&& ref6 = x;          // 错误：右值引用不能绑定到左值

.. list-table::
   :header-rows: 1

   * - 引用类型
     - 左值
     - 亡值
     - 纯右值
   * - ``T&``
     - Yes
     - No
     - No
   * - ``const T&``
     - Yes
     - Yes
     - Yes
   * - ``T&&``
     - No
     - Yes
     - Yes
   * - ``const T&&``
     - No
     - Yes
     - Yes

判断规则速查
^^^^^^^^^^^^

.. code-block:: cpp

   int x = 42;

   // 左值：有名字、可取地址
   x;                  // 左值：变量名
   *ptr;               // 左值：解引用
   ++x;                // 左值：前置自增返回引用
   arr[0];             // 左值：下标访问
   str = "hello";      // 左值：赋值表达式返回左值

   // 右值：临时的、不可取地址
   42;                 // 纯右值：字面量
   x++;                // 纯右值：后置自增返回副本
   x + y;              // 纯右值：算术表达式
   std::move(x);       // 亡值：std::move 将左值转为亡值
   func();             // 右值：函数返回非引用类型

**易错点**：``std::move(x)`` 本身不做任何移动操作，它只是把左值 x 转换为亡值，
表示"我可以被移动"。真正执行移动的是移动构造函数或移动赋值运算符。

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

const 正确性
------------

``const`` 是 C++ 类型系统中最重要的修饰符之一。正确使用 ``const`` 能让代码更安全、
更清晰，也能让编译器帮你捕获错误。一句话概括：**能用 ``const`` 的地方就用 ``const``**。

const 变量
^^^^^^^^^^

.. code-block:: cpp

   const int x = 42;    // 必须初始化，之后不可修改
   // x = 100;          // 错误：不能修改 const 变量

   const int& ref = x;  // const 引用：不能通过 ref 修改 x
   // ref = 100;        // 错误

const 指针判读法
^^^^^^^^^^^^^^^^

``const`` 在 ``*`` 的左边还是右边，含义完全不同：

.. code-block:: cpp

   int x = 1, y = 2;

   const int* p1 = &x;      // 指向常量的指针：不能通过 p1 修改 *p1
   // *p1 = 100;            // 错误
   p1 = &y;                 // OK：指针本身可以改指向

   int* const p2 = &x;      // 常量指针：p2 不能改指向
   *p2 = 100;               // OK：可以通过 p2 修改 *p2
   // p2 = &y;              // 错误

   const int* const p3 = &x; // 指向常量的常量指针：都不能改
   // *p3 = 100;            // 错误
   // p3 = &y;              // 错误

**判读口诀**：``const`` 在 ``*`` 左边 = "指向的东西是 const"（不能改值），
``const`` 在 ``*`` 右边 = "指针本身是 const"（不能改指向）。
从右往左读：``const int*`` 读作"指向 const int 的指针"，
``int* const`` 读作"const 指针，指向 int"。

const 成员函数
^^^^^^^^^^^^^^

.. code-block:: cpp

   class Point {
       double x_, y_;
   public:
       double getX() const { return x_; }  // 承诺不修改对象状态
       void setX(double x) { x_ = x; }    // 非 const：可以修改
   };

   void print(const Point& p) {
       // p.setX(1.0);    // 错误：const 引用只能调用 const 成员函数
       std::cout << p.getX();  // OK：getX() 是 const 的
   }

``const`` 成员函数的语义：**承诺不修改对象的任何非 ``mutable`` 成员**。
编译器会在编译期检查这个承诺。

``mutable`` 关键字允许某些成员在 ``const`` 函数中被修改（如缓存、互斥锁）：

.. code-block:: cpp

   class Cache {
       mutable std::mutex mtx_;  // mutable：即使在 const 函数中也能加锁
       mutable std::string cached_result_;
       bool valid_ = false;
   public:
       std::string getData() const {
           std::lock_guard<std::mutex> lock(mtx_);  // OK：mutable
           if (!valid_) {
               cached_result_ = compute();  // OK：mutable
               valid_ = true;
           }
           return cached_result_;
       }
   };

const 与函数参数
^^^^^^^^^^^^^^^^

.. code-block:: cpp

   // 好：避免拷贝 + 防止修改
   void process(const std::string& name) {
       std::cout << name;  // 只读访问
   }

   // 不好：不必要的拷贝
   void process_bad(std::string name) {
       std::cout << name;  // 每次调用都复制整个字符串
   }

**规则**：对于非内置类型（class、string、vector 等），
如果函数只需要读取参数，用 ``const T&`` 传参。
对于内置类型（int、double、指针等），直接按值传参即可（拷贝开销可忽略）。

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

override 与 final (C++11)
^^^^^^^^^^^^^^^^^^^^^^^^^

``override`` 关键字让编译器检查你是否真的重写了基类虚函数，防止拼写错误：

.. code-block:: cpp

   class Base {
   public:
       virtual void foo() const {}
   };

   class Derived : public Base {
   public:
       // void foo() constt override {}  // 编译错误！拼写错误被 override 捕获
       void foo() const override {}       // 正确：编译器确认重写了 Base::foo
   };

``final`` 关键字阻止进一步重写或阻止类被继承：

.. code-block:: cpp

   class Base {
   public:
       virtual void foo() final {}  // foo 不能被子类重写
   };

   class Derived final : public Base {  // Derived 不能被继承
       // void foo() override {}        // 错误：foo 是 final 的
   };

**建议**：所有重写的虚函数都加上 ``override``，这是防御性编程的最佳实践。

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * -
     - 运行时多态
     - 编译时多态
   * - 机制
     - ``virtual`` 函数 + vtable
     - 模板 (template)
   * - 绑定时机
     - 运行时（动态绑定）
     - 编译时（静态绑定）
   * - 性能
     - 有虚函数调用开销（查 vtable）
     - 零开销（编译器生成特化代码）
   * - 灵活性
     - 可以在运行时切换行为
     - 类型在编译时确定
   * - 典型应用
     - 接口抽象、插件系统
     - STL 容器、数学库、序列化

.. code-block:: cpp

   // 运行时多态：通过基类指针调用
   void print_area(Shape* s) { std::cout << s->area() << "\n"; }

   // 编译时多态：模板为每种类型生成专属代码
   template<typename T>
   T max_val(T a, T b) { return (a > b) ? a : b; }

运算符重载
----------

运算符重载让你为自定义类型定义运算符的行为，使自定义类型像内置类型一样自然使用。

可重载运算符
^^^^^^^^^^^^

几乎所有的运算符都可以重载，但以下运算符**不能**重载：

- ``::`` （作用域解析）
- ``.*`` （成员指针访问）
- ``.`` （成员访问）
- ``?:`` （三目运算符）

成员函数 vs 非成员函数重载
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   class Vec2 {
       double x_, y_;
   public:
       Vec2(double x, double y) : x_(x), y_(y) {}

       // 成员函数重载：左操作数必须是本类类型
       Vec2 operator+(const Vec2& rhs) const {
           return Vec2(x_ + rhs.x_, y_ + rhs.y_);
       }

       // 成员函数重载：前置自增
       Vec2& operator++() { ++x_; ++y_; return *this; }

       // 成员函数重载：后置自增（用 int 参数区分）
       Vec2 operator++(int) {
           Vec2 tmp = *this;
           ++(*this);
           return tmp;
       }

       // 非成员函数重载：流插入运算符必须是非成员函数
       friend std::ostream& operator<<(std::ostream& os, const Vec2& v) {
           return os << "(" << v.x_ << ", " << v.y_ << ")";
       }
   };

**规则**：算术运算符通常作为非成员函数重载（保证对称性），
赋值运算符必须作为成员函数重载，流运算符必须作为非成员函数重载。

比较运算符与 C++20 三路比较
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

C++20 引入了 ``<=>``（spaceship 运算符），自动生成所有比较运算符：

.. code-block:: cpp

   #include <compare>

   class Point {
       int x_, y_;
   public:
       // C++20：定义 <=> 即可自动生成 <, <=, >, >=, ==, !=
       auto operator<=>(const Point&) const = default;
   };

   // 也可以手写 == 和 <=> 的自定义逻辑
   class Student {
       std::string name_;
       int score_;
   public:
       bool operator==(const Student& o) const { return name_ == o.name_; }
       auto operator<=>(const Student& o) const { return score_ <=> o.score_; }
   };

下标运算符与函数调用运算符
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   class Array {
       int data_[100];
   public:
       // 下标运算符：让对象像数组一样使用
       int& operator[](size_t i) { return data_[i]; }
       const int& operator[](size_t i) const { return data_[i]; }
   };

   // 函数调用运算符：让对象像函数一样使用（仿函数/函数对象）
   class Adder {
       int base_;
   public:
       Adder(int base) : base_(base) {}
       int operator()(int x) const { return base_ + x; }
   };

   Adder add5(5);
   std::cout << add5(10) << "\n";  // 输出 15，像函数一样调用

**Lambda 本质**：Lambda 表达式在编译器内部就是一个重载了 ``operator()`` 的匿名类。
``[capture]`` 部分对应构造函数参数，``(params)`` 对应 ``operator()`` 参数。

三/五/零法则
------------

这三个法则是 C++ 对象生命周期管理的核心准则，理解它们能避免绝大多数资源管理 bug。

Rule of Three（三法则）
^^^^^^^^^^^^^^^^^^^^^^^^

如果一个类需要**自定义**以下三个特殊成员函数中的任何一个，
那么它通常也需要自定义另外两个：

1. **析构函数** ``~T()``
2. **拷贝构造函数** ``T(const T&)``
3. **拷贝赋值运算符** ``T& operator=(const T&)``

.. code-block:: cpp

   class Buffer {
       int* data_;
       size_t size_;
   public:
       Buffer(size_t n) : data_(new int[n]), size_(n) {}
       ~Buffer() { delete[] data_; }                                    // 需要：手动释放

       Buffer(const Buffer& other) : data_(new int[other.size_]), size_(other.size_) {
           std::copy(other.data_, other.data_ + size_, data_);          // 需要：深拷贝
       }

       Buffer& operator=(const Buffer& other) {                         // 需要：深拷贝赋值
           if (this != &other) {
               delete[] data_;
               size_ = other.size_;
               data_ = new int[size_];
               std::copy(other.data_, other.data_ + size_, data_);
           }
           return *this;
       }
   };

**为什么？** 如果你自定义了析构函数（释放资源），但没有自定义拷贝操作，
编译器生成的默认拷贝只会做**浅拷贝**——两个对象的 ``data_`` 指向同一块内存，
析构时双重释放，程序崩溃。

Rule of Five（五法则）
^^^^^^^^^^^^^^^^^^^^^^

C++11 扩展了三法则，加上移动操作：

4. **移动构造函数** ``T(T&&) noexcept``
5. **移动赋值运算符** ``T& operator=(T&&) noexcept``

.. code-block:: cpp

   class Buffer {
       // ... 三法则的代码 ...

       Buffer(Buffer&& other) noexcept
           : data_(other.data_), size_(other.size_) {
           other.data_ = nullptr; other.size_ = 0;  // "偷走"资源
       }

       Buffer& operator=(Buffer&& other) noexcept {
           if (this != &other) {
               delete[] data_;
               data_ = other.data_; size_ = other.size_;
               other.data_ = nullptr; other.size_ = 0;
           }
           return *this;
       }
   };

**如果定义了移动操作但没有定义拷贝操作**，拷贝操作会被隐式删除。

Rule of Zero（零法则）
^^^^^^^^^^^^^^^^^^^^^^

**现代 C++ 的首选**：尽量不自定义任何特殊成员函数，让编译器生成默认版本。

.. code-block:: cpp

   class User {
       std::string name_;      // string 自己管理内存
       std::vector<int> tags_; // vector 自己管理内存
       std::unique_ptr<Profile> profile_;  // unique_ptr 自动释放
   public:
       User(std::string name) : name_(std::move(name)) {}
       // 不需要自定义析构、拷贝、移动——编译器自动生成正确的版本
   };

**为什么 Rule of Zero 是首选？** 因为使用 RAII 成员（string、vector、unique_ptr、lock_guard 等）
时，编译器自动生成的特殊成员函数就是正确的。自定义越多，出 bug 的风险越大。

**比喻**：Rule of Zero 就像"雇佣专业的搬家公司（RAII 成员）"——
你不需要自己搬东西（自定义特殊成员函数），搬家公司会正确处理一切。

类型转换
--------

C++ 提供了四种命名转换操作符，比 C 风格强制转换更安全、更明确。

static_cast
^^^^^^^^^^^

最常用的转换，用于**编译期已知的安全转换**：

.. code-block:: cpp

   // 数值类型转换
   double d = 3.14;
   int i = static_cast<int>(d);  // i = 3，截断小数部分

   // 继承层次中的上行转换（安全）
   class Dog : public Animal {};
   Dog dog;
   Animal& a = static_cast<Animal&>(dog);  // OK：派生类到基类

   // void* 与其他指针之间的转换
   int x = 42;
   void* vp = &x;
   int* ip = static_cast<int*>(vp);  // OK

dynamic_cast
^^^^^^^^^^^^

用于**运行时多态的向下转换**，依赖 RTTI（运行时类型信息）：

.. code-block:: cpp

   class Animal { public: virtual ~Animal() = default; };
   class Dog : public Animal { public: void bark() {} };
   class Cat : public Animal { public: void meow() {} };

   Animal* a = new Dog();

   // 向下转换：基类指针转为派生类指针
   Dog* dog = dynamic_cast<Dog*>(a);
   if (dog) {
       dog->bark();  // OK：转换成功
   }

   Cat* cat = dynamic_cast<Cat*>(a);
   if (!cat) {
       std::cout << "转换失败：a 不是 Cat\n";  // 转换失败返回 nullptr
   }

**要求**：基类必须有虚函数（至少有虚析构函数），否则 ``dynamic_cast`` 编译失败。

const_cast
^^^^^^^^^^

**唯一能操作 ``const`` 属性的转换**——去除或添加 ``const``：

.. code-block:: cpp

   const int x = 42;
   const int* p = &x;

   int* mutable_p = const_cast<int*>(p);  // 去除 const
   *mutable_p = 100;  // 未定义行为！如果 x 确实是 const 的

**警告**：``const_cast`` 去除 const 后修改一个原本就是 const 的变量是**未定义行为**。
它主要用于与不接受 const 的旧 C API 交互。

reinterpret_cast
^^^^^^^^^^^^^^^^

**最危险的转换**——直接重新解释底层位模式：

.. code-block:: cpp

   int x = 42;
   int* p = &x;

   // 把指针解释为整数（仅用于特殊场景，如调试、与 C API 交互）
   uintptr_t addr = reinterpret_cast<uintptr_t>(p);

   // 把一种指针类型解释为另一种
   float* fp = reinterpret_cast<float*>(p);  // 危险：位模式完全重新解释

**使用场景**：与底层 C API 交互、序列化、嵌入式硬件寄存器访问。
一般业务代码中**不应使用**。

C 风格转换 vs 命名转换
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   // C 风格转换：不明确意图，可能引发意外
   int i = (int)d;           // 可能是 static_cast，也可能是 reinterpret_cast

   // C++ 命名转换：意图明确，可搜索，可审查
   int i = static_cast<int>(d);  // 明确是安全的数值转换

**建议**：永远使用 C++ 命名转换操作符，不要使用 C 风格转换。
命名转换让代码审查更容易，也让编译器帮你检查更多错误。

RAII (Resource Acquisition Is Initialization)
----------------------------------------------

RAII 是 C++ 最重要的编程范式——**在构造函数中获取资源，在析构函数中释放资源**。
它不是某个具体的语法特性，而是一种**设计哲学**。

核心思想
^^^^^^^^

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

**比喻**：RAII 就像"带保险的租赁"——你签合同时拿到钥匙（获取资源），
合同到期自动还钥匙（释放资源）。不管合同期间发生了什么意外（异常），
钥匙都会被自动归还。

RAII 与异常安全
^^^^^^^^^^^^^^^

RAII 的最大价值在异常场景中体现：

.. code-block:: cpp

   void dangerous_operation() {
       FileHandle fh1("data1.txt");
       FileHandle fh2("data2.txt");

       // 如果这里抛出异常...
       do_something_risky();

       // fh2 和 fh1 的析构函数会被自动调用（按构造的逆序），
       // 文件句柄不会泄漏
   }

没有 RAII 时，你需要手动 ``try/catch`` 并在 ``catch`` 中释放每个资源——
这在资源多的时候极其容易出错。

RAII 应用：锁守卫
^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   #include <mutex>

   class ThreadSafeCounter {
       mutable std::mutex mtx_;
       int count_ = 0;
   public:
       void increment() {
           std::lock_guard<std::mutex> lock(mtx_);  // 构造时加锁
           ++count_;
       }  // 析构时自动解锁

       // C++17：std::scoped_lock 可以同时锁多个互斥锁，避免死锁
       void transfer(ThreadSafeCounter& other) {
           std::scoped_lock lock(mtx_, other.mtx_);  // 同时锁两个锁
           ++count_;
           --other.count_;
       }
   };

异常处理
--------

异常处理是 C++ 处理运行时错误的标准机制。虽然在嵌入式等场景中可能被禁用，
但理解异常机制对于阅读和编写 C++ 代码至关重要。

基本语法
^^^^^^^^

.. code-block:: cpp

   #include <stdexcept>

   double divide(double a, double b) {
       if (b == 0) {
           throw std::invalid_argument("division by zero");  // 抛出异常
       }
       return a / b;
   }

   try {
       double result = divide(10, 0);
   } catch (const std::invalid_argument& e) {
       std::cout << "参数错误: " << e.what() << "\n";  // 捕获特定异常
   } catch (const std::exception& e) {
       std::cout << "其他错误: " << e.what() << "\n";  // 捕获所有标准异常
   } catch (...) {
       std::cout << "未知错误\n";  // 捕获所有异常（包括非标准异常）
   }

异常类层次
^^^^^^^^^^

.. code-block:: text

   std::exception
   ├── std::logic_error          // 程序逻辑错误（应该在编码时避免）
   │   ├── std::invalid_argument
   │   ├── std::domain_error
   │   ├── std::out_of_range
   │   └── std::length_error
   └── std::runtime_error        // 运行时错误（无法在编码时预见）
       ├── std::range_error
       ├── std::overflow_error
       └── std::underflow_error

栈展开 (Stack Unwinding)
^^^^^^^^^^^^^^^^^^^^^^^^

当异常被抛出时，程序沿着调用栈向上传播，每经过一个函数调用，
该函数中已构造的局部对象都会被**逆序析构**——这就是栈展开。

.. code-block:: cpp

   void func_c() { throw std::runtime_error("error"); }
   void func_b() { std::string s = "hello"; func_c(); }  // s 在异常传播时被析构
   void func_a() { std::vector<int> v = {1,2,3}; func_b(); }  // v 在异常传播时被析构

   int main() {
       try { func_a(); }
       catch (const std::exception& e) { std::cout << e.what(); }
   }

noexcept 说明符
^^^^^^^^^^^^^^^

``noexcept`` 告诉编译器和调用者：这个函数**不会抛出异常**。

.. code-block:: cpp

   void safe_function() noexcept {  // 承诺不抛异常
       // 如果这里意外抛出异常，程序会直接调用 std::terminate()
   }

   // 移动操作应该标记为 noexcept
   Buffer(Buffer&& other) noexcept : data_(other.data_), size_(other.size_) {
       other.data_ = nullptr;
       other.size_ = 0;
   }

**为什么移动操作要 ``noexcept``？** 因为 STL 容器（如 ``std::vector``）在扩容时
需要移动元素。如果移动操作不是 ``noexcept``，vector 会选择**拷贝**（更安全）而不是移动。
标记 ``noexcept`` 可以让 vector 使用移动操作，获得更好的性能。

异常安全保证
^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - 级别
     - 含义
   * - 不抛异常保证
     - 操作永远不会失败（如析构函数、移动操作）
   * - 强保证
     - 操作要么完全成功，要么完全回滚（事务语义）
   * - 基本保证
     - 操作可能失败，但对象仍处于有效状态，无资源泄漏

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

unique_ptr 自定义删除器
^^^^^^^^^^^^^^^^^^^^^^^^

默认情况下，``unique_ptr`` 对 ``new`` 创建的对象调用 ``delete``。
对于非 ``new`` 创建的资源（如 ``fopen`` 返回的 ``FILE*``），需要自定义删除器：

.. code-block:: cpp

   // 方式一：函数指针类型
   std::unique_ptr<FILE, decltype(&fclose)> fp(fopen("data.txt", "r"), &fclose);

   // 方式二：Lambda 类型（C++20 推荐，因为无状态 Lambda 可以优化掉额外开销）
   auto deleter = [](FILE* f) { if (f) fclose(f); };
   std::unique_ptr<FILE, decltype(deleter)> fp2(fopen("data.txt", "r"), deleter);

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

shared_ptr 自定义删除器
^^^^^^^^^^^^^^^^^^^^^^^^

与 ``unique_ptr`` 不同，``shared_ptr`` 的删除器**不影响类型**，使用更灵活：

.. code-block:: cpp

   // shared_ptr 的删除器在构造时传入，不影响类型
   std::shared_ptr<FILE> fp(fopen("data.txt", "r"), [](FILE* f) {
       if (f) fclose(f);
   });

   // 可以用同一个类型 shared_ptr<FILE> 管理不同删除器的资源
   std::shared_ptr<FILE> fp2(fopen("data2.txt", "r"), &fclose);  // 同一类型

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
   // 此时 s1 处于"合法但未指定"的状态

**比喻**：``std::move`` 就像在物品上贴一个"可转让"标签。
贴标签本身不移动任何东西，但它告诉别人："这个东西你可以拿走，
不需要复制一份新的。"

移动后的对象状态
^^^^^^^^^^^^^^^^

移动后的对象处于**合法但未指定 (valid but unspecified)** 的状态：

.. code-block:: cpp

   std::string s1 = "hello";
   std::string s2 = std::move(s1);

   // 以下操作对 s1 是安全的：
   s1 = "new value";    // ✅ 安全：可以赋新值
   s1.empty();          // ✅ 安全：可以查询状态（但结果未指定）
   std::string s3(s1);  // ✅ 安全：可以拷贝（但内容未指定）

   // 以下操作是危险的：
   // char c = s1[0];   // ❌ 危险：内容未指定，可能读到垃圾值

**规则**：移动后的对象只能做两件事——赋新值和销毁。不要读取其内容。

std::exchange
^^^^^^^^^^^^^

``std::exchange`` 是手动实现移动操作的实用工具：

.. code-block:: cpp

   #include <utility>

   class Buffer {
       int* data_ = nullptr;
       size_t size_ = 0;
   public:
       Buffer(Buffer&& other) noexcept
           : data_(std::exchange(other.data_, nullptr))   // 取走 other.data_，并置空
           , size_(std::exchange(other.size_, 0))         // 取走 other.size_，并置零
       {}
   };

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

.. list-table::
   :header-rows: 1

   * - 捕获方式
     - 含义
   * - ``[=]``
     - 按值捕获所有外部变量（创建副本）
   * - ``[&]``
     - 按引用捕获所有外部变量（直接访问原变量）
   * - ``[x]``
     - 按值捕获变量 x
   * - ``[&x]``
     - 按引用捕获变量 x
   * - ``[this]``
     - 捕获当前对象指针
   * - ``[*this]``
     - 按值捕获当前对象（C++20）

**易错点**：按值捕获的变量默认是 ``const`` 的——Lambda 内部不能修改它们。
如果需要修改，使用 ``mutable`` 关键字：

.. code-block:: cpp

   int count = 0;
   auto increment = [count]() mutable { count++; };  // mutable 允许修改副本

[*this] 捕获 (C++20)
^^^^^^^^^^^^^^^^^^^^^

C++20 允许按值捕获 ``this`` 指针指向的对象，避免悬垂指针问题：

.. code-block:: cpp

   class Widget {
       int value_ = 42;
   public:
       auto get_lambda() {
           // [this] 捕获的是指针——如果 Widget 被销毁，指针悬垂
           // [*this] 捕获的是对象的副本——安全
           return [*this]() { return value_; };
       }
   };

   auto f = Widget{}.get_lambda();  // Widget 临时对象已销毁
   // [this] 版本：悬垂指针，未定义行为
   // [*this] 版本：安全，值是 42 的副本

**什么时候用 ``[*this]``？** 当 Lambda 的生命周期可能超过当前对象时，
必须用 ``[*this]`` 按值捕获。

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

类模板参数推导 CTAD (C++17)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

C++17 之前，使用类模板必须显式指定类型参数。C++17 引入了 CTAD，让编译器自动推导：

.. code-block:: cpp

   // C++17 之前：必须写全类型
   std::pair<int, double> p1(1, 2.0);
   std::vector<int> v1{1, 2, 3};

   // C++17：编译器自动推导
   std::pair p2(1, 2.0);           // 推导为 pair<int, double>
   std::vector v2{1, 2, 3};        // 推导为 vector<int>

   // 自定义推导指南（deduction guide）
   template<typename T>
   class Wrapper {
       T value_;
   public:
       Wrapper(T v) : value_(v) {}
   };
   // 推导指南：告诉编译器如何从构造函数参数推导模板参数
   template<typename T>
   Wrapper(T) -> Wrapper<T>;

枚举类型
--------

非限定枚举 (Unscoped Enum)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

C 风格的枚举，存在隐式转换问题：

.. code-block:: cpp

   enum Color { Red, Green, Blue };  // 非限定枚举

   Color c = Red;
   int i = c;          // OK：隐式转换为 int（这是个坑！）
   if (c == 0) {}      // OK：可以与整数比较（容易出错）

限定枚举 (Scoped Enum / enum class) (C++11)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

C++11 引入了强类型的 ``enum class``，解决了非限定枚举的所有问题：

.. code-block:: cpp

   enum class Color : uint8_t { Red = 0, Green = 1, Blue = 2 };

   Color c = Color::Red;
   // int i = c;             // 错误！不允许隐式转换
   int i = static_cast<int>(c);  // OK：显式转换

   // 可以指定底层类型，节省内存或满足协议要求
   enum class ErrorCode : uint16_t {
       Success = 0,
       NotFound = 404,
       ServerError = 500
   };

   // 与 switch 配合使用
   switch (c) {
       case Color::Red:   std::cout << "Red\n";   break;
       case Color::Green: std::cout << "Green\n"; break;
       case Color::Blue:  std::cout << "Blue\n";  break;
   }

**建议**：始终使用 ``enum class``，不要使用非限定枚举。

预处理器
--------

预处理器在**编译之前**处理源代码，执行宏替换、文件包含、条件编译等操作。

#include
^^^^^^^^^

.. code-block:: cpp

   #include <iostream>    // 角括号：在系统目录中查找（标准库、第三方库）
   #include "myheader.h"  // 双引号：先在当前目录查找，找不到再查系统目录

宏定义
^^^^^^

.. code-block:: cpp

   // 对象宏：常量定义（推荐用 constexpr 代替）
   #define MAX_SIZE 1024

   // 函数宏：注意括号！
   #define SQUARE(x) ((x) * (x))  // 必须加括号，否则 SQUARE(1+2) 会出错

   // 预定义宏
   std::cout << __FILE__ << ":" << __LINE__;  // 当前文件名和行号
   std::cout << __func__;                      // 当前函数名
   std::cout << __cplusplus;                   // C++ 标准版本号

**易错点**：宏定义没有类型检查，不会进入调试符号，容易产生难以排查的 bug。
现代 C++ 中，能用 ``constexpr``、``const``、``inline`` 代替的场景都不要用宏。

条件编译
^^^^^^^^

.. code-block:: cpp

   #ifdef DEBUG
       std::cout << "Debug mode\n";
   #else
       std::cout << "Release mode\n";
   #endif

   #ifndef MY_HEADER_H    // Include Guard：防止头文件被重复包含
   #define MY_HEADER_H

   // 头文件内容...

   #endif // MY_HEADER_H

   // 现代替代方案（非标准但被所有主流编译器支持）：
   #pragma once           // 更简洁，效果相同

字符串化与连接
^^^^^^^^^^^^^^

.. code-block:: cpp

   // # 运算符：将宏参数转为字符串
   #define STRINGIFY(x) #x
   std::cout << STRINGIFY(hello);  // 输出 "hello"

   // ## 运算符：连接两个 token
   #define CONCAT(a, b) a##b
   int CONCAT(my, var) = 42;  // 等价于 int myvar = 42;

命名空间
--------

命名空间用于组织代码、避免命名冲突。

基本用法
^^^^^^^^

.. code-block:: cpp

   namespace MyLib {
       class Widget { /* ... */ };
       void process() { /* ... */ }
   }

   namespace MyLib::SubLib {  // C++17 嵌套命名空间简写
       class Helper { /* ... */ };
   }

   // 使用方式
   MyLib::Widget w;                // 完全限定名
   MyLib::process();               // 完全限定名

using 声明与 using 指令
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   // using 声明：引入特定名称（推荐）
   using MyLib::Widget;
   Widget w;  // OK

   // using 指令：引入整个命名空间（谨慎使用）
   using namespace MyLib;
   Widget w2;  // OK，但污染当前作用域

**警告**：不要在头文件中使用 ``using namespace``，否则所有包含该头文件的
翻译单元都会被污染。

匿名命名空间
^^^^^^^^^^^^

替代 C 风格的 ``static``，限制变量/函数的链接性为当前翻译单元：

.. code-block:: cpp

   namespace {  // 匿名命名空间：内部链接，仅当前文件可见
       int internal_counter = 0;
       void helper() { ++internal_counter; }
   }

命名空间别名与 ADL
^^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   // 命名空间别名
   namespace fs = std::filesystem;
   fs::path p("/tmp/test");

   // ADL (Argument-Dependent Lookup) / Koenig Lookup
   // 调用函数时，编译器会在参数类型所在的命名空间中查找函数
   std::cout << "hello";  // 不需要写 std::operator<<(std::cout, "hello")
                          // 编译器自动在 std 命名空间中找到 operator<<

作用域、存储持续期与链接性
--------------------------

作用域
^^^^^^

.. code-block:: cpp

   int global_var = 1;           // 文件作用域：整个文件可见

   namespace NS {
       int ns_var = 2;           // 命名空间作用域
   }

   void func() {
       int local_var = 3;        // 块作用域：仅在函数内可见
       {
           int inner_var = 4;    // 内层块作用域
           // local_var 仍然可见
       }
       // inner_var 不可见
   }

存储持续期
^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - 存储持续期
     - 生命周期
     - 示例
   * - 自动 (auto)
     - 声明所在块的开始到结束
     - 局部变量 ``int x;``
   * - 静态 (static)
     - 程序启动到程序结束
     - 全局变量、``static`` 局部变量
   * - 动态 (dynamic)
     - ``new`` 到 ``delete``
     - ``new int(42)``
   * - 线程 (thread)
     - 线程创建到线程结束
     - ``thread_local int x;``

链接性
^^^^^^

.. code-block:: cpp

   // 内部链接：仅当前翻译单元可见
   static int internal_var = 1;           // C 风格
   namespace { int anon_var = 2; }        // 匿名命名空间（推荐）

   // 外部链接：其他翻译单元可见
   int global_var = 3;                    // 外部链接
   extern int external_var;               // 声明（不定义）

   // C++17：inline 变量——解决头文件中全局变量的多重定义问题
   inline int shared_var = 42;            // 可以在头文件中定义，不会重复定义

STL 概览
--------

STL (Standard Template Library) 是 C++ 标准库的核心，包含容器、算法和迭代器。

序列容器
^^^^^^^^

.. code-block:: cpp

   #include <vector>
   #include <array>
   #include <deque>
   #include <list>

   // vector：动态数组，随机访问 O(1)，尾部插入 O(1) 均摊
   std::vector<int> v = {1, 2, 3};
   v.push_back(4);
   v[0];  // 随机访问

   // array：固定大小数组，栈上分配
   std::array<int, 3> arr = {1, 2, 3};

   // deque：双端队列，头尾插入 O(1)
   std::deque<int> dq = {2, 3};
   dq.push_front(1);
   dq.push_back(4);

   // list：双向链表，任意位置插入 O(1)，不支持随机访问
   std::list<int> lst = {1, 2, 3};
   auto it = lst.begin();
   std::advance(it, 1);
   lst.insert(it, 99);  // 在位置 1 插入 99

关联容器
^^^^^^^^

.. code-block:: cpp

   #include <set>
   #include <map>

   // set：有序集合，自动去重，O(log n) 查找
   std::set<int> s = {3, 1, 4, 1, 5};
   // s = {1, 3, 4, 5}，自动排序去重

   // map：有序键值对，O(log n) 查找
   std::map<std::string, int> m = {{"alice", 90}, {"bob", 85}};
   m["charlie"] = 95;
   for (const auto& [name, score] : m) {  // 结构化绑定
       std::cout << name << ": " << score << "\n";
   }

无序容器
^^^^^^^^

.. code-block:: cpp

   #include <unordered_set>
   #include <unordered_map>

   // unordered_set：哈希集合，平均 O(1) 查找
   std::unordered_set<int> us = {1, 2, 3};

   // unordered_map：哈希键值对，平均 O(1) 查找
   std::unordered_map<std::string, int> um;
   um["key"] = 42;

容器适配器
^^^^^^^^^^

.. code-block:: cpp

   #include <stack>
   #include <queue>

   // stack：后进先出 (LIFO)
   std::stack<int> stk;
   stk.push(1); stk.push(2);
   stk.top();   // 2
   stk.pop();   // 移除 2

   // queue：先进先出 (FIFO)
   std::queue<int> q;
   q.push(1); q.push(2);
   q.front();   // 1
   q.pop();     // 移除 1

   // priority_queue：优先队列（默认最大堆）
   std::priority_queue<int> pq;
   pq.push(3); pq.push(1); pq.push(2);
   pq.top();    // 3（最大值）

迭代器
^^^^^^

.. code-block:: cpp

   std::vector<int> v = {1, 2, 3, 4, 5};

   // 正向迭代
   for (auto it = v.begin(); it != v.end(); ++it) {
       std::cout << *it << " ";
   }

   // const 迭代器：不能修改元素
   for (auto it = v.cbegin(); it != v.cend(); ++it) {
       // *it = 10;  // 错误
   }

   // 反向迭代
   for (auto it = v.rbegin(); it != v.rend(); ++it) {
       std::cout << *it << " ";  // 5 4 3 2 1
   }

常用算法
^^^^^^^^

.. code-block:: cpp

   #include <algorithm>
   #include <numeric>

   std::vector<int> v = {3, 1, 4, 1, 5, 9};

   std::sort(v.begin(), v.end());                    // 排序
   auto it = std::find(v.begin(), v.end(), 4);       // 查找
   auto cnt = std::count(v.begin(), v.end(), 1);     // 计数
   std::reverse(v.begin(), v.end());                  // 反转
   std::transform(v.begin(), v.end(), v.begin(),
                  [](int x) { return x * 2; });       // 变换

   // std::erase (C++20)：直接删除满足条件的元素
   std::erase_if(v, [](int x) { return x < 3; });   // 删除小于 3 的元素

   // accumulate：累加
   int sum = std::accumulate(v.begin(), v.end(), 0);

string 与 string_view
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: cpp

   #include <string>
   #include <string_view>

   // std::string：拥有字符串数据，可修改
   std::string s = "hello";
   s += " world";

   // std::string_view (C++17)：只读视图，不拥有数据，零拷贝
   std::string_view sv = s;           // 指向 s 的数据，不复制
   sv = "another string literal";     // 可以指向字面量

   void process(std::string_view sv) {  // 推荐用 string_view 作只读参数
       std::cout << sv << "\n";
   }

pair 与 tuple
^^^^^^^^^^^^^

.. code-block:: cpp

   #include <utility>
   #include <tuple>

   // pair：两个值
   std::pair<std::string, int> p = {"alice", 90};
   auto [name, score] = p;  // 结构化绑定

   // tuple：多个值
   auto t = std::tuple{1, "hello", 3.14};
   auto [a, b, c] = t;  // 结构化绑定

文件 I/O
--------

文件流
^^^^^^

.. code-block:: cpp

   #include <fstream>

   // 写文件
   {
       std::ofstream out("data.txt");  // 默认文本模式
       out << "Hello, World!\n";
       out << 42 << " " << 3.14 << "\n";
   }  // 离开作用域自动关闭

   // 读文件
   {
       std::ifstream in("data.txt");
       std::string line;
       while (std::getline(in, line)) {
           std::cout << line << "\n";
       }
   }

   // 二进制模式
   {
       std::ofstream out("data.bin", std::ios::binary);
       int x = 42;
       out.write(reinterpret_cast<const char*>(&x), sizeof(x));
   }

   // 追加模式
   {
       std::ofstream out("log.txt", std::ios::app);
       out << "New log entry\n";
   }

stringstream
^^^^^^^^^^^^

.. code-block:: cpp

   #include <sstream>

   // 字符串拼接
   std::ostringstream oss;
   oss << "Name: " << name << ", Age: " << age;
   std::string result = oss.str();

   // 字符串解析
   std::istringstream iss("42 3.14 hello");
   int i; double d; std::string s;
   iss >> i >> d >> s;  // i=42, d=3.14, s="hello"

格式化输出
^^^^^^^^^^

.. code-block:: cpp

   #include <iomanip>

   std::cout << std::fixed << std::setprecision(2) << 3.14159;  // 输出 3.14
   std::cout << std::setw(10) << std::setfill('*') << 42;       // 输出 ********42
   std::cout << std::hex << std::showbase << 255;                // 输出 0xff

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
