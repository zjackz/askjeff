# MCP Full Flow Test Report: Amazon Bestsellers
**Date:** 2025-12-16T10:40:00
**Target URL:** `https://www.amazon.com/gp/bestsellers/sporting-goods/16062041/ref=pd_zg_hrsr_sporting-goods`
**API Endpoint:** `http://localhost:8001/api/mcp/fetch`

## 1. Request Payload

```json
{
  "input": "https://www.amazon.com/gp/bestsellers/sporting-goods/16062041/ref=pd_zg_hrsr_sporting-goods",
  "type": "auto"
}
```

## 2. Response (Duration: 2.5s)
**Status Code:** 200

### Response Body

```json
{
  "status": "success",
  "message": "Successfully fetched 1000 items. Import Batch ID: 10",
  "count": 1000,
  "data": [
    {
      "asin": "B0054J2GDQ",
      "title": "Listerine Total Care Alcohol-Free Anticavity Mouthwash, 6 Benefit Fluoride Mouthwash for Bad Breath and Enamel Strength, Fresh Mint Flavor, Twin Convenience Pack, 2 x 1 L",
      "price": 15.94,
      "currency": "USD",
      "sales_rank": null,
      "reviews": 21178,
      "rating": 4.6,
      "category": null,
      "image_url": null,
      "raw_data": {
        "产品ASIN码": "B0054J2GDQ",
        "月销量": "64347",
        "月销售额": "1025691.18",
        "标题": "Listerine Total Care Alcohol-Free Anticavity Mouthwash, 6 Benefit Fluoride Mouthwash for Bad Breath and Enamel Strength, Fresh Mint Flavor, Twin Convenience Pack, 2 x 1 L",
        "品牌": "Listerine",
        "所处类目排名": "类目：Mouthwashes，排名:10",
        "价格": 15.94,
        "外包装尺寸": "29.44*22.86*7.77",
        "产品分类": "MOUTHWASH",
        "上线天数": 3206,
        "上线日期": "2017-03-07",
        "评论数": 21178,
        "星级": 4.6,
        "卖家": "Amazon"
      }
    },
    ...
  ]
}
```

## 3. Execution Log
1. **Input Parsing**: The system correctly identified the input as a URL and extracted Node ID `16062041`.
2. **MCP Tool Call**: Called `category_more_poroducts` with `{"nodeId": "16062041", "amzSite": "US"}`.
3. **Data Fetching**: Successfully retrieved 1000 items from Sorftime MCP.
4. **Data Normalization**: Mapped Chinese keys (e.g., `产品ASIN码`, `标题`) to system fields.
5. **Import Batch Creation**: Created Import Batch #10 and saved data to `imports/mcp_import_16062041.csv`.
