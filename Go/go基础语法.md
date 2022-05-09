## command
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



## 数组array [10]int{}

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

  

## 切片(动态数组) slice []int{}

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

        

## map map[string]string{}

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

- map作为实参传入的为map对象地址

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

### 定义结构体

```
// 2.定义一个结构体Book
type Book struct {
	title string
	auth  string
}

// 3.传递的是book的副本？(尝试修改book的内容来验证)
func changeBook(book Book) {
	book.auth = "new_auth"
}

// 4.传入指针
func changeBook2(book *Book) {
	book.auth = "new_auth"
}


func main() {
	// 2.type定义结构体
	var book1 Book
	book1.title = "Learning Golang"
	book1.auth = "kk"
	fmt.Printf("book1 type is :%T\n", book1) // book1 type is :main.Book
	fmt.Printf("%v\n", book1)                // {Learning Golang kk}

	// 3.验证实参传入type时，传入的是副本
	changeBook(book1)         // 传入book1，看book1.auth是否会被函数修改。
	fmt.Printf("%v\n", book1) // {Learning Golang kk}， 未被修改。

	// 4.传入指针
	changeBook2(&book1)       // 注意传入的是指针
	fmt.Printf("%v\n", book1) // {Learning Golang new_auth}
}
```



### 封装

- 属性的赋值使用 `:` 符号

- 访问对象的方法/属性时，可以不需要使用指针，最终结果一致。

- 修改对象的属性时，需要传递对象指针，否则修改的是对象的副本。

- 类名、属性名、方法名的首字母大写（公有）、首字母小写（私有）

  - 如果类名 首字母大写，表示其他包也能够访问，也能通过这个类来实体化对象。
  - 如果类的属性名 首字母大写，表示该属性能够对外访问（公有），否则只能供类内部使用（私有）。
  - 类的方法同理

  ```
  // 定义一个英雄类
  type Hero struct {
  	// 定义方法...
  	Name  string
  	Ad    int
  	Level int
  }
  
  // 为英雄类定义方法
  func (this Hero) Show() { // this 可以理解为self，指结构体自身，只是个变量名。
  	// this Hero的Hero 表示当前func属于结构体Hero
  	fmt.Println("name =", this.Name)
  	fmt.Println("AD =", this.Ad)
  	fmt.Println("level =", this.Level)
  }
  
  // 为英雄类定义方法
  //    self|class|funcName|out data type
  func (this Hero) GetName() string {
  	return this.Name
  }
  
  // 为英雄类定义方法
  //    self|class|funcName|ArgName|ArgType
  //      ↓    ↓      ↓        ↓       ↓
  func (this Hero) SetName(newName string) {
  	// this 是调用该方法的对象的一个副本
  	this.Name = newName
  }
  
  // 为英雄类定义方法
  // 下面这些函数名+2的，都改为了指针传入
  func (this *Hero) Show2() {
  	// 对于只访问不修改的行为，结果上来看，(*Hero)Show2() == (Hero)Show()
  	fmt.Println("name =", this.Name)
  	fmt.Println("AD =", this.Ad)
  	fmt.Println("level =", this.Level)
  }
  
  // 为英雄类定义方法
  //    self|class_pointer|funcName|out data type
  //      ↓     ↓          ↓         ↓
  func (this *Hero)   GetName2()  string {
  	return this.Name
  }
  
  // 为英雄类定义方法
  //    self|class_pointer|funcName|ArgName|ArgType
  //      ↓     ↓           ↓         ↓      ↓
  func (this *Hero)     SetName2(newName string) {
  	this.Name = newName
  }
  
  func main() {
  	// 创建一个对象
  	hero := Hero{Name: "kk", Ad: 100, Level: 1} // 属性的赋值使用 :
  	hero.Show()                                 // name = kk
  	/*	name = kk
  		AD = 100
  		level = 1*/
  
  	// 尝试这样调用修改，发现是不变的…… 传入的是副本！
  	hero.SetName("yyyyy")
  	hero.Show()
  	/*	name = kk
  		AD = 100
  		level = 1*/
  	// 因此，要通过指针的方式传入参数……
  
  	fmt.Println("-----")
  	hero2 := Hero{Name: "yy", Ad: 111, Level: 11}
  	hero2.Show()
  	hero2.SetName2("KKYY")
  	hero2.Show()
  	/*	name = yy
  		AD = 111
  		level = 11
  		name = KKYY
  		AD = 111
  		level = 11
  		*/
  }
  ```

  

