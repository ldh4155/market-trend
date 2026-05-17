from datetime import date

from fastapi.testclient import TestClient

import app.api.router as router_module
from app.db.session import get_db
from app.main import app
from app.schemas.kis_snapshot import (
    KisNewHighPricePoint,
    KisThirtyDayNewHighResponse,
    KisThirtyDayNewHighResult,
    KisWeeklyNewHighResponse,
    KisWeeklyNewHighResult,
)


client = TestClient(app)


def _override_db():
    yield object()


def test_kis_weekly_new_highs_endpoint_returns_service_response(monkeypatch):
    def fake_get_weekly_new_high_intersection(db, *, base_date=None):
        assert base_date == date(2026, 5, 17)
        return KisWeeklyNewHighResponse(
            base_date=date(2026, 5, 17),
            current_week_start=date(2026, 5, 11),
            current_week_end=date(2026, 5, 17),
            previous_week_start=date(2026, 5, 4),
            previous_week_end=date(2026, 5, 10),
            results=[KisWeeklyNewHighResult(stock_code="005930", stock_name="삼성전자")],
        )

    app.dependency_overrides[get_db] = _override_db
    monkeypatch.setattr(
        router_module,
        "get_weekly_new_high_intersection",
        fake_get_weekly_new_high_intersection,
    )
    try:
        response = client.get("/api/new-highs/weekly?base_date=2026-05-17")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "base_date": "2026-05-17",
        "current_week_start": "2026-05-11",
        "current_week_end": "2026-05-17",
        "previous_week_start": "2026-05-04",
        "previous_week_end": "2026-05-10",
        "results": [{"stock_code": "005930", "stock_name": "삼성전자"}],
    }


def test_kis_thirty_day_new_highs_endpoint_returns_service_response(monkeypatch):
    def fake_get_thirty_day_new_high_repeats(db, *, end_date=None):
        assert end_date == date(2026, 5, 17)
        return KisThirtyDayNewHighResponse(
            start_date=date(2026, 4, 18),
            end_date=date(2026, 5, 17),
            results=[
                KisThirtyDayNewHighResult(
                    stock_code="005930",
                    stock_name="삼성전자",
                    appearance_count=2,
                    prices=[
                        KisNewHighPricePoint(
                            collected_date=date(2026, 4, 18),
                            new_high_price=80000,
                        ),
                        KisNewHighPricePoint(
                            collected_date=date(2026, 5, 17),
                            new_high_price=82000,
                        ),
                    ],
                )
            ],
        )

    app.dependency_overrides[get_db] = _override_db
    monkeypatch.setattr(
        router_module,
        "get_thirty_day_new_high_repeats",
        fake_get_thirty_day_new_high_repeats,
    )
    try:
        response = client.get("/api/new-highs/30d?end_date=2026-05-17")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "start_date": "2026-04-18",
        "end_date": "2026-05-17",
        "results": [
            {
                "stock_code": "005930",
                "stock_name": "삼성전자",
                "appearance_count": 2,
                "prices": [
                    {"collected_date": "2026-04-18", "new_high_price": 80000},
                    {"collected_date": "2026-05-17", "new_high_price": 82000},
                ],
            }
        ],
    }
