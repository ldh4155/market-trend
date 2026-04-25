import httpx
from app.core.config import settings

_DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"
_MAX_GROUPS_PER_REQUEST = 5


async def fetch_trend(
    start_date: str,
    end_date: str,
    time_unit: str,
    keyword_groups: list[dict],
) -> dict:
    """
    Naver DataLab 통합 검색어 트렌드 API 단일 호출.
    keyword_groups: [{"groupName": str, "keywords": [str]}] 최대 5개
    """
    headers = {
        "X-Naver-Client-Id": settings.NAVER_DATALAB_CLIENT_ID,
        "X-Naver-Client-Secret": settings.NAVER_DATALAB_CLIENT_SECRET,
        "Content-Type": "application/json",
    }
    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(_DATALAB_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()


def chunk_keyword_groups(items: list[tuple[str, list[str]]]) -> list[list[dict]]:
    """이름-키워드 쌍 리스트를 API 제한(5개)에 맞춰 배치로 분할."""
    batches = []
    for i in range(0, len(items), _MAX_GROUPS_PER_REQUEST):
        chunk = items[i : i + _MAX_GROUPS_PER_REQUEST]
        batches.append(
            [{"groupName": name, "keywords": keywords} for name, keywords in chunk]
        )
    return batches
