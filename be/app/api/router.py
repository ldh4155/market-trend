from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data.sectors import SECTOR_NAMES
from app.db.session import get_db
from app.schemas.kis_snapshot import (
    KisThirtyDayNewHighResponse,
    KisWeeklyNewHighResponse,
)
from app.schemas.trend import (
    CompanyTrendRequest,
    CompanyTrendResponse,
    SectorListResponse,
    SectorTrendRequest,
    SectorTrendResponse,
)
from app.services.kis_snapshot_service import (
    get_thirty_day_new_high_repeats,
    get_weekly_new_high_intersection,
)
from app.services.trend_service import get_company_trends, get_sector_trends

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/trends/sectors/list", response_model=SectorListResponse)
async def list_sectors():
    """사용 가능한 섹터 목록을 반환한다."""
    return {"sectors": SECTOR_NAMES}


@router.post("/trends/sectors", response_model=SectorTrendResponse)
async def sector_trends(request: SectorTrendRequest):
    """선택한 섹터의 검색 트렌드를 비교한다."""
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
    """특정 섹터 내 기업의 검색 트렌드를 비교한다."""
    try:
        return await get_company_trends(
            request.start_date,
            request.end_date,
            request.time_unit.value,
            request.sector,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Naver DataLab API 오류: {e}")


@router.get(
    "/new-highs/weekly",
    response_model=KisWeeklyNewHighResponse,
)
def kis_weekly_new_highs(
    base_date: date | None = None,
    db: Session = Depends(get_db),
):
    """이번 주와 저번 주 모두 신고가로 등장한 종목을 반환한다."""
    return get_weekly_new_high_intersection(db, base_date=base_date)


@router.get(
    "/new-highs/30d",
    response_model=KisThirtyDayNewHighResponse,
)
def kis_thirty_day_new_highs(
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    """최근 30일 동안 신고가에 2번 이상 등장한 종목과 가격 이력을 반환한다."""
    return get_thirty_day_new_high_repeats(db, end_date=end_date)