### 继承

- 在结构体声明中引入需要被继承的结构体

  ```
  // 定义类：人
  type Human struct {
  	name string
  	sex  string
  }
  
  func (this *Human) Eat() {
  	fmt.Printf("%v eating\n", this.name)
  }
  
  func (this *Human) Walk() {
  	fmt.Printf("%v walking\n", this.name)
  }
  
  // 定义类：超人
  // 超人会继承人的属性
  type Superman struct {
  	Human // 继承了Human类，好省事儿……
  	level int
  }
  
  // 重定义父类方法
  func (this *Superman) Eat() {
  	fmt.Println("超人吃饭！")
  }
  
  // 定义子类新方法
  func (this *Superman) Fly() {
  	fmt.Printf("%v is flying!\n", this.name)
  }
  
  func main() {
  	h := Human{name: "kk", sex: "M"}
  	h.Eat() // kk eating
  
  	// 定义一个子类对象
  	s := Superman{Human{"yy", "M"}, 99} // 这里用name:"yy" 会报错，奇怪。
  	s.Fly()                             // yy is flying!
  	s.Eat()                             // 超人吃饭！
  	s.Walk()                            // yy walking
  
  	// 另一种定义子类对象的方法
  	var b Superman
  	b.name = "bb"
  	b.sex = "M"
  	b.level = 99
  	b.Fly()  // bb is flying!
  	b.Eat()  // 超人吃饭
  	b.Walk() // bb walking
  }
  
  ```

  

### 多态

- 多态：通过调用父类暴露的接口，实现子类定义的方法功能

  > 定义一个接口完成多态的实现：
  >
  > ​    - 父类定义接口，
  >
  > ​    - 子类实现接口（实现父类的全部接口！”全部“是关键词）。
  >
  > ​    - 父类类型的变量，指向给子类的具体数据变量。
  >
  > 相当于， 谁能干这个活儿，就指针到谁那里，让它干- -！

  ```
  // Animal InterFace 本质上是一个指针
  type AnimalIF interface {
  	Sleep()
  	GetColor() string // 获取动物颜色
  	GetType() string  // 获取动物种类
  }
  
  
  // 具体的类
  type Cat struct {
  	// AnimalIF	// 从语法来说，要继承Animal接口，但这里不用这样，否则接口就没意义了。
  	// 只要实现animal interface的三个方法，就等于Cat继承了AnimalIF
  	color string // 猫的颜色
  }
  
  
  // Cat类要把接口中的方法全部实现，否则指向接口中的指针不完全（待补充，没彻底明白）
  func (this *Cat) Sleep() {
  	fmt.Printf("%v color cat had been sleep.\n", this.color)
  }
  
  func (this *Cat) GetColor() string {
  	return this.color
  }
  
  func (this *Cat) GetType() string {
  	return "Cat"
  }
  
  
  // 具体的类，同Cat类一样，要在类中将Interface中定义的方法全部实现。
  type Dog struct {
  	color string
  }
  
  func (this *Dog) Sleep() {
  	fmt.Printf("%v color dog had been sleep.\n", this.color)
  }
  
  func (this *Dog) GetColor() string {
  	return this.color
  }
  
  func (this *Dog) GetType() string {
  	return "Dog"
  }
  
  // 至此，一个interface实现了两个具体的类。
  
  
  // 附加一个，把对接口的调用再封装一下。
  func showAnimal(animal AnimalIF) {
  	animal.Sleep()                           // 传入什么调用什么， （多态） 如：传入Cat，就指向Cat的Sleep()方法。
  	fmt.Println("color=", animal.GetColor()) // 同理。
  	fmt.Println("type=", animal.GetType())
  
  }
  
  func main() {
  	var animal AnimalIF    // 定义变量animal, 接口的数据类型, 就是父类的指针
  	animal = &Cat{"green"} // interface本身接收的是指针，因此要传入指针。
  	animal.Sleep()         // 调用Cat的Sleep() 方法
  	// green color cat had been sleep.
  
  	animal = &Dog{"red"}
  	animal.Sleep() // 调用Dog的Sleep方法，这就发生了多态现象
  	// red color dog had been sleep.
  
  	// 附加的那个。
  	fmt.Println("==============")
  	Tom := Cat{"Blue"}
  	Wangwang := Dog{"White"}
  	showAnimal(&Tom)
  	showAnimal(&Wangwang)
  	/*
  		Blue color cat had been sleep.
  		color= Blue
  		type= Cat
  		White color dog had been sleep.
  		color= White
  		type= Dog
  	*/
  
  }
  ```

  

