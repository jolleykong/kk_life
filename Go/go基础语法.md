# command
- go run

- go build


# grammar
- 每个源文件
    - 开始都用package声明，指明这个文件属于哪个包。
    - 接着是import它导入其他包的列表。
    - 然后是func存储在文件中的程序声明。

- 名为main的包比较特殊，用来定义一个独立的可执行程序，而不是库。main总是程序开始执行的地方。

- import声明必须跟在package声明之后。
    - 导入的顺序没有关系，gofmt会按照字母顺序表进行排序。

- import声明之后，是组成程序的函数、变量、常量、类型（func、var、const、type）声明。
    - 声明的顺序没有关系。


- 函数声明
    一个函数的声明由func关键字、函数名、参数列表（main函数为空）、返回值列表（可为空）、放在大括号内的函数体 组成。

- Go不需要在语句或声明后面使用；结尾，除非有多个语句或声明出现在同一行。
    - { 操作符号必须和func在同一行，不能独立成行。
    - x+y表达式中，+后面可以有换行符，但是+前面不能换行。
- 函数和其他包级别的实体可以任意次序声明，调用可以出现在声明之前。



# for 循环

- go中唯一的循环语句。

- 第一种形式

  ```
  for i := 0; i <= 10; i++ {
  	fmt.Printf("%d,", i)
  }
  // 0,1,2,3,4,5,6,7,8,9,10,
  ```

- 第二种形式 == while

  ```
  // 没有声明和结束字句，即：没有initialization和post
  for i <= 10 {
  	// do someting when 1<=10.
  }
  ```

- 第三种形式 无限循环

  ```
  // 循环是无限的，可以通过break或return等语句进行终止。
  
  for {
  		fmt.Println(time.Now().Clock())
  		time.Sleep(time.Second * 1)
  	}
  	
  ```

  

# 语法要点

## 变量声明方法 var

- new(T)

  > 创建一个T类型变量，初始化为T类型的零值，返回其地址(*T)

1. 声明一个变量，指定类型。 默认值是类型零值

   ```
   var a int
   fmt.Println("a =", a)
   fmt.Printf("type of a = %T\n", a)
   ```

2. 声明一个变量，指定类型， 并初始化一个值

   ```
   var b int = 1
   fmt.Println("b =", b)
   fmt.Printf("type of b = %T\n", b)
   
   var bb string = "bbbbb"
   fmt.Printf("bb = %s,type of bb = %T\n", bb, bb)
   ```

3. 声明一个变量，初始化时省去数据类型

   ```
   var c = 1
   fmt.Println("c =", c)
   fmt.Printf("type of b = %T\n", b)
   
   var cc = "ccccc"
   fmt.Printf("cc = %s,type of cc = %T\n", cc, cc)
   ```

4. 常用，省去var关键字，直接自动匹配推算出类型。

   通常在一个函数内部使用，不适合包级别变量。

   ```
   // 唯独方法4与前三者不同。方法4只能在函数体内使用。
   // 操作符 := 声明并赋值 （对已经声明对象操作会报错）
   // 操作符 = 仅赋值（对未声明变量做赋值会报错）
   e := 100
   fmt.Println("e = ", e)
   fmt.Printf("type of e = %T\n", e)
   
   f := "ffffff"
   fmt.Println("f = ", f)
   fmt.Printf("type of f = %T\n", f)
   
   g := 3.1411111
   fmt.Println("g = ", g)
   fmt.Printf("type of g = %T\n", g)
   ```

### 声明多个变量

- 多个变量相同数据类型的

  ```
  var xx, yy int = 100, 200
  fmt.Println("xx= ", xx, " yy=", yy)
  ```

- 多个变量不同数据类型的

  ```
  var uu, vv = 100, "abcd"
  fmt.Println("uu= ", uu, " vv=", vv)
  ```

- 多行进行多个变量声明

  ```
  var (
  hh int    = 100
  jj bool   = true
  nn string = "bbvvccnn"
  )
  fmt.Println("hh=", hh, "jj=", jj, "nn=", nn)
  ```



### 声明常量 const

- 把var换成const 就是声明常量。

- 常量为只读属性，对常量进行修改会报错。

- 可以用常量来定义枚举类型

  ```
  	// 把var换成const 就是声明常量。
  	// 常量是只读属性噢。
  	const length int = 10
  	fmt.Println(length)
  
  	/* 对常量进行修改会报错。
  	length := 1000
  	fmt.Println(length)
  	*/
  
  	// 用const来定义枚举类型
  	const (
  		beijing  = 0
  		shanghai = 1
  		liaoning = 2
  		jilin    = 3
  	)
  	// 当枚举内容过多时，可以用iota
  	// 在const中添加一个关键字iota，每行的iota都会累加1
  	// 第一行的iota默认值为0
  
  	const (
  		bj = iota
  		sh
  		ln
  		jl
  	)
  
  	fmt.Println(beijing, shanghai, liaoning, jilin, bj, sh, ln, jl)
  
  	// iota可以参加数学运算，但是会有个小问题
  	// 参加数学运算后，iota依然只对自己进行自增，
  	// 因此在乘除时可能会出现预期之外的结果，如
  	const (
  		b = 10 * iota // 0
  		c             // 10*1 = 10
  		d             // 10*2 = 20
  	)
  	fmt.Println(b, c, d) // 0 10 20
  
  	// iota是以行作为单位进行自增的
  	const (
  		aa, bb = iota + 1, iota + 2 // iota=0,0 -> 0+1,0+2
  		cc, dd                      // iota=1,1 --> 1+1,1+2
  		ee, ff                      // iota=2,2 ---> 2+1,2+2
  		gg, hh = iota * 2, iota * 3 // iota=3,3 ----> 3*2,3*3
  		ii, jj                      // iota=4,4 -----> 4*2,4*3
  	)
  	fmt.Println(aa, bb, cc, dd, ee, ff, gg, hh, ii, jj) // 1 2 2 3 3 4 6 9 8 12
  ```

### 空标识符变量（临时变量） _

- Golang不允许临时变量，但可以用_ 空标识符来实现类似功能

- 空标识符_可以用在任何语法需要变量名，但程序逻辑不需要的地方

  ```
  for _, arg := range os.Args[1:] {
    do something with [arg]
  }
  
  // 每一次迭代，range产生一对值： 索引和这个索引对应的元素
  // 虽然例子里没使用索引，但是语法上range循环需要处理，因此
  // 使用空标识符 _ 来做“临时变量“，go不允许临时变量，
  // 空标识符_可以用在任何语法需要变量名，但程序逻辑不需要的地方
  // 如，丢弃每次迭代产生的无用索引。
  // 大多数go 程序员喜欢搭配range和_ 来写这个程序，
  // 因为索引在os.Args上是隐式的，使用_和range更不易犯错。
  ```

  

## 函数 func

### 函数的多返回值

1. 返回一个值的函数

   ```
   func foo1(a string, b int) int { // a b为两个形参，返回值为int类型，返回一个值
   	fmt.Println("a=", a)
   	fmt.Println("b=", b)
   
   	c := 100
   
   	return c
   }
   ```

2. 返回两个值的函数，匿名

   ```
   func foo2(a string, b int) (int, int) {
   	c := 101
   	d := 102
   	return c, d
   }
   ```

3. 允许给返回值命名，有形参名称

   ```
   func foo3(a string, b int) (r1 int, r2 int) {
   	r1 = 101 // 如果未对r1 r2赋值， 那么会返回为0。因为两个有名称的形参定义后，初始化的默认值是0值。
   	r2 = 102
   	return
   }
   ```

4. 多个返回值类型一致时，可以一次声明类型

   ```
   func foo4(a string, b int) (r1, r2 int) {
   	r1 = 201 // 如果未对r1 r2赋值， 那么会返回为0。因为两个有名称的形参定义后，初始化的默认值是0值。
   	r2 = 202
   	return
   }
   ```

### main函数与init函数

```
init函数与import导包执行顺序
	主main --> 
		import --> 
				const .. --> 
				var .. --> 
						子init() --> 
								子main()
```

### 匿名导入import以使用init()

> 从 init函数 一环节可以看到，在import包之后，调用函数时会先执行包的init()，
> 有一种情况就是，如果import了包，但只需要包的init()，除此之外在程序中并不需要
> 用到包中任何一个function，此时直接使用，在编译运行阶段会抛出错误，提示引用的包未被使用。
>
> 此时可以用_ 匿名的方式导入包，这样便无法使用包内方法，但会执行包的init方法。

```
import (
	// 方法1 匿名
	_ "06-import/lib1" // 以_作为别名给lib1，相当于以匿名方式导入lib1包

	// 方法2 常规导入
	"06-import/lib2" // 常规导入包

	// 方法3 命名别名
	kklib3 "06-import/lib3" // 以kklib3作为别名给lib3，方便后面以别名引用包。

	// 方法4 导入当前命名空间，尽量少用
	. "06-import/lib4" // 导入到当前命名空间，引用时无需加包名
)
```



### 指针

- `&x` 获取变量x的指针
- `*x` 获取变量x的值

```
// 使用指针的方法
func changeValue2(p *int) { // step1 ，* 表示p是一个指向int类型的指针
	*p = 10 //	step3，改变当前p所指向的内存地址的值。
}

func pointer() {
	var a int = 1
	changeValue2(&a)     // step2，&表示传递的是a的内存地址
	fmt.Println("a=", a) // a = 10
}

/*
changeValue2(p *int) ,在内存中创建p，值为初始化地址0
传参&a， 将a在内存中的地址赋值给p，即：p在内存中的数据为参数a的内存地址 p=&a
*p=10 ，修改p所指向的地址的值，即p中值指向a，修改a的值为10.此时a已经被修改。
*/

a := 100
changeValue2(a)
pointer()
```

> /*
>
> var addr        value
>
> a  0x0089AB     1           //
>
> p1 0x0999A1     0x0089AB    //一级指针，跳转一次便拿到目标。
>
> p2 0x0999B1     0x0999A1    //二级指针，两次
>
> p3 0x0999C1     0x0999B1    //三级指针，三次……
>
> */

```
// 交换两个变量值

// 值传递方式swap1
func swap1(a, b int) (int, int) {
	var temp int
	temp = a
	a = b
	b = temp
	return a, b
}

// 值传递方式 m1

func m1() {
	var a int = 10
	var b int = 20
	a, b = swap1(a, b)
	fmt.Println("a=", a, "b=", b)
}

// 指针方式 swap2 地址传递
func swap2(a, b *int) {
	var tmp int
	tmp = *a // tmp == main::a
	*a = *b  // main::a == main::b
	*b = tmp // main::b == tmp
}

// 地址传递方式 m2
func m2() {
	var a int = 10
	var b int = 20
	swap2(&a, &b)
	fmt.Println("a==", a, "b==", b)

	// 一级指针
	var p *int
	p = &a
	fmt.Println(&a) //0x14000122020
	fmt.Println(p)  //0x14000122020
	fmt.Println(&p) //0x1400011c020

	var pp **int //**int，二级指针
	pp = &p
	fmt.Println(&p)  //0x1400011c020
	fmt.Println(pp)  //0x1400011c020
	fmt.Println(&pp) //0x1400011c028
}

func main() {
	// 值传递方式m1
	m1() // a= 20 b= 10

	// 指针实现地址传递方式m2
	m2() // a== 20 b== 10

}
```



### defer

defer 在函数结束前执行， 多个defer会按照后进先出原则执行

- defer和return的先后顺序

  > return 和 defer 同时在一个函数中， return要优先于defer调用
  >
  > 可以理解为：defer 紧跟在函数}前面调用，return在`} `的前面
  >
  > ​		`return 0 ^}` ,其中`^ `的位置为refer的调用位置

