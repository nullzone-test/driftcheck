# driftcheck

Lightweight model drift detection for production ML pipelines. Monitors feature distributions, prediction confidence, and data quality metrics — alerts before your model silently degrades.

## Why driftcheck?

Most drift detection tools are heavyweight (Evidently, NannyML) or require a full MLOps platform. `driftcheck` is a single pip install that hooks into your existing inference pipeline with 3 lines of code.

## Installation

```bash
pip install driftcheck
```

## Quick Start

```python
from driftcheck import DriftMonitor

monitor = DriftMonitor(
    reference_data="s3://my-bucket/training_features.parquet",
    alert_webhook="https://hooks.slack.com/services/T00/B00/xxx"
)

# Call on each prediction batch
monitor.check(current_batch_df)
```

## Features

- **Statistical tests**: KS, PSI, Chi-squared, Jensen-Shannon divergence
- **Confidence monitoring**: tracks prediction probability distributions
- **Schema validation**: detects missing/extra/retyped columns
- **Adaptive thresholds**: auto-calibrates sensitivity per feature
- **Zero-config alerts**: Slack, PagerDuty, or custom webhook
- **Lightweight**: no DB, no server — runs in-process or as a cron job

## Architecture

```
driftcheck/
├── __init__.py
├── monitor.py          Core DriftMonitor class
├── statistics/
│   ├── ks.py           Kolmogorov-Smirnov test
│   ├── psi.py          Population Stability Index
│   ├── chi2.py         Chi-squared test
│   └── jsd.py          Jensen-Shannon divergence
├── alerts/
│   ├── slack.py        Slack webhook integration
│   ├── pagerduty.py    PagerDuty events API
│   └── webhook.py      Generic HTTP POST
├── schema.py           Schema validation
├── thresholds.py       Adaptive threshold calibration
└── io/
    ├── parquet.py      Parquet reader (pyarrow)
    ├── csv.py          CSV reader
    └── s3.py           S3 integration
```

## Configuration

```yaml
# driftcheck.yaml
reference:
  path: s3://ml-data/reference/features_2024q3.parquet
  refresh_interval: 7d

monitors:
  - name: feature_drift
    tests: [ks, psi]
    threshold: 0.05
    features: ["age", "income", "credit_score", "tenure"]

  - name: prediction_confidence
    type: confidence
    min_mean: 0.75
    max_entropy: 1.2

  - name: schema
    type: schema
    strict: true

alerts:
  slack:
    webhook_url: ${SLACK_WEBHOOK_URL}
    channel: "#ml-alerts"
  pagerduty:
    routing_key: ${PD_ROUTING_KEY}
    severity: warning
```

## Usage Examples

### As a library

```python
from driftcheck import DriftMonitor, KSTest, PSITest

monitor = DriftMonitor(
    reference_data="./reference.parquet",
    tests=[KSTest(threshold=0.05), PSITest(threshold=0.1)],
    features=["age", "income", "credit_score"]
)

results = monitor.check(new_batch_df)
for alert in results.alerts:
    print(f"DRIFT: {alert.feature} — {alert.test} p={alert.p_value:.4f}")
```

### As a CLI

```bash
# One-shot check
driftcheck run --reference ref.parquet --current today.parquet

# Continuous monitoring (cron-friendly)
driftcheck watch --config driftcheck.yaml --interval 1h
```

## Benchmarks

| Dataset size | Features | Time (single check) | Memory |
|-------------|----------|-------------------|--------|
| 10K rows | 20 | 45ms | 12MB |
| 100K rows | 50 | 320ms | 89MB |
| 1M rows | 100 | 2.1s | 410MB |

## Contributing

```bash
git clone https://github.com/nullzone-test/driftcheck.git
cd driftcheck
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make test
```

## License

Apache 2.0
