# Sorftime API Documentation

> **Source**: Extracted from `Sorftime Aamazon APIs - 标准版.pdf` (Text Dump).

## 1. Overview
- **Base URL**: `https://standardapi.sorftime.com/api` (Inferred from previous context, though not explicitly in text dump, usually standard)
- **Authentication**:
  - Header: `Authorization: BasicAuth <Key>`
  - Header: `ContentType: application/json;charset=UTF-8`
- **Domain Mapping**:
  - 1: US (美国)
  - 2: GB (英国)
  - 3: DE (德国)
  - 4: FR (法国)
  - 5: IN (印度)
  - 6: CA (加拿大)
  - 7: JP (日本)
  - 8: ES (西班牙)
  - 9: IT (意大利)
  - 10: MX (墨西哥)
  - 11: AE (阿联酋)
  - 12: AU (澳洲)
  - 13: BR (巴西)
  - 14: SA (沙特)

## 2. Common Response Structure

```json
{
  "requestLeft": "Integer (Remaining requests for the month)",
  "requestConsumed": "Integer (Requests consumed by this call)",
  "requestCount": "Integer (Requests count in this minute)",
  "code": "Integer (0: Success, others: Error)",
  "message": "String (Response message)",
  "data": "Object/Array (Specific data)"
}
```

## 3. Endpoints

### 3.1 Category Market

#### 1. Category Tree (`/CategoryTree`)
- **Method**: POST
- **Cost**: 5 requests
- **URL**: `/CategoryTree?domain=<domain_id>`
- **Parameters**:
  - `gzip` (Optional, 0 or 1): If 1, returns Base64 encoded Gzip string.
- **Data**: `CategoryTreeObject` Array

#### 2. Category Best Sellers (`/CategoryRequest`)
- **Method**: POST
- **Cost**: 5 requests (Historical: 10 per 3 days)
- **URL**: `/CategoryRequest?domain=<domain_id>`
- **Parameters**:
  - `nodeId` (String, Required): Category Node ID.
  - `queryStart` (String, Optional): Start date (yyyy-MM-dd) for historical data.
  - `queryDate` (String, Optional): End date (yyyy-MM-dd).
  - `querydays` (Integer, Optional): Legacy parameter.
- **Data**: `CategoryObject`

#### 3. Category All Hot Products (`/CategoryProducts`)
- **Method**: POST
- **Cost**: 5 requests
- **URL**: `/CategoryRequest?domain=<domain_id>` (Note: URL seems same as above, likely distinguished by params or typo in doc? Doc says `/CategoryRequest` but title is different. **Wait, doc says URL is `/CategoryRequest` for both?** Let's assume it might be a typo in doc or controlled by params. Actually, looking at param `page`, it might be the same endpoint but different behavior if `page` is present? No, `CategoryRequest` above has `nodeId` too. Let's check if `CategoryProducts` is a distinct endpoint name in other docs. For now, trust the doc text: URL is `/CategoryRequest` but params include `page`.)
  - *Correction*: The text says "3. 类目全部热销产品（CategoryProducts）... URL：/CategoryRequest...". This implies it might be the same endpoint, but the title suggests `CategoryProducts`. Let's treat it as `CategoryRequest` with `page` parameter for now.
- **Parameters**:
  - `nodeId` (String, Required)
  - `page` (Integer, Optional): Default 1. Max 100 products per page.
- **Data**: `ProductListObject`

#### 4. Category Market History Trend (`/CategoryTrend`)
- **Method**: POST
- **Cost**: 2 requests
- **URL**: `/CategoryTrend?domain=<domain_id>`
- **Parameters**:
  - `nodeId` (String, Required)
  - `trendIndex` (Integer, Required): Trend type (0-39, e.g., 0: Sales, 1: Brand Count, etc.)
- **Data**: String Array (Trend data)

### 3.2 Products

#### 5. Product Details (`/ProductRequest`)
- **Method**: POST
- **Cost**: 1 request
- **URL**: `/ProductRequest?domain=<domain_id>`
- **Parameters**:
  - `asin` (String, Required): Comma separated for multiple (max 10).
  - `trend` (Integer, Optional): 1: Include trend (default), 2: Exclude.
  - `queryTrendStartDt` (String, Optional): Start date (yyyy-MM-dd).
  - `queryTrendEndDt` (String, Optional): End date.
  - `gzip` (Optional): 0 or 1.
