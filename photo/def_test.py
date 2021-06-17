
d = {
    'v1':1,
    'v2':2,
    'v3':3
}


def func(v2,v3,v1):
    print(v1,v2,v3)

def fun2(dic):
    print(dic)

# func(**d)
# fun2(d)
dic = {
    'a':[1,2,3],
    'b':'abc',
    'c':{
        'd':1,
    }
}

def f(d):
    d['c'] = {}
    print(d)
    d['a'][0] = 4
    print(d)
    d['a'] = []
    print(d)
    d['b'] = '123'
    print(d)
    d = {}
    print(d)
    d = 123
    print(d)

f(dic)
print('dic:--', dic)


ar = [1,'233',{}]

def fa(a):
    a[0] = 2
    print(a)
    a[2] = {'1':'2'}
    print(a)
    a = []
    print(a)
    a = '[][][]'
    print(a)

fa(ar)
print('ar:--', ar)

c = '13'


def fc(co):
    co = 444
    print(co)

fc(c)
print('c:---',c)

class Test:
    def f1(self):
        pass
    @classmethod
    def f2(cls):
        pass
    @staticmethod
    def f3():
        pass
    @property
    def f4(self):
        return self.__class__

t = Test()

# {'a': [1, 2, 3], 'b': 'abc', 'c': {}}
# {'a': [4, 2, 3], 'b': 'abc', 'c': {}}
# {'a': [], 'b': 'abc', 'c': {}}
# {'a': [], 'b': '123', 'c': {}}

# 证明只有更改引用才能影响原列表或字典且非引用的函数不影响

# 参数顺序无关紧要，字典用**kwargs的方法可以将键名匹配参数传入

# json相关：
# c= '{"a": true, "b": 2}'
# d=json.loads(c)
# d
# {'a': True, 'b': 2}
# d['a']
# True
# type(d['a'])
# <class 'bool'>
# c= '{"a": True, "b": 2}'
# d=json.loads(c)
# json.decoder.JSONDecodeError: Expecting value: