https://dev.mysql.com/doc/internals/en/innodb-page-overview.html

![ ](clip_image001-1598785866906.png)

 

 

| InnoDB Page 结构      |                    |              |                          |
| --------------------- | ------------------ | ------------ | ------------------------ |
| 名称                  | 中文名             | 占用空间大小 | 简单描述                 |
| File Header           | 文件头部           | 38 bytes     | 页的一些通用信息         |
| Page Header           | 页面头部           | 56 bytes     | 数据页专有的一些信息     |
| Infimum + Supremum    | 最小记录和最大记录 | 26 bytes     | 两个虚拟的行记录         |
| User Records          | 用户记录           | 不确定       | 实际存储的行记录内容     |
| Free Space            | 空闲空间           | 不确定       | 页中尚未使用的空间       |
| Page Directory(slots) | 页面目录           | 不确定       | 页中的某些记录的相对位置 |
| File Trailer          | 文件尾部           | 8 bytes      | 校验页是否完整           |

一个page去掉必要的占用后，只剩下 (16*1024 - 38 -56 -26 -8 ) = 16256 bytes

38+56+26+8=128 

 

 

| **File header** **结构** |          |                                                              |
| ------------------------ | -------- | ------------------------------------------------------------ |
| **Name**                 | **Size** | **Remarks**                                                  |
| FIL_PAGE_SPACE           | 4        | 4 ID of the space the page is in                             |
| FIL_PAGE_OFFSET          | 4        | ordinal page number from start of space                      |
| FIL_PAGE_PREV            | 4        | offset of previous page in key order                         |
| FIL_PAGE_NEXT            | 4        | offset of next page in key order                             |
| FIL_PAGE_LSN             | 8        | log serial number of page's latest log record                |
| FIL_PAGE_TYPE            | 2        | current defined types are: FIL_PAGE_INDEX, FIL_PAGE_UNDO_LOG, FIL_PAGE_INODE, FIL_PAGE_IBUF_FREE_LIST |
| FIL_PAGE_FILE_FLUSH_LSN  | 8        | "the file has been flushed to disk at least up to  this lsn" (log serial number), valid only on the first page of the file |
| FIL_PAGE_ARCH_LOG_NO     | 4        | the latest archived log file  number at the time that FIL_PAGE_FILE_FLUSH_LSN was written (in the log) |

 

来自 <https://dev.mysql.com/doc/internals/en/innodb-fil-header.html> 

 

 

 

 

 

| **page header** **结构** |          |                                                              |
| ------------------------ | -------- | ------------------------------------------------------------ |
| **Name**                 | **Size** | **Remarks**                                                  |
| PAGE_N_DIR_SLOTS         | 2        | number of directory slots in the Page Directory part;  initial value = 2 |
| PAGE_HEAP_TOP            | 2        | record pointer to first record in heap                       |
| PAGE_N_HEAP              | 2        | number of heap records; initial value = 2                    |
| PAGE_FREE                | 2        | record pointer to first free record                          |
| PAGE_GARBAGE             | 2        | "number of bytes in deleted records"                         |
| PAGE_LAST_INSERT         | 2        | record pointer to the last inserted record                   |
| PAGE_DIRECTION           | 2        | either PAGE_LEFT, PAGE_RIGHT, or PAGE_NO_DIRECTION           |
| PAGE_N_DIRECTION         | 2        | number of consecutive inserts in the same direction,  for example, "last 5 were all to the left" |
| PAGE_N_RECS              | 2        | number of user records                                       |
| PAGE_MAX_TRX_ID          | 8        | the highest ID of a transaction which might have  changed a record on the page (only set for secondary indexes) |
| PAGE_LEVEL               | 2        | level within the index (0 for a leaf page)                   |
| PAGE_INDEX_ID            | 8        | identifier of the index the page belongs to                  |
| PAGE_BTR_SEG_LEAF        | 10       | "file segment header for the leaf pages in a  B-tree" (this is irrelevant here) |
| PAGE_BTR_SEG_TOP         | 10       | "file segment header for the non-leaf pages in a  B-tree" (this is irrelevant here) |

 

来自 <https://dev.mysql.com/doc/internals/en/innodb-page-header.html> 

 

 

| **File Trailer** **结构** |          |                                                              |
| ------------------------- | -------- | ------------------------------------------------------------ |
| **Name**                  | **Size** | **Remarks**                                                  |
| FIL_PAGE_END_LSN          | 8        | low 4 bytes = checksum of page, last  4 bytes = same as FIL_PAGE_LSN |

 

来自 <https://dev.mysql.com/doc/internals/en/innodb-fil-trailer.html> 