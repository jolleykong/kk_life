# isinstance , issubclass 

# 判断对象与类之间的关系 isinstance 。
# isinstance(a,b) 判断a是否是b类，或b类的派生类 的实例化对象。
class A:
    pass

class B(A):
    pass

class C(B):
    pass
obj = B()

print(isinstance(obj,B))    # True
print(isinstance(obj,A))    # True


# 判断类与类之间的关系 issubclass 
# issubclass (a,b) 判断a是否是b类，或b类的派生类 的派生类。（判断a是否是b的子孙类）
print(issubclass(B,A))      # True
print(issubclass(A,B))      # False
print(issubclass(C,B))      # True
print(issubclass(C,A))      # True