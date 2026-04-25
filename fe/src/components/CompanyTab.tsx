import { useState } from 'react'
import { fetchCompanyTrends } from '../api'
import type { TimeUnit, CompanyTrendResult } from '../types'
import DateRangeForm from './DateRangeForm'
import TrendChart from './TrendChart'

interface Props {
  sectors: string[]
}

export default function CompanyTab({ sectors }: Props) {
  const today = new Date().toISOString().slice(0, 10)
  const threeMonthsAgo = new Date(Date.now() - 90 * 86400000).toISOString().slice(0, 10)

  const [startDate, setStartDate] = useState(threeMonthsAgo)
  const [endDate, setEndDate] = useState(today)
  const [timeUnit, setTimeUnit] = useState<TimeUnit>('week')
  const [sector, setSector] = useState('')
  const [results, setResults] = useState<CompanyTrendResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSearch() {
    if (!sector) {
      setError('섹터를 선택해주세요.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await fetchCompanyTrends(startDate, endDate, timeUnit, sector)
      setResults(res.results)
    } catch {
      setError('검색 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const chartSeries = results.map((r) => ({ name: r.company, data: r.data }))

  return (
    <div className="tab-content">
      <DateRangeForm
        startDate={startDate}
        endDate={endDate}
        timeUnit={timeUnit}
        onStartDate={setStartDate}
        onEndDate={setEndDate}
        onTimeUnit={setTimeUnit}
      />

      <div className="date-form">
        <label>
          섹터
          <select value={sector} onChange={(e) => setSector(e.target.value)}>
            <option value="">-- 선택 --</option>
            {sectors.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      <button className="search-btn" onClick={handleSearch} disabled={loading}>
        {loading ? '검색 중...' : '검색'}
      </button>

      {results.length > 0 && (
        <div className="chart-area">
          <div className="rank-list">
            {results.map((r, i) => (
              <span key={r.company} className="rank-item">
                {i + 1}. {r.company} <em>{r.average_ratio.toFixed(1)}</em>
              </span>
            ))}
          </div>
          <TrendChart series={chartSeries} />
        </div>
      )}
    </div>
  )
}
