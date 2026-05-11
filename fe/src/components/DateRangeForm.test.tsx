import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import DateRangeForm from './DateRangeForm'

describe('날짜 범위 폼', () => {
  it('현재 날짜와 집계 단위를 표시하고 변경 값을 콜백으로 전달한다', async () => {
    const user = userEvent.setup()
    const onStartDate = vi.fn()
    const onEndDate = vi.fn()
    const onTimeUnit = vi.fn()

    render(
      <DateRangeForm
        startDate="2026-01-01"
        endDate="2026-01-31"
        timeUnit="week"
        onStartDate={onStartDate}
        onEndDate={onEndDate}
        onTimeUnit={onTimeUnit}
      />,
    )

    const [start, end] = screen.getAllByDisplayValue(/\d{4}-\d{2}-\d{2}/)
    fireEvent.change(start, { target: { value: '2026-02-01' } })
    fireEvent.change(end, { target: { value: '2026-02-28' } })
    await user.selectOptions(screen.getByRole('combobox'), 'month')

    expect(onStartDate).toHaveBeenLastCalledWith('2026-02-01')
    expect(onEndDate).toHaveBeenLastCalledWith('2026-02-28')
    expect(onTimeUnit).toHaveBeenCalledWith('month')
  })
})
