'use client';

import { useAppSelector } from '@/store/hooks';
import { formatCurrency, formatPercentage } from '@/lib/utils';

export const PortfolioSummary = () => {
  const { transactions } = useAppSelector((state) => state.portfolio);
  const { funds } = useAppSelector((state) => state.funds);

  // Calculate total values and changes
  const totalValue = 0; // Implement calculation
  const totalChange = 0; // Implement calculation
  const totalChangePercentage = 0; // Implement calculation
  const averageHoldingDays = 0; // Implement calculation

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Total Value</h3>
        <p className="text-2xl font-bold">{formatCurrency(totalValue)}</p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Total Change</h3>
        <p className={`text-2xl font-bold ${totalChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {formatCurrency(totalChange)}
        </p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Total Change (%)</h3>
        <p className={`text-2xl font-bold ${totalChangePercentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {formatPercentage(totalChangePercentage)}
        </p>
      </div>

      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-sm font-medium text-gray-500">Average Holding Days</h3>
        <p className="text-2xl font-bold">{averageHoldingDays.toFixed(1)}</p>
      </div>
    </div>
  );
}; 