### 



## 数组array

- 数组 array 的长度是固定的

- 固定长度的数组作为参数(形参)的时候,是严格匹配数组类型的

- 数组作为参数传入时,传入的是值拷贝的副本

- 数组形式

  ```
  数组 array形式:
  	myArray := [10]int			// 0,0,0,0,0,0,0,0,0,0
  	myArray := [10]int{1,2,3,4} // 1,2,3,4,0,0,0,0,0,0
  ```

  

### array声明

- 初始化

  ```
  var myArray1 [10]int
  ```

- 初始化并指定值

  ```
  // 前4个元素指定值， 后面元素默认0
  myArray2 := [10]int{1, 2, 3, 4}
  
  // 指定全部元素
  myArray3 := [4]int{11, 22, 33, 44}
  ```

- 查看数组类型

  ```
  fmt.Printf("myArray1 types = %T\n", myArray1) // myArray1 types = [10]int
  
  fmt.Printf("myArray2 types = %T\n", myArray2) // myArray2 types = [10]int
  
  fmt.Printf("myArray3 types = %T\n", myArray3) // myArray3 types = [4]int
  ```

  

### array使用

- 将数组作为参数传递会面临一个问题：数组形参是固定长度，不适用不同长度的数组，因此,需要将数组作为参数的时候,要使用动态数组。

  > 将数组作为参数传递
  >
  > ```
  > myArray10 := [4]int{11, 22, 33, 44}
  > printArrayA(myArray10) // 运行正常
  > 
  > myArray20 := [8]int{88, 77, 66, 55, 44, 33, 22, 11}
  > printArrayA(myArray20) 
  > // cannot use myArray20 (variable of type [8]int) as type [4]int in argument to printArray
  > ```

