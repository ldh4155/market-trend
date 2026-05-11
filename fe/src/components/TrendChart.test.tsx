import { render, screen } from '@testing-library/react'
import type React from 'react'
import { describe, expect, it, vi } from 'vitest'
import TrendChart from './TrendChart'

vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  LineChart: ({ children, data }: { children: React.ReactNode; data: unknown[] }) => (
    <div data-testid="line-chart" data-points={data.length}>{children}</div>
  ),
  Line: ({ dataKey, stroke }: { dataKey: string; stroke: string }) => (
    <div data-testid="line" data-key={dataKey} data-stroke={stroke} />
  ),
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
}))

describe('트렌드 차트', () => {
  it('시리즈가 없으면 아무것도 렌더링하지 않는다', () => {
    const { container } = render(<TrendChart series={[]} />)

    expect(container).toBeEmptyDOMElement()
  })

  it('시리즈마다 하나의 라인을 렌더링한다', () => {
    render(
      <TrendChart
        series={[
          { name: 'Tech', data: [{ period: '2026-W01', ratio: 45 }] },
          { name: 'Finance', data: [{ period: '2026-W01', ratio: 31 }] },
        ]}
      />,
    )

    expect(screen.getByTestId('line-chart')).toHaveAttribute('data-points', '1')
    expect(screen.getAllByTestId('line')).toHaveLength(2)
    expect(screen.getAllByTestId('line').map((line) => line.dataset.key)).toEqual(['Tech', 'Finance'])
  })
})
