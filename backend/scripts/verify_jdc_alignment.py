import os
import sys

# Add backend to path so we can import packages
sys.path.append("/app")
sys.path.append("/app/packages/jeff-data-core")

from jeff_data_core import get_config, get_metrics, register_jdc_metrics, init_config, JDCConfig
from prometheus_client import CollectorRegistry, generate_latest

def test_config():
    print("Testing Config...")
    # Simulate env var
    os.environ["JDC_DATABASE_URL"] = "postgresql://test:test@localhost:5432/jdc_test"
    os.environ["JDC_DEFAULT_BATCH_SIZE"] = "5000"
    
    # 1. Test Auto Load
    cfg = get_config()
    print(f"JDC_DATABASE_URL: {cfg.DATABASE_URL}")
    assert cfg.DATABASE_URL == "postgresql://test:test@localhost:5432/jdc_test"
    print(f"JDC_DEFAULT_BATCH_SIZE: {cfg.DEFAULT_BATCH_SIZE}")
    assert cfg.DEFAULT_BATCH_SIZE == 5000
    
    # 2. Test Injection
    custom_cfg = JDCConfig(DATABASE_URL="sqlite:///:memory:")
    init_config(custom_cfg)
    assert get_config().DATABASE_URL == "sqlite:///:memory:"
    print("Config Test Passed!")

def test_metrics():
    print("\nTesting Metrics...")
    registry = CollectorRegistry()
    
    # 1. Register to custom registry
    register_jdc_metrics(registry)
    metrics = get_metrics()
    
    # 2. Record some data
    metrics.etl_rows_processed.labels(pipeline="amazon_ads", status="success").inc(100)
    
    # 3. Export
    output = generate_latest(registry).decode()
    print("Metrics Output:")
    print(output)
    
    assert "jdc_etl_rows_processed_total{pipeline=\"amazon_ads\",status=\"success\"} 100.0" in output
    print("Metrics Test Passed!")

if __name__ == "__main__":
    try:
        test_config()
        test_metrics()
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)
