from enum import Enum
from pydantic import BaseModel, field_validator
from app.data.sectors import SECTOR_NAMES


class TimeUnit(str, Enum):
    date = "date"
    week = "week"
    month = "month"


class DataPoint(BaseModel):
    period: str
    ratio: float


class SectorTrendRequest(BaseModel):
    start_date: str
    end_date: str
    time_unit: TimeUnit = TimeUnit.week
    sectors: list[str]

    @field_validator("sectors")
    @classmethod
    def validate_sectors(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("sectors는 최소 1개 이상 입력해야 합니다.")
        invalid = [s for s in v if s not in SECTOR_NAMES]
        if invalid:
            raise ValueError(f"알 수 없는 섹터: {invalid}. 사용 가능: {SECTOR_NAMES}")
        return v


class SectorTrendResult(BaseModel):
    sector: str
    average_ratio: float
    data: list[DataPoint]


class SectorTrendResponse(BaseModel):
    start_date: str
    end_date: str
    time_unit: str
    results: list[SectorTrendResult]


class CompanyTrendRequest(BaseModel):
    start_date: str
    end_date: str
    time_unit: TimeUnit = TimeUnit.week
    sector: str

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v: str) -> str:
        if v not in SECTOR_NAMES:
            raise ValueError(f"알 수 없는 섹터: '{v}'. 사용 가능: {SECTOR_NAMES}")
        return v


class CompanyTrendResult(BaseModel):
    company: str
    average_ratio: float
    data: list[DataPoint]


class CompanyTrendResponse(BaseModel):
    start_date: str
    end_date: str
    time_unit: str
    sector: str
    results: list[CompanyTrendResult]


class SectorListResponse(BaseModel):
    sectors: list[str]
