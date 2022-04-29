# command
go run

go build


# grammar
- 每个源文件
    - 开始都用package声明，指明这个文件属于哪个包。
    - 接着是它导入其他包的列表。
    - 然后是存储在文件中的程序声明。

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
- 函数和其他包级别的实体可以任意次序声明，调用可以出现在声明之前。（这一点比Python有意思）

# os包
- 提供一些函数和变量，以与平台无关的方式与操作系统打交道。
- os.Args 获取命令行参数
    - 字符串slice
    - go中所有索引使用半开区间，即：范围索引中，包含第一个索引，不包含最后一个索引

# 操作符号
:=  短变量声明



# for 循环
- go中唯一的循环语句。
- 第一种形式
```
for initialization; condition ; post {
        // zero or more...
    }

- initialization （初始化） 语句在循环开始之前执行。如果存在，必须是一个简单的语句，比如一个简短的变量声明，一个递增或赋值语句，或一个函数调用。
- condition（条件） 是一个布尔表达式，在循环的每一次迭代开始前推演，如果推演结果为真，循环继续执行。
- post 循环体之后被执行，然后条件被再次推演，条件为假之后结束循环。
- 上面三个部分都是可以省略的。

- 没有initialization和post，则为传统的while循环
for condtion {
    // zero or more ...
}

- 如果条件部分也不存在，则为传统的无限循环
for {
    // zero or more...
}
 循环是无限的，尽管这种形式的循环可以通过break或return等语句进行终止。


```
- 第二种形式
```

// for mode 1
func for1() {
	var s, sep string
	for i := 1; i < len(os.Args); i++ { // os.Args[0]为程序本身的命令，因此从1开始取命令行参数
		s += sep + os.Args[i] // 此时sep未赋值，默认为''空字符串
		sep = " "             // 第一个索引使用之后，显式赋值为空格字符。
	}
	fmt.Println(s)
}

// for mode 2
// 这是for循环的第二种形式。循环在字符串或slice数据上迭代，
func for2() {
	s, sep := "", ""                  // 短的变量声明法，初始化变量
	for _, arg := range os.Args[1:] { // 每一次迭代，range产生一对值： 索引和这个索引对应的元素
		// 虽然例子里没使用索引，但是语法上range循环需要处理，因此
		// 使用空标识符 _ 来做“临时变量“，go不允许临时变量，
		// 空标识符_可以用在任何语法需要变量名，但程序逻辑不需要的地方
		// 如，丢弃每次迭代产生的无用索引。
		// 大多数go 程序员喜欢搭配range和_ 来写这个程序，
		// 因为索引在os.Args上是隐式的，使用_和range更不易犯错。
		s += sep + arg
		sep = " "
	}
	fmt.Println(s)
}
```


# 变量声明方法
1. `s := ""` 通常在一个函数内部使用，不适合包级别变量。
2. `var s string` 以来默认初始化为空字符串的""
3. `var s = ""` 很少用，除非声明多个变量。
4. `var s string = ""` 类型一致情况下是冗余的，类型不一致时是必须的。
- 四种方法都可以，正常情况下应当使用前两种方式，使用显式的初始化来说明初始化变量的重要性，使用隐式的初始化来表明初始化变量不重要。

- new(T)

  > 创建一个T类型变量，初始化为T类型的零值，返回其地址(*T)

# bufio包
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

# io/ioutil包





# 语法要点
- 变量声明
    1. 声明一个变量，指定类型。 默认值是0
    
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
    
       ```
       // 唯独方法4与前三者不同。方法4只能在函数体内使用。
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
    
    5. 声明多个变量
    
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
    
       
    
- 函数
    - 多返回值
    - main函数与init函数
    
- defer

- 指针

- 切片slice

    - slice声明方式

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

        

    - slice使用方式

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

                

- map
  - map声明方式
    
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
      
         

- interface
    - 万能类型
    - 类型断言

- 结构体
    - 结构体标签

- 反射

- OOP
    - 封装
      - 属性的赋值使用 : 符号
    - 继承
    - 多态

- golang高阶
    - goroutine
    - channel

```
8小时专职Golang工程师(如果你想低成本学习Go语言) 

笔记及资料:链接: https://pan.baidu.com/s/1glckD7XGInHDFQQKCRE66g 提取码: gyj3
```


- 闭包
