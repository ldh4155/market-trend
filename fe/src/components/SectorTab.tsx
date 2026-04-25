import { useState } from 'react'
import { fetchSectorTrends } from '../api'
import type { TimeUnit, SectorTrendResult } from '../types'
import DateRangeForm from './DateRangeForm'
import TrendChart from './TrendChart'

interface Props {
  sectors: string[]
}

export default function SectorTab({ sectors }: Props) {
  const today = new Date().toISOString().slice(0, 10)
  const threeMonthsAgo = new Date(Date.now() - 90 * 86400000).toISOString().slice(0, 10)

  const [startDate, setStartDate] = useState(threeMonthsAgo)
  const [endDate, setEndDate] = useState(today)
  const [timeUnit, setTimeUnit] = useState<TimeUnit>('week')
  const [selected, setSelected] = useState<string[]>([])
  const [results, setResults] = useState<SectorTrendResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function toggleSector(sector: string) {
    setSelected((prev) =>
      prev.includes(sector) ? prev.filter((s) => s !== sector) : [...prev, sector],
    )
  }

  async function handleSearch() {
    if (selected.length === 0) {
      setError('섹터를 1개 이상 선택해주세요.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await fetchSectorTrends(startDate, endDate, timeUnit, selected)
      setResults(res.results)
    } catch {
      setError('검색 중 오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const chartSeries = results.map((r) => ({ name: r.sector, data: r.data }))

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

      <div className="sector-grid">
        {sectors.map((s) => (
          <label key={s} className={`sector-chip ${selected.includes(s) ? 'selected' : ''}`}>
            <input
              type="checkbox"
              checked={selected.includes(s)}
              onChange={() => toggleSector(s)}
            />
            {s}
          </label>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      <button className="search-btn" onClick={handleSearch} disabled={loading}>
        {loading ? '검색 중...' : '검색'}
      </button>

      {results.length > 0 && (
        <div className="chart-area">
          <div className="rank-list">
            {results.map((r, i) => (
              <span key={r.sector} className="rank-item">
                {i + 1}. {r.sector} <em>{r.average_ratio.toFixed(1)}</em>
              </span>
            ))}
          </div>
          <TrendChart series={chartSeries} />
        </div>
      )}
    </div>
  )
}