- 将数组作为参数传递,实际传入的是实参的副本(值拷贝)

  ```
  //实际传入的是实参的副本
  // 验证一下 -> demo2
  func printArrayB(myArray [4]int) {
  	// myArray是值拷贝,实际传入的是实参的副本
  	for idx, value := range myArray {
  		fmt.Println("idx:", idx, "value:", value)
  	}
  	myArray[0] = 999 // 修改的是拷贝的元素,并不是原数组对象.
  }
  
  func demo2() {
  	myArray10 := [4]int{11, 22, 33, 44}
  	printArrayB(myArray10)
  	// 调用函数后, 再次打印myArray10,来观察函数中myArray[0] = 999 动作是否对数组造成了修改
  	for idx, value := range myArray10 {
  		fmt.Println(idx, value)
  	}
  }
  
  demo2()
  ```

  

## 切片(动态数组) slice

- 动态数组 slice, 也叫切片, 长度是不定的

- 切片作为参数(形参)的时候,形参类型是一致的-->  如: []int

- 切片作为参数传入时,是引用传递,传递的是本身

- 动态数组\切片 slice 形式:

  ```
  	myArray := []int{}			// 什么也没有
  	myArray := []int{1,2,3,4} // 1,2,3,4 -- 给几个元素,就多长.
  ```

  

