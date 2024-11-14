import { useAppSelector } from '@/store/hooks';
import { useMemo } from 'react';
import { Transaction } from '@/types';

export const usePortfolio = () => {
  const { transactions } = useAppSelector((state) => state.portfolio);
  const { funds } = useAppSelector((state) => state.funds);

  const portfolioSummary = useMemo(() => {
    const summary = new Map<string, {
      symbol: string;
      fullName: string;
      quantity: number;
      totalValue: number;
      totalCost: number;
      changePercent: number;
      changeMoney: number;
    }>();

    transactions.forEach((transaction) => {
      const currentSummary = summary.get(transaction.symbol) || {
        symbol: transaction.symbol,
        fullName: funds[transaction.symbol] || transaction.symbol,
        quantity: 0,
        totalValue: 0,
        totalCost: 0,
        changePercent: 0,
        changeMoney: 0,
      };

      if (transaction.type === 'buy') {
        currentSummary.quantity += transaction.quantity;
      } else {
        currentSummary.quantity -= transaction.quantity;
      }

      summary.set(transaction.symbol, currentSummary);
    });

    return Array.from(summary.values());
  }, [transactions, funds]);

  return { portfolioSummary };
}; 