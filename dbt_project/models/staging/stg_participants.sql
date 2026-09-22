with source as (
    select * from {{ source('raw', 'participants') }}
)

select
    participant_id,
    participant_name,
    sport,
    competition,
    popularity_score,
    strength_score,
    home_advantage
from source