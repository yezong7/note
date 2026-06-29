C 语言参考手册
==============

本文档是一份全面的 C 语言参考手册，涵盖运算符、指针与数组、内存布局、大小端、
GCC 编译流程、预处理器、函数指针应用、位操作、进程间通信、常用函数以及经典编程题。
每个知识点均配有原理说明、代码示例和易懂的类比。


运算符与优先级
--------------

C 语言的运算符优先级决定了表达式的求值顺序。可以把它想象成数学中的"先乘除、后加减"
——C 语言有更细粒度的优先级规则。优先级数字越小，优先级越高。

^^^^^^^^^^^^^^^^
优先级总览表
^^^^^^^^^^^^^^^^

+----------+-----------------------------+----------+-------------------+
| 优先级   | 运算符                      | 结合性   | 含义              |
+==========+=============================+==========+===================+
| 1        | ``()``  ``[]``  ``->``  ``.`` | 左→右    | 括号、下标、成员  |
+----------+-----------------------------+----------+-------------------+
| 2        | ``!``  ``~``  ``++``  ``--`` | 右→左    | 单目运算          |
|          | ``(type)``  ``*``  ``&``     |          |                   |
|          | ``sizeof``                   |          |                   |
+----------+-----------------------------+----------+-------------------+
| 3        | ``*``  ``/``  ``%``          | 左→右    | 乘、除、取模      |
+----------+-----------------------------+----------+-------------------+
| 4        | ``+``  ``-``                 | 左→右    | 加、减            |
+----------+-----------------------------+----------+-------------------+
| 5        | ``<<``  ``>>``               | 左→右    | 左移、右移        |
+----------+-----------------------------+----------+-------------------+
| 6        | ``<``  ``<=``  ``>``  ``>=`` | 左→右    | 关系比较          |
+----------+-----------------------------+----------+-------------------+
| 7        | ``==``  ``!=``               | 左→右    | 相等、不等        |
+----------+-----------------------------+----------+-------------------+
| 8        | ``&``                        | 左→右    | 按位与            |
+----------+-----------------------------+----------+-------------------+
| 9        | ``^``                        | 左→右    | 按位异或          |
+----------+-----------------------------+----------+-------------------+
| 10       | ``|``                        | 左→右    | 按位或            |
+----------+-----------------------------+----------+-------------------+
| 11       | ``&&``                       | 左→右    | 逻辑与            |
+----------+-----------------------------+----------+-------------------+
| 12       | ``||``                       | 左→右    | 逻辑或            |
+----------+-----------------------------+----------+-------------------+
| 13       | ``?:``                       | 右→左    | 三目条件          |
+----------+-----------------------------+----------+-------------------+
| 14       | ``=``  ``+=``  ``-=``  等    | 右→左    | 赋值              |
+----------+-----------------------------+----------+-------------------+
| 15       | ``,``                        | 左→右    | 逗号              |
+----------+-----------------------------+----------+-------------------+

^^^^^^^^^^^^^^^^
逐级详解与示例
^^^^^^^^^^^^^^^^

**第 1 级：括号、下标、成员（左→右）**

这三个运算符的优先级最高，就像数学中括号一定最先算。

.. code-block:: c

   #include <stdio.h>

   struct Point {
       int x;
       int y;
   };

   int main() {
       int arr[5] = {10, 20, 30, 40, 50};
       struct Point p = {3, 4};

       // [] 下标运算：访问数组第 2 个元素
       printf("arr[2] = %d\n", arr[2]);     // 输出 30

       // . 成员运算：访问结构体成员
       printf("p.x = %d\n", p.x);           // 输出 3

       // () 括号运算：强制改变优先级
       int result = (2 + 3) * 4;              // 先算 2+3=5，再乘 4 = 20
       printf("result = %d\n", result);       // 输出 20

       return 0;
   }

**第 2 级：单目运算符（右→左）**

单目运算符只作用于一个操作数。结合方向从右向左，意味着连续的单目运算符从最右边开始计算。
想象穿衣服：先穿最里面的（最右边的），再穿外面的。

.. code-block:: c

   #include <stdio.h>

   int main() {
       int a = 5;

       // ++ 自增：前置先加后用，后置先用后加
       int b = ++a;   // a 先变为 6，b = 6
       int c = a++;    // c = 6（先用），a 再变为 7
       printf("a=%d, b=%d, c=%d\n", a, b, c);  // a=7, b=6, c=6

       // -- 自减：同理
       int d = 10;
       int e = --d;    // d 先变为 9，e = 9
       printf("d=%d, e=%d\n", d, e);            // d=9, e=9

       // ~ 按位取反：每个 bit 翻转（0变1，1变0）
       unsigned char x = 0x0F;   // 0000 1111
       unsigned char y = ~x;     // 1111 0000 = 0xF0
       printf("~0x0F = 0x%02X\n", y);           // 输出 F0

       // & 取地址运算符：获取变量的内存地址
       int val = 42;
       int *p = &val;            // p 存储 val 的地址
       printf("val 的地址: %p, 值: %d\n", (void*)p, *p);

       // * 解引用运算符：通过地址访问值
       *p = 100;                 // 通过指针修改 val 的值
       printf("val = %d\n", val);               // 输出 100

       // ! 逻辑非：真变假，假变真
       int flag = 0;
       printf("!0 = %d, !1 = %d\n", !flag, !5); // 输出 1, 0

       // sizeof 计算类型或变量占用的字节数
       printf("int: %zu 字节\n", sizeof(int));       // 通常为 4
       printf("double: %zu 字节\n", sizeof(double));  // 通常为 8

       return 0;
   }

   // 右→左结合示例：
   // **pp 等价于 *(*pp)，先解引用最右边的 *，再解引用左边的 *
   // &*p  等价于 &(*p)，先解引用 p 得到值，再取该值的地址（结果还是 p）

**第 3 级：乘、除、取模（左→右）**

.. code-block:: c

   int a = 20 / 3;      // 整数除法，结果为 6（截断小数）
   int b = 20 % 3;      // 取模（取余），结果为 2
   int c = 3 * 4;       // 乘法，结果为 12

   // 易错点：整数除法会截断
   double d = 20 / 3;    // d = 6.0，不是 6.666...（因为两边都是 int）
   double e = 20.0 / 3;  // e = 6.666...（至少一边是浮点数）

   // 取模只能用于整数
   // double f = 20.0 % 3;  // 编译错误！

**第 4 级：加、减（左→右）**

.. code-block:: c

   int sum = 10 + 20;    // 30
   int diff = 30 - 15;   // 15

   // 指针加减：移动的字节数取决于类型大小
   int arr[5] = {10, 20, 30, 40, 50};
   int *p = arr;         // p 指向 arr[0]
   p = p + 2;            // p 现在指向 arr[2]，跳过了 2 个 int（8 字节）
   printf("*p = %d\n", *p);  // 输出 30

**第 5 级：移位（左→右）**

移位运算相当于乘以或除以 2 的 n 次方。左移 n 位 = 乘以 2^n，右移 n 位 = 除以 2^n。

.. code-block:: c

   int a = 1 << 3;   // 0001 → 1000，等于 8（1 * 2^3）
   int b = 16 >> 2;  // 10000 → 00100，等于 4（16 / 2^2）

   // 实际应用：用移位代替乘除法提高效率
   int x = 100;
   int y = x << 1;   // y = 200（相当于 x * 2）
   int z = x >> 2;   // z = 25（相当于 x / 4）

   // 警告：对负数右移是未定义行为（取决于编译器实现）
   // 对有符号数左移可能溢出

**第 6 级：关系比较（左→右）**

.. code-block:: c

   int a = 5, b = 10;
   if (a < b)  printf("a 小于 b\n");
   if (a <= b) printf("a 小于等于 b\n");
   if (a > b)  printf("a 大于 b\n");      // 不会执行
   if (a >= b) printf("a 大于等于 b\n");  // 不会执行

**第 7 级：相等与不等（左→右）**

.. code-block:: c

   int a = 5;
   if (a == 5) printf("相等\n");    // 注意是 == 不是 =
   if (a != 3) printf("不等\n");

   // 易错点：== 写成 = 是最常见的 bug
   // if (a = 5)   // 这是赋值，永远为真！
   // if (a == 5)  // 这才是比较

   // 浮点数不要用 == 比较，因为精度问题
   double d1 = 0.1 + 0.2;
   double d2 = 0.3;
   // if (d1 == d2)  // 可能为假！
   // 正确做法：比较差值是否足够小
   if ((d1 - d2) < 1e-9 && (d1 - d2) > -1e-9)
       printf("近似相等\n");

**第 8~10 级：按位与、异或、或（左→右）**

这三个运算符对整数的每一个二进制位进行操作，就像两排开关逐个对比。

.. code-block:: c

   unsigned int a = 0x0F;   // 0000 1111
   unsigned int b = 0x33;   // 0011 0011

   // 按位 AND：两位都为 1 才为 1
   unsigned int c = a & b;  // 0000 0011 = 0x03
   printf("a & b = 0x%02X\n", c);

   // 按位 XOR：两位不同才为 1
   unsigned int d = a ^ b;  // 0011 1100 = 0x3C
   printf("a ^ b = 0x%02X\n", d);

   // 按位 OR：至少一位为 1 就为 1
   unsigned int e = a | b;  // 0011 1111 = 0x3F
   printf("a | b = 0x%02X\n", e);

**第 11~12 级：逻辑与、逻辑或（左→右）**

逻辑运算符用于布尔判断，结果只有 0（假）或 1（真）。重要特性：**短路求值**。