- **Data**: `ProductObject` (or Array if multiple ASINs)

#### 6. Product Search (`/ProductQuery`)
- **Method**: POST
- **Cost**: 5 requests
- **URL**: `/ProductQuery?domain=<domain_id>`
- **Parameters**:
  - `query` (Integer, Optional): 1: Single condition (default), 2: Multi-condition.
  - `queryType` (Integer): Condition type (1: Similar, 2: Category, 3: Brand, etc.)
  - `pattern` (String/JSON): Value for the condition.
  - `queryMonth` (String, Optional): Historical month (yyyy-MM).
  - `page` (Integer, Optional): Default 1.
- **Data**: `ProductListObject`

#### 7. Official Sub-variant Sales (`/AsinSalesVolume`)
- **Method**: POST
- **Cost**: 1 request
- **URL**: `/AsinSalesVolume?domain=<domain_id>`
- **Parameters**:
  - `asin` (String, Required)
  - `queryDate` (String, Optional): Start date.
  - `queryEndDate` (String, Optional): End date.
  - `page` (Integer, Optional): Default 1.
- **Data**: 2D String Array

#### 8. Product Variation History (`/ProductVariationHistory`)
- **Method**: POST
- **Cost**: 1 request
- **URL**: `/ProductVariationHistory?domain=<domain_id>`
- **Parameters**:
  - `asin` (String, Required)
- **Data**: String Array

#### 10. Product Realtime Data (`/ProductRealtimeRequest`)
- **Method**: POST
- **Cost**: 0 requests (Consumes Points: 1 or 2)
- **URL**: `/ProductRealtimeRequest?domain=<domain_id>`
- **Parameters**:
  - `asin` (String, Required)
  - `update` (Integer, Optional): Update threshold hours (default 24).

#### 11. Product Realtime Status (`/ProductRealtimeRequestStatusQuery`)
- **Method**: POST
- **URL**: `/ProductRealtimeRequestStatusQuery?domain=<domain_id>`
- **Parameters**:
  - `queryDate` (String, Required): yyyy-MM-dd.

#### 14. Product Reviews (`/ProductReviewsQuery`)
- **Method**: POST
- **Cost**: 5 requests
- **URL**: `/ProductReviewsQuery?domain=<domain_id>`
- **Parameters**:
  - `asin` (String, Required)
  - `querystartdt` (String, Optional)
  - `star` (Integer, Optional): Filter by star.
  - `onlyPurchase` (Integer, Optional)
  - `pageIndex` (Integer, Optional)
- **Data**: `ReviewsObject` Array

### 3.3 Keywords

#### 18. Keyword Query (`/KeywordQuery`)
- **Method**: POST
- **Cost**: 5 requests
- **URL**: `/KeywordQuery?domain=<domain_id>`
- **Parameters**:
  - `pattern` (Object): `KeywordQueryPatternObject`
  - `pageIndex` (Integer)
  - `pageSize` (Integer)
- **Data**: `KeywordSummeryObject` Array

#### 20. Keyword Details (`/KeywordRequest`)
- **Method**: POST
- **Cost**: 1 request
- **URL**: `/KeywordRequest?domain=<domain_id>`
- **Parameters**:
  - `keyword` (String, Required)
- **Data**: `KeywordObject`

#### 23. ASIN Reverse Keyword (`/ASINRequestKeywordv2`)
- **Method**: POST
- **Cost**: 1 request
- **URL**: `/ASINRequestKeywordv2?domain=<domain_id>`
- **Parameters**:
  - `asin` (String, Required)
  - `pageIndex` (Integer)
  - `pageSize` (Integer)
- **Data**: `ASINKeywordItemObject` Array

## 4. Data Objects (Key Fields)

### CategoryTreeObject
- `id`, `ParentId`, `nodeid`, `Name`, `CNName`, `URL`

### ProductSummeryObject
- `title`, `photo`, `asin`, `parentAsin`, `price`, `brand`, `rank`, `ratings`, `salesVolumeOfDaily`, `salesVolumeOfMonth`

### ProductObject
- `title`, `photo`, `Description`, `listingSalesVolumeOfDailyTrend`, `listingSalesOfMonthTrend`, `priceTrend`, `variationASIN`, `attribute`

### KeywordSummeryObject
- `keyword`, `searchVolume`, `rank`, `cpc`, `top3asin`

---
*Note: This documentation is a summary. Refer to the full text dump for detailed field descriptions and enum values.*
