export interface Fund {
  symbol: string;
  name: string;
}

export interface HistoricalData {
  Date: string;
  Price: number;
  NumberOfShares: number;
  NumberOfInvestors: number;
  PortfolioSize: number;
}

export interface Transaction {
  id: number;
  portfolio_id: number;
  symbol: string;
  date: string;
  type: 'buy' | 'sell';
  quantity: number;
}

export interface FundState {
  funds: Record<string, string>;
  selectedFund: string | null;
  historicalData: HistoricalData[] | null;
  timeFilter: string;
  loading: boolean;
  error: string | null;
}

export interface PortfolioState {
  transactions: Transaction[];
  items: PortfolioItem[];
  currentPrices: Record<string, number>;
  metrics: PortfolioMetrics;
  loading: boolean;
  error: string | null;
}

export interface PortfolioItem {
  symbol: string;
  quantity: number;
  averageHoldingDays: number;
  totalCost: number;
  currentValue: number;
  changeMoney: number;
  changePercent: number;
  changePerAHD: number;
}

export interface PortfolioMetrics {
  totalQuantity: number;
  totalCost: number;
  totalValue: number;
  averageHoldingDays: number;
  changeMoney: number;
  changePercent: number;
  changePerAHD: number;
} 