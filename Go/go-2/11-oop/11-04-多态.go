/*
	多态

定义一个接口完成多态的实现

相当于， 谁能干这个活儿，就指针到谁那里，让它干- -！
*/
package main

import "fmt"

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

// 具体的类
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

// 附加一个
func showAnimal(animal AnimalIF) {
	animal.Sleep()                           // 传入什么调用什么， （多态） 如：传入Cat，就指向Cat的Sleep()方法。
	fmt.Println("color=", animal.GetColor()) // 同理。
	fmt.Println("type=", animal.GetType())

}

func main() {
	var animal AnimalIF    // 接口的数据类型，就是父类的指针
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
