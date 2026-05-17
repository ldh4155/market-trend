from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KisNearHighLowSnapshot(Base):
    # 한국투자증권 신고/신저근접종목 상위 API 응답을 일자별로 저장하는 스냅샷 테이블.
    __tablename__ = "kis_near_highlow_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "collected_date",
            "market_code",
            "price_class_code",
            "stock_code",
            name="uq_kis_near_highlow_snapshot_daily_stock",
        ),
        Index("ix_kis_near_highlow_snapshots_lookup", "collected_date", "price_class_code"),
    )

    # 내부 식별자.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # API를 호출해 데이터를 수집한 기준일. 같은 날짜의 중복 저장 방지에 사용한다.
    collected_date: Mapped[str] = mapped_column(String(10), nullable=False)

    # 실제 DB에 row가 저장된 시각.
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # KIS 조건 시장 분류 코드. 국내 주식은 J를 사용한다.
    market_code: Mapped[str] = mapped_column(String(4), nullable=False, default="J")

    # 조회 대상 시장 코드. 0000 전체, 0001 거래소, 1001 코스닥 등.
    input_market_code: Mapped[str] = mapped_column(String(4), nullable=False, default="0000")

    # 가격 구분 코드. 0은 신고근접, 1은 신저근접.
    price_class_code: Mapped[str] = mapped_column(String(1), nullable=False, default="0")

    # 유가증권 단축 종목코드.
    stock_code: Mapped[str] = mapped_column(String(12), nullable=False, index=True)

    # HTS 기준 한글 종목명.
    stock_name: Mapped[str] = mapped_column(String(120), nullable=False)

    # API 호출 시점의 주식 현재가.
    current_price: Mapped[int] = mapped_column(Integer, nullable=False)

    # API 호출 시점의 누적 거래량.
    accumulated_volume: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # 신고근접 조회에서 제공되는 신 최고가.
    new_high_price: Mapped[int | None] = mapped_column(Integer)

    # 현재가가 신 최고가에 얼마나 근접했는지 나타내는 비율.
    high_near_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))

    # 신저근접 조회에서 제공되는 신 최저가.
    new_low_price: Mapped[int | None] = mapped_column(Integer)

    # 현재가가 신 최저가에 얼마나 근접했는지 나타내는 비율.
    low_near_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))

    # 당일 기준가.
    base_price: Mapped[int | None] = mapped_column(Integer)
