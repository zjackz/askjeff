from pydantic import BaseModel, Field, AliasChoices, ConfigDict
from typing import List, Optional, Any, Dict, Union

# --- Common Models ---

class SorftimeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    requestLeft: Optional[int] = Field(None, validation_alias=AliasChoices('requestLeft', 'RequestLeft'))
    requestConsumed: Optional[int] = Field(None, validation_alias=AliasChoices('requestConsumed', 'RequestConsumed'))
    requestCount: Optional[int] = Field(None, validation_alias=AliasChoices('requestCount', 'RequestCount'))
    code: int = Field(..., validation_alias=AliasChoices('code', 'Code'))
    message: Optional[str] = Field(None, validation_alias=AliasChoices('message', 'Message'))
    data: Optional[Any] = Field(None, validation_alias=AliasChoices('data', 'Data'))

# --- Product Data Models ---

class ProductObject(BaseModel):
    Title: Optional[str] = None
    Photo: Optional[List[str]] = None
    EBCPhoto: Optional[List[str]] = None
    StoreName: Optional[str] = None
    Description: Optional[str] = None
    ProductBadge: Optional[List[str]] = None
    UpdateDate: Optional[str] = None
    ListingSalesVolumeOfDailyTrend: Optional[List[Any]] = None
    ListingSalesOfDailyTrend: Optional[List[Any]] = None
    ListingSalesVolumeOfMonthTrend: Optional[List[Any]] = None
    ListingSalesOfMonthTrend: Optional[List[Any]] = None
    RankTrend: Optional[List[Any]] = None
    BsrRankTrend: Optional[List[Dict[str, Any]]] = None
    DealTrend: Optional[List[Any]] = None
    OffSale: Optional[int] = None
    Asin: Optional[str] = None
    ParentAsin: Optional[str] = None
    VariationASIN: Optional[List[str]] = None
    Attribute: Optional[str] = None
    VariationASINCount: Optional[int] = None
    PriceTrend: Optional[List[Any]] = None
    ListPriceTrend: Optional[List[Any]] = None
    ProductType: Optional[str] = None
    Coupon: Optional[int] = None
    SalesPrice: Optional[int] = None
    Brand: Optional[str] = None
    BuyboxSeller: Optional[str] = None
    BuyboxSellerId: Optional[str] = None
    BuyboxSellerAddress: Optional[str] = None
    IsFBA: Optional[bool] = None
    ShipCost: Optional[int] = None
    ShipsFrom: Optional[str] = None
    FbaFee: Optional[int] = None
    FbaDetetail: Optional[List[str]] = None
    PlatformFee: Optional[int] = None
    Profit: Optional[int] = None
    ProfitRate: Optional[float] = None
    OnlineDate: Optional[str] = None
    OnlineDays: Optional[int] = None
    RatingsCount: Optional[int] = None
    OneStartRatings: Optional[float] = None
    TwoStartRatings: Optional[float] = None
    ThreeStartRatings: Optional[float] = None
    FourStartRatings: Optional[float] = None
    FiveStartRatings: Optional[float] = None
    Category: Optional[List[str]] = None
    BsrCategory: Optional[List[List[str]]] = None
    Rank: Optional[int] = None
    SellerCount: Optional[int] = None
    HasVideo: Optional[bool] = None
    APlus: Optional[bool] = None
    HasBrandStore: Optional[bool] = None
    Size: Optional[List[str]] = None
    Weight: Optional[int] = None
    ExtraSavings: Optional[List[Dict[str, Any]]] = None
    Feature: Optional[List[str]] = None
    ProductInfo: Optional[List[str]] = None
    Property: Optional[List[str]] = None
    BrandPromotion: Optional[str] = None
    DealType: Optional[str] = None

# --- Product Request Models ---

class ProductRequestPayload(BaseModel):
    ASIN: str  # Comma separated for multiple
    Trend: int = 1  # 1: Include, 2: Exclude
    QueryTrendStartDt: Optional[str] = None
    QueryTrendEndDt: Optional[str] = None
    gzip: int = 0

class ProductQueryPayload(BaseModel):
    query: int = 1 # 1: Single condition
    queryType: int # 1: Similar, 2: Category, 3: Brand, etc.
    pattern: Union[str, Dict]
    page: int = 1

# --- Category Request Models ---

class CategoryRequestPayload(BaseModel):
    nodeId: str
    queryStart: Optional[str] = None
    queryDate: Optional[str] = None

class CategoryTrendPayload(BaseModel):
    nodeId: str
    trendIndex: int

# --- Keyword Request Models ---

class KeywordQueryPayload(BaseModel):
    pattern: Dict[str, Any]
    pageIndex: int = 1
    pageSize: int = 20

class KeywordRequestPayload(BaseModel):
    keyword: str

# --- Test API Models ---

class TestProductRequest(BaseModel):
    ASIN: str
    Trend: int = 1
    domain: int = 1

class TestCategoryRequest(BaseModel):
    nodeId: str
    domain: int = 1

class TestCategoryTreeRequest(BaseModel):
    domain: int = 1

class TestCategoryTrendRequest(BaseModel):
    nodeId: str
    trendIndex: int = 0
    domain: int = 1

class TestProductQueryRequest(BaseModel):
    queryType: int
    pattern: str
    domain: int = 1
    page: int = 1

class TestKeywordQueryRequest(BaseModel):
    keyword: str # Simplified for test: just search by keyword string
    domain: int = 1
    page: int = 1

class TestKeywordDetailRequest(BaseModel):
    keyword: str
    domain: int = 1
