/*
	访问对象的方法/属性时，可以不需要使用指针，最终结果一致。
	修改对象的属性时，需要传递指针，否则修改的是副本，不能达到目的。

	类名、属性名、方法名的首字母大写（公有）、首字母小写（私有）
	如果类名 首字母大写，表示其他包也能够访问，也能通过这个类来实体化对象。
	如果类的属性名 首字母大写，表示该属性能够对外访问（公有），否则只能供类内部使用（私有）。
	类的方法同理

*/
package main

import "fmt"

// 定义一个英雄类
type Hero struct {
	// 定义方法...
	Name  string
	Ad    int
	Level int
}

func (this Hero) Show() { // this 可以理解为self，指结构体自身，只是个变量名。
	// this Hero的Hero 表示当前func属于结构体Hero
	fmt.Println("name =", this.Name)
	fmt.Println("AD =", this.Ad)
	fmt.Println("level =", this.Level)
}

//    self|class|funcName|out data type
func (this Hero) GetName() string {
	return this.Name
}

//    self|class|funcName|ArgName|ArgType
func (this Hero) SetName(newName string) {
	// this 是调用该方法的对象的一个副本
	this.Name = newName
}

// 下面这些函数名+2的，都改为了指针传入
func (this *Hero) Show2() {
	// 对于只访问不修改的行为，结果上来看，(*Hero)Show2() == (Hero)Show()
	fmt.Println("name =", this.Name)
	fmt.Println("AD =", this.Ad)
	fmt.Println("level =", this.Level)
}

//    self|class_pointer|funcName|out data type
func (this *Hero) GetName2() string {
	return this.Name
}

//    self|class_pointer|funcName|ArgName|ArgType
func (this *Hero) SetName2(newName string) {
	this.Name = newName
}

func main() {
	// 创建一个对象
	hero := Hero{Name: "kk", Ad: 100, Level: 1}
	hero.Show() // name = kk
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
		level = 11*/

}
