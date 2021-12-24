8.0用XB可能遇到密码验证问题， 可能需要这个包libdbi-dbd-mysql



yum install libdbi-dbd-mysql   

[8.0用XB可能遇到密码验证问题， 可能需要这个包libdbi-dbd-mysql]()

 

 

change master to 后加 get_master_public_key=1;

[注意：8.0以后版本配置复制时需要加参数]()

 

[8.0新特性]()



8.0版本中优化了redo写性能，支持并行写入

无锁化处理，不再需要由锁来控制写入顺序

每个MTR（MTR：mini trx）写入前，事先预分配写入的偏移量

存在大LSN已写完但小LSN还没写完的情况，即空洞

有一个新的log writen线程负责扫描log buffer，找到未写完的MTR，再将其刷新到redo log中

 

 

 

[Redo]()