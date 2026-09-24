from dagster import Definitions
from dagster_dbt import DbtCliResource

from orchestration.assets import raw_bets, raw_customers, raw_events, raw_participants
from orchestration.dbt_assets import churn_dbt_assets
from orchestration.dbt_project import dbt_project

defs = Definitions(
    assets=[raw_customers, raw_bets, raw_events, raw_participants, churn_dbt_assets],
    resources={
        "dbt": DbtCliResource(project_dir=dbt_project),
    },
)
