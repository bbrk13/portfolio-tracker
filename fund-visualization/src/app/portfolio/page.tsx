'use client';

import { useEffect } from 'react';
import { useAppDispatch } from '@/store/hooks';
import { PortfolioTable } from '@/components/portfolio/PortfolioTable';
import { TransactionDialog } from '@/components/portfolio/TransactionDialog';
import { TransactionList } from '@/components/portfolio/TransactionList';
import { fetchPortfolio } from '@/store/slices/portfolioSlice';

export default function PortfolioPage() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(fetchPortfolio());
  }, [dispatch]);

  return (
    <div className="space-y-8">
      <section className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Portfolio Management</h2>
          <TransactionDialog />
        </div>
        <PortfolioTable />
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Transaction History</h2>
        <TransactionList />
      </section>
    </div>
  );
} 