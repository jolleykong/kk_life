- 概念对比

  | MySQL       | MongoDB            |
  | ----------- | ------------------ |
  | database    | database           |
  | table       | collection         |
  | row         | json or bson       |
  | column      | field              |
  | index       | index              |
  | table joins | \$lookup或嵌套文档 |
  | primary key | _id                |
  | 统计分析    | aggregation        |
  | redo log    | Journal log        |
  | binlog      | Oplog log          |

  

- 语句对比

  | SQL                                                   | MongoDB                                                      |
  | ----------------------------------------------------- | ------------------------------------------------------------ |
  | `create table`                                        | `db.<dbname>.insert({<key>:<value>}) `<br>或 `db.createCollection("<dbname>")` |
  | `alter table add column`<br>`alter table drop column` | `db.<dbname>.update({},{'$set':{a:2}})` 或删除字段 `$unset`  |
  | `create index` <br>或 `alter table add index`         | `db.<dbname>.createIndex({ x:1, a:-1})`<br> `/*1为正序索引，-1为倒序索引*/` |
  | `drop table` 或 `truncate table`                      | `db.<dbname>.drop()`                                         |
  | `drop database`                                       | `db.dropDatabase()`                                          |
  | `insert into`                                         | `db.<dbname>.insertOne()` 或 `db.<dbname>.insert()`          |
  | `select col1 from test order by a limit 1,2`          | `db.test.find({xxx:10},{x:1,a:1}).sort({a:1}).skip(1).limit(2)` |
  | `update`                                              | `db.<dbname>.update( {x:1},{$set:{a:6}} )`                   |
  | `delete from`                                         | `db.<dbname>.deleteMany({x:1})`                              |

