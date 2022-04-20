/*
	go.mod 文件中require中记录了依赖的具体版本信息
	- 可以通过go mod edit -replace=[old_pkg_dir_name]=[new_pkg_dir_name] 的方式修改go.mod文件中指定的包版本
		//old_pkg_dir_name 是 GOPATH/pkg/mod/下要调整的包目录中,对应当前require记录版本的实际目录名,new_pkg_dir_name同理.
	- 完成修改后,检查go.mod文件内容,会发现修改的包多了一条replace记录,使用 => 方式链接到了new_pkg_dir_name对应的版本.

	end.
*/
package main
