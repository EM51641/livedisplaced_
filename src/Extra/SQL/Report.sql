drop function if exists AggCooPerYearPerCatPerCntry(integer, varchar, varchar);
drop function if exists AggCoaPerYearPerCatPerCntry(integer, varchar, varchar);
drop function if exists AggCooTop10PerCatPerYearPerCntry(integer, varchar, varchar);
drop function if exists AggCoaTop10PerCatPerYearPerCntry(integer, varchar, varchar);
drop function if exists AggCooPerYearPerCntryPerCat(integer, varchar, varchar);
drop function if exists AggCoaPerYearPerCntryPerCat(integer, varchar, varchar);
drop function if exists AggCooPerCntryPerCat(varchar, varchar);
drop function if exists AggCoaPerCntryPerCat(varchar, varchar);
drop function if exists AggCooPerCntry(varchar);
drop function if exists AggCoaPerCntry(varchar);
create function AggCooPerYearPerCatPerCntry(integer, varchar, varchar) returns table(number bigint, name varchar, iso_2 varchar) AS $$ begin return query
select sum(Population.number) as number_,
       co.name as name_,
       co.iso_2 as iso_2_
from Population
       inner join Country as co on co.id = Population.country_id
       inner join Country as ca on ca.id = Population.country_arrival_id
where ca.is_recognized = true
       and Population.year = $1
       and Population.category::varchar = $2
       and ca.iso_2 = $3
group by name_,
       iso_2_
having sum(Population.number) > 0
order by number_ desc;
end;
$$ language 'plpgsql';
create function AggCoaPerYearPerCatPerCntry(integer, varchar, varchar) returns table(number bigint, name varchar, iso_2 varchar) AS $$ begin return query
select sum(Population.number) as number_,
       ca.name as name_,
       ca.iso_2 as iso_2_
from Population
       inner join Country as ca on ca.id = Population.country_arrival_id
       inner join Country as co on co.id = Population.country_id
where ca.is_recognized = true
       and Population.year = $1
       and Population.category::varchar = $2
       and co.iso_2 = $3
group by name_,
       iso_2_
having sum(Population.number) > 0
order by number_ desc;
end;
$$ language 'plpgsql';
create function AggCooTop10PerCatPerYearPerCntry(integer, varchar, varchar) returns table(number bigint, name text, iso_2 varchar) AS $$ begin return query with "TOP_10_COUNTRIES" AS(
       select sum(Population.number) as number_,
              co.name as name_,
              co.iso_2 as iso_2_
       from Population
              inner join Country as co on co.id = Population.country_id
              inner join Country as ca on ca.id = Population.country_arrival_id
       where co.is_recognized = true
              and Population.year = $1
              and Population.category::varchar = $2
              and ca.iso_2 = $3
       group by name_,
              iso_2_
       having sum(Population.number) > 0
       order by number_ desc
       limit 10
)
select number_,
       name_,
       iso_2_
from(
              select sum(Population.number) as number_,
                     'Others' as name_,
                     NULL as iso_2_
              from Population
                     inner join Country as co on co.id = Population.country_id
                     inner join Country as ca on ca.id = Population.country_arrival_id
              where Population.year = $1
                     and Population.category::varchar = $2
                     and ca.iso_2 = $3
                     and co.iso_2 NOT IN (
                            select "TOP_10_COUNTRIES".iso_2_
                            from "TOP_10_COUNTRIES"
                     )
              group by name_
              union all
              (
                     SELECT "TOP_10_COUNTRIES".number_,
                            "TOP_10_COUNTRIES".name_,
                            "TOP_10_COUNTRIES".iso_2_
                     FROM "TOP_10_COUNTRIES"
              )
       ) as combined
order by (
              case
                     when combined.name_ = 'Others' then 1
                     else 0
              end
       ),
       number_ desc;
