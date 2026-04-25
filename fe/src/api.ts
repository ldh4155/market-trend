import axios from 'axios'
import type { TimeUnit, SectorTrendResponse, CompanyTrendResponse } from './types'

const client = axios.create({ baseURL: '/api' })

export async function fetchSectorList(): Promise<string[]> {
  const res = await client.get<{ sectors: string[] }>('/trends/sectors/list')
  return res.data.sectors
}

export async function fetchSectorTrends(
  startDate: string,
  endDate: string,
  timeUnit: TimeUnit,
  sectors: string[],
): Promise<SectorTrendResponse> {
  const res = await client.post<SectorTrendResponse>('/trends/sectors', {
    start_date: startDate,
    end_date: endDate,
    time_unit: timeUnit,
    sectors,
  })
  return res.data
}

export async function fetchCompanyTrends(
  startDate: string,
  endDate: string,
  timeUnit: TimeUnit,
  sector: string,
): Promise<CompanyTrendResponse> {
  const res = await client.post<CompanyTrendResponse>('/trends/companies', {
    start_date: startDate,
    end_date: endDate,
    time_unit: timeUnit,
    sector,
  })
  return res.data
}
