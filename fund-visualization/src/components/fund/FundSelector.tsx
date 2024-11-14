'use client';

import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { setSelectedFund } from '@/store/slices/fundSlice';
import { Select } from '../common/Select';

export const FundSelector = () => {
  const dispatch = useAppDispatch();
  const { funds } = useAppSelector((state) => state.funds);

  const options = Object.entries(funds).map(([symbol, name]) => ({
    value: symbol,
    label: `${symbol} - ${name}`
  }));

  return (
    <div className="w-full max-w-md">
      <Select
        label="Search Fund:"
        options={options}
        onChange={(e) => dispatch(setSelectedFund(e.target.value))}
        className="w-full"
        placeholder="Select a fund..."
      />
    </div>
  );
}; 