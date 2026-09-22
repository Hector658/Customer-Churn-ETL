with customers as (
    select * from {{ ref('stg_customers') }}
),

bets as (
    select * from {{ ref('stg_bets') }}
),

customer_bet_stats as (
    select
        user_id,
        min(placement_date) as first_bet_date,
        max(placement_date) as last_bet_date,
        count(*) as total_bets,
        count(distinct placement_date::date) as active_days,
        sum(bet_amount) as total_bet_amount,
        avg(bet_amount) as average_bet_amount
    from bets
    group by user_id
),

overall_max_date as (
    select max(placement_date) as max_bet_date
    from bets
)

select
    c.user_id,
    c.segment_client,
    c.register_date,
    s.first_bet_date,
    s.last_bet_date,
    coalesce(s.total_bets, 0) as total_bets,
    coalesce(s.active_days, 0) as active_days,
    case
        when s.active_days > 0 then s.total_bets::numeric / s.active_days
        else null
    end as bets_per_active_day,
    coalesce(s.total_bet_amount, 0) as total_bet_amount,
    s.average_bet_amount,
    (s.first_bet_date is not null) as ever_bet,
    extract(day from (s.first_bet_date - c.register_date)) as days_to_first_bet,
    extract(day from (m.max_bet_date - s.last_bet_date)) as days_since_last_bet
from customers c
left join customer_bet_stats s on c.user_id = s.user_id
cross join overall_max_date m