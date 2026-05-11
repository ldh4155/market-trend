import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fetchCompanyTrends, fetchSectorList, fetchSectorTrends } from './api'

const { get, post } = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({ get, post })),
  },
}))

describe('API 클라이언트', () => {
  beforeEach(() => {
    get.mockReset()
    post.mockReset()
  })

  it('섹터 목록 조회 API를 호출하고 섹터 배열을 반환한다', async () => {
    get.mockResolvedValueOnce({ data: { sectors: ['Tech', 'Finance'] } })

    await expect(fetchSectorList()).resolves.toEqual(['Tech', 'Finance'])
    expect(get).toHaveBeenCalledWith('/trends/sectors/list')
  })

  it('섹터 트렌드 검색 조건을 백엔드 필드명으로 전송한다', async () => {
    const response = { results: [] }
    post.mockResolvedValueOnce({ data: response })

    await expect(fetchSectorTrends('2026-01-01', '2026-01-31', 'week', ['Tech'])).resolves.toBe(response)
    expect(post).toHaveBeenCalledWith('/trends/sectors', {
      start_date: '2026-01-01',
      end_date: '2026-01-31',
      time_unit: 'week',
      sectors: ['Tech'],
    })
  })

  it('기업 트렌드 검색 조건을 백엔드 필드명으로 전송한다', async () => {
    const response = { results: [] }
    post.mockResolvedValueOnce({ data: response })

    await expect(fetchCompanyTrends('2026-02-01', '2026-02-28', 'month', 'Tech')).resolves.toBe(response)
    expect(post).toHaveBeenCalledWith('/trends/companies', {
      start_date: '2026-02-01',
      end_date: '2026-02-28',
      time_unit: 'month',
      sector: 'Tech',
    })
  })
})
