import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
});

export interface BacktestRequest {
  strategy: string;
  symbol: string;
  start_date: string;
  end_date: string;
  initial_cash: number;
  params: Record<string, any>;
}

export interface BacktestResult {
  final_value: number;
  pnl: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_trades: number;
  win_rate: number;
}

export const runBacktest = async (data: BacktestRequest) => {
  const response = await api.post<{ status: string; result: BacktestResult }>('/backtest/run', data);
  return response.data;
};

export const getStrategies = async () => {
  const response = await api.get<string[]>('/backtest/strategies');
  return response.data;
};