### 闭包



### 结构体标签

#### 结构体标签在json中的作用：使用json转换结构体

```
/*
	结构体标签在json中的作用
*/
package main

import (
	"encoding/json"
	"fmt"
)

// 定义一个Movie类
//   要想使json库正常转换结构体,需要结构体指定json tag
type Movie struct {
	Title  string   `json:"title"` // 符合json标签规则,即:指定json的key
	Year   int      `json:"year"`
	Price  int      `json:"price"`
	Actors []string `json:"actors"`
}

func main() {

	// 1. 结构体转json

	movie := Movie{"让子弹飞", 2010, 90, []string{"姜文", "葛优", "周润发"}}

	// struct --> json
	jsonStr, err := json.Marshal(movie)
	if err != nil {
		fmt.Println("json marshal error", err)
		return
	}
	// 输出
	fmt.Printf("jsonStr = %s \n", jsonStr) // jsonStr = {"title":"让子弹飞","year":2010,"price":90,"actors":["姜文","葛优","周润发"]}
	// fmt.Println(jsonStr) 不行,会输出奇怪的东西.

	// 2. json转结构体
	// jsonStr = {"title":"让子弹飞","year":2010,"price":90,"actors":["姜文","葛优","周润发"]}
	// 首先定义一个结构体
	movie2 := Movie{}
	err = json.Unmarshal(jsonStr, &movie2)
	if err != nil {
		fmt.Println("json to struct failed,", err)
		return
	}
	fmt.Printf("%v,%T\n", movie2, movie2) // {让子弹飞 2010 90 [姜文 葛优 周润发]},main.Movie

}

```



#### 通过反射获取结构体标签



## interface 万能类型

### 万能类型

- interface 属于通用万能类型,

- interface{} 空接口
  - int\string\float32\float64\struct 都实现了interface{},可以用interface{}类型引用任意的数据类型.

- interface 使用类型断言机制,对引用的数据进行类型判断.

  ```
  // interface{} 是万能数据类型
  func myFunc(arg interface{}) {
  	fmt.Println(arg)
  	// interface{} 如何区分此时引用的底层数据类型是什么类型?
  
  	// 给interface{}提供"类型断言"机制,
  	//    即:允许interface进行类型判断
  	// 判断arg是否为字符串
  	// 		arg.(string)   判断arg是否为string类型
  	value, ok := arg.(string)
  	if !ok {
  		fmt.Println("arg is not string.")
  		fmt.Printf("value type : %T\n", arg) 
  	} else {
  		fmt.Println("arg is string type,value=", value)
  	}
  }
  
  type Books struct {
  	auth string
  }
  
  func main() {
  	myFunc(23) // 23
  	// 				arg is not string.
  	// 				value type : int
  
  	book := Books{"kk"}
  	myFunc(book) // {kk}
  	//				arg is not string.
  	//				value type : main.Books
  
  	myFunc("ss") // ss
  	//				arg is string type,value= ss
  
  }
  ```

  

### 



### 类型断言

- 断言：
  1. 得到动态类型 type (来自pair结构)
  2. 判断type是否实现了目标接口

#### 变量的内置pair结构

类型断言的实现机制。