.. code-block:: c

   int a = 0, b = 5;

   // && 逻辑与：两边都为真才为真，左边为假则右边不执行（短路）
   if (a != 0 && b / a > 2) {
       // a 为 0，a != 0 为假，短路，b / a 不会执行（避免除零错误）
   }

   // || 逻辑或：至少一边为真就为真，左边为真则右边不执行（短路）
   if (a == 0 || b / a > 2) {
       // a == 0 为真，短路，b / a 不会执行
   }

   // 短路求值的实际用途：空指针检查
   int *p = NULL;
   if (p != NULL && *p > 0) {
       // 先检查 p 是否为空，为空则短路，不会解引用空指针
   }

**第 13 级：三目条件运算符（右→左）**

三目运算符是 if-else 的简写形式，像一个"岔路口"：条件为真走左边，为假走右边。

.. code-block:: c

   int a = 10, b = 20;
   int max = (a > b) ? a : b;   // 条件为真取 a，否则取 b
   printf("max = %d\n", max);    // 输出 20

   // 等价于：
   // int max;
   // if (a > b) max = a;
   // else max = b;

   // 可以嵌套（但不建议太深，影响可读性）
   int x = 0;
   const char *msg = (x > 0) ? "正数" : (x < 0) ? "负数" : "零";
   printf("%s\n", msg);  // 输出 "零"

**第 14 级：赋值运算符（右→左）**

赋值运算符的结合方向从右向左，意味着连续赋值从最右边开始。

.. code-block:: c

   // 基本赋值
   int a = 10;

   // 复合赋值运算符
   a += 5;   // a = a + 5   → 15
   a -= 3;   // a = a - 3   → 12
   a *= 2;   // a = a * 2   → 24
   a /= 4;   // a = a / 4   → 6
   a %= 5;   // a = a % 5   → 1
   a <<= 3;  // a = a << 3  → 8
   a >>= 1;  // a = a >> 1  → 4
   a &= 0x0F; // a = a & 0x0F
   a ^= 0xFF; // a = a ^ 0xFF
   a |= 0x10; // a = a | 0x10

   // 右→左结合：连续赋值
   int x, y, z;
   x = y = z = 100;  // 从右往左：z=100, y=z=100, x=y=100

**第 15 级：逗号运算符（左→右）**

逗号运算符从左向右依次求值，整个表达式的值为最后一个子表达式的值。
可以把逗号运算符想象成"一条指令流水线"：依次执行每一步，最终结果取最后一步的值。

.. code-block:: c

   int a, b;
   a = (1, 2, 3);    // 依次求值 1、2、3，a = 3（最后一个）
   b = (a++, a + 10); // 先 a++（a 变为 4），再 a+10 = 14，b = 14

   // 常见用法：在 for 循环中同时操作多个变量
   for (int i = 0, j = 10; i < j; i++, j--) {
       printf("i=%d, j=%d\n", i, j);
   }


指针与数组
----------

指针和数组是 C 语言的核心，也是最难理解的部分。简单来说：

- **数组**就像一排连续的储物柜，每个柜子存一个值。
- **指针**就像一张写着储物柜编号的纸条，告诉你去哪里找东西。

^^^^^^^^^^^^^^^^
1. 数组
^^^^^^^^^^^^^^^^

数组是一段**连续的内存空间**，存储相同类型的元素。就像一排编了号的储物柜，
编号从 0 开始。

.. code-block:: c

   #include <stdio.h>

   int main() {
       // 声明并初始化一个包含 4 个 int 的数组
       int a[4] = {1, 2, 3, 4};

       // 内存布局（假设 int 占 4 字节，起始地址 0x1000）：
       // 地址    值
       // 0x1000  1    ← a[0]
       // 0x1004  2    ← a[1]
       // 0x1008  3    ← a[2]
       // 0x100C  4    ← a[3]

       // 数组名 a 在大多数情况下会"退化"为指向首元素的指针
       // 即 a 等价于 &a[0]，类型为 int*
       printf("a = %p, &a[0] = %p\n", (void*)a, (void*)&a[0]);
       // 两个地址相同

       // 遍历数组
       for (int i = 0; i < 4; i++) {
           printf("a[%d] = %d\n", i, a[i]);
       }

       // 数组大小
       printf("数组占用 %zu 字节\n", sizeof(a));     // 16（4 个 int）
       printf("单个元素 %zu 字节\n", sizeof(a[0]));   // 4

       // 计算元素个数
       int count = sizeof(a) / sizeof(a[0]);  // 16 / 4 = 4
       printf("元素个数: %d\n", count);

       return 0;
   }

^^^^^^^^^^^^^^^^
2. 指针
^^^^^^^^^^^^^^^^

指针是一个变量，它存储的是**另一个变量的内存地址**。就像一张写着"储物柜 A-03"的纸条，
纸条本身不是东西，但它告诉你去哪里找东西。

.. code-block:: c

   #include <stdio.h>

   int main() {
       int a[4] = {1, 2, 3, 4};

       // 声明一个指向 int 的指针，指向数组首地址
       int *p = a;      // 等价于 int *p = &a[0];

       // 通过指针访问数组元素的三种方式：
       printf("方式1: *p = %d\n", *p);           // 1，解引用
       printf("方式2: *(p+2) = %d\n", *(p+2));   // 3，指针算术
       printf("方式3: p[1] = %d\n", p[1]);       // 2，下标（本质就是 *(p+1)）

       // 指针移动
       p++;              // p 向后移动一个 int 的大小（4 字节）
       printf("p++ 后: *p = %d\n", *p);  // 2

       // 指针相减：得到两个指针之间的元素个数
       int *start = &a[0];
       int *end = &a[3];
       ptrdiff_t diff = end - start;    // 3
       printf("间隔 %td 个元素\n", diff);

       // 空指针：不指向任何有效地址
       int *np = NULL;
       // *np = 10;  // 段错误！解引用空指针是未定义行为

       return 0;
   }

^^^^^^^^^^^^^^^^
3. 数组指针（指向数组的指针）
^^^^^^^^^^^^^^^^

数组指针的含义是：**整个数组的地址**。注意，虽然数组首地址的值和首元素地址的值相同，
但它们的类型不同，指针算术行为也不同。

类比：数组首元素地址是"第一间房的门牌号"，数组指针是"整栋楼的门牌号"。

.. code-block:: c

   #include <stdio.h>

   int main() {
       int arr[5] = {10, 20, 30, 40, 50};

       // 声明一个数组指针：指向包含 5 个 int 的数组
       int (*arr_ptr)[5] = &arr;

       // arr_ptr 的类型是 int(*)[5]，指向整个数组
       // arr       的类型是 int*，指向第一个元素

       // 通过数组指针访问元素
       printf("arr_ptr[0][2] = %d\n", (*arr_ptr)[2]);  // 30

       // 数组指针的真正用途：二维数组
       int matrix[3][4] = {
           {1,  2,  3,  4},
           {5,  6,  7,  8},
           {9, 10, 11, 12}
       };

       // matrix[0] 的类型是 int[4]，所以 matrix 的类型是 int(*)[4]
       // 可以用数组指针来遍历二维数组的每一行
       int (*row_ptr)[4] = matrix;   // 指向第一行

       for (int i = 0; i < 3; i++) {
           for (int j = 0; j < 4; j++) {
               printf("%3d ", row_ptr[i][j]);
           }
           printf("\n");
       }

       // 指针算术：row_ptr + 1 跳过一整行（4 个 int = 16 字节）
       printf("第二行首元素: %d\n", (*(row_ptr + 1))[0]);  // 5

       return 0;
   }

^^^^^^^^^^^^^^^^
4. 指针数组（存储指针的数组）
^^^^^^^^^^^^^^^^

指针数组是一个数组，其中每个元素都是一个指针。就像一排储物柜，
每个柜子里放的不是物品本身，而是一张写着"东西在别处"的纸条。

.. code-block:: c

   #include <stdio.h>

   int main() {
       int a = 10, b = 20, c = 30;

       // 声明一个包含 3 个 int* 的数组
       int *ptr_arr[3] = {&a, &b, &c};

       // 内存布局：
       // ptr_arr[0] → &a → 10
       // ptr_arr[1] → &b → 20
       // ptr_arr[2] → &c → 30

       for (int i = 0; i < 3; i++) {
           printf("ptr_arr[%d] 指向的值: %d\n", i, *ptr_arr[i]);
       }

       // 指针数组最常见的用途：字符串数组
       const char *names[] = {
           "Alice",
           "Bob",
           "Charlie"
       };

       for (int i = 0; i < 3; i++) {
           printf("名字: %s\n", names[i]);
       }

       // 二维字符数组 vs 指针数组的区别：
       // char matrix[3][10]  → 3行×10列的连续内存，每行固定10字节
       // char *arr[3]        → 3个指针，每个指向不同的字符串（长度可不同）

       return 0;
   }

^^^^^^^^^^^^^^^^
5. 函数指针
^^^^^^^^^^^^^^^^

函数指针是一个变量，它存储的是**函数的入口地址**。就像一张写着"去某某办公室找某某人办事"的条子。

函数指针让你可以把"做什么事"作为参数传递，实现灵活的回调机制。

.. code-block:: c

   #include <stdio.h>

   // 定义两个简单的函数
   int add(int a, int b) { return a + b; }
   int sub(int a, int b) { return a - b; }

   int main() {
       // 声明一个函数指针：指向"接受两个 int，返回 int"的函数
       int (*func_ptr)(int, int);

       // 指向 add 函数
       func_ptr = add;
       printf("add(3, 4) = %d\n", func_ptr(3, 4));  // 7

       // 指向 sub 函数
       func_ptr = sub;
       printf("sub(3, 4) = %d\n", func_ptr(3, 4));  // -1

       // 用 typedef 简化函数指针类型
       typedef int (*operation_t)(int, int);
       operation_t ops[] = {add, sub};

       const char *names[] = {"add", "sub"};
       for (int i = 0; i < 2; i++) {
           printf("%s(10, 3) = %d\n", names[i], ops[i](10, 3));
       }

       return 0;
   }

