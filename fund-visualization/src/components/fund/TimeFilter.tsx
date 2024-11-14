'use client';

import { useAppDispatch } from '@/store/hooks';
import { setTimeFilter } from '@/store/slices/fundSlice';
import { Button } from '../common/Button';

const timeFilters = [
  { label: 'Last Week', value: 'week' },
  { label: 'Last Month', value: 'month' },
  { label: 'Last 3 Months', value: '3_months' },
  { label: 'Last 6 Months', value: '6_months' },
  { label: 'Last Year', value: 'year' },
  { label: 'Last 3 Years', value: '3_years' },
  { label: 'Since New Year', value: 'since_new_year' },
  { label: 'All Data', value: 'all' },
];

export const TimeFilter = () => {
  const dispatch = useAppDispatch();

  return (
    <div className="flex gap-2 overflow-x-auto p-4">
      {timeFilters.map(({ label, value }) => (
        <Button
          key={value}
          variant="secondary"
          onClick={() => dispatch(setTimeFilter(value))}
        >
          {label}
        </Button>
      ))}
    </div>
  );
}; 