'use client';

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useAppSelector } from '@/store/hooks';

export const FundChart = () => {
  const { selectedFund, historicalData } = useAppSelector((state) => state.funds);

  if (!selectedFund || !historicalData) {
    return (
      <div className="h-[400px] flex items-center justify-center bg-gray-50 rounded-lg">
        <p className="text-gray-500">Select a fund to view its chart</p>
      </div>
    );
  }

  return (
    <div className="h-[400px] bg-white rounded-lg p-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={historicalData}>
          <XAxis dataKey="Date" />
          <YAxis />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="Price" 
            stroke="#4f46e5" 
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}; 