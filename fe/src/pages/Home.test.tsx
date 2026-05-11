import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchSectorList } from '../api'
import Home from './Home'

vi.mock('../api', () => ({
  fetchSectorList: vi.fn(),
}))

vi.mock('../components/SectorTab', () => ({
  default: ({ sectors }: { sectors: string[] }) => (
    <div data-testid="sector-tab">{sectors.join(',')}</div>
  ),
}))

vi.mock('../components/CompanyTab', () => ({
  default: ({ sectors }: { sectors: string[] }) => (
    <div data-testid="company-tab">{sectors.join(',')}</div>
  ),
}))

const fetchSectorListMock = vi.mocked(fetchSectorList)

describe('홈 화면', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    fetchSectorListMock.mockResolvedValue(['Tech', 'Finance'])
  })

  it('섹터 목록을 불러오고 기본으로 섹터 검색 탭을 보여준다', async () => {
    render(<Home />)

    expect(screen.getByRole('heading', { name: 'Market Trend' })).toBeInTheDocument()
    await waitFor(() => expect(fetchSectorListMock).toHaveBeenCalledTimes(1))
    expect(screen.getByTestId('sector-tab')).toHaveTextContent('Tech,Finance')
  })

  it('기업 검색 탭으로 전환한다', async () => {
    const user = userEvent.setup()
    render(<Home />)

    await user.click(screen.getAllByRole('button')[1])

    expect(screen.getByTestId('company-tab')).toBeInTheDocument()
    expect(screen.getByTestId('company-tab')).toHaveTextContent('Tech,Finance')
  })
})