> - golang中定义的变量,实际变量是由两部分构成:type,value.
>   - type和value就是变量的pair结构.每个变量都有两个指针指向type和value.
>     - type 当前变量的类型
>     - value 当前变量的值
>   - type 当前变量的类型分为两类, 一个变量只能是其中一种的类型.
>     - static type 静态类型: 基本的类型,int float string等等等等.
>     -  concrete type 具体类型: 具体类型就是interface所指向的具体数据类型,即:系统runtime实际看到的类型.

```
/*示例*/
func main() {

	// 1.
	var a string // pair < statictype:string, value:"abced">
	a = "abced"

	// 2.
	var allType interface{} // pair<type:string, value:"abced">
	allType = a

	value, ok := allType.(string)
	fmt.Println(value, ok) // abced true.变量赋值给其他变量后,变量的pair也不会变化.

	// 3.
	// tty: pair <type:*os.File,value:"/dev/tty" 文件描述符>
	tty, err := os.OpenFile("/dev/tty", os.O_RDWR, 0)

	if err != nil {
		fmt.Println("open error", err)
		return
	}

	// r:pair<type: , value: >
	var r io.Reader
	
	// r:pair<type: *os.File, value: "/dev/tty" 文件描述符>
	r = tty

	// w:pair<type:,value:>
	var w io.Writer
	
	// w:pair<type: *os.File ,value: "/dev/tty" 文件描述符>
	w = r.(io.Writer) // 断言

	w.Write([]byte("HELLO this is a test!")) // HELLO this is a test!

}
```

```
/* 换一种理解方式去理解示例*/
// 定义接口Reader
type Reader interface {
	ReadBook()
}

// 定义接口Writer
type Writer interface {
	WriteBook()
}

// 定义类Book
type Book struct {
}

// 定义类方法ReadBook()
func (this *Book) ReadBook() {
	fmt.Println("read a book")
}

// 定义类方法WriteBook()
func (this *Book) WriteBook() {
	fmt.Println("write a book")
}

func main() {
	// b pair <type: Book, value: 实例化对象的地址>
	b := &Book{} // Book类实例化对象后的指针

	// r: pair<type:null,value:null>
	var r Reader
	
	// fmt.Printf("%T,%v\n", r, r)	// <nil>,<nil>,即:r: pair<type:null,value:null>
	
	// r: pair<type:Book,value:实例化对象的地址>
	r = b

	// Book.ReadBook()
	r.ReadBook() // read a book

	// w: pair<type:null,value:null>
	var w Writer

	// 断言
	//   step 1. 得到动态类型 type
	//   step 2. 判断type是否实现了目标接口

	// 1. 得到type:Book(r的type是Book),
	// 2.Book是否实现了Writer()? 实现了 --> 断言成功.即:reader指向的Book对象,Book对象实现了Writer接口
	// w: pair<type:Book,value:实例化对象的地址>
	w = r.(Writer)

	w.WriteBook() // write a book

}
```





### 反射

- golang中定义的变量,实际变量是由两部分构成:type,value.

- 反射就是通过变量,获取type或value

  > - ValueOf
  >
  > ​        获取输入参数接口中的数据的值,如果接口为空则返回0
  >
  > ​       `func ValueOf(i interface{}) Value (...)`
  >
  > - TypeOf
  >
  > ​        动态获取输入参数接口中的值的类型,如果接口为空则返回nil
  >
  > ​       `func TypeOf(i interface{}) Type (...)`

- 反射使用了reflect包

- 简单反射

  ```
  import (
  	"fmt"
  	"reflect"
  )
  
  // 定义一个方法,传入变量后,返回变量的类型和变量的值
  func relectNum(arg interface{}) {
  	// 对arg进行反射处理
  	fmt.Println("type:", reflect.TypeOf(arg))
  	fmt.Println("value:", reflect.ValueOf(arg))
  
  }
  
  func main() {
  	// 比较简单的反射
  	var fnum float64 = 1.2345
  	relectNum(fnum)
  	// 		type: float64
  	// 		value: 1.2345
  }
  
  ```

  

