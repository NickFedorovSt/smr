/**
 * 8.7. AlertsPanel — панель уведомлений и рисков.
 *
 * Автоматически отображает предупреждения:
 *  - 🔴 Просроченные предписания СДО (planned_fix_date < TODAY)
 *  - 🟡 Сертификаты с истекающим сроком (expiry_date < TODAY+30)
 *  - 🟠 ЛС с нераспределёнными объёмами (SUM percentage < 100%)
 *  - 🔴 Остаток лимита отрицательный (перерасход бюджета)
 *
 * Данные: GET /projects/{id}/alerts
 */

import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Badge, Card, Empty, List, Space, Spin, Tag, Typography } from 'antd';
import {
  AlertOutlined,
  ExclamationCircleOutlined,
  SafetyCertificateOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import { projectsApi } from 'api/client';
import type { AlertItem, AlertSeverity, UUID } from 'types';

const { Text } = Typography;

interface AlertsPanelProps {
  projectId: UUID;
  /** Внешний триггер обновления (инкремент). */
  refreshTrigger?: number;
}

const severityConfig: Record<AlertSeverity, { color: string; icon: React.ReactNode; antType: 'error' | 'warning' | 'info' }> = {
  critical: { color: 'red', icon: <ExclamationCircleOutlined />, antType: 'error' },
  warning: { color: 'orange', icon: <WarningOutlined />, antType: 'warning' },
  info: { color: 'blue', icon: <AlertOutlined />, antType: 'info' },
};

const categoryLabels: Record<string, { label: string; icon: React.ReactNode }> = {
  overdue_inspection: { label: 'Просроченные предписания', icon: <ExclamationCircleOutlined /> },
  expiring_certificate: { label: 'Истекающие сертификаты', icon: <SafetyCertificateOutlined /> },
  uncovered_ls: { label: 'Нераспределённые ЛС', icon: <WarningOutlined /> },
  budget_overrun: { label: 'Перерасход бюджета', icon: <AlertOutlined /> },
};

const AlertsPanel: React.FC<AlertsPanelProps> = ({ projectId, refreshTrigger }) => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setAlerts(await projectsApi.getAlerts(projectId));
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => { load(); }, [load, refreshTrigger]);

  const criticalCount = alerts.filter((a) => a.severity === 'critical').length;
  const warningCount = alerts.filter((a) => a.severity === 'warning').length;

  return (
    <Card
      title={
        <Space>
          <AlertOutlined />
          <Text strong>Уведомления и риски</Text>
          {criticalCount > 0 && <Badge count={criticalCount} style={{ backgroundColor: '#ff4d4f' }} />}
          {warningCount > 0 && <Badge count={warningCount} style={{ backgroundColor: '#faad14' }} />}
        </Space>
      }
      size="small"
    >
      <Spin spinning={loading}>
        {alerts.length === 0 && !loading ? (
          <Empty description="Нет активных предупреждений" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        ) : (
          <List
            dataSource={alerts}
            size="small"
            renderItem={(item) => {
              const cfg = severityConfig[item.severity];
              const cat = categoryLabels[item.category];
              return (
                <List.Item style={{ padding: '8px 0' }}>
                  <Alert
                    type={cfg.antType}
                    showIcon
                    icon={cat?.icon || cfg.icon}
                    style={{ width: '100%' }}
                    message={
                      <Space>
                        <Tag color={cfg.color}>{cat?.label || item.category}</Tag>
                        <Text>{item.message}</Text>
                      </Space>
                    }
                  />
                </List.Item>
              );
            }}
          />
        )}
      </Spin>
    </Card>
  );
};

export default AlertsPanel;
