import { describe, expect, it } from 'vitest'

import {
  evenAllocation,
  formatDisciplineOutcome,
  formatResultValue,
  isPlaceOnlyResult,
  TOTAL_CONFIDENCE_POINTS,
} from './display'

describe('display utils', () => {
  it('allocates exactly 100 points for one or two picks', () => {
    expect(evenAllocation([10])).toEqual({ 10: TOTAL_CONFIDENCE_POINTS })
    expect(evenAllocation([10, 20])).toEqual({ 10: 50, 20: 50 })
  })

  it('hides place-only result text when formatting discipline values', () => {
    expect(isPlaceOnlyResult('2 место')).toBe(true)
    expect(
      formatResultValue({
        year: 2026,
        event_title: 'Игры',
        discipline_id: 'run',
        result_text: '2 место',
        result_value: null,
        result_unit: null,
      }),
    ).toBe('не опубликован')
  })

  it('deduplicates equal place and points in discipline outcome', () => {
    expect(
      formatDisciplineOutcome({
        year: 2026,
        event_title: 'Игры',
        discipline_id: 'run',
        place: 2,
        points: 2,
      }),
    ).toBe('2 место')
    expect(
      formatDisciplineOutcome({
        year: 2026,
        event_title: 'Игры',
        discipline_id: 'run',
        place: 2,
        points: 12,
      }),
    ).toBe('2 место · 12 очков')
  })
})
