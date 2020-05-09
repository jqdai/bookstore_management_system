# 实验报告

## 实验题目

- 图书销售管理系统的设计与实现
- 项目地址：[demo](https://github.com/jqdai/bookstore_management_system)

## 开发环境

- 操作系统：Windows 10 64位（DirectX 12）
- IDE：pycharm 2020.1（专业版）
- 数据库管理软件：sqlite3
- 编程语言：python 3.8
- Web开发环境：django 3.0.5

## 数据库设计

介绍本项目的数据库设计，给出系统数据库的 ER 图，对每个表的功能和属性进行说明。

### 数据库设计简介与 ER 图

- 本项目共设计有 5 个模式: Admin, Publisher, Author, Book, Transaction
- ER 图如下图所示（下图可在 github 中直接查看。若想本地查看，请打开本文件夹下的“中期实验ER图.JPG”文件）

![image](https://github.com/jqdai/bookstore_management_system/blob/master/%E4%B8%AD%E6%9C%9F%E5%AE%9E%E9%AA%8CER%E5%9B%BE.JPG)

### 各模式功能与属性说明

#### Admin

##### 属性

- id: 自动生成的主码
- user: 利用 django 自带的用户系统维护用户名、密码、邮箱等信息
- name: 真实姓名
- gender: 性别
- age: 年龄
- address: 住址（复合属性本应拆分为 city、street 等属性，此处简化无伤大雅）
- phone: 电话（可以作为多值属性，但一方面实际场景中不会记录多个电话，另一方面多值属性的处理方法在下面的 Author 模式中有体现，因此此处不作多值属性处理）

##### 方法

- __str\_\_(self): 返回用户名（注意是 self.**user**.get_username() ）

##### 功能

- 在 django 自带用户系统的基础上扩充几个信息，但真正起到登录、改密码等作用的是自带的 django.contrib.auth.models.User
- 在 Transaction 模式中，每条交易记录要注明是谁下的单，就是通过 ruler 属性记录的 Admin（其实是 username）实现的
- 通过 ForeignKey 成为 Transaction 模式的 ruler 属性，表示每个订单的负责人。一个订单只能有唯一的负责人，而一个管理员可以下很多单
- 支持检索和修改信息

#### Publisher

##### 属性

- id: 自动生成的主码
- name: 出版社名称

##### 方法

- __str\_\_(self): 返回出版社名称
- get_absolute_url(self): 返回一个通向该出版社详细信息页的 url，以其 id 属性作为参数，并显示其出版的图书

##### 功能

- 维护所有出现过的出版社名称，并在其详细信息页显示其名称、出版书籍等信息且可修改
- 通过 ForeignKey 成为 Book 模式的 publisher 属性，表示每本图书的出版社。一本书只能有唯一的出版社，而一个出版社可以出版多本图书
- 支持检索和修改信息

#### Author

##### 属性

- id: 自动生成的主码
- name: 作者姓名

##### 方法

- __str\_\_(self): 返回作者姓名
- get_absolute_url(self): 返回一个通向该作者详细信息页的 url，以其 id 属性作为参数，并显示其创作的图书

##### 功能

- 维护所有出现过的作者姓名，并在其详细信息页显示其姓名、所作图书等信息且可修改
- 通过 MayToManyField 成为 Book 模式的 author 属性，表示每本图书的作者。一本书可以有多个作者，一个作者也可以写多本书
- 支持检索和修改信息
- 因此处表现了多值属性的特性，因此 Admin 模式中的 phone 属性简化为单值属性无伤大雅

#### Book

##### 属性

- id: 自动生成的主码
- ISBN: ISBN国际书号
- language: 语言
- author: 作者，通过 ManyToManyField 用 Author 模式储存
- publisher: 出版社， 通过 ForeignKey 用Publisher 模式储存
- price: 零售价
- inventory: 库存数量

##### 方法

- __str\_\_(self): 返回一个表示图书信息的字符串：《书名》，作者，国际书号，出版社
- get_absolute_url(self): 返回一个通向该图书详细信息页的 url，以其 id 属性作为参数，并显示其交易记录
- get_author(self): 返回图书全部作者，根据图书去 Author 模式中查找相应的作者，若有多位则使用'，'.join(...)的方法返回一个字符串

##### 功能

- 维护所有出现过的图书，并在其详细信息页显示其名称、国际书号、作者、出版社等信息且可修改
- 通过 MayToManyField 利用 Author 模式储存作者信息，避免冗余和不一致
- 通过 ForeignKey 利用 Publisher 模式储存出版社信息，避免冗余和不一致
- 通过 ForeignKey 成为 Transaction 模式的 book 属性，表示每条交易记录的交易主体。一条记录只能有唯一的交易主体，一本书也可以有多条交易记录
- 支持检索和修改信息

#### Transaction

##### 属性

- in_out: 区别订单类型，是进货还是出货
- book: 交易主体，通过 ForeignKey 利用 Book 模式储存
- ruler: 订单负责人（下单人）， 通过 ForeignKey 利用 Admin 模式储存
- cost: 成交金额。若是进货，则表示进价；若是出货，则表示零售价
- amount: 成交量
- time: 成交时间，由系统自动生成
- paid: 订单付款状态。不在库中的图书进货和库存图书销售下单后自动设为“已付款”，库存图书进货则设为“未付款”。对未付款订单，可以手动付款，状态更新为“已付款”，同时自动增加库存量；也可选择退货，状态更新为“已退款”，不更新库存

##### 方法

- __str\_\_(self): 返回一个表示订单的字符串
- recent_deal(self): 返回在过去一天内成交的订单（实际并未使用）

##### 功能

- 维护所有成交过的订单，可根据自定义的时间范围检索
- 通过 ForeignKey 利用 Book 模式储存商品信息，避免冗余和不一致

## 系统设计

对照实验要求，展示系统的主要功能，适当截图，对每个功能内部的实现流程进行说明。对某些关键的功能实现，可以通过展示代码来分析。

- 

## 特色和创新点

如果你的系统有任何功能或技术上的特色或创新之处，请在这里加以说明。

## 提交文件说明

### 运行方法

- 解压后在 IDE 中打开项目文件夹，推荐使用 pycharm 2020.1（专业版）
- 在此处打开终端，执行以下命令
```text
py manage.py runserver
```
- 访问127.0.0.1:8000即可进入主页，推荐使用 Google Chrome 浏览器

### URL 说明

- 所有网页都必须先登录再查看内容或操作
- 以下各网址前缀 127.0.0.1:8000 已省略
- admin/ 超级管理员网站
- bookstore/ 默认主页
- bookstore/books 图书列表（含检索功能）
- bookstore/book/<int:bid> 查看图书信息与相关交易记录
- bookstore/book/<int:bid>/io 在库图书补货与销售
- bookstore/book/<int:bid>/edit 修改图书信息
- bookstore/newbook/ 新书上架
- bookstore/transactions 所有交易记录（含检索功能）
- bookstore/transactions/payment 订单付款和退货
- bookstore/user/<int:uid>/profile 查看用户个人信息
- bookstore/user/<int:uid>/profile/update 修改用户个人信息
- bookstore/publishers 出版社列表
- bookstore/publishers/<int:pid> 查看出版社信息
- bookstore/publishers/<int:pid>/update 出版出版社信息
- bookstore/author 作者列表
- bookstore/authors/<int:aid> 查看作者信息
- bookstore/authors/<int:aid>/update 修改作者信息
- accounts/login 登录
- accounts/password_reset 通过邮件重置密码

### 超级管理员账号

- 用户名：chuan
- 密码：12345678
- 邮箱：6324upup@258.com
- 修改密码的验证邮件在终端查收

## 实验总结

### 收获

### 困难

