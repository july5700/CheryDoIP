# -*- coding: utf-8 -*-
"""
演示 @dataclass 自动生成的 __eq__ 和 __repr__ 方法
"""

from dataclasses import dataclass


# 不用 @dataclass 的普通类
class NormalClass:
    def __init__(self, name, value):
        self.name = name
        self.value = value


# 使用 @dataclass 的类
@dataclass
class DataClass:
    name: str
    value: int


# 创建对象
obj1 = NormalClass("test", 100)
obj2 = NormalClass("test", 100)

dc1 = DataClass("test", 100)
dc2 = DataClass("test", 100)

print("=" * 60)
print("【1】打印对象 (测试 __repr__)")
print("=" * 60)
print(f"普通类对象：{obj1}")
print(f"数据类对象：{dc1}")
print()

print("=" * 60)
print("【2】比较对象 (测试 __eq__)")
print("=" * 60)
print(f"普通类 obj1 == obj2: {obj1 == obj2}")
print(f"数据类 dc1 == dc2: {dc1 == dc2}")
print()

print("=" * 60)
print("【3】查看对象的属性")
print("=" * 60)
print(f"dc1.name = {dc1.name}")
print(f"dc1.value = {dc1.value}")
print()

print("=" * 60)
print("【4】查看类的方法")
print("=" * 60)
print(f"DataClass 有 __init__: {hasattr(DataClass, '__init__')}")
print(f"DataClass 有 __repr__: {hasattr(DataClass, '__repr__')}")
print(f"DataClass 有 __eq__: {hasattr(DataClass, '__eq__')}")
print()

print("=" * 60)
print("【5】手动调用 __repr__ 和 __eq__")
print("=" * 60)
print(f"dc1.__repr__() = {dc1.__repr__()}")
print(f"dc1.__eq__(dc2) = {dc1.__eq__(dc2)}")
