with source as (
    select * from {{ source('raw', 'bets') }}
)

select *
from source