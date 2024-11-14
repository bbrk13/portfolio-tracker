'use client';

import { useAppSelector } from '@/store/hooks';
import { formatDate } from '@/lib/utils';

export const TransactionList = () => {
  const { transactions } = useAppSelector((state) => state.portfolio);

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Symbol
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Quantity
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {transactions.map((transaction) => (
            <tr key={transaction.id}>
              <td className="px-6 py-4 whitespace-nowrap">
                {formatDate(transaction.date)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`capitalize ${
                  transaction.type === 'buy' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {transaction.type}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {transaction.symbol}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {transaction.quantity}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}; 