from datetime import date

from pydantic import BaseModel


class KisWeeklyNewHighResult(BaseModel):
    # 주간 비교에서 두 주 모두 신고가로 등장한 종목 정보.
    stock_code: str
    stock_name: str


class KisWeeklyNewHighResponse(BaseModel):
    # 기준 주와 직전 주의 신고가 교집합 응답.
    base_date: date
    current_week_start: date
    current_week_end: date
    previous_week_start: date
    previous_week_end: date
    results: list[KisWeeklyNewHighResult]


class KisNewHighPricePoint(BaseModel):
    # 특정 수집일에 기록된 신고가 가격.
    collected_date: date
    new_high_price: int | None


class KisThirtyDayNewHighResult(BaseModel):
    # 최근 30일 동안 신고가에 반복 등장한 종목의 집계 정보.
    stock_code: str
    stock_name: str
    appearance_count: int
    prices: list[KisNewHighPricePoint]


class KisThirtyDayNewHighResponse(BaseModel):
    # 최근 30일 반복 신고가 종목 응답.
    start_date: date
    end_date: date
    results: list[KisThirtyDayNewHighResult]
