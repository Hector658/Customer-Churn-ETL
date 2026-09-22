with source as (
    select * from {{ source('raw', 'customers') }}
)

select
    user_id,
    register_date,
    age,
    residence_country,
    payment_method,
    segment_client,
    active_days,
    annual_bets,
    n_bets
from source