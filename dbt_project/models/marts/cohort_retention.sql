with bets as (
    select * from {{ ref('stg_bets') }}
),

customer_cohort as (
    select
        user_id,
        date_trunc('month', min(placement_date)) as cohort_month
    from bets
    group by user_id
),

activity as (
    select distinct
        b.user_id,
        date_trunc('month', b.placement_date) as activity_month,
        c.cohort_month
    from bets b
    inner join customer_cohort c on b.user_id = c.user_id
),

months_since as (
    select
        cohort_month,
        activity_month,
        user_id,
        (date_part('year', activity_month) - date_part('year', cohort_month)) * 12
            + (date_part('month', activity_month) - date_part('month', cohort_month))
            as months_since_cohort
    from activity
),

cohort_sizes as (
    select
        cohort_month,
        count(distinct user_id) as cohort_size
    from months_since
    where months_since_cohort = 0
    group by cohort_month
),

retention_counts as (
    select
        cohort_month,
        months_since_cohort,
        count(distinct user_id) as active_customers
    from months_since
    group by cohort_month, months_since_cohort
)

select
    r.cohort_month,
    r.months_since_cohort,
    r.active_customers,
    s.cohort_size,
    round((r.active_customers::numeric / s.cohort_size), 4) as retention
from retention_counts r
inner join cohort_sizes s on r.cohort_month = s.cohort_month
order by r.cohort_month, r.months_since_cohort