end;
$$ language 'plpgsql';
create function AggCoaTop10PerCatPerYearPerCntry(integer, varchar, varchar) returns table(number bigint, name text, iso_2 varchar) AS $$ begin return query with "TOP_10_COUNTRIES" AS(
       select sum(Population.number) as number_,
              ca.name as name_,
              ca.iso_2 as iso_2_
       from Population
              inner join Country as co on co.id = Population.country_id
              inner join Country as ca on ca.id = Population.country_arrival_id
       where ca.is_recognized = true
              and Population.year = $1
              and Population.category::varchar = $2
              and co.iso_2 = $3
       group by name_,
              iso_2_
       having sum(Population.number) > 0
       order by number_ desc
       limit 10
)
select number_,
       name_,
       iso_2_
from(
              select sum(Population.number) as number_,
                     'Others' as name_,
                     NULL as iso_2_
              from Population
                     inner join Country as co on co.id = Population.country_id
                     inner join Country as ca on ca.id = Population.country_arrival_id
              where Population.year = $1
                     and Population.category::varchar = $2
                     and co.iso_2 = $3
                     and ca.iso_2 NOT IN (
                            select "TOP_10_COUNTRIES".iso_2_
                            from "TOP_10_COUNTRIES"
                     )
              group by name_
              union all
              (
                     SELECT "TOP_10_COUNTRIES".number_,
                            "TOP_10_COUNTRIES".name_,
                            "TOP_10_COUNTRIES".iso_2_
                     FROM "TOP_10_COUNTRIES"
              )
       ) as combined
order by (
              case
                     when combined.name_ = 'Others' then 1
                     else 0
              end
       ),
       number_ desc;
end;
$$ language 'plpgsql';
create function AggCooPerYearPerCntryPerCat(integer, varchar, varchar) returns table(number bigint, name varchar, iso_2 varchar) AS $$ begin return query
select sum(Population.number) as number_,
       Country.name as name_,
       Country.iso_2 as iso_2_
from Population
       inner join Country on Country.id = Population.country_id
where Country.is_recognized = true
       and Population.year = $1
       and Population.category::varchar = $2
       and Country.iso_2 = $3
group by name_,
       iso_2_
having sum(Population.number) > 0
order by number_ desc;
end;
$$ language 'plpgsql';
create function AggCoaPerYearPerCntryPerCat(integer, varchar, varchar) returns table(number bigint, name varchar, iso_2 varchar) AS $$ begin return query
select sum(Population.number) as number_,
       Country.name as name_,
       Country.iso_2 as iso_2_
from Population
       inner join Country on Country.id = Population.country_arrival_id
where Country.is_recognized = true
       and Population.year = $1
       and Population.category::varchar = $2
       and Country.iso_2 = $3
group by name_,
       iso_2_
having sum(Population.number) > 0
order by number_ desc;
end;
$$ language 'plpgsql';
create function AggCooPerCntry(varchar) returns table(number bigint, year integer) AS $$ begin return query
select sum(Population.number) as number_,
       Population.year as year_
from Population
       inner join Country on Country.id = Population.country_id
where Country.is_recognized = true
       and Country.iso_2 = $1
group by year_
having sum(Population.number) > 0
order by year_ asc;
end;
$$ language 'plpgsql';
create function AggCoaPerCntry(varchar) returns table(number bigint, year integer) AS $$ begin return query
select sum(Population.number) as number_,
       Population.year as year_
from Population
       inner join Country on Country.id = Population.country_arrival_id
where Country.is_recognized = true
       and Country.iso_2 = $1
group by year_
having sum(Population.number) > 0
order by year_ asc;
end;
$$ language 'plpgsql';
create function AggCooPerCntryPerCat(varchar, varchar) returns table(number bigint, year integer) AS $$ begin return query
select sum(Population.number) as number_,
       Population.year as year_
from Population
       inner join Country on Country.id = Population.country_id
where Country.is_recognized = true
       and Country.iso_2 = $1
       and Population.category::varchar = $2
group by year_
having sum(Population.number) > 0
order by year_ asc;
end;
$$ language 'plpgsql';
create function AggCoaPerCntryPerCat(varchar, varchar) returns table(number bigint, year integer) AS $$ begin return query
select sum(Population.number) as number_,
       Population.year as year_
from Population
       inner join Country on Country.id = Population.country_arrival_id
where Country.is_recognized = true
       and Country.iso_2 = $1
       and Population.category::varchar = $2
group by year_
having sum(Population.number) > 0
order by year_ asc;
end;
$$ language 'plpgsql';