^^^^^^^^^^^^^^^^
6. 指针函数（返回指针的函数）
^^^^^^^^^^^^^^^^

指针函数是指**返回值为指针的函数**。注意：绝对不要返回局部变量的地址，
因为局部变量在函数返回后就被销毁了。

类比：指针函数就像一个"快递员"，帮你去仓库取东西并告诉你地址。但如果仓库拆了（局部变量销毁），
给你的地址就没用了。

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>

   // 正确：返回堆内存的地址（调用者负责 free）
   int *create_array(int size) {
       int *arr = (int *)malloc(size * sizeof(int));
       if (arr == NULL) return NULL;

       for (int i = 0; i < size; i++) {
           arr[i] = i * 10;
       }
       return arr;
   }

   // 正确：返回静态变量的地址（但要注意不是线程安全的）
   int *get_static_value(void) {
       static int val = 42;
       return &val;
   }

   // 错误示例（不要这样做）：
   // int *bad_function(void) {
   //     int local = 100;
   //     return &local;    // 局部变量，函数返回后无效！
   // }

   int main() {
       int *arr = create_array(5);
       if (arr != NULL) {
           for (int i = 0; i < 5; i++) {
               printf("arr[%d] = %d\n", i, arr[i]);
           }
           free(arr);  // 必须释放
       }

       int *p = get_static_value();
       printf("静态值: %d\n", *p);

       return 0;
   }

^^^^^^^^^^^^^^^^
7. 双指针（指向指针的指针）
^^^^^^^^^^^^^^^^

双指针存储的是**一个指针变量的地址**。通过双指针可以修改指针本身的指向。

类比：如果普通指针是"写着柜子编号的纸条"，双指针就是"写着纸条所在位置的纸条"——
你可以通过它换掉原来的纸条。

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>

   // 通过双指针修改调用者的指针
   void allocate(int **pp, int size) {
       *pp = (int *)malloc(size * sizeof(int));
       // *pp 改变了 main 中 p 的指向
   }

   int main() {
       // 基本用法
       int a = 10;
       int *p = &a;       // p 存储 a 的地址
       int **pp = &p;      // pp 存储 p 的地址

       printf("a = %d\n", a);         // 10
       printf("*p = %d\n", *p);       // 10（通过 p 访问 a）
       printf("**pp = %d\n", **pp);   // 10（通过 pp 访问 p，再访问 a）

       // 通过双指针修改指针的指向
       int b = 20;
       *pp = &b;           // 等价于 p = &b
       printf("*p = %d\n", *p);  // 20（p 现在指向 b）

       // 实际应用：函数内分配内存
       int *arr = NULL;
       allocate(&arr, 5);
       if (arr != NULL) {
           for (int i = 0; i < 5; i++) {
               arr[i] = i + 1;
               printf("arr[%d] = %d\n", i, arr[i]);
           }
           free(arr);
       }

       // 二维数组与双指针
       // 注意：int ** 不能直接指向 int[][]，两者的内存布局不同
       // 动态二维数组的正确做法：
       int rows = 3, cols = 4;
       int **matrix = (int **)malloc(rows * sizeof(int *));
       for (int i = 0; i < rows; i++) {
           matrix[i] = (int *)malloc(cols * sizeof(int));
       }
       // 使用...
       for (int i = 0; i < rows; i++) {
           free(matrix[i]);
       }
       free(matrix);

       return 0;
   }


内存布局
--------

一个 C 程序在内存中的布局就像一栋大楼，不同楼层有不同的用途。
理解内存布局对于避免内存泄漏、野指针和栈溢出至关重要。

^^^^^^^^^^^^^^^^
内存分区总览
^^^^^^^^^^^^^^^^

从低地址到高地址，程序的内存空间分为以下区域：

.. code-block:: text

   高地址 +-------------------+
          |    栈 (Stack)     | <- 函数调用信息、局部变量（向下增长）
          +-------------------+
          |       ...         |
          |   (栈和堆之间     |
          |    有较大的间隔)   |
          |       ...         |
          +-------------------+
          |    堆 (Heap)      | <- 动态分配内存（向上增长）
          +-------------------+
          |   BSS 段          | <- 未初始化的全局/静态变量（初始化为 0）
          +-------------------+
          |   data 段         | <- 已初始化的全局/静态变量
          +-------------------+
          |   rodata 段       | <- 字符串字面量、const 全局变量（只读）
          +-------------------+
          |   代码段 (.text)   | <- 程序指令（只读、可执行）
   低地址 +-------------------+

^^^^^^^^^^^^^^^^
栈空间（Stack）
^^^^^^^^^^^^^^^^

栈用于管理函数调用。每次调用函数时，会在栈上创建一个**栈帧**（Stack Frame），
包含函数的返回地址、参数、局部变量等。函数返回时，栈帧自动销毁。

就像叠盘子：后放的先取（LIFO，后进先出）。

.. code-block:: c

   #include <stdio.h>

   void func_b(int n) {
       int local_b = n * 2;   // 局部变量在栈上
       printf("func_b: local_b = %d\n", local_b);
   }  // local_b 在这里被销毁

   void func_a(int n) {
       int local_a = n + 1;   // 局部变量在栈上
       func_b(local_a);
       printf("func_a: local_a = %d\n", local_a);
   }  // local_a 在这里被销毁

   int main() {
       int x = 10;
       func_a(x);
       // 调用 func_a 时，栈帧：[main 栈帧][func_a 栈帧]
       // 调用 func_b 时，栈帧：[main 栈帧][func_a 栈帧][func_b 栈帧]
       // func_b 返回后：[main 栈帧][func_a 栈帧]
       // func_a 返回后：[main 栈帧]
       return 0;
   }

**栈溢出（Stack Overflow）**

栈空间有限（通常 1~8 MB），递归太深或局部数组太大会导致栈溢出。

.. code-block:: c

   // 危险：无限递归导致栈溢出
   // void infinite() { infinite(); }

   // 危险：局部数组过大
   // void big_array() {
   //     int arr[10000000];  // 约 40 MB，超过栈空间
   // }

   // 安全做法：大数组用堆分配
   void safe_big_array() {
       int *arr = (int *)malloc(10000000 * sizeof(int));
       // ... 使用 arr ...
       free(arr);
   }

^^^^^^^^^^^^^^^^
堆空间（Heap）
^^^^^^^^^^^^^^^^

堆用于动态内存分配。需要手动申请（malloc/calloc/realloc）和释放（free）。
堆空间比栈大得多，但管理不当会导致内存泄漏和碎片。

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>

   int main() {
       // malloc：分配指定字节数的内存（不初始化）
       int *p1 = (int *)malloc(5 * sizeof(int));

       // calloc：分配并初始化为 0
       int *p2 = (int *)calloc(5, sizeof(int));

       // realloc：调整已分配内存的大小
       p1 = (int *)realloc(p1, 10 * sizeof(int));

       // 使用完毕必须释放
       free(p1);
       free(p2);
       p1 = NULL;  // 好习惯：释放后置空，避免野指针
       p2 = NULL;

       return 0;
   }

**堆的常见问题：**

- **内存泄漏**：malloc 了但忘了 free
- **野指针**：free 后继续使用指针
- **重复释放**：对同一块内存 free 两次
- **内存碎片**：频繁分配释放不同大小的内存，导致堆空间碎片化

^^^^^^^^^^^^^^^^
BSS 段
^^^^^^^^^^^^^^^^

BSS（Block Started by Symbol）段存放**未初始化**或**初始化为 0** 的全局变量和静态变量。
程序加载时，系统自动将 BSS 段清零。

.. code-block:: c

   // BSS 段中的变量（程序启动时自动为 0）
   int global_uninit;           // 未初始化的全局变量
   int global_zero = 0;         // 初始化为 0 的全局变量
   static int static_uninit;    // 未初始化的静态局部变量

   #include <stdio.h>

   int main() {
       // 它们的初始值都是 0
       printf("global_uninit = %d\n", global_uninit);   // 0
       printf("global_zero = %d\n", global_zero);       // 0
       printf("static_uninit = %d\n", static_uninit);   // 0

       // 注意：局部变量不在 BSS 段，它们在栈上，不会自动初始化
       // int local;  // 未定义值，可能是任何数！

       return 0;
   }

^^^^^^^^^^^^^^^^
data 段
^^^^^^^^^^^^^^^^

data 段存放**已初始化**（非零）的全局变量和静态变量。这些值在程序加载时从可执行文件中读取。

.. code-block:: c

   // data 段中的变量（编译时就有确定的初始值）
   int global_init = 42;
   static int static_init = 100;
   char global_str[] = "hello";   // 字符数组内容在 data 段

   #include <stdio.h>

   int main() {
       static int local_static = 200;  // 静态局部变量也在 data 段
       printf("global_init = %d\n", global_init);
       printf("static_init = %d\n", static_init);
       printf("local_static = %d\n", local_static);
       return 0;
   }

^^^^^^^^^^^^^^^^
rodata 段（只读数据）
^^^^^^^^^^^^^^^^

rodata（Read-Only Data）段存放**字符串字面量**和 ``const`` 修饰的全局/静态变量。
尝试修改这些数据会导致段错误。

.. code-block:: c

   #include <stdio.h>

   // rodata 段中的数据
   const int MAX_SIZE = 1024;              // const 全局变量
   const char *greeting = "Hello, World!"; // 指针变量在 data 段，字符串本身在 rodata 段

   int main() {
       // 字符串字面量在 rodata 段
       printf("%s\n", "This is in rodata");

       // 尝试修改字符串字面量是未定义行为（通常段错误）
       // char *s = "hello";
       // s[0] = 'H';  // 崩溃！

       // 正确做法：用字符数组（内容在栈上，可以修改）
       char buf[] = "hello";
       buf[0] = 'H';   // 合法
       printf("%s\n", buf);  // "Hello"

       return 0;
   }

^^^^^^^^^^^^^^^^
代码段（.text）
^^^^^^^^^^^^^^^^

代码段存放程序的机器指令。通常是只读且可执行的，防止程序意外修改自身指令。

.. code-block:: c

   // 你写的每一行 C 代码，编译后都变成机器指令存在代码段
   int add(int a, int b) {    // add 函数的指令在代码段
       return a + b;
   }

   int main() {               // main 函数的指令在代码段
       int result = add(1, 2);
       return 0;
   }


大小端
------

大小端描述的是**多字节数据在内存中的字节排列顺序**。这个问题源于一个事实：
一个 32 位整数占 4 个字节，但这 4 个字节在内存中谁先谁后？

^^^^^^^^^^^^^^^^
什么是大端和小端
^^^^^^^^^^^^^^^^

以 32 位整数 ``0x12345678`` 为例（最高字节是 ``0x12``，最低字节是 ``0x78``）：

.. code-block:: text

   假设存储起始地址为 0x1000：

   大端序（Big-Endian）：低地址存高字节
   地址      0x1000  0x1001  0x1002  0x1003
   内容      0x12    0x34    0x56    0x78
   读起来从左到右：12 34 56 78，和人类书写顺序一致。

   小端序（Little-Endian）：低地址存低字节
   地址      0x1000  0x1001  0x1002  0x1003
   内容      0x78    0x56    0x34    0x12
   CPU 读取时，先读到低位字节，适合硬件直接做加法。

类比：假设你要把数字 1234 写在一张纸上。

- 大端序：从左到右写 1、2、3、4（人类的自然习惯）
- 小端序：从左到右写 4、3、2、1（倒着写）

^^^^^^^^^^^^^^^^
谁用大端，谁用小端
^^^^^^^^^^^^^^^^

- **大端序**：网络协议（TCP/IP 使用大端序，也叫**网络字节序**）、PowerPC、SPARC
- **小端序**：x86/x64（Intel、AMD）、ARM（默认小端，可配置）
- **双端**（可配置）：ARM、MIPS

^^^^^^^^^^^^^^^^
判断当前系统的大小端
^^^^^^^^^^^^^^^^

.. code-block:: c

   #include <stdio.h>

   // 方法 1：使用指针强制类型转换
   int is_little_endian(void) {
       int num = 1;              // 0x00000001
       char *p = (char *)&num;   // 取最低地址的字节
       return (*p == 1);         // 小端：最低地址存的是 0x01
   }

   // 方法 2：使用联合体（union）
   int is_little_endian_union(void) {
       union {
           int i;
           char c;
       } u;
       u.i = 1;
       return (u.c == 1);       // 小端：最低字节是 1
   }

   int main() {
       if (is_little_endian()) {
           printf("当前系统是小端序\n");
       } else {
           printf("当前系统是大端序\n");
       }
       return 0;
   }

^^^^^^^^^^^^^^^^
字节序转换函数
^^^^^^^^^^^^^^^^

网络编程中经常需要在主机字节序和网络字节序之间转换。这些函数定义在 ``<arpa/inet.h>`` 中。

.. code-block:: c

   #include <stdio.h>
   #include <arpa/inet.h>  // Linux/macOS
   // #include <winsock2.h>  // Windows

   int main() {
       uint32_t host_val = 0x12345678;

       // htonl: host to network long (32 位)
       uint32_t net_val = htonl(host_val);

       // htons: host to network short (16 位)
       uint16_t host_port = 8080;
       uint16_t net_port = htons(host_port);

       // ntohl: network to host long (32 位)
       uint32_t back = ntohl(net_val);

       // ntohs: network to host short (16 位)
       uint16_t back_port = ntohs(net_port);

       printf("主机序: 0x%08X\n", host_val);
       printf("网络序: 0x%08X\n", net_val);
       printf("转回来: 0x%08X\n", back);

       // 在小端系统上（如 x86）：
       // 0x12345678 → htonl → 0x78563412（字节反转）

       return 0;
   }

**记忆技巧：**

- ``h`` = host（主机），``n`` = network（网络），``l`` = long（32位），``s`` = short（16位）
- 主机是小端 → 网络是大端：转换就是反转字节序
- 主机是大端 → 网络是大端：转换是空操作（但仍然建议调用，保证可移植性）


GCC 编译流程
-------------

C 语言源代码从文本文件变成可执行程序，需要经过四个阶段。
可以把它想象成"翻译一篇外文文章"的四个步骤：先查缩写（预处理）、再翻译成草稿（编译）、
然后排版成正式文件（汇编）、最后装订成书（链接）。

^^^^^^^^^^^^^^^^
四步编译流程
^^^^^^^^^^^^^^^^

.. code-block:: text

   源文件        预处理         编译           汇编           链接
   demo.c  -->  demo.i  -->  demo.S  -->  demo.o  -->  demo
   (源代码)    (展开后)     (汇编代码)   (目标文件)   (可执行文件)

^^^^^^^^^^^^^^^^
各阶段详解
^^^^^^^^^^^^^^^^

**第 1 步：预处理（-E）**

处理所有 ``#`` 开头的指令：展开头文件、替换宏定义、处理条件编译。
结果是一个纯 C 代码文件（.i），没有 ``#include`` 和 ``#define``。

.. code-block:: bash

   # -E 只做预处理，结果输出到 demo.i
   gcc -E demo.c -o demo.i

   # demo.i 中会包含 stdio.h 的所有内容（可能有几万行）

**第 2 步：编译（-S）**

将预处理后的 C 代码翻译成**汇编代码**。这是最复杂的一步，
涉及词法分析、语法分析、语义分析、优化等。

.. code-block:: bash

   # -S 只编译到汇编代码，结果输出到 demo.S
   gcc -S demo.i -o demo.S

   # demo.S 中是汇编指令，如：
   #   movl $42, -4(%rbp)
   #   call printf

**第 3 步：汇编（-c）**

将汇编代码翻译成**机器码**，生成目标文件（.o）。目标文件包含机器指令和数据，
但其中的外部符号（如 printf）还未解析。

.. code-block:: bash

   # -c 只汇编，结果输出到 demo.o
   gcc -c demo.S -o demo.o

**第 4 步：链接**

将多个目标文件和库文件合并，解析所有外部符号的引用，生成最终的可执行文件。

.. code-block:: bash

   # 默认输出名为 a.out 的可执行文件
   gcc demo.o -o demo

   # 运行
   ./demo

^^^^^^^^^^^^^^^^
完整编译示例
^^^^^^^^^^^^^^^^

.. code-block:: c

   /* demo.c */
   #include <stdio.h>

   #define PI 3.14159

   int main() {
       double radius = 5.0;
       double area = PI * radius * radius;
       printf("半径 %.1f 的圆面积 = %.2f\n", radius, area);
       return 0;
   }

.. code-block:: bash

   # 一步到位（内部自动完成四步）
   gcc demo.c -o demo

   # 分步执行
   gcc -E demo.c -o demo.i    # 预处理
   gcc -S demo.i -o demo.S    # 编译
   gcc -c demo.S -o demo.o    # 汇编
   gcc demo.o -o demo          # 链接

^^^^^^^^^^^^^^^^
常用 GCC 参数
^^^^^^^^^^^^^^^^

.. code-block:: text

   +-------------+----------------------------------------------------+
   | 参数        | 说明                                                |
   +=============+====================================================+
   | -o <file>   | 指定输出文件名                                      |
   | -E          | 只预处理                                            |
   | -S          | 只编译到汇编                                        |
   | -c          | 只编译到目标文件                                    |
   | -O0         | 不优化（调试用）                                    |
   | -O1/-O2/-O3 | 优化级别，-O2 推荐生产环境，-O3 最激进优化          |
   | -Wall       | 开启所有常用警告                                    |
   | -Werror     | 将警告视为错误                                      |
   | -g          | 生成调试信息（gdb 需要）                            |
   | -std=c11    | 指定 C 语言标准（c89, c99, c11, c17）              |
   | -I<dir>     | 添加头文件搜索路径                                  |
   | -L<dir>     | 添加库文件搜索路径                                  |
   | -l<name>    | 链接指定库（如 -lm 链接 libm 数学库）              |
   | -rpath<path>| 指定运行时动态库搜索路径                            |
   | -fpic       | 生成位置无关代码（创建共享库时必需）                |
   | -shared     | 创建共享库（.so 文件）                              |
   | -static     | 静态链接（不依赖动态库，文件更大）                  |
   | -lm         | 链接数学库（math.h 中的函数）                       |
   | -pthread    | 链接 POSIX 线程库                                   |
   +-------------+----------------------------------------------------+

.. code-block:: bash

   # 常用组合示例

   # 调试版本：不开优化，包含调试信息
   gcc -O0 -g -Wall demo.c -o demo_debug

   # 发布版本：O2 优化，开启所有警告
   gcc -O2 -Wall -Werror demo.c -o demo_release

   # 使用 C11 标准编译，链接数学库
   gcc -std=c11 -Wall demo.c -o demo -lm

   # 指定头文件和库文件搜索路径
   gcc -I/usr/local/include -L/usr/local/lib -lmylib demo.c -o demo


