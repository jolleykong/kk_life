# 8.0版本开始，有多种hint可以玩

> refman-8.0-en.html-chapter/optimization.html#optimizer-hints

| Hint Name                  | Description                                                  | Applicable Scopes  |
| -------------------------- | ------------------------------------------------------------ | ------------------ |
| BKA NO_BKA                 | Affects Batched Key Access join processing                   | Query block, table |
| BNL NO_BNL                 | Affects Block Nested-Loop join processing                    | Query block, table |
| HASH_JOIN NO_HASH_JOIN     | Affects Hash Join optimization                               | Query block, table |
| INDEX_MERGE NO_INDEX_MERGE | Affects Index Merge optimization                             | Table, index       |
| JOIN_FIXED_ORDER           | Use table order specified in FROM clause for join order      | Query block        |
| JOIN_ORDER                 | Use table order specified in hint for join order             | Query block        |
| JOIN_PREFIX                | Use table order specified in hint for first tables of join order | Query block        |
| JOIN_SUFFIX                | Use table order specified in hint for last tables of join order | Query block        |
| MAX_EXECUTION_TIME         | Limits statement execution time                              | Global             |
| MERGE NO_MERGE             | Affects derived table/view merging into outer query block    | Table              |
| MRR NO_MRR                 | Affects Multi-Range Read optimization                        | Table, index       |
| NO_ICP                     | Affects Index Condition Pushdown optimization                | Table, index       |
| NO_RANGE_OPTIMIZATION      | Affects range optimization                                   | Table, index       |
| QB_NAME                    | Assigns name to query block                                  | Query block        |
| RESOURCE_GROUP             | Set resource group during statement execution                | Global             |
| SEMIJOIN NO_SEMIJOIN       | Affects semijoin strategies; beginning with MySQL 8.0.17, this also applies to antijoins | Query block        |
| SKIP_SCAN NO_SKIP_SCAN     | Affects Skip Scan optimization                               | Table, index       |
| SET_VAR                    | Set variable during statement execution                      | Global             |
| SUBQUERY                   | Affects materialization, IN-to-EXISTS subquery stratgies     | Query block        |

>#### Optimizer Hint Syntax
>
>The parser recognizes optimizer hint comments after the initial keyword of SELECT, UPDATE , INSERT , REPLACE ), and DELETE statements. Hints are permitted in these contexts:
>
>- At the beginning of query and data change statements: 
>
>  ```
>   SELECT /*+ ... */ ...
>   INSERT /*+ ... */ ...
>   REPLACE /*+ ... */ ...
>   UPDATE /*+ ... */ ...
>   DELETE /*+ ... */ ...
>  ```
>
>
>- At the beginning of query blocks: 
>
>  ```
>   (SELECT /*+ ... */ ... )
>   (SELECT ... ) UNION (SELECT /*+ ... */ ... )
>   (SELECT /*+ ... */ ... ) UNION (SELECT /*+ ... */ ... )
>   UPDATE ... WHERE x IN (SELECT /*+ ... */ ...)
>   INSERT ... SELECT /*+ ... */ ...
>  ```
>
>
>- In hintable statements prefaced by EXPLAIN . For example: 
>
>  ```
>   EXPLAIN SELECT /*+ ... */ ...
>   EXPLAIN UPDATE ... WHERE x IN (SELECT /*+ ... */ ...)
>  ```
>
>
> The implication is that you can use EXPLAIN to see how optimizer hints affect execution plans. Use SHOW WARNINGS immediately after EXPLAIN to see how hints are used. The extended EXPLAIN output displayed by a following SHOW WARNINGS) indicates which hints were used. Ignored hints are not displayed

 

> select  /*+ NO_BKA(t1, t2) */ t1.* from t1 inner join t2 inner join t3;



> #### Join-Order Optimizer Hints
>
> Join-order hints affect the order in which the optimizer joins tables. 
>
> Syntax of the JOIN_FIXED_ORDER hint: 
>
> ```
> hint_name([@query_block_name])
> ```
>
> Syntax of other join-order hints: 
>
> ```
> hint_name([@query_block_name] tbl_name [, tbl_name] ...)
> hint_name(tbl_name[@query_block_name] [, tbl_name[@query_block_name]] ...)
> ```
>
> The syntax refers to these terms:
>
> -  *`hint_name`*: These hint names are permitted:
>
>  -  JOIN_FIXED_ORDER : Force the optimizer to join tables using the order in which they appear in the `FROM` clause. This is the same as specifying `SELECT STRAIGHT_JOIN`. 
>
>  -  JOIN_ORDER : Instruct the optimizer to join tables using the specified table order. The hint applies to the named tables. The optimizer may place tables that are not named anywhere in the join order, including between specified tables. 
>
>  -  JOIN_PREFIX : Instruct the optimizer to join tables using the specified table order for the first tables of the join execution plan. The hint applies to the named tables. The optimizer places all other tables after the named tables. 
>
>  -  JOIN_SUFFIX : Instruct the optimizer to join tables using the specified table order for the last tables of the join execution plan. The hint applies to the named tables. The optimizer places all other tables before the named tables.
>
> -  *`tbl_name`*: The name of a table used in the statement. A hint that names tables applies to all tables that it names. The JOIN_FIXED_ORDER hint names no tables and applies to all tables in the `FROM` clause of the query block in which it occurs. 
>
>    If a table has an alias, hints must refer to the alias, not the table name. 
>
>    Table names in hints cannot be qualified with schema names. 
>
> -  *`query_block_name`*: The query block to which the hint applies. If the hint includes no leading `@*`query_block_name`*`, the hint applies to the query block in which it occurs. For `*`tbl_name`*@*`query_block_name`*` syntax, the hint applies to the named table in the named query block. To assign a name to a query block, see [Optimizer Hints for Naming Query Blocks] .
>
> *Example*
>
> ```
> SELECT
> /*+ JOIN_PREFIX(t2, t5@subq2, t4@subq1)
>     JOIN_ORDER(t4@subq1, t3)
>     JOIN_SUFFIX(t1) */
> COUNT(*) FROM t1 JOIN t2 JOIN t3
>            WHERE t1.f1 IN (SELECT /*+ QB_NAME(subq1) */ f1 FROM t4)
>              AND t2.f1 IN (SELECT /*+ QB_NAME(subq2) */ f1 FROM t5);
> ```

![ ](.pics/clip_image007.png)

 