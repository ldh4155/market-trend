import pytest
from pydantic import ValidationError

from app.data.sectors import SECTOR_NAMES
from app.schemas.trend import CompanyTrendRequest, SectorTrendRequest, TimeUnit


def test_sector_trend_request_defaults_time_unit_to_week():
    """섹터 트렌드 요청은 집계 단위 기본값으로 week를 사용한다."""
    request = SectorTrendRequest(
        start_date="2026-01-01",
        end_date="2026-01-31",
        sectors=[SECTOR_NAMES[0]],
    )

    assert request.time_unit == TimeUnit.week


def test_sector_trend_request_rejects_empty_sectors():
    """섹터 트렌드 요청은 빈 섹터 목록을 허용하지 않는다."""
    with pytest.raises(ValidationError):
        SectorTrendRequest(
            start_date="2026-01-01",
            end_date="2026-01-31",
            sectors=[],
        )


def test_company_trend_request_rejects_unknown_sector():
    """기업 트렌드 요청은 존재하지 않는 섹터를 허용하지 않는다."""
    with pytest.raises(ValidationError):
        CompanyTrendRequest(
            start_date="2026-01-01",
            end_date="2026-01-31",
            sector="unknown-sector",
        )
