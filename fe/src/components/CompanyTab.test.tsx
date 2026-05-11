import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchCompanyTrends } from '../api'
import CompanyTab from './CompanyTab'

vi.mock('../api', () => ({
  fetchCompanyTrends: vi.fn(),
}))

vi.mock('./TrendChart', () => ({
  default: ({ series }: { series: { name: string }[] }) => (
    <div data-testid="trend-chart">{series.map((item) => item.name).join(',')}</div>
  ),
}))

const fetchCompanyTrendsMock = vi.mocked(fetchCompanyTrends)

describe('기업 검색 탭', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('섹터를 선택하지 않고 검색하면 검증 오류를 보여준다', async () => {
    const user = userEvent.setup()
    const { container } = render(<CompanyTab sectors={['Tech']} />)

    await user.click(screen.getByRole('button'))

    expect(fetchCompanyTrendsMock).not.toHaveBeenCalled()
    expect(container.querySelector('.error')).toBeInTheDocument()
  })

  it('선택한 섹터의 기업 트렌드를 조회하고 순위를 렌더링한다', async () => {
    const user = userEvent.setup()
    fetchCompanyTrendsMock.mockResolvedValueOnce({
      start_date: '2026-01-01',
      end_date: '2026-01-31',
      time_unit: 'week',
      sector: 'Tech',
      results: [
        {
          company: 'Acme',
          average_ratio: 55.01,
          data: [{ period: '2026-W01', ratio: 55 }],
        },
      ],
    })

    render(<CompanyTab sectors={['Tech', 'Finance']} />)

    await user.selectOptions(screen.getAllByRole('combobox')[1], 'Tech')
    await user.click(screen.getByRole('button'))

    await waitFor(() => expect(fetchCompanyTrendsMock).toHaveBeenCalledTimes(1))
    expect(fetchCompanyTrendsMock.mock.calls[0][2]).toBe('week')
    expect(fetchCompanyTrendsMock.mock.calls[0][3]).toBe('Tech')
    expect(await screen.findByText(/1\. Acme/)).toBeInTheDocument()
    expect(screen.getByText('55.0')).toBeInTheDocument()
    expect(screen.getByTestId('trend-chart')).toHaveTextContent('Acme')
  })
})