### slice声明

1. 声明,初始化定义默认值

   ```
   slice1 := []int{1, 2, 3}
   ```

   

2. 声明，再初始化

   ```
   var slice2 []int
   slice2 = make([]int, 3)
   ```

   

3. 声明,初始化分配空间

   ```
   var slice3 []int = make([]int, 3)
   ```

   

4. 声明,初始化分配空间

   ```
   slice4 := make([]int, 3)
   ```



### slice使用

- slice的追加

    > 1. 声明一个切片,长度为3,容量为5
    >
    >    ```
    >    var numbers = make([]int, 3, 5)
    >    fmt.Printf("len=%d,cap=%d,slice=%v\n", len(numbers), cap(numbers), numbers)
    >    
    >    // len=3,cap=5,slice=[0 0 0]
    >    ```
    >
    >    > ```
    >    > // 结构图简介
    >    > // [----    cap    ----]
    >    > // [--  len  --]
    >    > // | 0 | 0 | 0 | x | x |
    >    > //             ^
    >    > //            ptr
    >    > 
    >    > // len 长度: 0 ~ ptr
    >    > // ptr 尾部指针,永远指向当前切片的合法元素的最后位置
    >    > // cap 容量
    >    > // 后面的空间是不可以访问的,但底层已经开辟了.
    >    > ```
    >
    > 2. 需要开辟这部分空间, 要使用append
    >
    >    ```
    >    // 接下来向这个切片追加元素
    >    numbers = append(numbers, 1)
    >    fmt.Printf("len=%d,cap=%d,slice=%v\n", len(numbers), cap(numbers), numbers)
    >    // len=4,cap=5,slice=[0 0 0 1]
    >          
    >    // 继续追加1个元素
    >    numbers = append(numbers, 2)
    >    fmt.Printf("len=%d,cap=%d,slice=%v\n", len(numbers), cap(numbers), numbers)
    >    // len=5,cap=5,slice=[0 0 0 1 2]
    >          
    >    // 继续追加
    >    numbers = append(numbers, 1)
    >    fmt.Printf("len=%d,cap=%d,slice=%v\n", len(numbers), cap(numbers), numbers)
    >    // len=6,cap=10,slice=[0 0 0 1 2 1]
    >          
    >    // 自动扩容cap,会开辟已有cap长度的cap
    >    ```