- 复杂反射

  ```
  import (
  	"fmt"
  	"reflect"
  )
  
  // 定义User类
  type User struct {
  	Id   int
  	Name string
  	Age  int
  }
  
  // 打印对象信息
  func (this *User) Call() { // 传入指针的方法不被记入inputType.NumMethod(),回头研究一下为什么.
  	// 据说在go 1.17开始 NumMethod() 只能导出接口的不公共的方法.
  	fmt.Println("user is called..")
  	fmt.Printf("%v\n", this)
  }
  func (this User) Call2() {
  	fmt.Println("user is called..")
  	fmt.Printf("%v\n", this)
  }
  
  func DofiledAndMethod(input interface{}) {
  	// 获取input的type
  	inputType := reflect.TypeOf(input)
  	fmt.Println("type :", inputType)
  
  	// 获取input的value
  	inputValue := reflect.ValueOf(input)
  	fmt.Println("value:", inputValue)
  
  	// 通过type获取里面的属性
  	//  1.获取interface的reflect.Type,通过Type 得到NumField,即:属性数量,进行遍历
  	//  2.得到每一个Field,数据类型
  	//  3.通过field的Interface()方法,得到对应的value.
  	for i := 0; i < inputType.NumField(); i++ {
  		field := inputType.Field(i)              // 获取字段类型,type
  		value := inputValue.Field(i).Interface() // 获取字段值,value
  		//fmt.Println(field, value)
  		fmt.Printf("type: %s:%v=%v\n", field.Name, field.Type, value)
  	}
  
  	// 通过type,获取里面的方法method
  	// go 1.17开始,Call()方法传入指针的话不会被统计. 回头研究这块细节.
  	// 临时完成实验的方法是使用Call2(),即:不使用指针传入,该为值传入.
  	for i := 0; i < inputType.NumMethod(); i++ {
  		m := inputType.Method(i)
  		fmt.Printf("method: %s:%v\n", m.Name, m.Type)
  	}
  }
  
  func main() {
  	user := User{1, "kk", 21}
  	user.Call()
  	fmt.Println("----------------------")
  	DofiledAndMethod(user)
  	/*
  		type : main.User
  		value: {1 kk 21}
  		{Id  int  0 [0] false} 1
  		Id:int=1
  		{Name  string  8 [1] false} kk
  		Name:string=kk
  		{Age  int  24 [2] false} 21
  		Age:int=21
  
  	*/
  }
  
  ```

#### 通过反射获取结构体标签

```
/*
	反射解析结构体标签
		结构体标签,就是结构体属性的注释,类json
		格式: `info:"name"` kv结构,支持多个kv,用空格间隔
*/
package main

import (
	"fmt"
	"reflect"
)

// 定义结构体,定义结构体标签
type resume struct {
	Name string `info:"name"`         // kv结构
	Sex  string `info:"sex" doc:"性别"` // 可以有多个kv
}

// 通过反射获取结构体标签
func findTag(str interface{}) {
	// 反射获取结构体全部元素,Elem() 表示获取当前结构体元素
	t := reflect.TypeOf(str).Elem()

	for i := 0; i < t.NumField(); i++ {
		taginfostring := t.Field(i).Tag.Get("info")
		fmt.Println("info:", taginfostring)
		//
		tagdocstring := t.Field(i).Tag.Get("doc")
		fmt.Println("doc:", tagdocstring)
	}
}

func main() {
	var kk resume // 实例化对象
	findTag(&kk)  // findTag()中使用了.Elem(),因此这里要传入指针.
	/*
	   info: name
	   doc:
	   info: sex
	   doc: 性别
	*/

}

```





# goroutine

