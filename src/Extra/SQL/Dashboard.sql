drop function if exists AggPerCooPerCoaPerCat(varchar, varchar, varchar);
drop function if exists AggPerCooPerCoa(varchar, varchar, varchar);
create function AggPerCooPerCoaPerCat(varchar, varchar, varchar) returns table(number bigint, year integer) AS $$ begin return query
select sum(Population.number) as number_,
    Population.year as year_
from Population
    inner join Country as origin on Population.country_id = origin.id
    inner join Country as arrival on Population.country_arrival_id = arrival.id
where origin.iso_2 = $1
    and arrival.iso_2 = $2
    and Population.category::varchar = $3
group by year_
order by year_ asc;
end;
$$ language 'plpgsql';
create function AggPerCooPerCoa(varchar, varchar, varchar) returns table(number bigint, year integer) AS $$ begin return query
select sum(Population.number) as number_,
    Population.year as year_
from Population
    inner join Country as origin on Population.country_id = origin.id
    inner join Country as arrival on Population.country_arrival_id = arrival.id
where origin.iso_2 = $1
    and arrival.iso_2 = $2
group by year_
order by year_ asc;
end;
$$ language 'plpgsql';