-- Core fact table for Arsenal matches (Redshift).
create table if not exists arsenal_matches (
    match_id              bigint        primary key,
    date                  timestamp     not null,
    opponent              varchar(128)  not null,
    home_or_away          varchar(8)    not null,
    goals_for             integer       not null,
    goals_against         integer       not null,
    goal_difference       integer       not null,
    result                varchar(1)    not null,
    rolling_goals_for_5   double precision,
    rolling_goal_diff_5   double precision
);

-- Helpful aggregates / views (run after COPY).
-- Average goals by venue
create or replace view vw_arsenal_avg_by_venue as
select
    home_or_away,
    avg(goals_for)::numeric(6,2)       as avg_goals_for,
    avg(goal_difference)::numeric(6,2) as avg_goal_diff
from arsenal_matches
group by 1;

-- Last 5 matches with form
create or replace view vw_arsenal_form_last5 as
select *
from arsenal_matches
order by date desc
limit 5;
