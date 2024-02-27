# C++ String 常用方法总结

## 运算符重载

- `+`, `+=`：连接字符串 
- `=` ：字符串赋值 
- `>`, `>=`, `<`, `<=` ：字符串比较 
- `==`, `!=` ：比较字符串 
- `<<`, `>>` ：输入，输出字符串 

## 常用函数

```c++
cout << str.size() << endl;     //返回字符串长度
cout << str.length() << endl;   //返回字符串长度
cout << str.empty() << endl;    //检查 str 是否为空，为空返回 1，否则返回 0
```

测试与返回结果如下所示：

```bash
123456 // 测试字符串
6
6
0
```

### 查找

```c++
string str;
cin >> str;
cout << str.find("test") << endl; //返回字符串 test 在 str 的位置
cout << str.find("test", 2) << endl;  //在 str[2]~str[n-1] 范围内查找并返回字符串 test 在 str 的位置
cout << str.rfind("test", 2) << endl; //在 str[0]~str[2] 范围内查找并返回字符串 test 在 str 的位置
cout << endl;
cout << str.find_first_of("strTest") << endl; //返回 strTest 中任何一个字符首次在 str 中出现的位置
cout << str.find_first_of("strTest", 2) << endl; //返回 strTest 中任何一个字符首次在 str[2]~str[n-1] 范围中出现的位置
cout << str.find_first_not_of("strTest") << endl; //返回除 strTest 以外的任何一个字符在 str 中首次出现的位置
cout << str.find_first_not_of("strTest", 2) << endl; //返回除 strTest 以外的任何一个字符在 str[2]~str[n-1] 范围中首次出现的位置
cout << endl;
cout << str.find_last_of("strTest") << endl; //返回 strTest 中任何一个字符最后一次在 str 中出现的位置
cout << str.find_last_of("strTest", 2) << endl; //返回 strTest 中任何一个字符最后一次在 str[0]~str[2] 范围中出现的位置
cout << str.find_last_not_of("strTest") << endl;    //返回除 strTest 以外的任何一个字符在 str 中最后一次出现的位置
cout << str.find_last_not_of("strTest", 2) << endl; //返回除 strTest 以外的任何一个字符在 str[0]~str[2] 范围中最后一次出现的位置
cout << endl;
cout << string::npos;  //以上函数如果没有找到，均返回string::npos
```

测试与返回结果如下所示：

```bash
0123test89strTest // 测试数据，以下依次为结果
4
4
4294967295
4
4
0
2
16
4294967295
9
2
4294967295
```

### 子串

```c++
cout << str.substr(3) << endl;      //返回 [3] 及以后的子串
cout << str.substr(2, 4) << endl;   //返回 str[2]~str[2+(4-1)] 子串(即从[2]开始4个字符组成的字符串)
```

测试与返回结果如下所示：

```bash
myStringTest //测试数据，以下依次为结果,下同

tringTest

Stri
```

### 替换

```c++
cout << str.replace(2, 4, "test") << endl; //返回把 [2]~[2+(4-1)] 的内容替换为 "test" 后的新字符串
cout << str.replace(2, 4, "qwer", 3) << endl; //返回把 [2]~[2+(4-1)] 的内容替换为 "qwer" 的前3个字符后的新字符串 
```

测试与返回结果如下所示：

```bash
yyyyyyyyyyyyyy

yytestyyyyyyyy

yyqweyyyyyyyy
```

### 插入

```c++
cout <<  str.insert(2, "test") << endl; //从 [2] 位置开始添加字符串 "test"，并返回形成的新字符串
cout <<  str.insert(2, "string", 3) << endl; //从 [2] 位置开始添加字符串 "string" 的前 3 个字符，并返回形成的新字符串
cout <<  str.insert(2, "123456", 1, 3) << endl; //从 [2] 位置开始添加字符串 "123456" 的前 [2]~[2+(3-1)] 个字符，并返回形成的新字符串
```

测试与返回结果如下所示：

```bash
yyyyyyyyy

yytestyyyyyyy

yystrtestyyyyyyy

yy234strtestyyyyyyy
```

### 追加

```c++
str.push_back('1'); //在 str 末尾添加字符'1'
cout << str << endl;
cout << str.append("abc") << endl; //在 str 末尾添加字符串"abc"
```

测试与返回结果如下所示：

```bash
asdf

asdf1

asdf1abc
```

### 删除

```c++
string str1 = str;
cout << str.erase(3) << endl;//删除 [3] 及以后的字符，并返回新字符串
cout << str1.erase(3, 5) << endl;//删除从 [3] 开始的 5 个字符，并返回新字符串
```

测试与返回结果如下所示：

```bash
1234567890

123

12390
```

### 交换

```c++
string str1, str2;
cin >> str1;
cin >> str2;
str1.swap(str2);//把 str1 与 str2 交换
cout << endl;
cout << str1 << endl << str2 << endl;
```

测试与返回结果如下所示：

```bash
123456
qwerty

qwerty
123456
```

## 参考文献

- [C++ string 字符串函数详解](https://www.renfei.org/blog/introduction-to-cpp-string.html)
- [string - C++ Reference](http://www.cplusplus.com/reference/string/string/) 