预处理器
--------

预处理器在编译之前运行，处理所有以 ``#`` 开头的指令。
可以把它想象成"排版编辑"：在正式印刷（编译）之前，先把所有缩写展开、注释删除、
条件分支选好。

^^^^^^^^^^^^^^^^
#include：文件包含
^^^^^^^^^^^^^^^^

.. code-block:: c

   // 系统头文件用尖括号，在系统目录中搜索
   #include <stdio.h>
   #include <stdlib.h>

   // 自定义头文件用双引号，先在当前目录搜索，再到系统目录
   #include "myheader.h"

^^^^^^^^^^^^^^^^
#define：宏定义
^^^^^^^^^^^^^^^^

宏定义是简单的**文本替换**，在预处理阶段完成。编译器看到的代码已经是替换后的版本。

.. code-block:: c

   // 对象宏：简单的文本替换
   #define PI 3.14159265
   #define MAX_SIZE 1024

   // 函数宏：带参数的文本替换
   #define SQUARE(x) ((x) * (x))
   #define MAX(a, b) ((a) > (b) ? (a) : (b))
   #define MIN(a, b) ((a) < (b) ? (a) : (b))

   #include <stdio.h>

   int main() {
       double area = PI * 5.0 * 5.0;  // 替换为 3.14159265 * 5.0 * 5.0

       int x = 3;
       int sq = SQUARE(x);   // 替换为 ((x) * (x)) = (3 * 3) = 9

       // 易错点：宏是文本替换，不是函数调用
       int y = SQUARE(x++);  // 替换为 ((x++) * (x++))，x 被自增了两次！
                              // 这是未定义行为，应避免

       printf("PI = %f\n", PI);
       printf("sq = %d\n", sq);
       printf("MAX(3, 5) = %d\n", MAX(3, 5));

       return 0;
   }

**宏定义的括号为什么重要：**

.. code-block:: c

   // 错误的宏定义
   #define BAD_SQUARE(x) x * x

   // 当调用 BAD_SQUARE(3 + 1) 时：
   // 展开为 3 + 1 * 3 + 1 = 3 + 3 + 1 = 7（错误！应该是 16）

   // 正确的宏定义：每个参数和整个表达式都加括号
   #define GOOD_SQUARE(x) ((x) * (x))

   // GOOD_SQUARE(3 + 1) 展开为 ((3 + 1) * (3 + 1)) = 16（正确）

^^^^^^^^^^^^^^^^
条件编译
^^^^^^^^^^^^^^^^

条件编译允许根据条件决定哪些代码参与编译。常用于跨平台代码、调试开关、防止头文件重复包含。

.. code-block:: c

   // 防止头文件重复包含（方式一）
   #ifndef MYHEADER_H
   #define MYHEADER_H

   // 头文件内容...
   void my_function(void);

   #endif /* MYHEADER_H */

   // 防止头文件重复包含（方式二，更简洁，但非标准）
   #pragma once

   // 平台特定代码
   #ifdef _WIN32
       #include <windows.h>
       void platform_init() { /* Windows 初始化 */ }
   #elif defined(__linux__)
       #include <unistd.h>
       void platform_init() { /* Linux 初始化 */ }
   #elif defined(__APPLE__)
       #include <TargetConditionals.h>
       void platform_init() { /* macOS 初始化 */ }
   #endif

   // 调试开关
   #ifdef DEBUG
       #define LOG(fmt, ...) printf("[DEBUG] " fmt "\n", ##__VA_ARGS__)
   #else
       #define LOG(fmt, ...)  // 生产环境：日志宏展开为空
   #endif

^^^^^^^^^^^^^^^^
extern "C" 详解
^^^^^^^^^^^^^^^^

``extern "C"`` 是 C++ 中的指令，告诉编译器用 C 语言的规则来处理函数名。

**为什么需要它？**

C 和 C++ 对函数名的"标识方式"不同：

- **C 语言**：只用函数名作为符号标识。函数 ``int add(int, int)`` 的符号就是 ``add``。
- **C++**：用函数名 + 参数类型做符号标识（**名称修饰/Name Mangling**）。
  函数 ``int add(int, int)`` 的符号可能是 ``_Z3addii``。
  这就是 C++ 能支持**函数重载**的原因——同名但参数不同的函数有不同的符号。

问题在于：如果一个 C 库的函数 ``add`` 被 C++ 代码调用，C++ 编译器会去找 ``_Z3addii``，
但 C 库中只有 ``add``，链接时就会报"未定义的符号"错误。

.. code-block:: c

   /* mymath.h - 一个 C 语言的数学库头文件 */

   #ifndef MYMATH_H
   #define MYMATH_H

   #ifdef __cplusplus
   extern "C" {
   #endif

   // 告诉 C++ 编译器：这些函数用 C 的方式链接
   int add(int a, int b);
   int subtract(int a, int b);

   #ifdef __cplusplus
   }
   #endif

   #endif /* MYMATH_H */

.. code-block:: c

   /* mymath.c - 实现 */
   #include "mymath.h"

   int add(int a, int b) {
       return a + b;
   }

   int subtract(int a, int b) {
       return a - b;
   }

.. code-block:: cpp

   /* main.cpp - C++ 代码调用 C 库 */
   #include <stdio.h>
   #include "mymath.h"  // extern "C" 生效

   int main() {
       printf("add(3, 4) = %d\n", add(3, 4));  // 正确链接
       return 0;
   }

**编译命令：**

.. code-block:: bash

   # 先编译 C 库
   gcc -c mymath.c -o mymath.o

   # 再编译 C++ 主程序并链接
   g++ main.cpp mymath.o -o demo

**使用场景：**

- C++ 调用 C 语言编写的库（OpenSSL、SQLite、Linux 系统调用等）
- C++ 项目中需要暴露 C 兼容接口供其他语言调用


函数指针应用
------------

函数指针是 C 语言实现**多态**和**策略模式**的核心机制。
通过函数指针，你可以把"做什么"作为参数传递，实现灵活的代码设计。

^^^^^^^^^^^^^^^^
回调函数
^^^^^^^^^^^^^^^^

回调函数就像"约定好的回电"：你告诉对方"事情办完了打这个电话"，
对方办好后按你给的号码打回来。

.. code-block:: c

   #include <stdio.h>

   // 定义回调函数类型
   typedef void (*callback_t)(int result);

   // 模拟异步计算
   void compute(int a, int b, callback_t on_complete) {
       int result = a + b;
       // 计算完成后，调用回调函数
       on_complete(result);
   }

   // 用户定义的回调函数
   void print_result(int result) {
       printf("计算结果: %d\n", result);
   }

   void log_result(int result) {
       printf("[LOG] 结果已计算: %d\n", result);
   }

   int main() {
       compute(3, 4, print_result);   // 输出: 计算结果: 7
       compute(10, 20, log_result);   // 输出: [LOG] 结果已计算: 30
       return 0;
   }

^^^^^^^^^^^^^^^^
策略模式与路由表
^^^^^^^^^^^^^^^^

函数指针数组可以实现"命令路由表"——根据输入选择不同的处理函数。
就像电话总机：来电号码不同，接通不同的分机。

.. code-block:: c

   #include <stdio.h>

   // 定义操作函数类型
   typedef int (*operation_t)(int, int);

   int add(int a, int b) { return a + b; }
   int sub(int a, int b) { return a - b; }
   int mul(int a, int b) { return a * b; }
   int div_op(int a, int b) { return b != 0 ? a / b : 0; }

   int main() {
       // 函数指针数组：相当于路由表
       operation_t ops[] = {add, sub, mul, div_op};
       const char *names[] = {"+", "-", "*", "/"};

       int a = 20, b = 5;
       for (int i = 0; i < 4; i++) {
           printf("%d %s %d = %d\n", a, names[i], b, ops[i](a, b));
       }
       // 输出：
       // 20 + 5 = 25
       // 20 - 5 = 15
       // 20 * 5 = 100
       // 20 / 5 = 4

       return 0;
   }

^^^^^^^^^^^^^^^^
状态机实现
^^^^^^^^^^^^^^^^

状态机是嵌入式开发中常用的模式。每个状态对应一个处理函数，
通过函数指针实现状态之间的切换。就像自动售货机：投币状态、选择状态、出货状态，
每个状态有不同的行为。

.. code-block:: c

   #include <stdio.h>

   // 前向声明
   typedef struct StateMachine StateMachine;

   // 状态函数类型：接收事件，返回下一个状态函数
   typedef void (*state_func_t)(StateMachine *sm, int event);

   struct StateMachine {
       state_func_t current_state;
       int data;
   };

   // 状态函数声明
   void idle_state(StateMachine *sm, int event);
   void running_state(StateMachine *sm, int event);
   void stopped_state(StateMachine *sm, int event);

   void idle_state(StateMachine *sm, int event) {
       printf("[空闲] 收到事件 %d\n", event);
       if (event == 1) {  // 启动事件
           printf("[空闲] -> 切换到运行状态\n");
           sm->current_state = running_state;
       }
   }

   void running_state(StateMachine *sm, int event) {
       printf("[运行] 收到事件 %d\n", event);
       if (event == 2) {  // 停止事件
           printf("[运行] -> 切换到停止状态\n");
           sm->current_state = stopped_state;
       } else if (event == 3) {
           sm->data++;
           printf("[运行] 数据更新: %d\n", sm->data);
       }
   }

   void stopped_state(StateMachine *sm, int event) {
       printf("[停止] 收到事件 %d\n", event);
       if (event == 0) {  // 重置事件
           printf("[停止] -> 切换到空闲状态\n");
           sm->current_state = idle_state;
       }
   }

   int main() {
       StateMachine sm = {idle_state, 0};

       int events[] = {1, 3, 3, 2, 0};  // 启动、更新、更新、停止、重置
       int n = sizeof(events) / sizeof(events[0]);

       for (int i = 0; i < n; i++) {
           sm.current_state(&sm, events[i]);
       }

       return 0;
   }

