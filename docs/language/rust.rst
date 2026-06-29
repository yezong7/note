Rust 语言
=========

Rust 学习笔记。

所有权系统
----------

- **所有权规则**：每个值有且仅有一个所有者
- **借用**：``&T`` 不可变借用，``&mut T`` 可变借用
- **生命周期**：``'a`` 标注引用的有效范围

.. code-block:: rust

   fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
       if x.len() > y.len() { x } else { y }
   }

模式匹配
--------

.. code-block:: rust

   match value {
       1 => println!("one"),
       2..=5 => println!("two to five"),
       _ => println!("other"),
   }

错误处理
--------

.. code-block:: rust

   use std::fs::File;
   use std::io::{self, Read};

   fn read_file(path: &str) -> Result<String, io::Error> {
       let mut file = File::open(path)?;
       let mut contents = String::new();
       file.read_to_string(&mut contents)?;
       Ok(contents)
   }

常用数据结构
------------

.. code-block:: rust

   // Vec
   let mut v = vec![1, 2, 3];
   v.push(4);

   // HashMap
   use std::collections::HashMap;
   let mut map = HashMap::new();
   map.insert("key", "value");

   // Option
   let x: Option<i32> = Some(5);
   let y: Option<i32> = None;

   // Result
   let ok: Result<i32, String> = Ok(5);
   let err: Result<i32, String> = Err("error".to_string());

并发
----

.. code-block:: rust

   use std::thread;
   use std::sync::{Arc, Mutex};

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

Trait
-----

.. code-block:: rust

   trait Summary {
       fn summarize(&self) -> String;

       fn preview(&self) -> String {
           format!("{}...", &self.summarize()[..20])
       }
   }

   struct Article {
       title: String,
       content: String,
   }

   impl Summary for Article {
       fn summarize(&self) -> String {
           format!("{}: {}", self.title, self.content)
       }
   }

.. note::

   持续更新中...
