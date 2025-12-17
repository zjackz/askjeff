from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.config import settings
from app.services.sorftime.client import SorftimeClient
from app.services.sorftime.models import (
    TestProductRequest, TestCategoryRequest, SorftimeResponse,
    TestCategoryTreeRequest, TestCategoryTrendRequest,
    TestProductQueryRequest, TestKeywordQueryRequest, TestKeywordDetailRequest
)

router = APIRouter()

def get_client(db: Session = Depends(get_db)):
    return SorftimeClient(account_sk=settings.sorftime_api_key, db=db)

@router.post("/test/product", response_model=SorftimeResponse)
async def test_product_request(
    request: TestProductRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        # Call product_request with comma-separated ASINs
        return await client.product_request(
            asin=request.ASIN,  # 直接传递逗号分隔的字符串
            trend=0,  # 不需要趋势数据
            domain=request.domain
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/category", response_model=SorftimeResponse)
async def test_category_request(
    request: TestCategoryRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.category_request(
            node_id=request.nodeId,
            domain=request.domain
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/category-tree", response_model=SorftimeResponse)
async def test_category_tree(
    request: TestCategoryTreeRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.category_tree(domain=request.domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/category-trend", response_model=SorftimeResponse)
async def test_category_trend(
    request: TestCategoryTrendRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.category_trend(
            node_id=request.nodeId,
            trend_index=request.trendIndex,
            domain=request.domain
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/product-query", response_model=SorftimeResponse)
async def test_product_query(
    request: TestProductQueryRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.product_query(
            query_type=request.queryType,
            pattern=request.pattern,
            page=request.page,
            domain=request.domain
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/keyword-query", response_model=SorftimeResponse)
async def test_keyword_query(
    request: TestKeywordQueryRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.keyword_query(
            pattern={"keyword": request.keyword},
            page_index=request.page,
            domain=request.domain
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/keyword-detail", response_model=SorftimeResponse)
async def test_keyword_detail(
    request: TestKeywordDetailRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.keyword_request(
            keyword=request.keyword,
            domain=request.domain
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
