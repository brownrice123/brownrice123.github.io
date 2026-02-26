with source as (
    select
        cast(date as date) as date,
        cast(metric_value as double) as metric_value
    from read_csv_auto('data/daily_metrics.csv', header=true)
),
scored as (
    select
        date,
        metric_value,
        avg(metric_value) over (
            order by date
            rows between 7 preceding and 1 preceding
        ) as baseline_7d
    from source
)
select
    date,
    metric_value,
    baseline_7d,
    case
        when baseline_7d is null or baseline_7d = 0 then null
        else (metric_value - baseline_7d) / baseline_7d
    end as deviation,
    case
        when baseline_7d is null then false
        when abs((metric_value - baseline_7d) / nullif(baseline_7d, 0)) >= 0.30 then true
        else false
    end as is_anomaly
from scored
order by date;
