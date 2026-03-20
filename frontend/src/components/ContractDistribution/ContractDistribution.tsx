/**
 * 8.2. ContractDistribution — форма привязки ЛС к договорам.
 *
 * - Прогресс-бар (0–100%)
 * - Кнопка «Сохранить» заблокирована при SUM > 100%
 * - Отображение незакрытого остатка в рублях
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Button, Card, InputNumber, message, Progress, Space, Table, Typography,
} from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { contractsApi, estimatesApi } from 'api/client';
import type { IncomeContract, LsIncomeContractLink, LocalEstimate, UUID } from 'types';

const { Text } = Typography;

interface ContractDistributionProps {
  projectId: UUID;
  incomeContractId: UUID;
  contractAmount: number;
}

interface LinkRow {
  lsId: UUID;
  lsCode: string;
  percentage: number;
  isNew?: boolean;
}

const ContractDistribution: React.FC<ContractDistributionProps> = ({
  projectId, incomeContractId, contractAmount,
}) => {
  const [links, setLinks] = useState<LinkRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const totalPct = links.reduce((sum, l) => sum + l.percentage, 0);
  const isOverLimit = totalPct > 100;
  const uncoveredAmount = contractAmount * (100 - totalPct) / 100;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const existing = await contractsApi.getLsIncomeLinks(incomeContractId);
      setLinks(existing.map((l) => ({
        lsId: l.lsId,
        lsCode: l.lsId.slice(0, 8),
        percentage: l.percentage,
      })));
    } finally {
      setLoading(false);
    }
  }, [incomeContractId]);

  useEffect(() => { load(); }, [load]);

  const handlePctChange = (idx: number, value: number | null) => {
    setLinks((prev) => prev.map((l, i) => i === idx ? { ...l, percentage: value ?? 0 } : l));
  };

  const handleRemove = (idx: number) => {
    setLinks((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleSave = async () => {
    if (isOverLimit) return;
    setSaving(true);
    try {
      for (const link of links) {
        await contractsApi.addLsIncome({
          lsId: link.lsId,
          incomeContractId,
          percentage: link.percentage,
        });
      }
      message.success('Распределение сохранено');
    } catch {
      message.error('Ошибка сохранения');
    } finally {
      setSaving(false);
    }
  };

  const columns: ColumnsType<LinkRow> = [
    { title: 'ЛС', dataIndex: 'lsCode', key: 'lsCode', width: 200 },
    {
      title: '% распределения', key: 'percentage', width: 180,
      render: (_: unknown, record: LinkRow, idx: number) => (
        <InputNumber
          min={0} max={100} step={0.01}
          value={record.percentage}
          onChange={(v) => handlePctChange(idx, v)}
          addonAfter="%"
          style={{ width: 140 }}
        />
      ),
    },
    {
      title: 'Сумма', key: 'amount', width: 160, align: 'right',
      render: (_: unknown, record: LinkRow) =>
        (contractAmount * record.percentage / 100).toLocaleString('ru-RU', { minimumFractionDigits: 2 }),
    },
    {
      title: '', key: 'actions', width: 60,
      render: (_: unknown, __: LinkRow, idx: number) => (
        <Button type="text" danger icon={<DeleteOutlined />} onClick={() => handleRemove(idx)} />
      ),
    },
  ];

  return (
    <Card title="Распределение ЛС по договору" size="small">
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Progress
          percent={Math.min(totalPct, 100)}
          status={isOverLimit ? 'exception' : totalPct >= 100 ? 'success' : 'active'}
          format={() => `${totalPct.toFixed(2)}%`}
        />

        {isOverLimit && (
          <Text type="danger">Сумма распределения превышает 100%!</Text>
        )}

        <Table<LinkRow>
          columns={columns}
          dataSource={links}
          rowKey="lsId"
          loading={loading}
          pagination={false}
          size="small"
        />

        <Space>
          <Text>Нераспределённый остаток: </Text>
          <Text strong style={{ color: uncoveredAmount < 0 ? '#ff4d4f' : undefined }}>
            {uncoveredAmount.toLocaleString('ru-RU', { minimumFractionDigits: 2 })} руб.
          </Text>
        </Space>

        <Button
          type="primary"
          onClick={handleSave}
          loading={saving}
          disabled={isOverLimit}
        >
          Сохранить
        </Button>
      </Space>
    </Card>
  );
};

export default ContractDistribution;
