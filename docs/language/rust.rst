Rust 语言
=========

Rust 是一门注重安全、并发和性能的系统编程语言。它的核心设计理念是：**在编译时消除内存安全问题，无需垃圾回收器**。
本文档是 Rust 语言的全面参考手册，涵盖从基础语法到高级特性的方方面面。

.. contents:: 目录
   :depth: 3
   :local:

所有权系统
----------

所有权是 Rust 最独特的特性，也是理解 Rust 的钥匙。

**比喻**：把值想象成一套房子——

- **所有权** = 房产证：每套房子有且仅有一个主人
- **移动（Move）** = 过户：把房产证交给别人，自己就不再是房主
- **借用（Borrow）** = 租房：可以住，但不能卖，租期到了必须归还
- **生命周期（Lifetime）** = 租期：租房合同约定的有效时间

所有权规则
^^^^^^^^^^

Rust 的所有权系统建立在三条铁律之上：

1. **每个值有且仅有一个所有者**
2. **同一时刻只能有一个所有者**
3. **当所有者离开作用域时，值被自动丢弃（drop）**

.. code-block:: rust

   fn main() {
       let s1 = String::from("hello"); // s1 是 "hello" 的所有者
       let s2 = s1;                    // 所有权转移给 s2，s1 失效
       // println!("{}", s1);          // 编译错误！s1 已经无效
       println!("{}", s2);             // 正常工作
   }

**为什么这样设计？** 传统语言用垃圾回收器（GC）或手动 free 来管理内存。
GC 有运行时开销，手动 free 容易出错（double free、use-after-free）。
Rust 用所有权规则在编译时就解决了这些问题——既没有 GC 的运行时开销，也没有手动管理的 Bug。

Move 语义与 Copy 类型
^^^^^^^^^^^^^^^^^^^^^^

**Move 语义**：对于堆上数据（如 ``String``、``Vec``），赋值会转移所有权。

.. code-block:: rust

   let s = String::from("hello");
   let t = s;           // Move：s 的所有权转移给 t
   // println!("{}", s); // 错误！s 已失效

**Copy 类型**：对于栈上简单数据（如 ``i32``、``f64``、``bool``、``char``），赋值会复制值。

.. code-block:: rust

   let x: i32 = 42;
   let y = x;         // Copy：x 和 y 都有效
   println!("{}", x); // 正常！i32 实现了 Copy trait

**判断标准**：如果一个类型实现了 ``Copy`` trait，赋值时会复制而不是移动。
所有整数、浮点数、布尔、字符以及由它们组成的元组都实现了 ``Copy``。
包含堆数据的类型（``String``、``Vec<T>``、``Box<T>``）**不能**实现 ``Copy``。

**类比**：Copy 像复印一份文件（原件和副本都有效），Move 像把钥匙交给别人（自己就没有了）。

借用
^^^^

借用允许你**使用**一个值而不获取其所有权。

- **不可变借用** ``&T``：可以同时存在多个，只读访问
- **可变借用** ``&mut T``：同一时刻只能存在一个，可读可写

.. code-block:: rust

   fn calculate_length(s: &String) -> usize {
       s.len()  // 借用 s，不获取所有权
   }

   fn append_world(s: &mut String) {
       s.push_str(" world");  // 可变借用，可以修改
   }

   fn main() {
       let mut s = String::from("hello");

       // 不可变借用：可以同时有多个
       let len = calculate_length(&s);
       println!("长度: {}", len);

       // 可变借用：同一时刻只能有一个
       append_world(&mut s);
       println!("{}", s);
   }

**借用规则**（编译器强制）：

1. 在任何给定时刻，要么有**一个**可变引用，要么有**任意数量**的不可变引用
2. 引用必须始终有效（不能悬垂引用）

**类比**：不可变借用像图书馆借书——多人可以同时借同一本书来读。
可变借用像去维修店修车——同一时间只能有一个人在修，修的时候车主也不能开走。

生命周期
^^^^^^^^

生命周期是编译器用来确保引用**始终有效**的机制。

**是什么**：生命周期标注（如 ``'a``）告诉编译器多个引用之间的存活时间关系。

**为什么需要**：当函数返回引用时，编译器需要知道返回值的有效期与哪个输入参数绑定。

.. code-block:: rust

   // 'a 表示：返回值的生命周期 = x 和 y 中较短的那个
   fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
       if x.len() > y.len() { x } else { y }
   }

   fn main() {
       let string1 = String::from("long string");
       let result;
       {
           let string2 = String::from("xyz");
           result = longest(string1.as_str(), string2.as_str());
           println!("最长: {}", result); // OK：string2 还活着
       }
       // println!("{}", result); // 编译错误！string2 已被释放
   }

**类比**：生命周期就像租房合同上的租期。如果房东（变量）要卖房（离开作用域），
租客（引用）必须在此之前搬走。编译器就是严格的房产中介，确保不会出现"房子塌了租客还在"的情况。

结构体中的生命周期标注
""""""""""""""""""""""

当结构体包含引用时，必须标注生命周期：

.. code-block:: rust

   // 这个结构体持有一个字符串切片的引用
   // 'a 表示：Excerpt 实例的生命周期不能超过它引用的数据
   struct Excerpt<'a> {
       part: &'a str,
   }

   impl<'a> Excerpt<'a> {
       fn level(&self) -> i32 {
           3  // 返回值不是引用，不需要生命周期标注
       }

       fn announce_and_return(&self, announcement: &str) -> &str {
           println!("注意: {}", announcement);
           self.part  // 返回值的生命周期与 self 绑定
       }
   }

   fn main() {
       let novel = String::from("Call me Ishmael. Some years ago...");
       let first_sentence;
       {
           let i = novel.find('.').unwrap_or(novel.len());
           first_sentence = Excerpt {
               part: &novel[..i],
           };
       }
       println!("摘录: {}", first_sentence.part);
   }

**类比**：结构体中的生命周期标注就像租房合同上写的"租客不得转租给比自己租期更长的人"。

生命周期省略规则
""""""""""""""""

编译器不是总需要你手写生命周期标注。当你遵循以下模式时，编译器会自动推断：

**规则一**：每个引用参数都获得各自的生命周期。

.. code-block:: rust

   // 你写的：
   fn foo(x: &str) -> &str { x }
   // 编译器推断为：
   fn foo<'a>(x: &'a str) -> &'a str { x }

**规则二**：如果只有一个输入生命周期参数，它被赋给所有输出生命周期。

.. code-block:: rust

   // 你写的：
   fn first_word(s: &str) -> &str { &s[..1] }
   // 编译器推断为：
   fn first_word<'a>(s: &'a str) -> &'a str { &s[..1] }

**规则三**：如果有多个输入参数但其中一个是 ``&self`` 或 ``&mut self``，则 self 的生命周期赋给所有输出。

.. code-block:: rust

   struct Parser<'input> {
       data: &'input str,
       pos: usize,
   }

   impl<'input> Parser<'input> {
       // 返回值的生命周期与 self 绑定，不需要手动标注
       fn next_token(&mut self) -> &str {
           &self.data[self.pos..self.pos + 1]
       }
   }

如果应用这三条规则后，编译器仍然无法确定返回值的生命周期，就会报错并要求你手动标注。

``'static`` 生命周期
""""""""""""""""""""

``'static`` 表示引用在**整个程序运行期间**都有效。

.. code-block:: rust

   // 字符串字面量的类型就是 &'static str
   let s: &'static str = "我会活到程序结束";

   // 在 trait bound 中常见
   fn print_it<T: std::fmt::Display + 'static>(input: T) {
       println!("'static: {}", input);
   }

**常见误解**：``'static`` 不意味着数据是"静态的"或"全局的"，而是说引用的有效期足够长。
字符串字面量是 ``'static`` 因为它们被嵌入到编译出的二进制文件中。

**类比**：``'static`` 就像永久产权——只要程序（小区）存在，你就一直拥有。

