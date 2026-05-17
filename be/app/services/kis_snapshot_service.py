from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import KisNearHighLowSnapshot
from app.schemas.kis_snapshot import (
    KisNewHighPricePoint,
    KisThirtyDayNewHighResponse,
    KisThirtyDayNewHighResult,
    KisWeeklyNewHighResponse,
    KisWeeklyNewHighResult,
)
from app.services.kis_client import KisClient


def collect_near_highlow_snapshots(
    db: Session,
    *,
    collected_date: date | None = None,
    price_class_code: str = "0",
    input_market_code: str = "0000",
) -> int:
    # 한국투자증권 API에서 신고/신저근접 종목을 받아 일자별 스냅샷으로 저장한다.
    client = KisClient()
    access_token = client.issue_access_token()
    rows = client.fetch_near_highlow(
        access_token=access_token,
        price_class_code=price_class_code,
        input_market_code=input_market_code,
    )
    values = [
        _snapshot_value(row, collected_date or date.today(), price_class_code, input_market_code)
        for row in rows
    ]
    if not values:
        return 0

    stmt = insert(KisNearHighLowSnapshot).values(values)
    update_columns = {
        column.name: getattr(stmt.excluded, column.name)
        for column in KisNearHighLowSnapshot.__table__.columns
        if column.name not in {"id", "collected_at"}
    }
    db.execute(
        stmt.on_conflict_do_update(
            constraint="uq_kis_near_highlow_snapshot_daily_stock",
            set_=update_columns,
        )
    )
    db.commit()
    return len(values)


def get_weekly_new_high_intersection(
    db: Session,
    *,
    base_date: date | None = None,
) -> KisWeeklyNewHighResponse:
    # 기준일이 속한 ISO 주와 직전 ISO 주 모두에 신고가로 등장한 종목을 찾는다.
    target_date = base_date or date.today()
    current_week_start = target_date - timedelta(days=target_date.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    previous_week_start = current_week_start - timedelta(days=7)
    previous_week_end = current_week_start - timedelta(days=1)

    current_week = _new_high_stocks_subquery(
        current_week_start,
        current_week_end,
        "current_week",
    )
    previous_week = _new_high_stocks_subquery(
        previous_week_start,
        previous_week_end,
        "previous_week",
    )

    rows = db.execute(
        select(current_week.c.stock_code, current_week.c.stock_name)
        .join(previous_week, previous_week.c.stock_code == current_week.c.stock_code)
        .order_by(current_week.c.stock_code)
    ).all()

    return KisWeeklyNewHighResponse(
        base_date=target_date,
        current_week_start=current_week_start,
        current_week_end=current_week_end,
        previous_week_start=previous_week_start,
        previous_week_end=previous_week_end,
        results=[
            KisWeeklyNewHighResult(stock_code=row.stock_code, stock_name=row.stock_name)
            for row in rows
        ],
    )


def get_thirty_day_new_high_repeats(
    db: Session,
    *,
    end_date: date | None = None,
) -> KisThirtyDayNewHighResponse:
    # 기준 종료일 포함 최근 30일 동안 신고가에 2번 이상 등장한 종목을 집계한다.
    target_end_date = end_date or date.today()
    start_date = target_end_date - timedelta(days=29)

    appearance_rows = db.execute(
        select(
            KisNearHighLowSnapshot.stock_code,
            func.max(KisNearHighLowSnapshot.stock_name).label("stock_name"),
            func.count(KisNearHighLowSnapshot.id).label("appearance_count"),
        )
        .where(_new_high_date_filter(start_date, target_end_date))
        .group_by(KisNearHighLowSnapshot.stock_code)
        .having(func.count(KisNearHighLowSnapshot.id) >= 2)
        .order_by(KisNearHighLowSnapshot.stock_code)
    ).all()

    stock_codes = [row.stock_code for row in appearance_rows]
    prices_by_stock_code: dict[str, list[KisNewHighPricePoint]] = {
        stock_code: [] for stock_code in stock_codes
    }
    if stock_codes:
        price_rows = db.execute(
            select(
                KisNearHighLowSnapshot.stock_code,
                KisNearHighLowSnapshot.collected_date,
                KisNearHighLowSnapshot.new_high_price,
            )
            .where(
                and_(
                    _new_high_date_filter(start_date, target_end_date),
                    KisNearHighLowSnapshot.stock_code.in_(stock_codes),
                )
            )
            .order_by(
                KisNearHighLowSnapshot.stock_code,
                KisNearHighLowSnapshot.collected_date,
            )
        ).all()
        for price_row in price_rows:
            prices_by_stock_code[price_row.stock_code].append(
                KisNewHighPricePoint(
                    collected_date=date.fromisoformat(price_row.collected_date),
                    new_high_price=price_row.new_high_price,
                )
            )

    results: list[KisThirtyDayNewHighResult] = []
    for row in appearance_rows:
        results.append(
            KisThirtyDayNewHighResult(
                stock_code=row.stock_code,
                stock_name=row.stock_name,
                appearance_count=row.appearance_count,
                prices=prices_by_stock_code[row.stock_code],
            )
        )

    return KisThirtyDayNewHighResponse(
        start_date=start_date,
        end_date=target_end_date,
        results=results,
    )


def _snapshot_value(
    row: dict[str, Any],
    collected_date: date,
    price_class_code: str,
    input_market_code: str,
) -> dict[str, Any]:
    return {
        "collected_date": collected_date.isoformat(),
        "market_code": "J",
        "input_market_code": input_market_code,
        "price_class_code": price_class_code,
        "stock_code": str(row.get("mksc_shrn_iscd") or "").strip(),
        "stock_name": str(row.get("hts_kor_isnm") or "").strip(),
        "current_price": _to_int(row.get("stck_prpr")),
        "accumulated_volume": _to_int(row.get("acml_vol")),
        "new_high_price": _to_optional_int(row.get("new_hgpr")),
        "high_near_rate": _to_optional_decimal(row.get("hprc_near_rate")),
        "new_low_price": _to_optional_int(row.get("new_lwpr")),
        "low_near_rate": _to_optional_decimal(row.get("lwpr_near_rate")),
        "base_price": _to_optional_int(row.get("stck_sdpr")),
    }


def _new_high_stocks_subquery(start_date: date, end_date: date, name: str):
    # 주간 교집합 계산을 위해 기간별 신고가 종목 목록을 중복 없이 만든다.
    return (
        select(
            KisNearHighLowSnapshot.stock_code.label("stock_code"),
            func.max(KisNearHighLowSnapshot.stock_name).label("stock_name"),
        )
        .where(_new_high_date_filter(start_date, end_date))
        .group_by(KisNearHighLowSnapshot.stock_code)
        .subquery(name)
    )


def _new_high_date_filter(start_date: date, end_date: date):
    # 신고근접 데이터만 ISO 날짜 문자열 범위로 필터링한다.
    return and_(
        KisNearHighLowSnapshot.price_class_code == "0",
        KisNearHighLowSnapshot.collected_date >= start_date.isoformat(),
        KisNearHighLowSnapshot.collected_date <= end_date.isoformat(),
    )


def _to_int(value: Any) -> int:
    parsed = _to_optional_int(value)
    return parsed if parsed is not None else 0


def _to_optional_int(value: Any) -> int | None:
    if value in {None, ""}:
        return None
    return int(str(value).replace(",", "").strip())


def _to_optional_decimal(value: Any) -> Decimal | None:
    if value in {None, ""}:
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except InvalidOperation:
        return None
