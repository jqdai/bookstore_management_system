# 图书管理系统

用 django 实现的图书管理系统，作为数据库引论课程的期中实验作业

## 开发环境

- Windows 10 64位（DirectX 12）
- pycharm 2020.1（专业版）
- python 3.8
- django 3.0.5

## 功能

- [x] 建立超级管理员和普通管理员（通过admin站点）
- [x] 维护图书记录（包括按书名、作者等检索）
- [x] 维护交易记录（包括按时间检索）
- [x] 查看书城所有图书信息
- [x] 按时间顺序查看交易记录
- [x] 所有系统功能只有登录后才能使用
- [x] 登录注销
- [x] 修改密码（通过邮箱，验证邮件发到终端）
- [x] 修改个人信息
- [x] 根据 ISBN、书名、作者、出版社等信息检索书籍
- [x] 新书上架
- [x] 查看某一段时间内的交易记录
- [x] 图书信息修改
- [x] 旧书补货
- [x] 旧书销售
- [x] 下单不付款，付款加库存
- [x] 交易记录中记录执行交易的管理员用户名
- [x] 付款 / 退货界面做成单选题
- [x] 表单提交后输出提示信息（操作成功与否，检索图书和修改个人信息两网页上未能成功，弹窗和跳转顺序反了）
- [x] 根据负责人检索订单（在管理员个人信息页面显示其负责的订单）
- [x] 手机号使用正则表达式验证（包括 models 和 forms）
- [x] 查询界面新增“重置”以重置表单
- [x] 图示模式新增语言属性，并可通过该属性检索
- [x] 建立 author 模式
- [x] 利用 split 和 __contain 处理一本书多个作者问题
- [x] 利用 Publisher 模式重构 Book 模式，利用 ForeignKey 处理出版社问题
- [ ] 利用 Author 模式重构 Book 模式，利用 ManyToMany 处理一本书多个作者问题
- [ ] 使用 Bootstrap / MDUI 改进前端网页
- [ ] 及时有效的提示弹窗
- [ ] 在图书信息栏显示图书所有作者

## 网页索引

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
- accounts/login 登录
- accounts/password_reset 通过邮件重置密码

## 数据库设计说明

- 不设置注册功能。本站点都是管理员，普通管理员账号由超级管理员直接配置，不需要注册功能
- 重置密码的邮件发送至终端（EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'）
- 用户邮箱只能通过 admin 站点更改，若不填则没法收到改密码的邮件（当然这里把邮件发送到终端，都可以收到）
- 图书进货和销售记录用同一个 schema 储存，通过 in_and_out 属性判断货物流向
- 销售订单的 cost 属性等于商品 price 属性
- 一本书有多个作者时，多个作者之间用一个中文逗号隔开
- 按时间检索交易记录时用日期选择表选择时间（推荐使用 Chrome 浏览器，弱智 IE 跳不出日期选择表）
- 主页显示访问主页的次数（关闭页面不归零，断开服务器链接不归零）
- Transactions.book = models.ForeignKey(Book)
- Book.publisher = models.ForeignKey(Publisher)

## 使用说明

- 进入项目，在 PowerShel 中输入指令 'py manage.py runserver', 进入网页 127.0.0.1:8000 即可使用
- 提供超级管理员账号（用户名:djq 密码:12345678）

## 贡献者

- [Jiaqi Dai](https://github.com/jqdai) - 复旦大学
