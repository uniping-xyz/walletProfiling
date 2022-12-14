

```
select DISTINCT(label)
from ethereum.tags
```


All Tags with frequency

```
select distinct label, Count(*) as contracts
from ethereum.tags
group by label
order by contracts desc
```