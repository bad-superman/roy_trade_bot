import React, { useState, useEffect, useRef } from 'react';
import { ProForm, ProFormSelect, ProFormDateRangePicker, ProFormMoney, ProFormDigit } from '@ant-design/pro-components';
import { Card, Row, Col, Statistic, message, Spin, Alert } from 'antd';
import ReactECharts from 'echarts-for-react';
import { runBacktest, getStrategies, getBacktestStatus, BacktestRequest, BacktestResult, TaskStatusResponse } from '../../api/backtest';
import dayjs from 'dayjs';

const BacktestPage: React.FC = () => {
  const [strategies, setStrategies] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const pollingTimer = useRef<any>(null);

  useEffect(() => {
    getStrategies().then(setStrategies).catch(console.error);
    return () => {
        if (pollingTimer.current) clearInterval(pollingTimer.current);
    }
  }, []);

  useEffect(() => {
      if (taskId) {
          setLoading(true);
          // Start polling
          pollingTimer.current = setInterval(async () => {
              try {
                  const statusRes = await getBacktestStatus(taskId);
                  console.log("Polling status:", statusRes);
                  
                  if (statusRes.state === 'SUCCESS' && statusRes.result) {
                      // Note: Celery result might be wrapped in {status: success, result: ...} from our worker
                      // Our worker returns {status: "success", result: {...actual data...}}
                      // Let's check the structure.
                      // The API returns result: result directly from AsyncResult.
                      // So we need to unwrap the inner result
                      const innerResult = statusRes.result as any;
                      if (innerResult.status === 'success') {
                           setResult(innerResult.result);
                           message.success('回测完成');
                      } else {
                          message.error('回测失败: ' + innerResult.error);
                      }
                      
                      setLoading(false);
                      setTaskId(null);
                      clearInterval(pollingTimer.current);
                  } else if (statusRes.state === 'FAILURE') {
                      message.error('回测失败: ' + statusRes.error);
                      setLoading(false);
                      setTaskId(null);
                      clearInterval(pollingTimer.current);
                  }
                  // PENDING or STARTED, continue polling
              } catch (e) {
                  console.error("Polling error", e);
                  // Don't stop polling on transient network error, but maybe count errors
              }
          }, 2000);
      }
      return () => {
          if (pollingTimer.current) clearInterval(pollingTimer.current);
      }
  }, [taskId]);

  const handleFinish = async (values: any) => {
    setResult(null);
    try {
      const request: BacktestRequest = {
        strategy: values.strategy,
        symbol: values.symbol,
        // 兼容处理：ProFormDateRangePicker 在某些情况下返回的是数组，某些版本可能包含 null
        start_date: values.dateRange && values.dateRange[0] ? dayjs(values.dateRange[0]).format('YYYY-MM-DD') : '',
        end_date: values.dateRange && values.dateRange[1] ? dayjs(values.dateRange[1]).format('YYYY-MM-DD') : '',
        initial_cash: values.initial_cash,
        params: {
          pfast: values.pfast,
          pslow: values.pslow
        }
      };

      const res = await runBacktest(request);
      if (res.status === 'submitted') {
        setTaskId(res.task_id);
        message.info('回测任务已提交，正在运行中...');
      }
    } catch (error) {
      console.error(error);
      message.error('提交失败');
    }
  };

  const getKLineOption = () => {
    if (!result || !result.chart_data) return {};

    // Split data for echarts
    const dates = result.chart_data.map(item => item[0]);
    const data = result.chart_data.map(item => [item[1], item[2], item[3], item[4]]); // Open, Close, Low, High

    // MarkPoints for Buy/Sell
    const markPoints = result.trade_markers.map(m => ({
        name: m.type === 'buy' ? 'Buy' : 'Sell',
        coord: [m.date, m.price],
        value: m.type === 'buy' ? 'Buy' : 'Sell',
        itemStyle: {
            color: m.type === 'buy' ? '#ef232a' : '#14b143'
        }
    }));

    return {
        title: { text: '回测K线图' },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        xAxis: {
            data: dates,
            scale: true,
            boundaryGap: false,
        },
        yAxis: {
            scale: true,
            splitArea: {
                show: true
            }
        },
        dataZoom: [
            {
                type: 'inside',
                start: 50,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                y: '90%',
                start: 50,
                end: 100
            }
        ],
        series: [
            {
                name: 'KLine',
                type: 'candlestick',
                data: data,
                itemStyle: {
                    color: '#ef232a', // Bullish (Red in China/some styles)
                    color0: '#14b143', // Bearish (Green)
                    borderColor: '#ef232a',
                    borderColor0: '#14b143'
                },
                markPoint: {
                    data: markPoints
                }
            }
        ]
    };
  };

  return (
    <div>
      <h2>回测系统</h2>
      <Row gutter={16}>
        <Col span={6}>
          <Card title="策略配置" bordered={false}>
            <ProForm
              onFinish={handleFinish}
              submitter={{
                searchConfig: {
                  submitText: loading ? '运行中...' : '开始回测',
                },
                submitButtonProps: {
                    loading: loading,
                    disabled: loading
                },
                resetButtonProps: {
                  style: {
                    display: 'none',
                  },
                },
              }}
            >
              <ProFormSelect
                name="strategy"
                label="选择策略"
                options={strategies.map(s => ({ label: s, value: s }))}
                rules={[{ required: true, message: '请选择策略' }]}
              />
              <ProFormSelect
                name="symbol"
                label="交易品种"
                options={[
                  { label: 'XAUUSD (黄金)', value: 'XAUUSD' },
                  { label: 'EURUSD (欧元)', value: 'EURUSD' },
                ]}
                initialValue="EURUSD"
                rules={[{ required: true, message: '请选择品种' }]}
              />
              <ProFormDateRangePicker
                name="dateRange"
                label="回测区间"
                initialValue={[dayjs().subtract(1, 'month'), dayjs()]}
                rules={[{ required: true, message: '请选择时间范围' }]}
              />
              <ProFormMoney
                name="initial_cash"
                label="初始资金"
                initialValue={10000}
                rules={[{ required: true }]}
              />
              
              {/* 动态参数 - 暂时硬编码 SmaCross 参数 */}
              <ProFormDigit name="pfast" label="快线周期" initialValue={10} />
              <ProFormDigit name="pslow" label="慢线周期" initialValue={30} />
            </ProForm>
          </Card>
        </Col>
        <Col span={18}>
          {loading && <Alert message="正在运行回测任务，请稍候..." type="info" showIcon style={{ marginBottom: 16 }} />}
          
            {result ? (
              <>
                <Row gutter={16} style={{ marginBottom: 24 }}>
                  <Col span={6}>
                    <Statistic title="最终权益" value={result.final_value} precision={2} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="净利润" value={result.pnl} precision={2} valueStyle={{ color: result.pnl >= 0 ? '#3f8600' : '#cf1322' }} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="夏普比率" value={result.sharpe_ratio} precision={2} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="最大回撤" value={result.max_drawdown} precision={2} suffix="%" />
                  </Col>
                </Row>
                <Card title="策略表现" bordered={false} style={{ minHeight: 500 }}>
                   <ReactECharts option={getKLineOption()} style={{ height: 500 }} />
                </Card>
              </>
            ) : (
              !loading && (
                <div style={{ textAlign: 'center', marginTop: 100, color: '#999' }}>
                  请配置策略并运行回测以查看结果
                </div>
              )
            )}
        </Col>
      </Row>
    </div>
  );
};

export default BacktestPage;
