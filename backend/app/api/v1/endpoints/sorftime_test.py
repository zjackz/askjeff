from fastapi import APIRouter, HTTPException, Depends
from app.services.sorftime.client import SorftimeClient
from app.services.sorftime.models import (
    TestProductRequest, TestCategoryRequest, SorftimeResponse,
    TestCategoryTreeRequest, TestCategoryTrendRequest,
    TestProductQueryRequest, TestKeywordQueryRequest, TestKeywordDetailRequest
)

router = APIRouter()

def get_client():
    return SorftimeClient()

@router.post("/test/product", response_model=SorftimeResponse)
async def test_product_request(
    request: TestProductRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        # Convert comma-separated string back to list for the client method
        asins_list = [x.strip() for x in request.ASIN.split(',') if x.strip()]
        return await client.fetch_product_details(asins_list, request.domain)
    except Exception as e:
        # If client returns a dict (mock error), return it directly
        if isinstance(e, dict):
             return e
        # Otherwise log and raise
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/category", response_model=SorftimeResponse)
async def test_category_request(
    request: TestCategoryRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.fetch_category_best_sellers(request.nodeId, request.domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/category-tree", response_model=SorftimeResponse)
async def test_category_tree(
    request: TestCategoryTreeRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.fetch_category_tree(request.domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/category-trend", response_model=SorftimeResponse)
async def test_category_trend(
    request: TestCategoryTrendRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.fetch_category_trend(request.nodeId, request.trendIndex, request.domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/product-query", response_model=SorftimeResponse)
async def test_product_query(
    request: TestProductQueryRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.search_products(request.queryType, request.pattern, request.page, request.domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/keyword-query", response_model=SorftimeResponse)
async def test_keyword_query(
    request: TestKeywordQueryRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.search_keywords(request.keyword, request.page, request.domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/keyword-detail", response_model=SorftimeResponse)
async def test_keyword_detail(
    request: TestKeywordDetailRequest,
    client: SorftimeClient = Depends(get_client)
):
    try:
        return await client.fetch_keyword_details(request.keyword, request.domain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
