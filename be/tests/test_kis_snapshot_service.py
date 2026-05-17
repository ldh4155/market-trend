from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import KisNearHighLowSnapshot
from app.services.kis_snapshot_service import (
    get_thirty_day_new_high_repeats,
    get_weekly_new_high_intersection,
)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()


def _add_snapshot(
    db,
    *,
    collected_date: str,
    stock_code: str,
    stock_name: str,
    price_class_code: str = "0",
    new_high_price: int | None = 1000,
):
    db.add(
        KisNearHighLowSnapshot(
            collected_date=collected_date,
            market_code="J",
            input_market_code="0000",
            price_class_code=price_class_code,
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=new_high_price or 0,
            accumulated_volume=100,
            new_high_price=new_high_price,
        )
    )


def test_get_weekly_new_high_intersection_returns_current_and_previous_week_overlap(db):
    _add_snapshot(db, collected_date="2026-05-11", stock_code="005930", stock_name="삼성전자")
    _add_snapshot(db, collected_date="2026-05-10", stock_code="005930", stock_name="삼성전자")
    _add_snapshot(db, collected_date="2026-05-12", stock_code="000660", stock_name="SK하이닉스")
    _add_snapshot(db, collected_date="2026-05-09", stock_code="035420", stock_name="NAVER")
    _add_snapshot(
        db,
        collected_date="2026-05-10",
        stock_code="051910",
        stock_name="LG화학",
        price_class_code="1",
    )
    db.commit()

    response = get_weekly_new_high_intersection(db, base_date=date(2026, 5, 17))

    assert response.base_date == date(2026, 5, 17)
    assert response.current_week_start == date(2026, 5, 11)
    assert response.current_week_end == date(2026, 5, 17)
    assert response.previous_week_start == date(2026, 5, 4)
    assert response.previous_week_end == date(2026, 5, 10)
    assert [result.model_dump() for result in response.results] == [
        {"stock_code": "005930", "stock_name": "삼성전자"},
    ]


def test_get_thirty_day_new_high_repeats_returns_prices_for_stocks_seen_at_least_twice(db):
    _add_snapshot(
        db,
        collected_date="2026-04-18",
        stock_code="005930",
        stock_name="삼성전자",
        new_high_price=80000,
    )
    _add_snapshot(
        db,
        collected_date="2026-05-17",
        stock_code="005930",
        stock_name="삼성전자",
        new_high_price=82000,
    )
    _add_snapshot(
        db,
        collected_date="2026-04-17",
        stock_code="005930",
        stock_name="삼성전자",
        new_high_price=79000,
    )
    _add_snapshot(db, collected_date="2026-05-01", stock_code="000660", stock_name="SK하이닉스")
    _add_snapshot(
        db,
        collected_date="2026-05-02",
        stock_code="035420",
        stock_name="NAVER",
        price_class_code="1",
    )
    db.commit()

    response = get_thirty_day_new_high_repeats(db, end_date=date(2026, 5, 17))

    assert response.start_date == date(2026, 4, 18)
    assert response.end_date == date(2026, 5, 17)
    assert [result.model_dump() for result in response.results] == [
        {
            "stock_code": "005930",
            "stock_name": "삼성전자",
            "appearance_count": 2,
            "prices": [
                {"collected_date": date(2026, 4, 18), "new_high_price": 80000},
                {"collected_date": date(2026, 5, 17), "new_high_price": 82000},
            ],
        }
    ]
