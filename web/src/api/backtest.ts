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

export interface TradeMarker {
    date: string;
    type: 'buy' | 'sell';
    price: number;
    amount: number;
}

export interface BacktestResult {
  final_value: number;
  pnl: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_trades: number;
  win_rate: number;
  chart_data: Array<[string, number, number, number, number]>; // Date, Open, Close, Low, High
  trade_markers: TradeMarker[];
}

export interface TaskResponse {
    task_id: string;
    status: string;
}

export interface TaskStatusResponse {
    state: string;
    status?: string;
    result?: BacktestResult; // Only present if state is SUCCESS
    error?: string;
}

export const runBacktest = async (data: BacktestRequest) => {
  // Updated to return task_id
  const response = await api.post<TaskResponse>('/backtest/run', data);
  return response.data;
};

export const getBacktestStatus = async (taskId: string) => {
    const response = await api.get<TaskStatusResponse>(`/backtest/status/${taskId}`);
    return response.data;
}

export const getStrategies = async () => {
  const response = await api.get<string[]>('/backtest/strategies');
  return response.data;
};
