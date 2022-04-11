/*
	继承
*/
package main

import "fmt"

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
	h.Eat()

	// 定义一个子类对象
	s := Superman{Human{"yy", "M"}, 99} // 这里用name:"yy" 会报错，奇怪。
	s.Fly()                             // kk eatingyy is flying!
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
