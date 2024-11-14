'use client';

import { useAppSelector } from '@/store/hooks';
import { formatCurrency, formatPercentage } from '@/lib/utils';

export const PortfolioTable = () => {
  const { transactions } = useAppSelector((state) => state.portfolio);

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Symbol
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Full Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Quantity
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Total Value
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Change (%)
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Change (₺)
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {/* Table rows will be populated from Redux state */}
        </tbody>
      </table>
    </div>
  );
}; 