^^^^^^^^^^^^^^^^
定时器回调与事件处理
^^^^^^^^^^^^^^^^

.. code-block:: c

   #include <stdio.h>
   #include <time.h>

   // 定时器回调类型
   typedef void (*timer_callback_t)(void *user_data);

   // 简易定时器结构
   typedef struct {
       timer_callback_t callback;
       void *user_data;
       int interval_ms;
       int elapsed_ms;
   } Timer;

   void timer_init(Timer *t, int interval, timer_callback_t cb, void *data) {
       t->callback = cb;
       t->user_data = data;
       t->interval_ms = interval;
       t->elapsed_ms = 0;
   }

   // 模拟定时器触发
   void timer_tick(Timer *t, int delta_ms) {
       t->elapsed_ms += delta_ms;
       if (t->elapsed_ms >= t->interval_ms) {
           t->callback(t->user_data);
           t->elapsed_ms = 0;
       }
   }

   // 回调函数示例
   void on_heartbeat(void *data) {
       int *count = (int *)data;
       (*count)++;
       printf("心跳 #%d\n", *count);
   }

   int main() {
       int heartbeat_count = 0;
       Timer timer;
       timer_init(&timer, 1000, on_heartbeat, &heartbeat_count);

       // 模拟时间流逝
       for (int tick = 0; tick < 5; tick++) {
           timer_tick(&timer, 300);
       }

       printf("总心跳次数: %d\n", heartbeat_count);
       return 0;
   }


位操作
------

位操作直接操作整数的二进制位，在嵌入式开发、网络协议、权限管理中非常常见。

^^^^^^^^^^^^^^^^
基本位操作
^^^^^^^^^^^^^^^^

把一个字节想象成 8 个排成一排的开关，每个开关只有 0（关）和 1（开）两种状态。

.. code-block:: c

   #include <stdio.h>

   // 辅助函数：打印二进制表示
   void print_binary(unsigned int n) {
       for (int i = 7; i >= 0; i--) {
           printf("%d", (n >> i) & 1);
       }
       printf("\n");
   }

   int main() {
       unsigned char a;

       // 1. 全部位清零
       a = 0;
       printf("全零: "); print_binary(a);  // 00000000

       // 或者用按位与
       a = 0xFF;
       a &= 0;           // 也是全零
       printf("与0: "); print_binary(a);   // 00000000

       // 2. 全部位设为 1
       a = ~0;            // 按位取反：0x00 → 0xFF
       printf("全一: "); print_binary(a);  // 11111111

       // 注意：a | 1 只会将最低位设为 1，不是全部置 1！
       // a = 0x00 | 1 = 0x01 → 00000001（错误做法）

       // 3. 某一位设为 1（置位）
       a = 0x00;
       a |= (1 << 3);    // 将第 3 位（从 0 开始）设为 1
       printf("第3位置1: "); print_binary(a);  // 00001000

       // 4. 某一位设为 0（清位）
       a = 0xFF;
       a &= ~(1 << 3);   // 将第 3 位设为 0
       printf("第3位置0: "); print_binary(a);  // 11110111

       // 5. 判断某一位是否为 1
       a = 0b10101010;   // 170
       int bit3 = (a >> 3) & 1;  // 取第 3 位
       int bit4 = (a >> 4) & 1;  // 取第 4 位
       printf("第3位: %d, 第4位: %d\n", bit3, bit4);  // 1, 0

       // 等价写法：
       bit3 = (a & (1 << 3)) != 0;
       bit4 = (a & (1 << 4)) != 0;

       return 0;
   }

^^^^^^^^^^^^^^^^
位操作常用技巧
^^^^^^^^^^^^^^^^

.. code-block:: c

   #include <stdio.h>

   int main() {
       // 1. 判断奇偶
       int n = 7;
       if (n & 1) {
           printf("%d 是奇数\n", n);  // 最低位为 1 就是奇数
       }

       // 2. 交换两个数（不用临时变量）
       int a = 3, b = 5;
       a ^= b;   // a = 3 ^ 5 = 6
       b ^= a;   // b = 5 ^ 6 = 3
       a ^= b;   // a = 6 ^ 3 = 5
       printf("a=%d, b=%d\n", a, b);  // a=5, b=3

       // 3. 求 2 的幂
       int power = 1 << 10;   // 2^10 = 1024

       // 4. 判断是否是 2 的幂（只有 1 个 bit 为 1）
       int x = 1024;
       int is_power_of_2 = (x > 0) && ((x & (x - 1)) == 0);
       printf("%d 是2的幂: %d\n", x, is_power_of_2);  // 1

       // 5. 统计二进制中 1 的个数
       unsigned int val = 0b10110100;  // 180
       int count = 0;
       unsigned int tmp = val;
       while (tmp) {
           count++;
           tmp &= (tmp - 1);  // 消除最低位的 1
       }
       printf("%u 的二进制有 %d 个 1\n", val, count);  // 4

       // 6. 掩码操作：提取指定位段
       unsigned int flags = 0b11010110;
       unsigned int bits_2_4 = (flags >> 2) & 0x07;  // 提取第 2~4 位
       printf("第2~4位: %u\n", bits_2_4);  // 5 (101)

       return 0;
   }


IPC 进程间通信
--------------

进程间通信（Inter-Process Communication, IPC）是指在不同进程之间传递数据和信号的机制。
在 Linux 系统中，进程之间的内存是隔离的，就像不同房间的人不能直接交流，
需要借助"传话筒"、"留言板"等工具。

^^^^^^^^^^^^^^^^
信号（Signal）
^^^^^^^^^^^^^^^^

信号是最简单的 IPC 机制，是**异步通知**。就像闹钟响了——你正在做别的事，
但闹钟响了你必须响应。信号不能携带大量数据，只能通知"发生了某件事"。

.. code-block:: c

   #include <stdio.h>
   #include <signal.h>
   #include <unistd.h>

   // 信号处理函数
   void handle_sigint(int sig) {
       printf("\n收到信号 %d (SIGINT)，执行清理...\n", sig);
       // 可以在这里做清理工作
       printf("清理完成，退出。\n");
       _exit(0);
   }

   int main() {
       // 注册信号处理函数：收到 SIGINT (Ctrl+C) 时调用 handle_sigint
       signal(SIGINT, handle_sigint);

       printf("程序运行中，按 Ctrl+C 触发信号...\n");
       while (1) {
           sleep(1);
       }

       return 0;
   }

**常用信号：**

.. code-block:: text

   信号名      编号  说明
   SIGHUP      1     终端挂断
   SIGINT      2     中断（Ctrl+C）
   SIGQUIT     3     退出（Ctrl+\）
   SIGKILL     9     强制终止（不可捕获）
   SIGSEGV     11    段错误
   SIGTERM     15    终止请求（默认信号）
   SIGCHLD     17    子进程状态变化
   SIGALRM     14    定时器到期

^^^^^^^^^^^^^^^^
管道（Pipe）
^^^^^^^^^^^^^^^^

管道是**单向**的数据通道，一端写入，另一端读取。就像水管，水从一端流进去，
从另一端流出来。管道常用于父子进程之间的通信。

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>
   #include <unistd.h>
   #include <string.h>
   #include <sys/wait.h>

   int main() {
       int pipefd[2];  // pipefd[0] 读端，pipefd[1] 写端
       pid_t pid;

       if (pipe(pipefd) == -1) {
           perror("pipe");
           exit(1);
       }

       pid = fork();
       if (pid == -1) {
           perror("fork");
           exit(1);
       }

       if (pid == 0) {
           // 子进程：读取数据
           close(pipefd[1]);  // 关闭写端
           char buf[100];
           int n = read(pipefd[0], buf, sizeof(buf) - 1);
           if (n > 0) {
               buf[n] = '\0';
               printf("子进程收到: %s\n", buf);
           }
           close(pipefd[0]);
       } else {
           // 父进程：写入数据
           close(pipefd[0]);  // 关闭读端
           const char *msg = "Hello from parent!";
           write(pipefd[1], msg, strlen(msg));
           close(pipefd[1]);
           wait(NULL);  // 等待子进程结束
       }

       return 0;
   }

^^^^^^^^^^^^^^^^
信号量（Semaphore）
^^^^^^^^^^^^^^^^

信号量是一个**计数器**，用于控制多个进程对共享资源的访问。
可以把它想象成停车场的计数牌：每进一辆车减 1，每出一辆车加 1，
计数为 0 时就不能再进了。

信号量的两个基本操作是 P（等待/减）和 V（释放/增）。

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>
   #include <sys/ipc.h>
   #include <sys/sem.h>
   #include <sys/wait.h>
   #include <unistd.h>

   // P 操作（等待）：信号量值减 1，如果为 0 则阻塞
   void sem_p(int semid) {
       struct sembuf op = {0, -1, 0};  // sem_num=0, sem_op=-1, sem_flg=0
       semop(semid, &op, 1);
   }

   // V 操作（释放）：信号量值加 1
   void sem_v(int semid) {
       struct sembuf op = {0, 1, 0};   // sem_num=0, sem_op=1, sem_flg=0
       semop(semid, &op, 1);
   }

   int main() {
       // 创建信号量，初始值为 1（互斥锁）
       int semid = semget(IPC_PRIVATE, 1, IPC_CREAT | 0666);
       semctl(semid, 0, SETVAL, 1);

       if (fork() == 0) {
           // 子进程
           sem_p(semid);
           printf("[子进程] 进入临界区\n");
           sleep(1);
           printf("[子进程] 离开临界区\n");
           sem_v(semid);
           exit(0);
       }

       // 父进程
       sem_p(semid);
       printf("[父进程] 进入临界区\n");
       sleep(1);
       printf("[父进程] 离开临界区\n");
       sem_v(semid);

       wait(NULL);
       semctl(semid, 0, IPC_RMID);  // 删除信号量
       return 0;
   }