- 创建goroutine

  ```
  /*
  	通过go 关键字来开辟一个goroutine
  		i.e: go newTask()
  	通过 runtime.Goexit() 退出当前的goroutine
  
  */
  
  package main
  
  import (
  	"fmt"
  	"time"
  )
  
  // 子 goroutine
  func newTask() {
  	i := 0
  	for {
  		i++
  		fmt.Printf("new goroutine: i = %d \n", i)
  		time.Sleep(1 * time.Second)
  	}
  }
  
  // 主 goroutine
  func main() {
  	// 创建一个goroutine ,执行newTask()流程
  	go newTask()
  
  	i := 0
  	for {
  		i++
  		fmt.Printf("new goroutine: i = %d \n", i)
  		time.Sleep(1 * time.Second)
  	}
  }
  
  ```

  ```
  /*
  
   */
  
  package main
  
  import (
  	"fmt"
  	"time"
  )
  
  // 子 goroutine
  func newTask() {
  	i := 0
  	for {
  		i++
  		fmt.Printf("new goroutine: i = %d \n", i)
  		time.Sleep(1 * time.Second)
  	}
  }
  
  // 主 goroutine
  func main() {
  	// 创建一个goroutine ,执行newTask()流程
  	go newTask()
  
  	fmt.Println("main goroutine exit.") // 主goroutine退出后,所有子goroutine立即结束
  
  	/*  主goroutine死循环部分
  	i := 0
  	for {
  		i++
  		fmt.Printf("new goroutine: i = %d \n", i)
  		time.Sleep(1 * time.Second)
  	}
  	*/
  
  }
  
  
  ```

  

## 匿名无参数函数加载goroutine

```
import (
	"fmt"
	"runtime"
	"time"
)

// 无传参无返回值的匿名函数 加载goroutine.
func main() {
	// 用go创建一个形参为空 返回为空的匿名函数
	go func() { //#1
		defer fmt.Println("A.defer")

		func() { //#2
			defer fmt.Println("B.defer")
			// 运行完便结束了,退出当前goroutine
			// return	return的话,只退出当前子函数(#2).也就是B不会被打印,但不影响外层循环的执行
			runtime.Goexit() // runtime.Goexit() 会退出整个goroutine(#2,#1),也就是B不会打印,A也不会打印.
			fmt.Println("B")
		}() // 注意这个用法

		fmt.Println("A")
	}() // 注意这个用法

	// 死循环
	for {
		time.Sleep(1 * time.Second)
	}
}

/*
B.defer
A.defer
*/

```

## 匿名有参数函数加载goroutine

```
import (
	"fmt"
	"time"
)

func main() {
	// 有传参返回值的匿名函数 加载goroutine.
	go func(a int, b int) bool { // 定义形参和返回类型, 匿名函数
		fmt.Println("a:", a, "b", b)
		return true
	}(10, 20) // 注意这个用法,传参.

	// 死循环
	for {
		time.Sleep(1 * time.Second)
	}
}

/*
a: 10 b 20
*/


/*
如何得到返回的true?
flag := go func(a int, b int) bool { ... 是不支持的, 函数不会把返回值抛给函数上一层
无法通过返回值拿到的, 这需要后面的channel知识来实现.--> 想让两个goroutine过程中间互相通信,使用channel
*/
```



# channel

- goroutine之间通信, 使用channel 管道
- channel有同步两个不同goroutine之间的能力

## channel基础

- 定义channel

  ```
  // 使用make()方法创建并初始化channel
  make(chan Type) // 等价于 make(chan Type,0) , 指定channel中互相传递的数据类型,
  
  make(chan Type, capacity) // 有无缓冲
  ```

