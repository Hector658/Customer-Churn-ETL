with bets as (
    select * from {{ ref('stg_bets') }}
),

monthly as (
    select
        date_trunc('month', placement_date) as month,
        count(distinct user_id) as active_customers,
        count(*) as total_bets,
        sum(bet_amount) as total_bet_amount
    from bets
    group by 1
)

select
    month,
    active_customers,
    total_bets,
    total_bet_amount,
    round(total_bets::numeric / active_customers, 2) as bets_per_active_customer,
    round((total_bet_amount / active_customers)::numeric, 2) as bet_amount_per_active_customer 
from monthly
order by month 