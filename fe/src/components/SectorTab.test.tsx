import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchSectorTrends } from '../api'
import SectorTab from './SectorTab'

vi.mock('../api', () => ({
  fetchSectorTrends: vi.fn(),
}))

vi.mock('./TrendChart', () => ({
  default: ({ series }: { series: { name: string }[] }) => (
    <div data-testid="trend-chart">{series.map((item) => item.name).join(',')}</div>
  ),
}))

const fetchSectorTrendsMock = vi.mocked(fetchSectorTrends)

describe('섹터 검색 탭', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('섹터를 하나도 선택하지 않고 검색하면 검증 오류를 보여준다', async () => {
    const user = userEvent.setup()
    const { container } = render(<SectorTab sectors={['Tech']} />)

    await user.click(screen.getByRole('button'))

    expect(fetchSectorTrendsMock).not.toHaveBeenCalled()
    expect(container.querySelector('.error')).toBeInTheDocument()
  })

  it('선택한 섹터 트렌드를 조회하고 순위를 렌더링한다', async () => {
    const user = userEvent.setup()
    fetchSectorTrendsMock.mockResolvedValueOnce({
      start_date: '2026-01-01',
      end_date: '2026-01-31',
      time_unit: 'week',
      results: [
        {
          sector: 'Tech',
          average_ratio: 42.35,
          data: [{ period: '2026-W01', ratio: 42 }],
        },
      ],
    })

    render(<SectorTab sectors={['Tech', 'Finance']} />)

    await user.click(screen.getByText('Tech'))
    await user.click(screen.getByRole('button'))

    await waitFor(() => expect(fetchSectorTrendsMock).toHaveBeenCalledTimes(1))
    expect(fetchSectorTrendsMock.mock.calls[0][2]).toBe('week')
    expect(fetchSectorTrendsMock.mock.calls[0][3]).toEqual(['Tech'])
    expect(await screen.findByText(/1\. Tech/)).toBeInTheDocument()
    expect(screen.getByText('42.4')).toBeInTheDocument()
    expect(screen.getByTestId('trend-chart')).toHaveTextContent('Tech')
  })
})
