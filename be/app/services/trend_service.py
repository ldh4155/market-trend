import asyncio
from app.data.sectors import SECTORS
from app.services.naver_datalab import fetch_trend, chunk_keyword_groups


def _parse_results(raw_results: list[dict]) -> dict[str, dict]:
    """API 응답에서 그룹별 average_ratio / data 추출."""
    parsed = {}
    for item in raw_results:
        name = item["title"]
        data = item["data"]
        avg = sum(d["ratio"] for d in data) / len(data) if data else 0.0
        parsed[name] = {"average_ratio": round(avg, 2), "data": data}
    return parsed


async def _fetch_all_batches(
    start_date: str,
    end_date: str,
    time_unit: str,
    items: list[tuple[str, list[str]]],
) -> dict[str, dict]:
    """배치 분할 후 병렬 호출, 결과 합산 반환."""
    batches = chunk_keyword_groups(items)
    tasks = [
        fetch_trend(start_date, end_date, time_unit, batch) for batch in batches
    ]
    responses = await asyncio.gather(*tasks)

    combined: dict[str, dict] = {}
    for resp in responses:
        combined.update(_parse_results(resp["results"]))
    return combined


async def get_sector_trends(
    start_date: str,
    end_date: str,
    time_unit: str,
    sectors: list[str],
) -> dict:
    items = [(s, SECTORS[s]["keywords"]) for s in sectors]
    combined = await _fetch_all_batches(start_date, end_date, time_unit, items)

    sorted_results = sorted(
        combined.items(), key=lambda x: x[1]["average_ratio"], reverse=True
    )
    return {
        "start_date": start_date,
        "end_date": end_date,
        "time_unit": time_unit,
        "results": [
            {"sector": name, **info} for name, info in sorted_results
        ],
    }


async def get_company_trends(
    start_date: str,
    end_date: str,
    time_unit: str,
    sector: str,
) -> dict:
    items = list(SECTORS[sector]["companies"].items())
    combined = await _fetch_all_batches(start_date, end_date, time_unit, items)

    sorted_results = sorted(
        combined.items(), key=lambda x: x[1]["average_ratio"], reverse=True
    )
    return {
        "start_date": start_date,
        "end_date": end_date,
        "time_unit": time_unit,
        "sector": sector,
        "results": [
            {"company": name, **info} for name, info in sorted_results
        ],
    }
