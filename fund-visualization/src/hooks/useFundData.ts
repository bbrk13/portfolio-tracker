import { useAppSelector } from '@/store/hooks';
import { useMemo } from 'react';
import { HistoricalData } from '@/types';
import { subDays, subMonths, subYears, parseISO } from 'date-fns';

export const useFundData = () => {
  const { selectedFund, historicalData, timeFilter } = useAppSelector((state) => state.funds);

  const filteredData = useMemo(() => {
    if (!historicalData) return null;

    const now = new Date();
    let filterDate = now;

    switch (timeFilter) {
      case 'week':
        filterDate = subDays(now, 7);
        break;
      case 'month':
        filterDate = subMonths(now, 1);
        break;
      case '3_months':
        filterDate = subMonths(now, 3);
        break;
      case '6_months':
        filterDate = subMonths(now, 6);
        break;
      case 'year':
        filterDate = subYears(now, 1);
        break;
      case '3_years':
        filterDate = subYears(now, 3);
        break;
      case 'since_new_year':
        filterDate = new Date(now.getFullYear(), 0, 1);
        break;
      default:
        return historicalData;
    }

    return historicalData.filter(data => 
      parseISO(data.Date) >= filterDate
    );
  }, [historicalData, timeFilter]);

  return { filteredData };
}; 