- slice的截取

    ```
    // 切片的截取,是浅copy
    s := []int{1, 2, 3}
    s1 := s[0:1] // 0
    s2 := s[0:2] // 0,1
    s3 := s[:]
    fmt.Println(s1, s2, s3) // [1] [1 2] [1 2 3]
    
    s2[0] = 999             // 这个需要注意,和py不同.切片截取后,实际指针指向的依然是相同的内存地址.也就是浅copy
    fmt.Println(s1, s2, s3) // [999] [999 2] [999 2 3]
    ```

    

    - 深copy截取

        ```
        // 深copy方式将截取拷贝为副本
        // copy函数,将底层数组的slice一起拷贝
        s11 := []int{1, 2, 3}
        s22 := make([]int, 3) // 如果此时初始化的长度与s11长度不一致,短的话会截断,长的话会初始化0.
        
        copy(s22, s11)        // 将s11 深copy到s22
        fmt.Println(s11, s22) // [1 2 3] [1 2 3]
        
        s22[0] = 999
        fmt.Println(s11, s22) //[1 2 3] [999 2 3]
        ```

        

## map

### map声明

1. 声明,再开辟空间

   ```
   var myMap1 map[string]int
   myMap1 = make(map[string]int, 10)
   ```

2. 声明并开辟空间,但不初始化值

   ```
   myMap2 := make(map[string]string)
   ```

3. 声明并初始化值

   ```
   myMap3 := map[string]string{ 
   	"one": "php",
   	"two": "golang",
   	}
   ```


### map使用

- map作为实参传入的为地址

- 遍历

  ```
  cityMap := make(map[string]string)
  // 遍历
  	for key, value := range cityMap {
  		fmt.Println("key:", key)
  		fmt.Println("value:", value)
  	}
  ```

- 添加

  ```
  	cityMap["China"] = "Beijing"
  	cityMap["U.S"] = "NewYork"
  ```

- 修改

  ```
  cityMap["China"] = "BEIJING"
  ```

- 删除

  ```
  delete(cityMap, "U.S")
  ```

  

## 结构体 struct

## 结构体标签

## 反射

## OOP

- 封装
  - 属性的赋值使用 : 符号
- 继承
- 多态
- 闭包

## interface 万能类型

- 万能类型
- 类型断言

## golang高阶

- goroutine
- channel



# 包

## os包

- 提供一些函数和变量，以与平台无关的方式与操作系统打交道。
- os.Args 获取命令行参数
  - 字符串slice
  - go中所有索引使用半开区间，即：范围索引中，包含第一个索引，不包含最后一个索引

## bufio包

- 扫描器特性 Scanner
  `bufio.NewScanner()`
  `ipt := bufio.NewScanner(os.Stdin)`
- 每次调用input.Scan()读取下一行，并去掉结尾的换行符，再调用input.Text()获取读到的内容。Scan函数在读到新行时返回true，否则返回false

- fmt.Printf 支持格式化输出
  - 一般的，log.Printf、log.Errorf之类以f结尾的函数，使用和fmt.Printf 相同的格式化规则，默认不写换行符。
  - 以ln结尾的函数，则使用%v的方式来格式化参数，并在最后追加换行符。

| verb       | info                         |
| ---------- | ---------------------------- |
| `%d`       | 十进制整数                   |
| `%x,%o,%b` | 十六进制、八进制、二进制整数 |
| `%f,%g,%e` | 浮点数                       |
| `%t`       | 布尔                         |
| `%c`       | 字符                         |
| `%s`       | 字符串                       |
| `%q`       | 带引号的字符串或字符         |
| `%v`       | 内置格式的任何值             |
| `%T`       | 任何值的类型                 |
| `%%`       | 百分号本身                   |

## io/ioutil包

