import asyncio

from app.services import naver_datalab
from app.services.naver_datalab import chunk_keyword_groups, fetch_trend


def test_chunk_keyword_groups_splits_items_into_naver_sized_batches():
    """키워드 그룹은 Naver API 제한에 맞춰 5개 단위로 나뉜다."""
    items = [(f"group-{index}", [f"keyword-{index}"]) for index in range(6)]

    batches = chunk_keyword_groups(items)

    assert len(batches) == 2
    assert len(batches[0]) == 5
    assert batches[0][0] == {"groupName": "group-0", "keywords": ["keyword-0"]}
    assert batches[1] == [{"groupName": "group-5", "keywords": ["keyword-5"]}]


def test_chunk_keyword_groups_returns_empty_list_for_empty_items():
    """키워드 그룹이 없으면 빈 배치 목록을 반환한다."""
    assert chunk_keyword_groups([]) == []


def test_fetch_trend_posts_payload_and_returns_json(monkeypatch):
    """Naver DataLab 요청은 인증 헤더와 검색 조건을 전송하고 JSON 응답을 반환한다."""
    requests = []
    response_payload = {"results": [{"title": "A", "data": []}]}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return response_payload

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, headers, json):
            requests.append({"url": url, "headers": headers, "json": json})
            return FakeResponse()

    monkeypatch.setattr(naver_datalab.httpx, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(naver_datalab.settings, "NAVER_DATALAB_CLIENT_ID", "client-id")
    monkeypatch.setattr(
        naver_datalab.settings,
        "NAVER_DATALAB_CLIENT_SECRET",
        "client-secret",
    )

    keyword_groups = [{"groupName": "A", "keywords": ["alpha"]}]
    result = asyncio.run(
        fetch_trend("2026-01-01", "2026-01-31", "week", keyword_groups)
    )

    assert result == response_payload
    assert requests == [
        {
            "url": "https://openapi.naver.com/v1/datalab/search",
            "headers": {
                "X-Naver-Client-Id": "client-id",
                "X-Naver-Client-Secret": "client-secret",
                "Content-Type": "application/json",
            },
            "json": {
                "startDate": "2026-01-01",
                "endDate": "2026-01-31",
                "timeUnit": "week",
                "keywordGroups": keyword_groups,
            },
        }
    ]
