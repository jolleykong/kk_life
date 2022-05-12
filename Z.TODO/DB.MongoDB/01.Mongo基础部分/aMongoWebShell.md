<iframe title="MongoDB Web Shell" allowfullscreen="" sandbox="allow-scripts allow-same-origin" width="100%" height="320" src="https://mws.mongodb.com/?version=latest" class="css-107tt68" style="box-sizing: border-box; border: 0px;"></iframe>



```
# 实现select insert 
db.collectionABC.find({ conditionB: 1 }).
forEach( function(i) { 
  i.ts_imported = new Date();
  db.collectionB.insert(i);
});
```

