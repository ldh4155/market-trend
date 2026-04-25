import type { TimeUnit } from '../types'

interface Props {
  startDate: string
  endDate: string
  timeUnit: TimeUnit
  onStartDate: (v: string) => void
  onEndDate: (v: string) => void
  onTimeUnit: (v: TimeUnit) => void
}

export default function DateRangeForm({
  startDate, endDate, timeUnit, onStartDate, onEndDate, onTimeUnit,
}: Props) {
  return (
    <div className="date-form">
      <label>
        시작일
        <input type="date" value={startDate} onChange={(e) => onStartDate(e.target.value)} />
      </label>
      <label>
        종료일
        <input type="date" value={endDate} onChange={(e) => onEndDate(e.target.value)} />
      </label>
      <label>
        단위
        <select value={timeUnit} onChange={(e) => onTimeUnit(e.target.value as TimeUnit)}>
          <option value="date">일별</option>
          <option value="week">주별</option>
          <option value="month">월별</option>
        </select>
      </label>
    </div>
  )
}
