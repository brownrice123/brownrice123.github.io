select
  company_id,
  company_name,
  segment
from {{ ref('companies') }}
