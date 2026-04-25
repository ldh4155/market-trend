export type TimeUnit = 'date' | 'week' | 'month'

export interface DataPoint {
  period: string
  ratio: number
}

export interface SectorTrendResult {
  sector: string
  average_ratio: number
  data: DataPoint[]
}

export interface SectorTrendResponse {
  start_date: string
  end_date: string
  time_unit: string
  results: SectorTrendResult[]
}

export interface CompanyTrendResult {
  company: string
  average_ratio: number
  data: DataPoint[]
}

export interface CompanyTrendResponse {
  start_date: string
  end_date: string
  time_unit: string
  sector: string
  results: CompanyTrendResult[]
}