- channel 基础使用

  > 向channel中写数据
  >
  > - channel <- value   // 发送value到channel
  > - <-channel               // 接收并将其丢弃
  > - x := <-channel        // 从channel中接收数据,并赋值给x
  > - x, ok := <-channel   // 功能同上,同时检查通道是否已经关闭或者是否为空
  >
  > ```
  > // 定义一个channel,并简单使用一下.
  > func main() {
  > 	// 定义一个channel
  > 	c := make(chan int) // c:=make(chan int,0)
  > 
  > 	// 开启一个goroutine
  > 	go func() {
  > 		defer fmt.Println("goroutine end.")
  > 		fmt.Println("goroutine running.")
  > 
  > 		c <- 666 // 将666发送到c
  > 	}()
  > 
  > 	num := <-c // 从c中接收数据并赋值给num
  > 
  > 	fmt.Println(num)
  > 	/*	当注释掉 num := <-c 和 fmt.Println(num) 时,也就是main永远不执行对channel传入的值,开启下面循环,会发现sub goroutine也永远被阻塞.
  > 		for {}
  > 	*/
  > 	fmt.Println("main goroutine end.")
  > }
  > ```
  >
  > > goroutine running.
  > > goroutine end.
  > > 666
  > > main goroutine end.
  >
  > - 如果main先于sub goroutine执行到num赋值,sub goroutine此时还没有将值发送给channel c,那么main会在num赋值这里被阻塞,等待channel 的传入后,再继续进行.这就是为何每次都是main 最后退出,而不会出现main先于num执行完毕的情况.
  >
  > - 同理,如果sub goroutine已经执行过c<-666,defer过后即将exit,但此时main还未执行到num赋值,那么sub也会被阻塞,直到main从channel中拿到值,sub才会继续进行下去(完成退出),也就是sub的defer肯定在main的num动作后才会执行.
  > - 也就是说,如果main不执行num := <-c,sub会永远被阻塞.(试一试,是这样的.)

## 有无缓冲的同步

### 无缓冲的channel在goroutine之间同步的过程

1. 两个goroutine都到达通道,但都没有执行发送或接收
2. 发送端goroutine向通道发送数据,此时该goroutine被锁住
3. 接收端goroutine从通道接收数据,此时该goroutine被锁住
4. 数据交换ing
5. 直到交换完成,发送和接收端goroutine的锁被释放,
6. goroutine们可以做其他事情了

### 有缓冲channel同步的过程

1. 接收端goroutine从channel中接收一个值,独立接收
2. 发送端goroutine向channel中发送新值,独立发送
3. 发送端向channel中发送新值,接收端从channel中接收另一个值,彼此之间不同步,也不阻塞
4. 当所有的发送和接收都完成时,通道里还有几个值,也有一些空间可以存放更多的值.
5. 当channel为空时,从channel中接收数据会阻塞,同理,当channel满时,向channel中发送数据会被阻塞.

```
package main

import (
	"fmt"
	"time"
)

func main() {
	// 初始化一个带有缓冲的channel c,
	c := make(chan int, 3)
	fmt.Println("len:", len(c), "cap:", cap(c)) // len: 0 cap: 3

	// 开启一个子goroutine
	go func() {
		defer fmt.Println("sub goroutine end.")

		for i := 0; i <= 5; i++ {
			c <- i
			fmt.Println("in len:", len(c), "cap:", cap(c), "current:", i)
		}
	}()

	time.Sleep(1 * time.Second)

	for i := 0; i <= 5; i++ {
		num := <-c
		fmt.Println("num:", num)
	}

	fmt.Println("main goroutine end.")
}

/*
	len: 0 cap: 3
	in len: 1 cap: 3 current: 0
	in len: 2 cap: 3 current: 1
	in len: 3 cap: 3 current: 2	// 缓冲容量满
	num: 0
	num: 1
	num: 2
	num: 3						// 缓冲消耗的同时,新值被插入,这一块没法同时打印,因此有顺序的误解
	in len: 3 cap: 3 current: 3	// 同上
	in len: 0 cap: 3 current: 4
	in len: 1 cap: 3 current: 5
	sub goroutine end.		// 同上
	num: 4
	num: 5
	main goroutine end.

*/
```



## 关闭channel

1. channel不像文件一样需要经常去关闭,只有确实没有任何发送数据了,或者想显式的结束range循环之类的,才会去关闭channel
2. 关闭channel后,无法向channel再发送数据. 即:再发送会引发panic错误,(错误后导致接收立即返回0)
3. 关闭channel后,可以继续从channel接收数据.
4. 对于nil channel,无论收发都会被阻塞.(nil channel ,即没经过make的channel,只做了var chan channel 声明的通道.)

```
/*
	关闭channel
*/
package main

import "fmt"

func main() {
	c := make(chan int)

	go func() {
		for i := 0; i < 5; i++ {
			c <- i
		}

		// close 关键字,关闭一个channel
		close(c)
	}()

	for {
		// ok如果为true,表示channel没有关闭,否则为已经关闭
		if data, ok := <-c; ok { // if的另一种简写方式
			fmt.Println(data)
		} else {
			break
		}
	}

	fmt.Println("main end.")
}
```

