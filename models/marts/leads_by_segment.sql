select
  segment,
  count(*) as lead_count
from {{ ref('stg_leads') }}
group by 1
order by 2 desc
