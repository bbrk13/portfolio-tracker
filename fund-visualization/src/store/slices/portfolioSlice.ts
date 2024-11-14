import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { PortfolioState, Transaction, PortfolioItem } from '@/types';
import { differenceInDays } from 'date-fns';
import { config } from '@/config';

interface PortfolioMetrics {
  totalQuantity: number;
  totalCost: number;
  totalValue: number;
  averageHoldingDays: number;
  changeMoney: number;
  changePercent: number;
  changePerAHD: number;
}

const calculateMetrics = (
  transactions: Transaction[],
  currentPrices: Record<string, number>
): { items: PortfolioItem[], metrics: PortfolioMetrics } => {
  const portfolioMap = new Map<string, {
    quantity: number;
    weightedDate: number;
    totalCost: number;
    symbol: string;
  }>();

  // Process all transactions
  transactions.forEach(transaction => {
    const existing = portfolioMap.get(transaction.symbol) || {
      quantity: 0,
      weightedDate: 0,
      totalCost: 0,
      symbol: transaction.symbol
    };

    const transactionDate = new Date(transaction.date).getTime();
    const quantity = transaction.type === 'buy' ? transaction.quantity : -transaction.quantity;
    const price = currentPrices[transaction.symbol] || 0;
    const cost = quantity * price;

    // Update weighted average date
    const newQuantity = existing.quantity + quantity;
    if (newQuantity > 0) {
      const existingWeight = existing.weightedDate * existing.quantity;
      const newWeight = transactionDate * quantity;
      existing.weightedDate = (existingWeight + newWeight) / newQuantity;
    }

    existing.quantity = newQuantity;
    existing.totalCost += cost;

    if (existing.quantity > 0) {
      portfolioMap.set(transaction.symbol, existing);
    } else {
      portfolioMap.delete(transaction.symbol);
    }
  });

  const now = new Date().getTime();
  let totalQuantity = 0;
  let totalCost = 0;
  let totalValue = 0;
  let weightedTotalDays = 0;

  const items = Array.from(portfolioMap.values()).map(item => {
    const currentPrice = currentPrices[item.symbol] || 0;
    const currentValue = item.quantity * currentPrice;
    const holdingDays = (now - item.weightedDate) / (1000 * 60 * 60 * 24);
    const changeMoney = currentValue - item.totalCost;
    const changePercent = (changeMoney / item.totalCost) * 100;
    const changePerAHD = changePercent / holdingDays;

    totalQuantity += item.quantity;
    totalCost += item.totalCost;
    totalValue += currentValue;
    weightedTotalDays += holdingDays * item.quantity;

    return {
      symbol: item.symbol,
      quantity: item.quantity,
      averageHoldingDays: holdingDays,
      totalCost: item.totalCost,
      currentValue: currentValue,
      changeMoney,
      changePercent,
      changePerAHD
    };
  });

  const averageHoldingDays = weightedTotalDays / totalQuantity;
  const changeMoney = totalValue - totalCost;
  const changePercent = (changeMoney / totalCost) * 100;
  const changePerAHD = changePercent / averageHoldingDays;

  return {
    items,
    metrics: {
      totalQuantity,
      totalCost,
      totalValue,
      averageHoldingDays,
      changeMoney,
      changePercent,
      changePerAHD
    }
  };
};

const initialState: PortfolioState = {
  transactions: [],
  items: [],
  currentPrices: {},
  metrics: {
    totalQuantity: 0,
    totalCost: 0,
    totalValue: 0,
    averageHoldingDays: 0,
    changeMoney: 0,
    changePercent: 0,
    changePerAHD: 0
  },
  loading: false,
  error: null,
};

export const fetchPortfolio = createAsyncThunk(
  'portfolio/fetchPortfolio',
  async () => {
    if (config.useMockData) {
      // Fetch transactions using fetch API instead of direct import
      const transactionsResponse = await fetch('/portfolios/my_transactions.json');
      const transactions = await transactionsResponse.json();

      // Get all fund symbols from transactions
      const symbols = [...new Set(transactions.map((t: Transaction) => t.symbol))];

      // Fetch latest prices for each fund
      const currentPrices: Record<string, number> = {};
      await Promise.all(
        symbols.map(async (symbol) => {
          try {
            const response = await fetch(`/funds/${symbol}.json`);
            const historicalData = await response.json();
            
            // Get the most recent price
            if (historicalData && historicalData.length > 0) {
              // Historical data is sorted by date in descending order
              currentPrices[symbol] = parseFloat(historicalData[0].Price);
            }
          } catch (error) {
            console.error(`Error fetching price for ${symbol}:`, error);
            currentPrices[symbol] = 0;
          }
        })
      );

      return {
        transactions,
        currentPrices
      };
    } else {
      // Rest of the code remains the same
      const [transactionsResponse, pricesResponse] = await Promise.all([
        axios.get('/api/portfolio/transactions'),
        axios.get('/api/prices')
      ]);
      return {
        transactions: transactionsResponse.data,
        currentPrices: pricesResponse.data
      };
    }
  }
);

export const fetchCurrentPrice = createAsyncThunk(
  'portfolio/fetchCurrentPrice',
  async (symbol: string) => {
    if (config.useMockData) {
      const response = await fetch(`/public/funds/${symbol}.json`);
      const historicalData = await response.json();
      return {
        symbol,
        price: parseFloat(historicalData[0].Price)
      };
    } else {
      const response = await axios.get(`/api/funds/${symbol}/price`);
      return {
        symbol,
        price: response.data.price
      };
    }
  }
);

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    addTransaction: (state, action: PayloadAction<Omit<Transaction, 'id' | 'portfolio_id'> & { price: number }>) => {
      const { price, ...transactionData } = action.payload;
      const newTransaction: Transaction = {
        ...transactionData,
        id: state.transactions.length + 1,
        portfolio_id: 1
      };
      
      // Update current prices
      state.currentPrices[newTransaction.symbol] = price;
      
      // Add transaction
      state.transactions.push(newTransaction);
      
      // Recalculate metrics
      const { items, metrics } = calculateMetrics(
        state.transactions,
        state.currentPrices
      );
      state.items = items;
      state.metrics = metrics;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPortfolio.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchPortfolio.fulfilled, (state, action) => {
        state.transactions = action.payload.transactions;
        const { items, metrics } = calculateMetrics(
          action.payload.transactions,
          action.payload.currentPrices
        );
        state.items = items;
        state.metrics = metrics;
        state.loading = false;
      })
      .addCase(fetchPortfolio.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to fetch portfolio';
        state.loading = false;
      });
  },
});

export const { addTransaction } = portfolioSlice.actions;
export default portfolioSlice.reducer; 