> /* 不关闭channel,即://close(c) ,输出结果会有报错,main 并未执行完便抛出了异常
> 0
> 1
> 2
> 3
> 4
> fatal error: all goroutines are asleep - deadlock!
> 	//   sub goroutine 完成了传入, main goroutine 接收完了channel中的数据,
> 	//   继续请求数据被阻塞,这就导致main的循环永远不会结束,进入死锁
>
> */
>
> /* 关闭channel,即:close(c),main执行完成,无异常
> 0
> 1
> 2
> 3
> 4
> main end.
>
> */



## channel与range的配合使用

```
/*
	channel与range的配合使用.

	for data := range c { } // range c : 尝试从channel c 中读数据,如果c中有数据,range就返回值,否则就阻塞

*/
// 复用channel的关闭的代码
package main

import "fmt"

func main() {
	c := make(chan int)

	go func() {
		for i := 0; i < 5; i++ {
			c <- i
		}

		// close 关键字,关闭一个channel
		close(c)
	}()

	/*
		for {
			// ok如果为true,表示channel没有关闭,否则为已经关闭
			if data, ok := <-c; ok { // if的另一种简写方式
				fmt.Println(data)
			} else {
				break
			}
		}
	*/
	// 这段for 可以简写. 用range来迭代,不断操作channel
	for data := range c { // range c : 尝试从c读数据,如果c中有数据,range就返回值,否则就阻塞
		fmt.Println(data)
	}

	fmt.Println("main end.")
}

```

## channel与select配合使用

> select具备多路channel的监控状态功能:
>
> - 单流程下,一个go只能监控一个channel的状态.
> - select可以完成监控多个channel的状态.
> - select动作是无序的,这个需要关注.
> - select可以和for搭配使用, 循环判断.
>
> 	select {
> 	  case <- chan1:
> 	  // 如果chan1成功读到数据,则进行该case处理语句
> 	  case chan2 <- 1:
> 	  // 如果成功向chan2 写入数据,则进行该case处理语句
> 	  default:
> 	  // 如果上面都没有成功,则进入default处理流程
> 	}

```
package main

import (
	"fmt"
)

func fibonacii(c, quit chan int) {
	x, y := 1, 1 // 初始化xy
	
	for {        // 开启循环
	
		select { // select的动作是无序的,也就是会随机select一个ready的case, 这里需要注意.这并不是按照书写的case顺序去依次顺次判断的.
		
		case c <- x:
		
			// 如果c可写,该case就会进来
			x, y = y, x+y // 赋值,赋值后x传入c,本次select结束,继续下一次for循环做select判断.

		case <-quit:
		
			// (select是无序的)sub go中完成10次循环后,会向quit中传入0,此时quit有效,select无序选择中选中了该case,for循环结束,函数调用结束.
			fmt.Println("quit")
			return // 结束for循环,也就是结束了fibonacii() .

			//default:
			//		用来验证select是无序的.
			//	fmt.Println("default")
		}
	}
}

func main() {
	c := make(chan int)
	quit := make(chan int)

	// sub goroutine
	go func() {
	
		for i := 0; i < 10; i++ { // 10次循环,每次都从channel中接收一个值并打印出来
		
			fmt.Println(<-c)
			
			//quit <- 1	  // 注释掉.这个只用来验证select动作是无序的.当解开注释的时候,可发现
			//在sub goroutine未完成10次循环时(依然在向channel中传入数据\依然在从channel中读取数据时),便读取了quit,结束了运行.
			//说明并不是因为10次循环后阻塞管道而继续选择另一个case,选择另一个case的原因是随机选择中了这个刚可用的case.
			
		}
		
		quit <- 0 // 完成10次循环后,向quit传递0值
	}()

	// main goroutine
	fibonacii(c, quit) // 执行函数,直到函数return, main goroutine也就结束了.
}

/*
1
1
2
3
5
8
13
21
34
55
quit
*/

```





# 包

## gomod

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

