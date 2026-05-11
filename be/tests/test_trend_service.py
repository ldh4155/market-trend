import asyncio

from app.services import trend_service


def test_get_sector_trends_sorts_by_average_ratio_and_handles_empty_data(
    monkeypatch,
):
    """섹터 트렌드는 평균 비율 내림차순으로 정렬하고 빈 데이터 평균을 0으로 처리한다."""
    monkeypatch.setattr(
        trend_service,
        "SECTORS",
        {
            "Low": {"keywords": ["low"]},
            "High": {"keywords": ["high"]},
            "Empty": {"keywords": ["empty"]},
        },
    )

    async def fake_fetch_trend(start_date, end_date, time_unit, keyword_groups):
        data_by_title = {
            "Low": [{"period": "2026-01-01", "ratio": 10.0}],
            "High": [{"period": "2026-01-01", "ratio": 50.0}],
            "Empty": [],
        }
        return {
            "results": [
                {"title": group["groupName"], "data": data_by_title[group["groupName"]]}
                for group in keyword_groups
            ]
        }

    monkeypatch.setattr(trend_service, "fetch_trend", fake_fetch_trend)

    result = asyncio.run(
        trend_service.get_sector_trends(
            "2026-01-01",
            "2026-01-31",
            "week",
            ["Low", "High", "Empty"],
        )
    )

    assert result["start_date"] == "2026-01-01"
    assert result["end_date"] == "2026-01-31"
    assert result["time_unit"] == "week"
    assert [item["sector"] for item in result["results"]] == ["High", "Low", "Empty"]
    assert [item["average_ratio"] for item in result["results"]] == [50.0, 10.0, 0.0]
