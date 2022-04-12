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
