import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { DataPoint } from '../types'

const COLORS = [
  '#4f86f7', '#f76f4f', '#4fc66a', '#f7c44f',
  '#a04ff7', '#4ff7e8', '#f74fa0', '#8fa04f',
]

interface Series {
  name: string
  data: DataPoint[]
}

interface Props {
  series: Series[]
}

export default function TrendChart({ series }: Props) {
  if (series.length === 0) return null

  const periods = series[0].data.map((d) => d.period)
  const chartData = periods.map((period) => {
    const row: Record<string, string | number> = { period }
    series.forEach((s) => {
      const point = s.data.find((d) => d.period === period)
      row[s.name] = point?.ratio ?? 0
    })
    return row
  })

  return (
    <ResponsiveContainer width="100%" height={360}>
      <LineChart data={chartData} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
        <XAxis dataKey="period" tick={{ fontSize: 11, fill: '#aaa' }} />
        <YAxis tick={{ fontSize: 11, fill: '#aaa' }} domain={[0, 100]} />
        <Tooltip
          contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 6 }}
          labelStyle={{ color: '#eee' }}
        />
        <Legend wrapperStyle={{ fontSize: 13 }} />
        {series.map((s, i) => (
          <Line
            key={s.name}
            type="monotone"
            dataKey={s.name}
            stroke={COLORS[i % COLORS.length]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
