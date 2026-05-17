import sys
from pathlib import Path

from sqlalchemy import func, select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.models import KisNearHighLowSnapshot
from app.services.kis_snapshot_service import collect_near_highlow_snapshots


def main() -> None:
    with SessionLocal() as db:
        saved_count = collect_near_highlow_snapshots(db, price_class_code="0")
        total_count = db.scalar(select(func.count()).select_from(KisNearHighLowSnapshot))
        latest_rows = db.scalars(
            select(KisNearHighLowSnapshot)
            .order_by(KisNearHighLowSnapshot.collected_at.desc())
            .limit(5)
        ).all()

    print(f"saved_count={saved_count}")
    print(f"total_count={total_count}")
    for row in latest_rows:
        print(
            f"{row.collected_date} {row.stock_code} {row.stock_name} "
            f"current={row.current_price} new_high={row.new_high_price}"
        )


if __name__ == "__main__":
    main()
