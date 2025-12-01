import React, { useState, useEffect } from 'react';
import { ProForm, ProFormSelect, ProFormDateRangePicker, ProFormMoney, ProFormDigit } from '@ant-design/pro-components';
import { Card, Row, Col, Statistic, message, Spin } from 'antd';
import ReactECharts from 'echarts-for-react';
import { runBacktest, getStrategies, BacktestRequest, BacktestResult } from '../../api/backtest';
import dayjs from 'dayjs';

const BacktestPage: React.FC = () => {
  const [strategies, setStrategies] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);

  useEffect(() => {
    getStrategies().then(setStrategies).catch(console.error);
  }, []);

  const handleFinish = async (values: any) => {
    setLoading(true);
    try {
      const request: BacktestRequest = {
        strategy: values.strategy,
        symbol: values.symbol,
        start_date: values.dateRange[0].format('YYYY-MM-DD'),
        end_date: values.dateRange[1].format('YYYY-MM-DD'),
        initial_cash: values.initial_cash,
        params: {
          pfast: values.pfast,
          pslow: values.pslow
        }
      };

      const res = await runBacktest(request);
      if (res.status === 'success') {
        setResult(res.result);
        message.success('回测完成');
      }
    } catch (error) {
      console.error(error);
      message.error('回测失败');
    } finally {
      setLoading(false);
    }
  };

  // 简单的图表配置，实际项目中应使用K线图数据
  const getOption = () => {
    if (!result) return {};
    return {
        title: { text: '回测收益概览' },
        tooltip: {},
        xAxis: { data: ['初始资金', '最终权益'] },
        yAxis: {},
        series: [{
            name: '金额',
            type: 'bar',
            data: [10000, result.final_value]
        }]
    };
  };

  return (
    <div>
      <h2>回测系统</h2>
      <Row gutter={16}>
        <Col span={8}>
          <Card title="策略配置" bordered={false}>
            <ProForm
              onFinish={handleFinish}
              submitter={{
                searchConfig: {
                  submitText: '开始回测',
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
        <Col span={16}>
          <Spin spinning={loading}>
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
                <Card title="回测结果可视化" bordered={false}>
                   <ReactECharts option={getOption()} />
                </Card>
              </>
            ) : (
              <div style={{ textAlign: 'center', marginTop: 50, color: '#999' }}>
                请运行回测以查看结果
              </div>
            )}
          </Spin>
        </Col>
      </Row>
    </div>
  );
};

export default BacktestPage;

