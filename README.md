# Three Meal（每日三餐）

[TOC]

## 1. 系统描述

系统分为3部分:

### 1.1 用户端

用户填写zipcode(94536, 94359, 9007 etc)，选择日期，默认今天，得到zipcode下，对应日期的三款meal，任意选择。
用户点开一个套餐，看到该套餐的信息。下单，填写地址，填写电话，完成。

### 1.2 大厨端

产生/编辑一款meal，选择支持的zipcode，设定每个zipcode的日期和时间（这样会出现某一zipcode下，某一天有多于三款的情况，由管理员决定谁被选中，也以此鼓励他们做精品）查看有多少人订餐了，订餐信息
后期SMS支持。

### 1.3 管理员

正常管理功能

---

## 2. 功能列表

1. 用户注册
2. 用户登录
3. 套餐发布
4. 套餐查看

---

## 3. 后期目标

1. Rest架构
2. 提供手机APP，可以使用Ionic框架做跨平台APP

---

## 4. 系统运行

调试模式：
```
python manage.py runserver -r -d
```

正式运行：
```
python manage.py runserver
```

---

## 5. TODO

- ~~用户查看自己的订单列表~~
- ~~大厨查看自己的订单列表~~
- ~~大厨编辑订单（处理、取消订单）~~
- ~~用户编辑订单（收获确认、取消订单）~~
- ~~管理员查看Meal列表（按ZipCode查询）~~
- ~~管理员编辑Meal（推荐、取消推荐）~~
- ~~用户根据ZipCode进行查询~~
- ~~今日菜单（根据zipcode查询今天被推荐的meal）~~

---
10月24日修改(hdl):

- 为命名统一，zipcode作为一个单词使用. 所以zip_code(s) 改成了 zipcode(s), Zip_code 改成了 Zipcode
- meal的url是否应该改成 /meal 而不是 /chef/meal . 同时，取消meal_oder . 待讨论




