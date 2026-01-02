# Jeff Data Core (JDC)

JDC is the standalone Data Engine for AskJeff. It is responsible for:

1. **Extracting** data from external sources (Amazon, Shopify, Scrapers).
2. **Loading** raw data into storage (Postgres/S3).
3. **Transforming** raw data into standardized business metrics.

## Philosophy

* **Zero Dependency**: This package does NOT import `app.*` from AskJeff.
* **Configuration Driven**: All credentials and connections are injected at runtime.

## Usage

```python
from jeff_data_core.core.engine import JeffDataEngine
from jeff_data_core.connectors.amazon import AmazonAdsConnector

# Initialize Engine
engine = JeffDataEngine(
    storage_url="postgresql://user:pass@localhost/db"
)

# Register Connector
connector = AmazonAdsConnector(
    client_id="...",
    client_secret="...",
    refresh_token="..."
)

# Run Sync
engine.run_sync(connector, date_range=("2023-01-01", "2023-01-31"))
```
