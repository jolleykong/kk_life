# MySQL物理备份方式

|                  | xtrabackup            | MySQL Enterprise Backup                 |
| ---------------- | --------------------- | --------------------------------------- |
| license          | GPL                   | proprietary                             |
| 价格             | 免费                  | 企业版MySQL自带                         |
| 支持版本         | MySQL，Percona，PXC   | MySQL                                   |
| 平台             | Linux                 | Linux，Solaris、Windows、MacOS、FreeBSD |
| 无阻塞备份InnoDB | Yes                   | Yes                                     |
| 支持增量备份     | Yes                   | Yes                                     |
| 支持压缩备份     | Yes                   | Yes                                     |
| 备份锁方式       | lock table for backup | lock instance for backup                |
| 加密备份         | Yes                   | Yes                                     |
| 备份包校验       | No                    | Yes                                     |



- MySQL 物理备份的方式
- Xtrabackup的工作原理
- Xtrabackup备份及恢复流程（5.7、8.0）
- Xtrabackup备份文件说明，搞清楚备份如何和binlog拼接
- Xtrabackup备份出来的Binlog位置和apply-log出的位置不一样时如何处理


