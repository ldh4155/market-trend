import pytest
from fastapi.testclient import TestClient

import app.api.router as router_module
from app.data.sectors import SECTOR_NAMES
from app.main import app


client = TestClient(app)


def test_health_check_returns_ok():
    """헬스 체크 API는 정상 상태를 반환한다."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_sectors_returns_configured_sector_names():
    """섹터 목록 API는 설정된 섹터명을 그대로 반환한다."""
    response = client.get("/api/trends/sectors/list")

    assert response.status_code == 200
    assert response.json() == {"sectors": SECTOR_NAMES}


def test_sector_trends_returns_service_response(monkeypatch):
    """섹터 트렌드 API는 요청 값을 서비스에 전달하고 응답을 반환한다."""
    sector = SECTOR_NAMES[0]

    async def fake_get_sector_trends(start_date, end_date, time_unit, sectors):
        assert start_date == "2026-01-01"
        assert end_date == "2026-01-31"
        assert time_unit == "week"
        assert sectors == [sector]
        return {
            "start_date": start_date,
            "end_date": end_date,
            "time_unit": time_unit,
            "results": [
                {
                    "sector": sector,
                    "average_ratio": 12.5,
                    "data": [{"period": "2026-01-01", "ratio": 12.5}],
                }
            ],
        }

    monkeypatch.setattr(router_module, "get_sector_trends", fake_get_sector_trends)

    response = client.post(
        "/api/trends/sectors",
        json={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "time_unit": "week",
            "sectors": [sector],
        },
    )

    assert response.status_code == 200
    assert response.json()["results"][0]["sector"] == sector


def test_sector_trends_validation_rejects_unknown_sector():
    """섹터 트렌드 API는 존재하지 않는 섹터 요청을 검증 오류로 처리한다."""
    response = client.post(
        "/api/trends/sectors",
        json={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "time_unit": "week",
            "sectors": ["unknown-sector"],
        },
    )

    assert response.status_code == 422


def test_sector_trends_service_error_returns_bad_gateway(monkeypatch):
    """섹터 트렌드 서비스 오류는 502 응답으로 변환된다."""
    sector = SECTOR_NAMES[0]

    async def fake_get_sector_trends(*args, **kwargs):
        raise RuntimeError("upstream failed")

    monkeypatch.setattr(router_module, "get_sector_trends", fake_get_sector_trends)

    response = client.post(
        "/api/trends/sectors",
        json={
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "sectors": [sector],
        },
    )

    assert response.status_code == 502
    assert "upstream failed" in response.json()["detail"]