^^^^^^^^^^^^^^^^
共享内存
^^^^^^^^^^^^^^^^

共享内存是**最快的 IPC 机制**。它让多个进程映射同一块物理内存，
就像多个房间共用一块白板——大家都能看到和修改白板上的内容。
但需要额外的同步机制（如信号量）来避免竞争。

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>
   #include <sys/ipc.h>
   #include <sys/shm.h>
   #include <sys/wait.h>
   #include <unistd.h>
   #include <string.h>

   #define SHM_SIZE 1024

   int main() {
       // 创建共享内存段
       int shmid = shmget(IPC_PRIVATE, SHM_SIZE, IPC_CREAT | 0666);
       if (shmid == -1) {
           perror("shmget");
           exit(1);
       }

       if (fork() == 0) {
           // 子进程：附加共享内存并读取
           char *shm = (char *)shmat(shmid, NULL, 0);
           sleep(1);  // 等父进程写入
           printf("子进程读到: %s\n", shm);
           shmdt(shm);
           exit(0);
       }

       // 父进程：附加共享内存并写入
       char *shm = (char *)shmat(shmid, NULL, 0);
       strcpy(shm, "Hello from shared memory!");
       printf("父进程已写入数据\n");
       shmdt(shm);

       wait(NULL);
       shmctl(shmid, IPC_RMID, NULL);  // 删除共享内存段
       return 0;
   }

^^^^^^^^^^^^^^^^
消息队列
^^^^^^^^^^^^^^^^

消息队列是**带类型的消息链表**。发送方把带有类型标识的消息放入队列，
接收方可以按类型选择性读取。就像邮局的信箱：信件按不同的信箱号分类。

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>
   #include <sys/ipc.h>
   #include <sys/msg.h>
   #include <sys/wait.h>
   #include <unistd.h>
   #include <string.h>

   // 消息结构体（mtype 必须 > 0）
   struct msgbuf {
       long mtype;         // 消息类型
       char mtext[256];    // 消息内容
   };

   int main() {
       int msqid = msgget(IPC_PRIVATE, IPC_CREAT | 0666);
       if (msqid == -1) {
           perror("msgget");
           exit(1);
       }

       if (fork() == 0) {
           // 子进程：接收类型为 1 的消息
           struct msgbuf msg;
           msgrcv(msqid, &msg, sizeof(msg.mtext), 1, 0);
           printf("子进程收到: [类型%ld] %s\n", msg.mtype, msg.mtext);
           exit(0);
       }

       // 父进程：发送类型为 1 的消息
       struct msgbuf msg;
       msg.mtype = 1;
       strcpy(msg.mtext, "Hello from message queue!");
       msgsnd(msqid, &msg, strlen(msg.mtext) + 1, 0);
       printf("父进程已发送消息\n");

       wait(NULL);
       msgctl(msqid, IPC_RMID, NULL);  // 删除消息队列
       return 0;
   }

^^^^^^^^^^^^^^^^
Socket
^^^^^^^^^^^^^^^^

Socket（套接字）是最通用的 IPC 机制，不仅可以在同一台机器上的进程间通信，
还可以通过网络进行跨机器通信。支持 TCP（可靠、面向连接）和 UDP（快速、无连接）。

.. code-block:: c

   /* TCP 服务器示例 */
   #include <stdio.h>
   #include <stdlib.h>
   #include <string.h>
   #include <unistd.h>
   #include <arpa/inet.h>

   #define PORT 8080
   #define BUF_SIZE 1024

   int main() {
       int server_fd, client_fd;
       struct sockaddr_in address;
       char buf[BUF_SIZE];

       // 1. 创建 socket
       server_fd = socket(AF_INET, SOCK_STREAM, 0);
       if (server_fd < 0) {
           perror("socket");
           exit(1);
       }

       // 2. 绑定地址
       memset(&address, 0, sizeof(address));
       address.sin_family = AF_INET;
       address.sin_addr.s_addr = INADDR_ANY;
       address.sin_port = htons(PORT);  // 使用 htons 转换字节序

       if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
           perror("bind");
           exit(1);
       }

       // 3. 监听
       listen(server_fd, 5);
       printf("服务器监听端口 %d...\n", PORT);

       // 4. 接受连接
       socklen_t addrlen = sizeof(address);
       client_fd = accept(server_fd, (struct sockaddr *)&address, &addrlen);
       if (client_fd < 0) {
           perror("accept");
           exit(1);
       }

       // 5. 读写数据
       int n = read(client_fd, buf, BUF_SIZE - 1);
       if (n > 0) {
           buf[n] = '\0';
           printf("收到: %s\n", buf);
           write(client_fd, "ACK", 3);
       }

       close(client_fd);
       close(server_fd);
       return 0;
   }

^^^^^^^^^^^^^^^^
IPC 机制对比
^^^^^^^^^^^^^^^^

.. code-block:: text

   +----------+----------+----------+----------+----------+
   | 机制     | 方向     | 速度     | 复杂度   | 适用场景 |
   +==========+==========+==========+==========+==========+
   | 信号     | 单向     | 快       | 低       | 通知/中断|
   | 管道     | 单向     | 中       | 低       | 父子进程 |
   | 消息队列 | 双向     | 中       | 中       | 结构通信 |
   | 信号量   | -        | 快       | 中       | 同步/互斥|
   | 共享内存 | 双向     | 最快     | 高       | 大数据量 |
   | Socket   | 双向     | 中       | 高       | 网络/跨机|
   +----------+----------+----------+----------+----------+


常用函数
--------

C 标准库提供了丰富的字符串、内存和转换函数。以下是开发中最常用的函数。

^^^^^^^^^^^^^^^^
字符处理函数（<ctype.h>）
^^^^^^^^^^^^^^^^

.. code-block:: c

   #include <stdio.h>
   #include <ctype.h>

   int main() {
       char c = 'A';

       // 大小写转换
       printf("tolower('A') = '%c'\n", tolower(c));  // 'a'
       printf("toupper('a') = '%c'\n", toupper('a'));  // 'A'

       // 字符判断
       printf("isdigit('5') = %d\n", isdigit('5'));   // 非零（是）
       printf("isdigit('a') = %d\n", isdigit('a'));   // 0（不是）
       printf("isalpha('z') = %d\n", isalpha('z'));   // 非零（是）
       printf("isalnum('3') = %d\n", isalnum('3'));   // 非零（是数字或字母）
       printf("isalnum('@') = %d\n", isalnum('@'));   // 0（不是）

       // 其他常用
       printf("isspace(' ') = %d\n", isspace(' '));   // 非零（是空白字符）
       printf("isupper('A') = %d\n", isupper('A'));   // 非零
       printf("islower('a') = %d\n", islower('a'));   // 非零

       // 实际应用：将字符串转为小写
       char str[] = "Hello, World!";
       for (int i = 0; str[i]; i++) {
           str[i] = tolower(str[i]);
       }
       printf("转小写: %s\n", str);  // "hello, world!"

       return 0;
   }

^^^^^^^^^^^^^^^^
字符串函数（<string.h>）
^^^^^^^^^^^^^^^^

.. code-block:: c

   #include <stdio.h>
   #include <string.h>

   int main() {
       // strlen：计算字符串长度（不含 '\0'）
       char *s = "Hello";
       printf("长度: %zu\n", strlen(s));  // 5

       // strcpy：复制字符串（目标缓冲区必须足够大）
       char dest[20];
       strcpy(dest, "World");
       printf("strcpy: %s\n", dest);  // "World"

       // strncpy：安全复制（最多复制 n 个字符）
       char dest2[4];
       strncpy(dest2, "Hello", sizeof(dest2) - 1);
       dest2[sizeof(dest2) - 1] = '\0';  // 手动添加终止符
       printf("strncpy: %s\n", dest2);  // "Hel"

       // strcmp：比较字符串（返回 0 表示相等）
       int result = strcmp("abc", "abd");
       printf("strcmp(abc, abd) = %d\n", result);  // 负数（'c' < 'd'）

       // strstr：查找子串
       char *pos = strstr("Hello, World!", "World");
       if (pos) {
           printf("找到子串: %s\n", pos);  // "World!"
           printf("位置: %td\n", pos - "Hello, World!");  // 7
       }

       // strtok：字符串分割（会修改原字符串！）
       char data[] = "one,two,three";
       char *token = strtok(data, ",");
       while (token != NULL) {
           printf("token: %s\n", token);
           token = strtok(NULL, ",");  // 后续调用传 NULL
       }
       // 输出: one, two, three

       return 0;
   }

^^^^^^^^^^^^^^^^
内存操作函数（<string.h>）
^^^^^^^^^^^^^^^^

内存操作函数与字符串函数的区别：内存函数不关心 ``'\0'``，按字节操作。

