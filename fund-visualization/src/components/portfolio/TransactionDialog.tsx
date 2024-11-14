'use client';

import { useState, useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { addTransaction, fetchCurrentPrice } from '@/store/slices/portfolioSlice';
import { Button } from '../common/Button';
import { Select } from '../common/Select';

export const TransactionDialog = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    type: 'buy' as 'buy' | 'sell',
    symbol: '',
    quantity: '',
    date: ''
  });

  const dispatch = useAppDispatch();
  const { funds } = useAppSelector((state) => state.funds);

  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      date: new Date().toISOString().slice(0, 10)
    }));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // First fetch the current price
    const priceResult = await dispatch(fetchCurrentPrice(formData.symbol)).unwrap();
    
    // Then add the transaction
    dispatch(addTransaction({
      ...formData,
      quantity: Number(formData.quantity),
      price: priceResult.price
    }));
    
    setIsOpen(false);
  };

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>
        Add Transaction
      </Button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">Add Transaction</h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <Select
                label="Type"
                options={[
                  { value: 'buy', label: 'Buy' },
                  { value: 'sell', label: 'Sell' }
                ]}
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              />

              <Select
                label="Fund"
                options={Object.entries(funds).map(([symbol, name]) => ({
                  value: symbol,
                  label: `${symbol} - ${name}`
                }))}
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
              />

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Quantity
                </label>
                <input
                  type="number"
                  className="input mt-1"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Date
                </label>
                <input
                  type="date"
                  className="input mt-1"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                />
              </div>

              <div className="flex justify-end gap-2 mt-4">
                <Button variant="secondary" onClick={() => setIsOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit">
                  Add Transaction
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}; 