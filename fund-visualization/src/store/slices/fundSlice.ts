import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { FundState } from '@/types';
import { config } from '@/config';

const initialState: FundState = {
  funds: {},
  selectedFund: null,
  historicalData: null,
  timeFilter: 'month',
  loading: false,
  error: null,
};

export const fetchFunds = createAsyncThunk(
  'funds/fetchFunds',
  async () => {
    if (config.useMockData) {
      const response = await fetch('/funds/funds.json');
      const files = await response.json();
      const funds = files.reduce((acc, file) => {
        const fundName = file.replace('.json', '');
        acc[fundName] = fundName;
        return acc;
      }, {});
      return funds;
    } else {
      const response = await axios.get('/api/funds');
      return response.data;
    }
  }
);

export const fetchHistoricalData = createAsyncThunk(
  'funds/fetchHistoricalData',
  async (symbol: string) => {
    if (config.useMockData) {
      const response = await fetch(`/public/funds/${symbol}.json`);
      return response.json();
    } else {
      const response = await axios.get(`/api/funds/${symbol}/historical`);
      return response.data;
    }
  }
);

const fundSlice = createSlice({
  name: 'funds',
  initialState,
  reducers: {
    setSelectedFund: (state, action) => {
      state.selectedFund = action.payload;
    },
    setTimeFilter: (state, action) => {
      state.timeFilter = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchFunds.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchFunds.fulfilled, (state, action) => {
        state.funds = action.payload;
        state.loading = false;
      })
      .addCase(fetchFunds.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to fetch funds';
        state.loading = false;
      })
      .addCase(fetchHistoricalData.fulfilled, (state, action) => {
        state.historicalData = action.payload;
      });
  },
});

export const { setSelectedFund, setTimeFilter } = fundSlice.actions;
export default fundSlice.reducer; 