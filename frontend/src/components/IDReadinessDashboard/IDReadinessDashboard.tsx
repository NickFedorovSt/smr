/**
 * 8.4. IDReadinessDashboard — дашборд готовности пакета ИД.
 *
 * - Progress Bar по каждому разделу (КЖ, АР, ЭОМ и т.д.)
 * - Сводный % готовности проекта к сдаче
 */

import React, { useCallback, useEffect, useState } from 'react';
import { Card, Col, Progress, Row, Statistic, Typography } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';
import { projectsApi } from 'api/client';
import type { IDReadinessItem, UUID } from 'types';

const { Title } = Typography;

interface IDReadinessDashboardProps {
  projectId: UUID;
}

const IDReadinessDashboard: React.FC<IDReadinessDashboardProps> = ({ projectId }) => {
  const [items, setItems] = useState<IDReadinessItem[]>([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await projectsApi.getIdReadiness(projectId);
      setItems(data);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => { load(); }, [load]);

  const totalDrawings = items.reduce((s, i) => s + i.drawingsCount, 0);
  const totalDone = items.reduce((s, i) => s + i.aosrDone, 0);
  const totalRequired = items.reduce((s, i) => s + i.aosrRequired, 0);
  const overallPct = totalRequired > 0 ? Math.round(totalDone / totalRequired * 100) : 0;

  return (
    <Card loading={loading}>
      <Title level={4}>Готовность пакета ИД к сдаче</Title>

      <Row gutter={[24, 16]} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Statistic title="Общая готовность" value={overallPct} suffix="%" prefix={<CheckCircleOutlined />} />
        </Col>
        <Col span={8}>
          <Statistic title="Чертежей" value={totalDrawings} />
        </Col>
        <Col span={8}>
          <Statistic title="АОСР оформлено / требуется" value={`${totalDone} / ${totalRequired}`} />
        </Col>
      </Row>

      <Row gutter={[16, 12]}>
        {items.map((item) => (
          <Col span={12} key={item.mark}>
            <Card size="small" title={item.mark}>
              <Progress
                percent={item.readinessPercent}
                status={item.readinessPercent >= 100 ? 'success' : 'active'}
                format={(pct) => `${pct?.toFixed(1)}%`}
              />
              <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                Чертежей: {item.drawingsCount} | АОСР: {item.aosrDone}/{item.aosrRequired}
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    </Card>
  );
};

export default IDReadinessDashboard;