常见生命周期陷阱
""""""""""""""""

**陷阱一：返回局部变量的引用**

.. code-block:: rust

   // 错误！dangle 返回了指向已释放内存的引用
   // fn dangle() -> &String {
   //     let s = String::from("hello");
   //     &s  // s 在函数结束时被释放
   // }

   // 解决方案：返回所有权
   fn no_dangle() -> String {
       let s = String::from("hello");
       s  // 移动所有权给调用者
   }

**陷阱二：结构体持有引用导致生命周期纠缠**

.. code-block:: rust

   // 问题：两个引用的生命周期不同，编译器无法推断
   // 解决方案：让结构体拥有数据，而不是借用
   struct OwnedData {
       data: String,  // 拥有而不是借用
   }

**陷阱三：在闭包中捕获引用**

.. code-block:: rust

   fn main() {
       let mut callbacks: Vec<Box<dyn Fn()>> = Vec::new();

       // 错误：s 的引用可能在闭包使用前失效
       // {
       //     let s = String::from("hello");
       //     callbacks.push(Box::new(|| println!("{}", s)));
       // }

       // 解决方案：使用 move 转移所有权
       {
           let s = String::from("hello");
           callbacks.push(Box::new(move || println!("{}", s)));
       }
       callbacks[0](); // "hello"
   }

模式匹配
--------

模式匹配是 Rust 中处理数据变体的强大工具。它不只是 ``match`` 表达式，更是一种**让编译器帮你检查是否遗漏了情况**的思维方式。

**比喻**：模式匹配就像海关安检——每种行李（数据形态）都必须经过对应检查通道，
编译器确保你不会遗漏任何一种行李。

基础 match
^^^^^^^^^^

``match`` 必须穷尽所有可能，否则编译器会报错。

.. code-block:: rust

   fn describe_number(n: i32) -> &'static str {
       match n {
           1 => "一",
           2..=5 => "二到五",
           6 | 7 => "周末",
           _ => "其他",
       }
   }

   fn main() {
       println!("{}", describe_number(1));   // 一
       println!("{}", describe_number(3));   // 二到五
       println!("{}", describe_number(7));   // 周末
       println!("{}", describe_number(42));  // 其他
   }

if let 和 while let
^^^^^^^^^^^^^^^^^^^

当你只关心**一种**情况时，``if let`` 比 ``match`` 更简洁：

.. code-block:: rust

   fn main() {
       let config_max: Option<u8> = Some(3);

       // match 写法（啰嗦）
       match config_max {
           Some(max) => println!("最大值: {}", max),
           _ => (),  // 必须处理 None
       }

       // if let 写法（简洁）
       if let Some(max) = config_max {
           println!("最大值: {}", max);
       }

       // if let + else
       let value = Some(42);
       let text = if let Some(v) = value {
           format!("有值: {}", v)
       } else {
           "无值".to_string()
       };
   }

``while let`` 在循环中持续匹配：

.. code-block:: rust

   fn main() {
       let mut stack = vec![1, 2, 3, 4, 5];

       // pop() 返回 Option<T>，当栈为空时返回 None，循环结束
       while let Some(top) = stack.pop() {
           println!("弹出: {}", top);
       }
       // 输出: 5, 4, 3, 2, 1
   }

解构结构体
^^^^^^^^^^

.. code-block:: rust

   struct Point {
       x: i32,
       y: i32,
   }

   fn main() {
       let p = Point { x: 10, y: 20 };

       // 解构绑定
       let Point { x, y } = p;
       println!("x={}, y={}", x, y);

       // 部分解构 + 重命名
       let Point { x: a, y: _ } = p;
       println!("x={}", a);

       // 在 match 中使用
       match p {
           Point { x: 0, y } => println!("在 y 轴上: y={}", y),
           Point { x, y: 0 } => println!("在 x 轴上: x={}", x),
           Point { x, y } => println!("一般点: ({}, {})", x, y),
       }
   }

解构枚举
^^^^^^^^^

.. code-block:: rust

   enum Message {
       Quit,
       Move { x: i32, y: i32 },
       Write(String),
       ChangeColor(i32, i32, i32),
   }

   fn process_message(msg: Message) {
       match msg {
           Message::Quit => println!("退出"),
           Message::Move { x, y } => println!("移动到 ({}, {})", x, y),
           Message::Write(text) => println!("消息: {}", text),
           Message::ChangeColor(r, g, b) => println!("颜色: ({}, {}, {})", r, g, b),
       }
   }

解构元组
^^^^^^^^^

.. code-block:: rust

   fn main() {
       let ((a, b), (c, d)): ((i32, i32), (i32, i32)) = ((1, 2), (3, 4));
       println!("a={}, b={}, c={}, d={}", a, b, c, d);

       // 在 for 循环中解构
       let points = vec![(1, 2), (3, 4), (5, 6)];
       for (x, y) in points {
           println!("({}, {})", x, y);
       }
   }

Match Guards（匹配守卫）
^^^^^^^^^^^^^^^^^^^^^^^^

在 ``match`` 分支后加 ``if`` 条件，进一步细化匹配：

.. code-block:: rust

   fn main() {
       let num = Some(4);

       match num {
           Some(x) if x < 0 => println!("负数: {}", x),
           Some(x) if x == 0 => println!("零"),
           Some(x) if x % 2 == 0 => println!("正偶数: {}", x),
           Some(x) => println!("正奇数: {}", x),
           None => println!("无值"),
       }

       // match guard 可以捕获外部变量
       let max = 10;
       let value = 5;
       match value {
           n if n > max => println!("{} 超过最大值 {}", n, max),
           n => println!("{} 在范围内", n),
       }
   }

**注意**：match guard 不会从模式中消耗值，因此不会影响穷尽性检查。

@ Bindings
^^^^^^^^^^

``@`` 运算符让你在检查值是否匹配模式的同时，将值绑定到变量：

.. code-block:: rust

   enum Temperature {
       Celsius(f64),
       Fahrenheit(f64),
   }

   fn classify_temp(temp: Temperature) {
       match temp {
           // 将值绑定到 t，同时检查范围
           Temperature::Celsius(t @ -40.0..=0.0) => {
               println!("严寒: {}°C", t)
           }
           Temperature::Celsius(t @ 0.0..=30.0) => {
               println!("舒适: {}°C", t)
           }
           Temperature::Celsius(t) => {
               println!("极端: {}°C", t)
           }
           Temperature::Fahrenheit(f @ -40.0..=32.0) => {
               println!("严寒: {}°F", f)
           }
           Temperature::Fahrenheit(f) => {
               println!("华氏: {}°F", f)
           }
       }
   }

穷尽性检查
^^^^^^^^^^

Rust 编译器**强制**你处理所有可能的情况。这是 Rust 安全性的又一体现。

.. code-block:: rust

   enum Direction {
       North, South, East, West,
   }

   fn go(dir: Direction) {
       match dir {
           Direction::North => println!("向北"),
           Direction::South => println!("向南"),
           // 如果漏掉 East 和 West，编译器会报错：
           // "non-exhaustive patterns: `East` and `West` not covered"
           Direction::East => println!("向东"),
           Direction::West => println!("向西"),
       }
   }

对于非穷尽类型（如 ``i32``），使用 ``_`` 通配符兜底：

.. code-block:: rust

   let x: i32 = 42;
   match x {
       0 => println!("零"),
       n @ 1..=100 => println!("小正数: {}", n),
       _ => println!("其他"),  // 兜底
   }

错误处理
--------

Rust 的错误处理哲学是：**让错误成为类型系统的一部分**，而不是靠 try-catch 在运行时捕获。

**比喻**：

- ``panic!`` = 火灾报警器：事情已经不可挽回，必须立刻撤离（程序崩溃）
- ``Result`` = 快递签收单：可能成功（``Ok``），可能失败（``Err``），你必须处理两种情况

panic! vs Result：不可恢复 vs 可恢复
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**panic!**（不可恢复错误）：

.. code-block:: rust

   fn main() {
       // 显式 panic
       panic!("程序出了大问题！");

       // 隐式 panic（数组越界）
       let v = vec![1, 2, 3];
       v[99]; // 运行时 panic
   }

**何时使用 panic!**：

- 代码处于不一致状态，继续执行会造成更大损害
- 原型开发阶段，快速失败
- 测试中断言失败
- 违反了"不可能发生"的不变量

**Result**（可恢复错误）：

.. code-block:: rust

   use std::fs::File;
   use std::io::{self, Read};

   fn read_file(path: &str) -> Result<String, io::Error> {
       let mut file = File::open(path)?;
       let mut contents = String::new();
       file.read_to_string(&mut contents)?;
       Ok(contents)
   }

   fn main() {
       match read_file("hello.txt") {
           Ok(content) => println!("文件内容: {}", content),
           Err(e) => println!("读取失败: {}", e),
       }
   }

``?`` 运算符
^^^^^^^^^^^^

``?`` 是错误传播的语法糖：

.. code-block:: rust

   // 不使用 ?（啰嗦）
   fn read_username_v1() -> Result<String, io::Error> {
       let f = File::open("username.txt");
       let mut f = match f {
           Ok(file) => file,
           Err(e) => return Err(e),  // 提前返回错误
       };

       let mut s = String::new();
       match f.read_to_string(&mut s) {
           Ok(_) => Ok(s),
           Err(e) => Err(e),
       }
   }

   // 使用 ?（简洁）
   fn read_username_v2() -> Result<String, io::Error> {
       let mut f = File::open("username.txt")?;
       let mut s = String::new();
       f.read_to_string(&mut s)?;
       Ok(s)
   }

   // 链式调用
   fn read_username_v3() -> Result<String, io::Error> {
       let mut s = String::new();
       File::open("username.txt")?.read_to_string(&mut s)?;
       Ok(s)
   }

   // 最简洁（标准库提供）
   fn read_username_v4() -> Result<String, io::Error> {
       std::fs::read_to_string("username.txt")
   }

**? 的工作原理**：如果 ``Result`` 是 ``Ok``，取出内部值继续；如果是 ``Err``，
调用 ``From`` trait 的 ``from`` 函数转换错误类型，然后 ``return Err(转换后的错误)``。

自定义错误类型
^^^^^^^^^^^^^^

在实际项目中，你通常需要定义自己的错误类型来统一处理各种可能的错误：

.. code-block:: rust

   use std::fmt;
   use std::io;
   use std::num;

   // 自定义错误枚举
   #[derive(Debug)]
   enum AppError {
       Io(io::Error),
       Parse(num::ParseIntError),
       Custom(String),
   }

   // 实现 Display trait（用于给用户看的错误信息）
   impl fmt::Display for AppError {
       fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
           match self {
               AppError::Io(e) => write!(f, "IO 错误: {}", e),
               AppError::Parse(e) => write!(f, "解析错误: {}", e),
               AppError::Custom(msg) => write!(f, "自定义错误: {}", msg),
           }
       }
   }

   // 实现 From trait（让 ? 运算符自动转换错误类型）
   impl From<io::Error> for AppError {
       fn from(e: io::Error) -> Self {
           AppError::Io(e)
       }
   }

   impl From<num::ParseIntError> for AppError {
       fn from(e: num::ParseIntError) -> Self {
           AppError::Parse(e)
       }
   }

   // 现在可以使用 ? 自动转换错误
   fn process_file(path: &str) -> Result<i32, AppError> {
       let content = std::fs::read_to_string(path)?; // io::Error -> AppError
       let number: i32 = content.trim().parse()?;     // ParseIntError -> AppError
       Ok(number * 2)
   }

``From`` trait 与错误转换
^^^^^^^^^^^^^^^^^^^^^^^^^

``From`` trait 是 ``?`` 运算符自动转换错误的核心机制：

.. code-block:: rust

   // 标准库定义：
   // trait From<T> {
   //     fn from(value: T) -> Self;
   // }

   // 当 ? 用于 Result 时：
   // 如果返回类型是 Result<_, E>，
   // 且 ? 作用于 Result<_, F>（其中 F != E），
   // 编译器会尝试调用 E::from(f) 来转换。

   use std::num::ParseIntError;

   #[derive(Debug)]
   struct MyError(String);

   impl From<ParseIntError> for MyError {
       fn from(e: ParseIntError) -> Self {
           MyError(format!("解析失败: {}", e))
       }
   }

   fn parse_two(s1: &str, s2: &str) -> Result<(i32, i32), MyError> {
       let a = s1.parse::<i32>()?; // ParseIntError -> MyError
       let b = s2.parse::<i32>()?; // ParseIntError -> MyError
       Ok((a, b))
   }

anyhow 和 thiserror crate
^^^^^^^^^^^^^^^^^^^^^^^^^

在实践中，手写错误类型比较繁琐。社区有两个流行的错误处理 crate：

**thiserror**：简化自定义错误类型的定义（用于库）。

.. code-block:: rust

   // Cargo.toml: thiserror = "1"
   use thiserror::Error;

   #[derive(Error, Debug)]
   enum AppError {
       #[error("IO 错误: {0}")]
       Io(#[from] std::io::Error),

       #[error("解析错误: {0}")]
       Parse(#[from] std::num::ParseIntError),

       #[error("自定义错误: {msg}")]
       Custom { msg: String },
   }

   // #[from] 自动生成 From 实现，让 ? 正常工作

**anyhow**：提供 ``anyhow::Result`` 和 ``anyhow::Error``，适合应用程序（不适合库）。

.. code-block:: rust

   // Cargo.toml: anyhow = "1"
   use anyhow::{Context, Result, bail, ensure};

   fn read_config(path: &str) -> Result<Config> {
       let content = std::fs::read_to_string(path)
           .context(format!("无法读取配置文件: {}", path))?;

       let config: Config = toml::from_str(&content)
           .context("配置文件格式错误")?;

       ensure!(config.port > 0, "端口号必须大于 0");

       if config.name.is_empty() {
           bail!("配置名称不能为空");
       }

       Ok(config)
   }

**选择建议**：

- 写**库**：用 ``thiserror`` 定义精确的错误类型
- 写**应用**：用 ``anyhow`` 快速处理各种错误

错误传播模式
^^^^^^^^^^^^

**模式一：层层传播，顶层处理**

.. code-block:: rust

   // 底层：返回具体错误
   fn read_data(path: &str) -> Result<String, io::Error> {
       std::fs::read_to_string(path)
   }

   // 中间层：传播 + 可能转换
   fn parse_data(path: &str) -> Result<Vec<i32>, AppError> {
       let content = read_data(path)?;  // io::Error -> AppError
       let numbers = content.lines()
           .map(|line| line.parse::<i32>())
           .collect::<Result<Vec<_>, _>>()?;  // ParseIntError -> AppError
       Ok(numbers)
   }

   // 顶层：处理所有错误
   fn main() {
       match parse_data("data.txt") {
           Ok(nums) => println!("数据: {:?}", nums),
           Err(e) => eprintln!("错误: {}", e),
       }
   }

**模式二：map_err 添加上下文**

.. code-block:: rust

   use std::fs;

   fn load_user(id: u32) -> Result<User, String> {
       let path = format!("users/{}.json", id);
       let content = fs::read_to_string(&path)
           .map_err(|e| format!("无法读取用户文件 {}: {}", path, e))?;

       let user: User = serde_json::from_str(&content)
           .map_err(|e| format!("用户数据格式错误: {}", e))?;

       Ok(user)
   }

常用数据结构
------------

String 与 &str
^^^^^^^^^^^^^^

这是 Rust 中最容易混淆的概念之一。

**String**：拥有数据的可变字符串，存储在堆上。

.. code-block:: rust

   let mut s = String::from("hello");
   s.push_str(" world");  // 可以修改
   // s 离开作用域时，堆上的内存被自动释放

**&str**：字符串切片，是对某处数据的**借用**。

.. code-block:: rust

   let s: &str = "hello";  // 字符串字面量，数据在程序二进制中
   let s2: &str = &String::from("world")[..];  // 借用 String 的一部分

**类比**：

- ``String`` = 你买的房子（拥有，可以装修）
- ``&str`` = 你租的房子（借用，不能拆墙）

**转换**：

.. code-block:: rust

   // &str -> String
   let s1: String = "hello".to_string();
   let s2: String = String::from("hello");
   let s3: String = "hello".to_owned();

   // String -> &str
   let s: String = String::from("hello");
   let slice: &str = &s;        // 自动解引用
   let slice2: &str = s.as_str(); // 显式转换

**函数参数选择**：

.. code-block:: rust

   // 如果只需要读取，用 &str（接受 &str 和 &String）
   fn greet(name: &str) {
       println!("Hello, {}!", name);
   }

   // 如果需要获取所有权，用 String
   fn store_name(name: String) {
       database.save(name);
   }

   // 如果既需要读取又可能需要存储，用 impl Into<String>
   fn flexible(name: impl Into<String>) {
       let name: String = name.into();
       // ...
   }

Vec<T>
^^^^^^

动态数组，所有元素类型相同，存储在堆上。

.. code-block:: rust

   fn main() {
       // 创建
       let mut v: Vec<i32> = Vec::new();
       let v2 = vec![1, 2, 3]; // 宏创建

       // 增
       v.push(1);
       v.push(2);
       v.extend([3, 4, 5]); // 批量添加

       // 删
       v.pop();            // 移除最后一个，返回 Option<T>
       v.remove(0);        // 移除指定索引，O(n) 操作
       v.retain(|&x| x > 2); // 保留满足条件的元素

       // 改
       v[0] = 10;         // 可能 panic（越界）
       if let Some(elem) = v.get_mut(0) {
           *elem = 10;    // 安全访问
       }

       // 查
       let first = v.first();         // Option<&T>
       let last = v.last();           // Option<&T>
       let found = v.iter().find(|&&x| x == 3); // Option<&T>

       // 遍历
       for item in &v {
           println!("{}", item);
       }
       for item in &mut v {
           *item *= 2;
       }

       // 排序
       v.sort();           // 原地排序
       v.sort_unstable();  // 更快但不保证相等元素顺序
       v.dedup();          // 去除连续重复元素
   }

HashMap<K, V>
^^^^^^^^^^^^^

哈希表，键值对存储。

.. code-block:: rust

   use std::collections::HashMap;

   fn main() {
       let mut scores: HashMap<String, i32> = HashMap::new();

       // 插入
       scores.insert("Alice".to_string(), 95);
       scores.insert("Bob".to_string(), 87);

       // 查询
       let alice_score = scores.get("Alice"); // Option<&i32>

       // 更新
       scores.entry("Alice".to_string()).and_modify(|e| *e += 5);
       scores.entry("Charlie".to_string()).or_insert(90); // 不存在才插入

       // 遍历
       for (name, score) in &scores {
           println!("{}: {}", name, score);
       }

       // 从迭代器构建
       let names = vec!["Alice", "Bob", "Charlie"];
       let ages = vec![25, 30, 35];
       let people: HashMap<&str, i32> = names.into_iter().zip(ages).collect();
   }

Option<T>
^^^^^^^^^

表示"可能有值，可能没有"。用 ``Option`` 代替 ``null``。

.. code-block:: rust

   fn main() {
       let x: Option<i32> = Some(42);
       let y: Option<i32> = None;

       // 安全解包
       match x {
           Some(v) => println!("有值: {}", v),
           None => println!("无值"),
       }

       // 链式操作
       let result = x
           .map(|v| v * 2)       // Some(84)
           .filter(|&v| v > 50)  // Some(84)
           .unwrap_or(0);        // 84

       // unwrap 和 expect（确定有值时使用，否则 panic）
       let value = x.unwrap();           // 42
       let value = x.expect("应该有值"); // 42
       // let value = y.unwrap();         // panic!

       // 组合子
       let a: Option<i32> = Some(1);
       let b: Option<i32> = Some(2);
       let sum = a.and_then(|x| b.map(|y| x + y)); // Some(3)
   }

Box<T>
^^^^^^

``Box<T>`` 将数据分配在堆上，栈上只保留一个指针。

**类比**：栈上数据像放在桌上的文件，``Box`` 像把文件锁进保险柜（堆），手里只拿钥匙（指针）。

.. code-block:: rust

   fn main() {
       // 基本使用
       let b = Box::new(5);
       println!("b = {}", b); // 自动解引用

       // 递归类型（编译器需要知道大小）
       enum List {
           Cons(i32, Box<List>),  // Box 让编译器知道大小
           Nil,
       }

       use List::{Cons, Nil};
       let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));

       // 大数据避免栈溢出
       let big_array = Box::new([0u8; 1_000_000]); // 1MB 在堆上

       // trait 对象（多态）
       let animals: Vec<Box<dyn std::fmt::Display>> = vec![
           Box::new("猫"),
           Box::new(42),
           Box::new(3.14),
       ];
       for animal in &animals {
           println!("{}", animal);
       }
   }

**何时使用 Box**：

- 递归类型（编译器需要知道大小）
- 大数据避免栈溢出
- trait 对象（动态分发）
- 转移所有权时减少复制

Rc<T> 和 Arc<T>
^^^^^^^^^^^^^^^^

引用计数智能指针，实现**共享所有权**。

**Rc<T>**（单线程）：

.. code-block:: rust

   use std::rc::Rc;

   fn main() {
       let a = Rc::new(5);
       let b = Rc::clone(&a);  // 引用计数 +1
       let c = Rc::clone(&a);  // 引用计数 +1

       println!("引用计数: {}", Rc::strong_count(&a)); // 3
       println!("a = {}, b = {}, c = {}", a, b, c);

       drop(c);  // 引用计数 -1
       println!("引用计数: {}", Rc::strong_count(&a)); // 2
   }

**Arc<T>**（多线程，原子引用计数）：

.. code-block:: rust

   use std::sync::Arc;
   use std::thread;

   fn main() {
       let data = Arc::new(vec![1, 2, 3]);
       let mut handles = vec![];

       for i in 0..3 {
           let data = Arc::clone(&data);
           handles.push(thread::spawn(move || {
               println!("线程 {}: {:?}", i, data);
           }));
       }

       for handle in handles {
           handle.join().unwrap();
       }
   }

**Rc vs Arc**：

- ``Rc``：更快（非原子操作），但**不能**跨线程
- ``Arc``：稍慢（原子操作），但**可以**跨线程

**类比**：``Rc`` 像办公室共用的文件（只能在办公室内传阅），``Arc`` 像加密云文档（可以安全地跨部门共享）。

Cell<T> 和 RefCell<T>
^^^^^^^^^^^^^^^^^^^^^

内部可变性（Interior Mutability）：即使有不可变引用，也能修改内部数据。

**Cell<T>**（适用于 Copy 类型）：

.. code-block:: rust

   use std::cell::Cell;

   struct Counter {
       count: Cell<i32>,
   }

   impl Counter {
       fn increment(&self) {  // 注意：&self，不是 &mut self
           self.count.set(self.count.get() + 1);
       }

       fn get(&self) -> i32 {
           self.count.get()
       }
   }

   fn main() {
       let counter = Counter { count: Cell::new(0) };
       counter.increment();
       counter.increment();
       println!("计数: {}", counter.get()); // 2
   }

**RefCell<T>**（适用于非 Copy 类型）：

.. code-block:: rust

   use std::cell::RefCell;

   fn main() {
       let data = RefCell::new(vec![1, 2, 3]);

       // 运行时借用检查（编译时检查不够用时）
       {
           let mut borrowed = data.borrow_mut(); // 可变借用
           borrowed.push(4);
       } // borrowed 离开作用域，借用结束

       let borrowed = data.borrow(); // 不可变借用
       println!("{:?}", *borrowed);  // [1, 2, 3, 4]
   }

**安全规则**：

- ``RefCell`` 在运行时检查借用规则
- 违反规则会 panic（而不是编译错误）
- 同样遵守：要么一个可变借用，要么多个不可变借用

**常见组合**：``Rc<RefCell<T>>`` 实现多个所有者共享可变数据。

.. code-block:: rust

   use std::cell::RefCell;
   use std::rc::Rc;

   fn main() {
       let shared_data = Rc::new(RefCell::new(vec![1, 2, 3]));

       let clone1 = Rc::clone(&shared_data);
       let clone2 = Rc::clone(&shared_data);

       clone1.borrow_mut().push(4);
       clone2.borrow_mut().push(5);

       println!("{:?}", shared_data.borrow()); // [1, 2, 3, 4, 5]
   }

BTreeMap 和 BTreeSet
^^^^^^^^^^^^^^^^^^^^

基于 B 树的有序集合，按键排序存储。

.. code-block:: rust

   use std::collections::{BTreeMap, BTreeSet};

   fn main() {
       // BTreeMap：有序键值对
       let mut map = BTreeMap::new();
       map.insert(3, "三");
       map.insert(1, "一");
       map.insert(2, "二");

       // 自动按键排序遍历
       for (key, value) in &map {
           println!("{}: {}", key, value); // 一, 二, 三
       }

       // 范围查询
       let range: Vec<_> = map.range(1..=2).collect();
       println!("范围查询: {:?}", range);

       // BTreeSet：有序集合
       let mut set = BTreeSet::new();
       set.insert(3);
       set.insert(1);
       set.insert(2);

       let min = set.iter().next();     // Some(&1)
       let max = set.iter().next_back(); // Some(&3)
   }

**HashMap vs BTreeMap**：

- ``HashMap``：O(1) 查找，无序，更常用
- ``BTreeMap``：O(log n) 查找，有序，支持范围查询

VecDeque
^^^^^^^^

双端队列，头部和尾部操作都是 O(1)。

.. code-block:: rust

   use std::collections::VecDeque;

   fn main() {
       let mut deque = VecDeque::new();

       // 两端操作
       deque.push_back(1);   // 尾部添加
       deque.push_back(2);
       deque.push_front(0);  // 头部添加

       deque.pop_front();    // 头部移除 -> Some(0)
       deque.pop_back();     // 尾部移除 -> Some(2)

       // 作为 FIFO 队列使用
       let mut queue = VecDeque::new();
       queue.push_back("任务1");
       queue.push_back("任务2");
       queue.push_back("任务3");

       while let Some(task) = queue.pop_front() {
           println!("处理: {}", task);
       }

       // 环形缓冲区
       let mut buffer = VecDeque::with_capacity(3);
       for i in 0..5 {
           if buffer.len() == buffer.capacity() {
               buffer.pop_front(); // 移除最旧的
           }
           buffer.push_back(i);
       }
       println!("缓冲区: {:?}", buffer); // [2, 3, 4]
   }

并发
----

Rust 的并发模型核心理念：**编译时防止数据竞争**。

**比喻**：传统语言的并发像多个人同时编辑同一份文档（可能冲突），
Rust 的并发像严格的图书馆借阅系统——要么多人只读（共享引用），一人可写（可变引用）。

Send 和 Sync traits
^^^^^^^^^^^^^^^^^^^^

这两个 marker trait 是 Rust 并发安全的基石：

- **Send**：如果 ``T: Send``，则 ``T`` 的实例可以安全地**发送到**其他线程
- **Sync**：如果 ``T: Sync``，则 ``&T`` 可以安全地**共享给**多个线程

.. code-block:: rust

   // 几乎所有类型都自动实现 Send 和 Sync
   // 例外：Rc<T> 不是 Send（非原子引用计数）
   //       Cell<T>、RefCell<T> 不是 Sync（非线程安全内部可变性）

   use std::rc::Rc;
   use std::thread;

   fn main() {
       let data = Rc::new(5);
       // 编译错误！Rc<i32> 没有实现 Send
       // thread::spawn(move || {
       //     println!("{}", data);
       // });

       // 使用 Arc 替代
       use std::sync::Arc;
       let data = Arc::new(5);
       thread::spawn(move || {
           println!("{}", data); // OK，Arc 实现了 Send
       }).join().unwrap();
   }

**规则**：

- 包含 ``Rc``、``Cell``、``RefCell`` 的类型**不是** ``Send``
- 包含 ``Rc``、``Cell``、``RefCell`` 的类型**不是** ``Sync``
- ``Mutex<T>`` 是 ``Sync``（即使 ``T`` 不是）
- ``Arc<T>`` 是 ``Send + Sync``（当 ``T: Send + Sync``）

线程基础
^^^^^^^^

.. code-block:: rust

   use std::thread;
   use std::time::Duration;

   fn main() {
       // 基本线程
       let handle = thread::spawn(|| {
           for i in 1..=5 {
               println!("子线程: {}", i);
               thread::sleep(Duration::from_millis(100));
           }
       });

       // 主线程继续执行
       for i in 1..=3 {
           println!("主线程: {}", i);
           thread::sleep(Duration::from_millis(150));
       }

       // 等待子线程结束
       handle.join().unwrap();

       // move 闭包：转移所有权到新线程
       let data = vec![1, 2, 3];
       let handle = thread::spawn(move || {
           println!("数据: {:?}", data);
       });
       handle.join().unwrap();
   }

Arc + Mutex：共享可变状态
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rust

   use std::sync::{Arc, Mutex};
   use std::thread;

   fn main() {
       let counter = Arc::new(Mutex::new(0));
       let mut handles = vec![];

       for _ in 0..10 {
           let counter = Arc::clone(&counter);
           let handle = thread::spawn(move || {
               let mut num = counter.lock().unwrap();
               *num += 1;
           });
           handles.push(handle);
       }

       for handle in handles {
           handle.join().unwrap();
       }

       println!("结果: {}", *counter.lock().unwrap()); // 10
   }

**lock() 的行为**：

- 返回 ``MutexGuard``（智能指针）
- ``MutexGuard`` 实现了 ``Deref`` 和 ``Drop``
- 离开作用域时自动释放锁（RAII）

**类比**：``Mutex`` 像会议室——一次只能一个人进去（锁住），用完自动出来（释放）。

Channel (mpsc)：消息传递
^^^^^^^^^^^^^^^^^^^^^^^^^

多生产者，单消费者的消息通道。

.. code-block:: rust

   use std::sync::mpsc;
   use std::thread;
   use std::time::Duration;

   fn main() {
       // 创建通道
       let (tx, rx) = mpsc::channel();

       // 生产者线程
       thread::spawn(move || {
           let messages = vec!["你好", "来自", "另一个", "线程"];
           for msg in messages {
               tx.send(msg.to_string()).unwrap();
               thread::sleep(Duration::from_millis(200));
           }
           // tx 被 drop 时，通道关闭
       });

       // 消费者（主线程）
       for received in rx {
           println!("收到: {}", received);
       }

       // 多生产者
       let (tx, rx) = mpsc::channel();
       for i in 0..3 {
           let tx = tx.clone();
           thread::spawn(move || {
               tx.send(format!("消息 {}", i)).unwrap();
           });
       }
       drop(tx); // 关闭原始发送端

       let messages: Vec<String> = rx.iter().collect();
       println!("所有消息: {:?}", messages);
   }

**类比**：Channel 像传送带——生产者把消息放上去，消费者从另一端取下来。

RwLock<T>
^^^^^^^^^

读写锁：允许多个读者**或**一个写者。

.. code-block:: rust

   use std::sync::{Arc, RwLock};
   use std::thread;

   fn main() {
       let data = Arc::new(RwLock::new(vec![1, 2, 3]));
       let mut handles = vec![];

       // 多个读者可以同时读
       for i in 0..3 {
           let data = Arc::clone(&data);
           handles.push(thread::spawn(move || {
               let read_guard = data.read().unwrap();
               println!("读者 {}: {:?}", i, *read_guard);
           }));
       }

       // 写者独占
       {
           let data = Arc::clone(&data);
           handles.push(thread::spawn(move || {
               let mut write_guard = data.write().unwrap();
               write_guard.push(4);
               println!("写者: {:?}", *write_guard);
           }));
       }

       for handle in handles {
           handle.join().unwrap();
       }
   }

**Mutex vs RwLock**：

- ``Mutex``：任何时候只允许一个访问者（简单，开销低）
- ``RwLock``：允许多读或一写（读多写少时更高效）

Atomic Types
^^^^^^^^^^^^

原子类型提供无锁的线程安全操作。

.. code-block:: rust

   use std::sync::atomic::{AtomicUsize, AtomicBool, Ordering};
   use std::sync::Arc;
   use std::thread;

   fn main() {
       let counter = Arc::new(AtomicUsize::new(0));
       let flag = Arc::new(AtomicBool::new(false));
       let mut handles = vec![];

       for _ in 0..10 {
           let counter = Arc::clone(&counter);
           handles.push(thread::spawn(move || {
               // 原子加法，无需锁
               counter.fetch_add(1, Ordering::SeqCst);
           }));
       }

       for handle in handles {
           handle.join().unwrap();
       }

       println!("计数: {}", counter.load(Ordering::SeqCst));

       // Ordering 选项：
       // Relaxed - 最宽松，只保证原子性
       // Acquire - 读取时使用，防止后续读写重排到此之前
       // Release - 写入时使用，防止之前的读写重排到此之后
       // SeqCst  - 最严格，所有操作全局有序（默认推荐）
   }

**何时使用**：

- 简单计数器、标志位：用原子类型（最快）
- 复杂数据结构：用 ``Mutex`` 或 ``RwLock``
- 需要保证顺序：用 ``SeqCst`` Ordering

Rayon 数据并行
^^^^^^^^^^^^^^

Rayon 是 Rust 最流行的数据并行库，将顺序迭代器变为并行。

.. code-block:: rust

   // Cargo.toml: rayon = "1"
   use rayon::prelude::*;

   fn main() {
       let numbers: Vec<i64> = (1..=1_000_000).collect();

       // 顺序版本
       let sum_sequential: i64 = numbers.iter().sum();

       // 并行版本（只需把 iter() 改为 par_iter()）
       let sum_parallel: i64 = numbers.par_iter().sum();

       assert_eq!(sum_sequential, sum_parallel);

       // 并行 map
       let squares: Vec<i64> = numbers.par_iter()
           .map(|&x| x * x)
           .collect();

       // 并行 filter + reduce
       let big_sum: i64 = numbers.par_iter()
           .filter(|&&x| x % 2 == 0)
           .sum();

       // 并行排序
       let mut data = vec![5, 3, 1, 4, 2];
       data.par_sort();
       println!("排序: {:?}", data);
   }

**原理**：Rayon 使用工作窃取（work-stealing）算法，自动将任务分配到线程池中。

**适用场景**：大数据集的 CPU 密集型操作（排序、搜索、数学计算）。
**不适用**：IO 密集型操作（网络、磁盘）或小数据集（线程调度开销大于收益）。

Trait
-----

Trait 定义了类型共享的行为，类似其他语言的接口，但更强大。

**比喻**：Trait 像职业资格证书——拥有"会计师"证书（``Display`` trait）的人（类型）
都可以做账（格式化输出），不管他是男是女（不管具体类型是什么）。

Trait 定义与实现
^^^^^^^^^^^^^^^^

.. code-block:: rust

   // 定义 trait
   trait Summary {
       fn summarize(&self) -> String;

       // 默认实现（可选覆盖）
       fn preview(&self) -> String {
           let s = self.summarize();
           if s.len() > 20 {
               format!("{}...", &s[..20])
           } else {
               s
           }
       }
   }

   struct Article {
       title: String,
       content: String,
   }

   struct Tweet {
       username: String,
       content: String,
   }

   // 为 Article 实现 trait
   impl Summary for Article {
       fn summarize(&self) -> String {
           format!("{}: {}", self.title, self.content)
       }
   }

   // 为 Tweet 实现 trait（使用默认 preview）
   impl Summary for Tweet {
       fn summarize(&self) -> String {
           format!("@{}: {}", self.username, self.content)
       }
   }

   fn main() {
       let article = Article {
           title: "Rust 入门".to_string(),
           content: "Rust 是一门系统编程语言...".to_string(),
       };
       let tweet = Tweet {
           username: "rustacean".to_string(),
           content: "今天学了 Rust！".to_string(),
       };

       println!("{}", article.summarize());
       println!("{}", tweet.preview()); // 使用默认实现
   }

Trait Bounds 与 where 子句
^^^^^^^^^^^^^^^^^^^^^^^^^^

限定泛型参数必须实现某些 trait：

.. code-block:: rust

   // 基本 trait bound
   fn print_summary<T: Summary>(item: &T) {
       println!("{}", item.summarize());
   }

   // 多个 trait bound（+ 语法）
   fn print_and_display<T: Summary + std::fmt::Display>(item: &T) {
       println!("{}", item);  // Display
       println!("{}", item.summarize()); // Summary
   }

   // where 子句（更清晰）
   fn complex_function<T, U>(t: &T, u: &U) -> String
   where
       T: Summary + Clone,
       U: Summary + std::fmt::Debug,
   {
       format!("{:?} - {}", u, t.summarize())
   }

Static Dispatch 与 Dynamic Dispatch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Static Dispatch (``impl Trait``)**：编译时确定具体类型，生成专用代码。

.. code-block:: rust

   // 编译器为每个具体类型生成一个函数副本
   fn notify(item: &impl Summary) {
       println!("突发新闻: {}", item.summarize());
   }

   // 等价于泛型写法
   fn notify2<T: Summary>(item: &T) {
       println!("突发新闻: {}", item.summarize());
   }

**Dynamic Dispatch (``dyn Trait``)**：运行时通过虚表（vtable）查找方法。

.. code-block:: rust

   // trait 对象：运行时多态
   fn notify_dynamic(item: &dyn Summary) {
       println!("突发新闻: {}", item.summarize());
   }

   fn main() {
       let article = Article { /* ... */ };
       let tweet = Tweet { /* ... */ };

       // 可以存储不同类型
       let items: Vec<Box<dyn Summary>> = vec![
           Box::new(article),
           Box::new(tweet),
       ];

       for item in &items {
           println!("{}", item.summarize());
       }
   }

**选择**：

- ``impl Trait`` / 泛型：性能更好（内联优化），但不能混合不同类型
- ``dyn Trait``：灵活（可以存储不同类型），但有虚表查找开销

Associated Types
^^^^^^^^^^^^^^^^

关联类型让 trait 的实现者指定具体类型：

.. code-block:: rust

   trait Iterator {
       type Item;  // 关联类型

       fn next(&mut self) -> Option<Self::Item>;
   }

   struct Counter {
       count: u32,
       max: u32,
   }

   impl Iterator for Counter {
       type Item = u32;  // 指定具体类型

       fn next(&mut self) -> Option<Self::Item> {
           if self.count < self.max {
               self.count += 1;
               Some(self.count)
           } else {
               None
           }
       }
   }

   fn main() {
       let mut counter = Counter { count: 0, max: 5 };
       while let Some(n) = counter.next() {
           println!("{}", n); // 1, 2, 3, 4, 5
       }
   }

**关联类型 vs 泛型参数**：

- 每个类型对 trait 的关联类型只能有一种实现（一对一）
- 泛型参数可以有多种实现（一对多，如 ``From<A>`` 和 ``From<B>``）

常用标准 Trait
^^^^^^^^^^^^^^

**Debug 和 Display**：

.. code-block:: rust

   use std::fmt;

   #[derive(Debug)] // 自动派生 Debug
   struct Point {
       x: f64,
       y: f64,
   }

   // 手动实现 Display
   impl fmt::Display for Point {
       fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
           write!(f, "({}, {})", self.x, self.y)
       }
   }

   fn main() {
       let p = Point { x: 1.0, y: 2.0 };
       println!("{:?}", p);  // Point { x: 1.0, y: 2.0 }（调试用）
       println!("{}", p);    // (1, 2)（用户友好）
   }

**Clone 和 Copy**：

.. code-block:: rust

   #[derive(Debug, Clone)]  // Clone：显式深拷贝
   struct Data {
       values: Vec<i32>,
   }

   #[derive(Debug, Clone, Copy)]  // Copy：隐式复制（要求所有字段也实现 Copy）
   struct Point {
       x: f64,
       y: f64,
   }

   fn main() {
       let data1 = Data { values: vec![1, 2, 3] };
       let data2 = data1.clone();  // 显式克隆
       // let data3 = data1;        // Move，data1 失效

       let p1 = Point { x: 1.0, y: 2.0 };
       let p2 = p1;   // Copy，p1 仍然有效
       let p3 = p1;   // 可以继续 Copy
       println!("{:?} {:?} {:?}", p1, p2, p3);
   }

**From 和 Into**：

.. code-block:: rust

   struct Celsius(f64);
   struct Fahrenheit(f64);

   // 实现 From（自动获得 Into）
   impl From<Celsius> for Fahrenheit {
       fn from(c: Celsius) -> Self {
           Fahrenheit(c.0 * 9.0 / 5.0 + 32.0)
       }
   }

   fn main() {
       let boiling = Celsius(100.0);

       let f1: Fahrenheit = Fahrenheit::from(Celsius(100.0)); // 显式
       let f2: Fahrenheit = Celsius(100.0).into();            // Into（自动获得）

       // 用于函数参数
       fn set_thermostat(temp: impl Into<Fahrenheit>) {
           let f: Fahrenheit = temp.into();
           println!("设置温度: {}°F", f.0);
       }

       set_thermostat(Celsius(25.0)); // 自动转换
   }

Orphan Rule
^^^^^^^^^^^

**规则**：你只能在以下情况下为类型实现 trait：

1. Trait 是你定义的（如 ``Summary``），**或者**
2. 类型是你定义的（如 ``MyStruct``）

.. code-block:: rust

   // OK：你定义的 trait + 标准库类型
   impl Summary for String { /* ... */ }

   // OK：标准库 trait + 你定义的类型
   impl std::fmt::Display for MyStruct { /* ... */ }

   // 错误：标准库 trait + 标准库类型（两边都不是你的）
   // impl std::fmt::Display for Vec<i32> { /* ... */ }

**解决方案：Newtype 模式**：

.. code-block:: rust

   struct Wrapper(Vec<String>);

   // 现在可以为 Wrapper 实现标准 trait
   impl std::fmt::Display for Wrapper {
       fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
           write!(f, "[{}]", self.0.join(", "))
       }
   }

异步编程
--------

Rust 的异步编程让你用少量线程处理大量并发 IO 操作。

**比喻**：同步编程像排队打饭——一个人打完才轮到下一个人。
异步编程像叫号系统——你拿了号可以先去做别的事，叫到你了再去取餐。

async/await 语法
^^^^^^^^^^^^^^^^

.. code-block:: rust

   // async fn 返回一个 Future
   async fn fetch_data(url: &str) -> Result<String, reqwest::Error> {
       let response = reqwest::get(url).await?; // .await 暂停当前任务
       let body = response.text().await?;
       Ok(body)
   }

   // 等价于返回 impl Future<Output = Result<String, reqwest::Error>>
   fn fetch_data_explicit(url: &str) -> impl std::future::Future<Output = Result<String, reqwest::Error>> + '_ {
       async move {
           let response = reqwest::get(url).await?;
           let body = response.text().await?;
           Ok(body)
       }
   }

**关键点**：

- ``async fn`` 不会立即执行，它返回一个 ``Future``
- ``.await`` 会暂停当前任务，让出线程给其他任务
- Future 只有在被 ``.await`` 或 spawn 时才会执行

Future Trait 基础
^^^^^^^^^^^^^^^^^

``Future`` 是 Rust 异步编程的核心 trait：

.. code-block:: rust

   // 简化的 Future trait（标准库定义）
   trait Future {
       type Output;
       fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
   }

   enum Poll<T> {
       Ready(T),    // Future 完成，返回结果
       Pending,     // Future 未完成，稍后再试
   }

**工作原理**：

1. 运行时调用 ``poll()`` 检查 Future 是否完成
2. 如果 ``Pending``，运行时会安排以后再检查
3. 如果 ``Ready(T)``, 返回结果

你通常不需要手动实现 ``Future``，``async/await`` 语法会自动生成。

Tokio Runtime
^^^^^^^^^^^^^

Tokio 是 Rust 最流行的异步运行时。

.. code-block:: rust

   // Cargo.toml: tokio = { version = "1", features = ["full"] }

   use tokio::time::{sleep, Duration};

   async fn hello() {
       println!("开始");
       sleep(Duration::from_secs(1)).await;
       println!("一秒后");
   }

   #[tokio::main] // 宏：设置 Tokio 运行时
   async fn main() {
       // 并发执行多个 Future
       let (r1, r2) = tokio::join!(
           hello(),
           hello(),
       );

       // spawn 创建独立任务
       let handle = tokio::spawn(async {
           sleep(Duration::from_millis(100)).await;
           42
       });
       let result = handle.await.unwrap();
       println!("结果: {}", result);

       // select! 等待第一个完成
       tokio::select! {
           _ = sleep(Duration::from_secs(1)) => println!("一秒到了"),
           _ = sleep(Duration::from_secs(2)) => println!("两秒到了"),
       }
   }

Pin 和 Unpin
^^^^^^^^^^^^

``Pin`` 确保值不会在内存中移动，这对自引用结构很重要。

.. code-block:: rust

   use std::pin::Pin;
   use std::future::Future;

   // 大多数类型是 Unpin 的，可以安全移动
   fn move_unpin<T: Unpin>(value: &mut T) {
       // 可以安全移动
   }

   // Pin<&mut T> 确保 T 不会被移动
   fn pinned_operation<F: Future>(future: Pin<&mut F>) {
       // future 保证不会被移动
   }

**为什么需要 Pin**：``async`` 块编译后会生成自引用结构体（一个字段引用另一个字段）。
如果结构体被移动，自引用就会变成悬垂指针。``Pin`` 防止这种移动。

**实际使用中**：大多数时候你不需要直接处理 ``Pin``。``tokio::spawn`` 和 ``.await``
会自动处理 ``Pin``。只有在手动实现 ``Future`` 或处理 ``!Unpin`` 类型时才需要关注。

async vs threads：何时用哪个
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: rust

   // 用 async：大量 IO 操作（网络、文件、数据库）
   async fn fetch_many_urls(urls: Vec<&str>) -> Vec<String> {
       let mut handles = vec![];
       for url in urls {
           handles.push(tokio::spawn(async move {
               reqwest::get(url).await.unwrap().text().await.unwrap()
           }));
       }
       let mut results = vec![];
       for handle in handles {
           results.push(handle.await.unwrap());
       }
       results
   }

   // 用线程：CPU 密集型计算
   fn parallel_compute(data: Vec<i32>) -> Vec<i32> {
       use rayon::prelude::*;
       data.par_iter().map(|&x| expensive_computation(x)).collect()
   }

**选择指南**：

+---------------------+---------------------------+---------------------------+
| 场景                | 推荐                      | 原因                      |
+=====================+===========================+===========================+
| 大量网络请求        | async + tokio             | 一个线程处理成千上万连接  |
+---------------------+---------------------------+---------------------------+
| 文件 IO             | async + tokio             | 非阻塞等待磁盘            |
+---------------------+---------------------------+---------------------------+
| CPU 密集计算        | 线程 + rayon              | 利用多核并行计算          |
+---------------------+---------------------------+---------------------------+
| 两者混合            | async 中 spawn_blocking   | 计算任务不阻塞异步运行时  |
+---------------------+---------------------------+---------------------------+

模块系统与项目结构
------------------

Rust 的模块系统控制代码的组织和可见性。

**比喻**：Crate 像一栋大楼，Module 像楼里的楼层，pub 像门上的"开放"标志。

mod、pub、use
^^^^^^^^^^^^^^

.. code-block:: rust

   // src/lib.rs 或 src/main.rs

   // 定义模块
   mod network {
       pub fn connect() {
           println!("连接到网络");
           helper::log("已连接");  // 同 crate 内可以访问私有模块
       }

       // 子模块（私有）
       mod helper {
           pub fn log(msg: &str) {
               println!("[LOG] {}", msg);
           }
       }

       // 公开子模块
       pub mod protocol {
           pub fn http_get(url: &str) -> String {
               format!("GET {}", url)
           }
       }
   }

   // 使用 use 导入
   use network::connect;
   use network::protocol::http_get;

   // 或者用路径
   fn main() {
       network::connect();
       let response = network::protocol::http_get("https://example.com");
   }

**可见性规则**：

- ``pub``：对外公开
- ``pub(crate)``：只在当前 crate 内可见
- ``pub(super)``：只在父模块可见
- ``pub(in path)``：只在指定路径内可见
- 无标记：只在当前模块内可见

文件层级
^^^^^^^^

.. code-block:: text

   my_project/
   ├── Cargo.toml
   └── src/
       ├── main.rs          // 二进制 crate 入口
       ├── lib.rs           // 库 crate 入口
       ├── config.rs        // mod config
       ├── config/          // 或者用文件夹
       │   ├── mod.rs       // config 模块的入口
       │   └── parser.rs    // config::parser
       └── network/
           ├── mod.rs       // network 模块的入口
           ├── tcp.rs       // network::tcp
           └── udp.rs       // network::udp

Cargo.toml 配置
^^^^^^^^^^^^^^^

.. code-block:: toml

   [package]
   name = "my_project"
   version = "0.1.0"
   edition = "2021"
   authors = ["Your Name <email@example.com>"]
   description = "项目描述"
   license = "MIT"

   [dependencies]
   # 基本依赖
   serde = "1"
   serde_json = "1"

   # 带 feature 的依赖
   tokio = { version = "1", features = ["full"] }

   # Git 依赖
   my_lib = { git = "https://github.com/user/repo", branch = "main" }

   # 本地路径依赖
   utils = { path = "../utils" }

   # 条件依赖
   [target.'cfg(windows)'.dependencies]
   winapi = "0.3"

   [dev-dependencies]  # 只在测试和 bench 中使用
   criterion = "0.5"

   [build-dependencies]  # 只在构建脚本中使用
   cc = "1"

   [features]
   default = ["json"]
   json = ["serde", "serde_json"]
   xml = ["quick-xml"]
   full = ["json", "xml"]

   [profile.release]
   opt-level = 3       # 最大优化
   lto = true          # 链接时优化
   codegen-units = 1   # 单编译单元（更慢但更优化）

Workspace 多 Crate 项目
^^^^^^^^^^^^^^^^^^^^^^^

Workspace 让多个相关的 crate 共享同一个 ``Cargo.lock`` 和 ``target`` 目录。

.. code-block:: text

   workspace/
   ├── Cargo.toml          // Workspace 根
   ├── Cargo.lock          // 共享锁文件
   ├── target/             // 共享构建目录
   ├── crates/
   │   ├── core/
   │   │   ├── Cargo.toml
   │   │   └── src/lib.rs
   │   ├── api/
   │   │   ├── Cargo.toml
   │   │   └── src/lib.rs
   │   └── cli/
   │       ├── Cargo.toml
   │       └── src/main.rs
   └── Cargo.toml

.. code-block:: toml

   # workspace/Cargo.toml（根）
   [workspace]
   members = [
       "crates/core",
       "crates/api",
       "crates/cli",
   ]

   # crates/api/Cargo.toml
   [package]
   name = "api"
   version = "0.1.0"

   [dependencies]
   core = { path = "../core" }  # 引用 workspace 内的 crate

**优势**：

- 统一管理依赖版本
- 一次编译所有 crate
- 共享构建缓存（减少编译时间）

宏
--

宏是 Rust 的元编程工具，在编译时生成代码。

**比喻**：函数像厨师做菜（接收食材，按固定流程烹饪）。
宏像菜谱生成器（根据你的需求，自动生成一整套做菜步骤）。

声明式宏 (macro_rules!)
^^^^^^^^^^^^^^^^^^^^^^^^

用模式匹配和代码替换来生成代码。

.. code-block:: rust

   // 基本宏：创建 HashMap
   macro_rules! hashmap {
       // 匹配 key => value 对
       ( $( $key:expr => $value:expr ),* $(,)? ) => {
           {
               let mut map = std::collections::HashMap::new();
               $(
                   map.insert($key, $value);
               )*
               map
           }
       };
   }

   fn main() {
       let scores = hashmap! {
           "Alice" => 95,
           "Bob" => 87,
           "Charlie" => 92,
       };
       println!("{:?}", scores);
   }

   // 更复杂的宏：自定义 vec
   macro_rules! my_vec {
       // 空 vec
       () => {
           Vec::new()
       };
       // 带初始值
       ( $( $x:expr ),+ $(,)? ) => {
           {
               let mut v = Vec::new();
               $(
                   v.push($x);
               )*
               v
           }
       };
       // 重复值：value; count
       ( $x:expr ; $count:expr ) => {
           vec![$x; $count]
       };
   }

   // 自动实现 trait 的宏
   macro_rules! impl_display {
       ( $type:ty, $fmt:expr ) => {
           impl std::fmt::Display for $type {
               fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
                   write!(f, $fmt, self)
               }
           }
       };
   }

**宏的模式语法**：

- ``$x:expr``：匹配一个表达式
- ``$x:ty``：匹配一个类型
- ``$x:ident``：匹配一个标识符
- ``$x:tt``：匹配一个 token tree
- ``$(...)  *``：零次或多次
- ``$(...) +``：一次或多次
- ``$(...) ?``：零次或一次

过程宏简介
^^^^^^^^^^

过程宏是更强大的宏系统，操作的是 Rust 语法树（TokenStream）。

**三种类型**：

**1. Derive 宏**：自动为结构体/枚举实现 trait。

.. code-block:: rust

   // 使用（常见）
   #[derive(Debug, Clone, Serialize, Deserialize)]
   struct User {
       name: String,
       age: u32,
   }

   // 定义（需要单独的 proc-macro crate）
   // my_macro/src/lib.rs
   use proc_macro::TokenStream;

   #[proc_macro_derive(MyTrait)]
   pub fn my_trait_derive(input: TokenStream) -> TokenStream {
       // 解析输入的代码，生成 impl MyTrait for StructName
       // ...
       TokenStream::new()
   }

**2. Attribute 宏**：为函数/结构体添加自定义属性。

.. code-block:: rust

   // 使用
   #[route(GET, "/users")]
   fn get_users() -> String {
       "Users".to_string()
   }

   // 定义
   #[proc_macro_attribute]
   pub fn route(attr: TokenStream, item: TokenStream) -> TokenStream {
       // attr: GET, "/users"
       // item: fn get_users() -> String { ... }
       // 生成路由注册代码
       item
   }

**3. Function-like 宏**：看起来像函数调用。

.. code-block:: rust

   // 使用
   let sql = sql!(SELECT * FROM users WHERE id = 1);

   // 定义
   #[proc_macro]
   pub fn sql(input: TokenStream) -> TokenStream {
       // 解析 SQL 语法，生成 Rust 代码
       // 可以在编译时检查 SQL 语法
       input
   }

**何时使用宏**：

- 需要减少样板代码（``#[derive]``）
- 需要编译时代码生成（ORM、Web 框架路由）
- 需要编译时检查（SQL、HTML 模板）
- 普通函数和泛型无法实现的场景

**何时不用宏**：

- 函数能解决的问题（宏是最后手段）
- 需要良好 IDE 支持的场景（宏可能影响代码补全）
- 团队对宏不熟悉（宏降低可读性）

附录：常用 Cargo 命令
---------------------

.. code-block:: bash

   # 创建项目
   cargo new my_project --bin     # 二进制项目
   cargo new my_lib --lib         # 库项目

   # 构建和运行
   cargo build                    # 调试构建
   cargo build --release          # 发布构建（优化）
   cargo run                      # 构建并运行
   cargo run -- arg1 arg2         # 传递参数

   # 测试
   cargo test                     # 运行所有测试
   cargo test test_name           # 运行匹配名称的测试
   cargo test -- --nocapture      # 显示 println! 输出

   # 文档
   cargo doc --open               # 生成并打开文档

   # 检查和格式化
   cargo check                    # 快速语法检查（不生成二进制）
   cargo fmt                      # 格式化代码
   cargo clippy                   # Lint 检查

   # 依赖管理
   cargo add serde --features derive  # 添加依赖
   cargo update                       # 更新依赖
   cargo tree                         # 查看依赖树

   # 发布
   cargo publish                    # 发布到 crates.io
   cargo package                    # 打包但不发布
