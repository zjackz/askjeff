# AskJeff Data Engine Architecture (JDE)

## 1. Vision

Build a centralized, robust **Data Engine** that ingests multi-source e-commerce data, normalizes it, and serves actionable insights to AI Agents.
**Philosophy**: "Raw Data First, Intelligence on Top."

## 2. Architecture Overview: Jeff Data Core (JDC)

To ensure **Pluggability** and **Reusability**, the Data Engine is designed as a standalone library, decoupled from the main AskJeff application.

```mermaid
graph TB
    subgraph "External World"
        A[Amazon Ads]
        B[Shopify]
        C[TikTok Shop]
    end

    subgraph "Jeff Data Core (Standalone Lib)"
        D[Source Connectors] --> E[Normalization Engine]
        E --> F[Standard Output (Pandas/JSON)]
    end

    subgraph "Host Applications"
        G[AskJeff Backend]
        H[Another Analytics App]
        I[Data Warehouse Script]
    end

    A & B & C --> D
    F --> G
    F --> H
    F --> I
```

## 3. Data Sources Strategy

We categorize data into 5 distinct layers based on their origin and role:

### 3.1 Internal Data (Amazon API)

* **Role**: The "Truth". Your actual business performance.
* **Examples**: Orders, Inventory, Ad Spend, ACOS.
* **Handling**: High-frequency sync via `AmazonAdsConnector` & `AmazonSPConnector`.

### 3.2 External Data (Scrapers)

* **Role**: The "Battlefield". What customers actually see.
* **Examples**: Organic Rankings, Competitor Ad Positions, BSR Badges.
* **Handling**: Scheduled crawls via `ScraperConnector`. Needs robust HTML parsing.

### 3.3 Market Data (3rd Party APIs)

* **Role**: The "God View". Macro trends beyond your store.
* **Examples**: Category Volume (Sorftime), Keyword Volume (SellerSprite).
* **Handling**: On-demand fetch via `MarketDataConnector` to benchmark internal performance.

### 3.4 AI Enrichment (LLM as a Processor)

* **Role**: The "Refinery". Converting unstructured text/images into structured insights.
* **Examples**:
  * Input: 100 negative reviews. -> Output: "Main issue: Zipper quality".
  * Input: Product Image. -> Output: "Style: Minimalist, Color: Blue".
* **Handling**: Implemented as `Transformation Pipelines` using DeepSeek/OpenAI.

### 3.5 User Context (Manual Input)

* **Role**: The "Strategy". Information only the human knows.
* **Examples**: Brand Positioning, Target Audience, COGS (if not in Amazon).
* **Handling**: Simple UI forms stored in `Context Tables`.

## 4. Core Design Principles

### 4.1 Zero Dependency

* **Rule**: JDC must NOT import anything from `app.*`.
* **Goal**: You should be able to copy the `jdc` folder to a completely new project, run `pip install -r requirements.txt`, and start fetching data immediately.

### 4.2 Configuration Injection

* Instead of reading `.env` directly, JDC accepts a `Config` object at initialization.

    ```python
    engine = JeffDataEngine(
        credentials={"amazon": {...}},
        storage_backend="postgres://..."
    )
    ```

### 4.3 Standardized Interface

* **Sources**: All connectors implement a standard protocol (e.g., `fetch_report(date_range)`).
* **Sinks**: Data can be output to multiple destinations (Postgres, S3, Local File) via adapters.

## 5. Package Structure (Proposed)

We will create a `packages` directory to house this independent library.

```text
/backend
  /packages
    /jeff-data-core        <-- The Independent Library
      /connectors          <-- Amazon, Shopify, etc.
      /normalizers         <-- Raw JSON -> Standard Schema
      /storage             <-- S3, Postgres Adapters
      pyproject.toml       <-- Its own dependencies
  /app                     <-- AskJeff Main App
    /services
      data_service.py      <-- Imports jeff-data-core
```

## 6. Implementation Roadmap

### Phase 1: The Core & Amazon Connector

* [ ] Setup `backend/packages/jeff-data-core` structure.
* [ ] Implement `AmazonAdsSource` (focusing on Search Term Reports).
* [ ] Implement `PostgresSink` (for Raw Data storage).

### Phase 2: Integration

* [ ] Import `jeff-data-core` into AskJeff.
* [ ] Create a Celery task in AskJeff to trigger the engine.

## 7. Technology Stack Recommendation

* **Language**: Python 3.12
* **Data Processing**: Pandas (for heavy lifting)
* **Validation**: Pydantic V2
* **HTTP Client**: Httpx (Async)
