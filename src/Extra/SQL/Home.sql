drop function if exists AggCooPerCatPerYear(integer, varchar);
drop function if exists AggCoaPerCatPerYear(integer, varchar);
drop function if exists AggCooTop10PerCatPerYear(integer, varchar);
drop function if exists AggCoaTop10PerCatPerYear(integer, varchar);
drop function if exists AggCooPerCat(varchar);
drop function if exists AggCoo();
create function AggCooPerCatPerYear(integer, varchar) returns table(number bigint, name varchar, iso_2 varchar) AS $$ begin return query
select sum(Population.number) as number_,
       Country.name as name_,
       Country.iso_2 as iso_2_
from Population
       inner join Country on Country.id = Population.country_id
where Country.is_recognized = true
       and Population.year = $1
       and Population.category::varchar = $2
group by name_,
       iso_2_
having sum(Population.number) > 0
order by number_ desc;
end;
$$ language 'plpgsql';
create function AggCoaPerCatPerYear(integer, varchar) returns table(number bigint, name varchar, iso_2 varchar) AS $$ begin return query
select sum(Population.number) as number_,
       Country.name as name_,
       Country.iso_2 as iso_2_
from Population
       inner join Country on Country.id = Population.country_arrival_id
where Country.is_recognized = true
       and Population.year = $1
       and Population.category::varchar = $2
group by name_,
       iso_2_
having sum(Population.number) > 0
order by number_ DESC;
end;
$$ language 'plpgsql';
create function AggCooTop10PerCatPerYear(integer, varchar) returns table(number bigint, name text, iso_2 text) AS $$ begin return query with "TOP_10_COUNTRIES" AS(
       select sum(Population.number) as number_,
              Country.name as name_,
              Country.iso_2 as iso_2_
       from Population
              inner join Country on Country.id = Population.country_id
       where Country.is_recognized = true
              and Population.year = $1
              and Population.category::varchar = $2
       group by name_,
              iso_2_
       having sum(Population.number) > 0
       order by number_ desc
       limit 10
)
select number_,
       name_,
       iso_2_
from (
              select sum(Population.number) as number_,
                     'Others' as name_,
                     NULL as iso_2_
              from Population
                     inner join Country on Country.id = Population.country_id
              where Country.is_recognized = true
                     and Population.year = $1
                     and Population.category::varchar = $2
                     and Country.iso_2 NOT IN (
                            select "TOP_10_COUNTRIES".iso_2_
                            from "TOP_10_COUNTRIES"
                     )
              group by name_,
                     iso_2_
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
create function AggCoaTop10PerCatPerYear(integer, varchar) returns table(number bigint, name text, iso_2 text) AS $$ begin return query with "TOP_10_COUNTRIES" AS(
       select sum(Population.number) as number_,
              Country.name as name_,
              Country.iso_2 as iso_2_
       from Population
              inner join Country on Country.id = Population.country_arrival_id
       where Country.is_recognized = true
              and Population.year = $1
              and Population.category::varchar = $2
       group by name_,
              iso_2_
       having sum(Population.number) > 0
       order by number_ desc
       limit 10
)
select number_,
       name_,
       iso_2_
from (
              select sum(Population.number) as number_,
                     'Others' as name_,
                     NULL as iso_2_
              from Population
                     inner join Country on Country.id = Population.country_arrival_id
              where Country.is_recognized = true
                     and Population.year = $1
                     and Population.category::varchar = $2
                     and Country.iso_2 NOT IN (
                            select "TOP_10_COUNTRIES".iso_2_
                            from "TOP_10_COUNTRIES"
                     )
              group by name_,
                     iso_2_
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
create function AggCooPerCat(varchar) returns table(number bigint, year int) AS $$ begin return query
select sum(Population.number) as number_,
       Population.year as year_
from Population
where Population.category::varchar = $1
group by year_
order by year_ ASC;
end;
$$ language 'plpgsql';
create function AggCoo() returns table(number bigint, year int) AS $$ begin return query
select sum(Population.number) as number_,
       Population.year as year_
from Population
group by year_
order by year_ ASC;
end;
$$ language 'plpgsql';