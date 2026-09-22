with source as (
    select * from {{ source('raw', 'events') }}
)

select *
from source