.. code-block:: c

   #include <stdio.h>
   #include <string.h>

   int main() {
       // memcpy：内存拷贝（源和目标不能重叠）
       int src[] = {1, 2, 3, 4, 5};
       int dst[5];
       memcpy(dst, src, sizeof(src));
       for (int i = 0; i < 5; i++) printf("%d ", dst[i]);
       printf("\n");  // 1 2 3 4 5

       // memmove：内存拷贝（源和目标可以重叠）
       int arr[] = {1, 2, 3, 4, 5};
       memmove(arr + 1, arr, 4 * sizeof(int));  // 右移一位
       for (int i = 0; i < 5; i++) printf("%d ", arr[i]);
       printf("\n");  // 1 1 2 3 4

       // memset：内存设置（按字节填充）
       char buf[10];
       memset(buf, 'A', sizeof(buf));
       for (int i = 0; i < 10; i++) printf("%c ", buf[i]);
       printf("\n");  // A A A A A A A A A A

       // 常见用法：清零
       int zero[5];
       memset(zero, 0, sizeof(zero));
       // 注意：memset 只能可靠地将字节设为 0 或 -1（0xFF）
       // memset(arr, 1, sizeof(arr)) 不会将每个 int 设为 1！

       // memcmp：内存比较
       int a[] = {1, 2, 3};
       int b[] = {1, 2, 4};
       int cmp = memcmp(a, b, sizeof(a));
       printf("memcmp: %d\n", cmp);  // 负数（3 < 4）

       return 0;
   }

^^^^^^^^^^^^^^^^
转换函数（<stdlib.h>）
^^^^^^^^^^^^^^^^

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>

   int main() {
       // atoi：字符串转 int（出错返回 0，无法区分错误）
       int i = atoi("123");
       printf("atoi(\"123\") = %d\n", i);  // 123
       printf("atoi(\"abc\") = %d\n", atoi("abc"));  // 0（错误）

       // atol：字符串转 long
       long l = atol("1234567890");
       printf("atol = %ld\n", l);

       // strtol：字符串转 long（更安全，可检测错误）
       char *endptr;
       long val = strtol("123abc", &endptr, 10);  // 10 表示十进制
       printf("strtol: %ld, 剩余: \"%s\"\n", val, endptr);
       // val = 123, 剩余: "abc"

       // 如果整个字符串都不是数字
       val = strtol("hello", &endptr, 10);
       if (endptr == "hello") {
           printf("没有有效的数字\n");
       }

       // strtod：字符串转 double
       double d = strtod("3.14abc", &endptr);
       printf("strtod: %f, 剩余: \"%s\"\n", d, endptr);  // 3.14, "abc"

       // base 参数：不同进制
       printf("十六进制 \"FF\" = %ld\n", strtol("FF", NULL, 16));  // 255
       printf("二进制 \"1010\" = %ld\n", strtol("1010", NULL, 2));  // 10
       printf("八进制 \"77\" = %ld\n", strtol("77", NULL, 8));     // 63

       return 0;
   }

**推荐使用 strtol/strtod 而非 atoi/atof**，因为前者能检测转换错误。


经典编程题
----------

^^^^^^^^^^^^^^^^
回文字符串判断
^^^^^^^^^^^^^^^^

回文字符串是正读和反读都一样的字符串，如 "level"、"racecar"。

思路：用双指针，一个从头，一个从尾，向中间靠拢，逐个比较。

.. code-block:: c

   #include <stdio.h>
   #include <string.h>
   #include <stdbool.h>
   #include <ctype.h>

   // 基本版本：区分大小写
   bool is_palindrome(const char *str) {
       int left = 0;
       int right = strlen(str) - 1;

       while (left < right) {
           if (str[left] != str[right]) {
               return false;
           }
           left++;
           right--;
       }
       return true;
   }

   // 忽略大小写和非字母字符
   bool is_palindrome_ignore_case(const char *str) {
       int left = 0;
       int right = strlen(str) - 1;

       while (left < right) {
           // 跳过非字母字符
           while (left < right && !isalpha(str[left])) left++;
           while (left < right && !isalpha(str[right])) right--;

           if (tolower(str[left]) != tolower(str[right])) {
               return false;
           }
           left++;
           right--;
       }
       return true;
   }

   int main() {
       printf("\"level\" 是回文: %d\n", is_palindrome("level"));         // 1
       printf("\"hello\" 是回文: %d\n", is_palindrome("hello"));         // 0
       printf("\"A man a plan a canal Panama\" 是回文: %d\n",
              is_palindrome_ignore_case("A man a plan a canal Panama")); // 1

       return 0;
   }

^^^^^^^^^^^^^^^^
字符串反转
^^^^^^^^^^^^^^^^

.. code-block:: c

   #include <stdio.h>
   #include <string.h>

   // 原地反转字符串
   void reverse_string(char *str) {
       int left = 0;
       int right = strlen(str) - 1;

       while (left < right) {
           // 交换两端的字符
           char temp = str[left];
           str[left] = str[right];
           str[right] = temp;
           left++;
           right--;
       }
   }

   // 反转字符串的前 n 个字符
   void reverse_n(char *str, int n) {
       int left = 0;
       int right = n - 1;
       while (left < right) {
           char temp = str[left];
           str[left] = str[right];
           str[right] = temp;
           left++;
           right--;
       }
   }

   int main() {
       // 基本反转
       char s1[] = "Hello, World!";
       reverse_string(s1);
       printf("反转: %s\n", s1);  // "!dlroW ,olleH"

       // 按单词反转（面试经典题）
       // 思路：先反转整个字符串，再逐个单词反转
       char s2[] = "Hello World C Language";

       // 第 1 步：整体反转 → "egaugnaC dlroW olleH"
       reverse_string(s2);

       // 第 2 步：逐个单词反转 → "Language C World Hello"
       int start = 0;
       for (int i = 0; ; i++) {
           if (s2[i] == ' ' || s2[i] == '\0') {
               reverse_n(s2 + start, i - start);
               start = i + 1;
           }
           if (s2[i] == '\0') break;
       }
       printf("单词反转: %s\n", s2);

       return 0;
   }

^^^^^^^^^^^^^^^^
链表指定位置增删
^^^^^^^^^^^^^^^^

链表是动态数据结构，元素在内存中不必连续。每个节点包含数据和指向下一个节点的指针，
就像一串珠子，每颗珠子都"记得"下一颗在哪里。

.. code-block:: c

   #include <stdio.h>
   #include <stdlib.h>

   // 链表节点定义
   typedef struct Node {
       int data;
       struct Node *next;
   } Node;

   // 创建新节点
   Node *create_node(int data) {
       Node *node = (Node *)malloc(sizeof(Node));
       if (node == NULL) {
           fprintf(stderr, "内存分配失败\n");
           exit(1);
       }
       node->data = data;
       node->next = NULL;
       return node;
   }

   // 在指定位置插入节点（0 表示头部）
   // 返回新的头指针
   Node *insert_at(Node *head, int pos, int data) {
       Node *new_node = create_node(data);

       if (pos == 0) {
           // 插入头部
           new_node->next = head;
           return new_node;
       }

       // 找到第 pos-1 个节点
       Node *curr = head;
       for (int i = 0; i < pos - 1 && curr != NULL; i++) {
           curr = curr->next;
       }

       if (curr == NULL) {
           printf("位置 %d 超出范围\n", pos);
           free(new_node);
           return head;
       }

       // 插入
       new_node->next = curr->next;
       curr->next = new_node;
       return head;
   }

   // 删除指定位置的节点
   Node *delete_at(Node *head, int pos) {
       if (head == NULL) {
           printf("链表为空\n");
           return NULL;
       }

       if (pos == 0) {
           // 删除头部
           Node *temp = head;
           head = head->next;
           free(temp);
           return head;
       }

       // 找到第 pos-1 个节点
       Node *curr = head;
       for (int i = 0; i < pos - 1 && curr->next != NULL; i++) {
           curr = curr->next;
       }

       if (curr->next == NULL) {
           printf("位置 %d 超出范围\n", pos);
           return head;
       }

       // 删除
       Node *temp = curr->next;
       curr->next = temp->next;
       free(temp);
       return head;
   }

   // 打印链表
   void print_list(Node *head) {
       Node *curr = head;
       while (curr != NULL) {
           printf("%d", curr->data);
           if (curr->next) printf(" -> ");
           curr = curr->next;
       }
       printf(" -> NULL\n");
   }

   // 释放整个链表
   void free_list(Node *head) {
       while (head != NULL) {
           Node *temp = head;
           head = head->next;
           free(temp);
       }
   }

   int main() {
       Node *list = NULL;

       // 构建链表：1 -> 2 -> 3
       list = insert_at(list, 0, 1);
       list = insert_at(list, 1, 2);
       list = insert_at(list, 2, 3);
       printf("初始链表: ");
       print_list(list);  // 1 -> 2 -> 3 -> NULL

       // 在位置 1 插入 10：1 -> 10 -> 2 -> 3
       list = insert_at(list, 1, 10);
       printf("插入10后: ");
       print_list(list);

       // 在位置 0 插入 0（头部插入）：0 -> 1 -> 10 -> 2 -> 3
       list = insert_at(list, 0, 0);
       printf("插入0后:  ");
       print_list(list);

       // 删除位置 2 的节点：0 -> 1 -> 2 -> 3
       list = delete_at(list, 2);
       printf("删除位置2: ");
       print_list(list);

       // 删除位置 0 的节点（头部删除）：1 -> 2 -> 3
       list = delete_at(list, 0);
       printf("删除位置0: ");
       print_list(list);

       free_list(list);
       return 0;
   }

**链表操作易错点：**

- 插入时忘记设置新节点的 ``next``
- 删除时忘记释放被删除节点的内存（内存泄漏）
- 操作头节点时忘记更新头指针
- 遍历时删除当前节点导致断链（需要先保存 ``next``）
