import { useAppSelector } from '@/store/hooks';
import { useMemo } from 'react';
import { differenceInDays, parseISO } from 'date-fns';

export const useTransactions = () => {
  const { transactions } = useAppSelector((state) => state.portfolio);

  const stats = useMemo(() => {
    let totalQuantity = 0;
    let totalWeightedDays = 0;
    const now = new Date();

    transactions.forEach((transaction) => {
      const quantity = transaction.type === 'buy' ? transaction.quantity : -transaction.quantity;
      totalQuantity += quantity;
      
      const holdingDays = differenceInDays(now, parseISO(transaction.date));
      totalWeightedDays += quantity * holdingDays;
    });

    const averageHoldingDays = totalQuantity > 0 ? totalWeightedDays / totalQuantity : 0;

    return {
      totalQuantity,
      averageHoldingDays,
    };
  }, [transactions]);

  return stats;
}; 