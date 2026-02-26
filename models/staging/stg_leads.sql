select
  lead_id,
  company_id,
  email,
  segment
from {{ ref('leads') }}
