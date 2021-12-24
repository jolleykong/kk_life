'''
Python编程知识-奇妙的三元组

给你一个包含 n 个整数的数组 nums，判断 nums 中是否存在三个元素 a，b，c ，使得 a + b + c = 0 ？请你找出所有满足条件且不重复的三元组。 *

      注意：答案中不可以包含重复的三元组。
      示例：
      给定数组 -1 0 1 2 -1 -4
      满足要求的三元组集合为：
      -1 0 1
      -1 -1 2

代码实现

请在下面 cell 中编写代码，实现题目描述的要求。

'''
nums = [-1,0,1,2,-1,-4]
result = []
i = 0
for c1 in nums[i:]:
    a = i + 1
    for c2 in nums[a:]:
        b = a + 1
        for c3 in nums[b:]:
            if c1 + c2 + c3 == 0:
                result.append(tuple(sorted((c1,c2,c3))))
            i += 1




print(set(result))