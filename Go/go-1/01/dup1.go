package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	dup1()
}

// dup via bufio from stdin
// $ echo -e "11\n11\n1\n123" | go run 1-1.go
func dup1() {
	counts := make(map[string]int)
	// map存储一个kv对集合，key可以是能够进行相等比较的任意类型，最常见字符串类型，value可以是任意类型
	// 这里，key是string，值是int。
	// 内置的函数make可以用来新建map。
	input := bufio.NewScanner(os.Stdin)
	for input.Scan() {
		counts[input.Text()]++
		// 每次从stdin中输入一行内容，这一行就作为map的键，对应的值加1
		// counts[input.Text()]++ 等价于
		// 		line := input.Text()
		// 		counts[line] = counts[line] + 1
		// 键在map中不存在时，也就是当一个新行第一次出现时，
		//   右边表达式counts[line] 根据类型被推演为零值，int的零值为0
	}

	for line, n := range counts {
		// 基于range对counts做循环，
		// counts是一个map，因此迭代会有2个值，即：key和value
		// key对应为行内容（line），value对应为重复次数（n）
		// 对counts的迭代是无序的。
		if n > 1 {
			fmt.Printf("%d\t%s\n", n, line)
		}
	}

}
