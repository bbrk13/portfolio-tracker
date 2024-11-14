'use client';

import { useEffect } from 'react';
import { useAppDispatch } from '@/store/hooks';
import { FundChart } from '@/components/fund/FundChart';
import { FundSelector } from '@/components/fund/FundSelector';
import { TimeFilter } from '@/components/fund/TimeFilter';
import { fetchFunds } from '@/store/slices/fundSlice';

export default function VisualizationPage() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(fetchFunds());
  }, [dispatch]);

  return (
    <div className="space-y-8">
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Fund Analysis</h2>
        <div className="space-y-4">
          <FundSelector />
          <TimeFilter />
          <div className="h-[500px]">
            <FundChart />
          </div>
        </div>
      </section>
    </div>
  );
} 