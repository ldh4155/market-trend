from fastapi import APIRouter, HTTPException
from app.schemas.trend import (
    SectorTrendRequest,
    SectorTrendResponse,
    CompanyTrendRequest,
    CompanyTrendResponse,
    SectorListResponse,
)
from app.services.trend_service import get_sector_trends, get_company_trends
from app.data.sectors import SECTOR_NAMES

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/trends/sectors/list", response_model=SectorListResponse)
async def list_sectors():
    """사용 가능한 섹터 목록 반환."""
    return {"sectors": SECTOR_NAMES}


@router.post("/trends/sectors", response_model=SectorTrendResponse)
async def sector_trends(request: SectorTrendRequest):
    """선택한 섹터들의 검색 트렌드 비교 (높은 순 정렬)."""
    try:
        return await get_sector_trends(
            request.start_date,
            request.end_date,
            request.time_unit.value,
            request.sectors,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Naver DataLab API 오류: {e}")


@router.post("/trends/companies", response_model=CompanyTrendResponse)
async def company_trends(request: CompanyTrendRequest):
    """특정 섹터 내 기업들의 검색 트렌드 비교 (높은 순 정렬)."""
    try:
        return await get_company_trends(
            request.start_date,
            request.end_date,
            request.time_unit.value,
            request.sector,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Naver DataLab API 오류: {e}")
