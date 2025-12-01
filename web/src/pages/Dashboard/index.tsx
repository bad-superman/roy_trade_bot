import React from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

const Dashboard: React.FC = () => (
  <div>
    <h2>仪表盘</h2>
    <Row gutter={16}>
      <Col span={8}>
        <Card>
          <Statistic
            title="总资产"
            value={112893.00}
            precision={2}
            valueStyle={{ color: '#3f8600' }}
            prefix={<ArrowUpOutlined />}
            suffix="$"
          />
        </Card>
      </Col>
      <Col span={8}>
        <Card>
          <Statistic
            title="今日盈亏"
            value={9.3}
            precision={2}
            valueStyle={{ color: '#cf1322' }}
            prefix={<ArrowDownOutlined />}
            suffix="%"
          />
        </Card>
      </Col>
      <Col span={8}>
        <Card>
          <Statistic
            title="运行策略数"
            value={3}
            prefix={<ArrowUpOutlined />}
          />
        </Card>
      </Col>
    </Row>
    <div style={{ marginTop: 24 }}>
        <Card title="系统状态">
            <p>API 服务: <span style={{ color: 'green' }}>运行中</span></p>
            <p>行情数据: <span style={{ color: 'green' }}>连接正常 (Redis)</span></p>
            <p>交易网关: <span style={{ color: 'orange' }}>Oanda (模拟)</span></p>
        </Card>
    </div>
  </div>
);

export default Dashboard;

