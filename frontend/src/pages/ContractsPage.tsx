/**
 * Страница «Договоры» — ContractDistribution + списки доходных/расходных договоров.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Card, Empty, Select, Space, Table, Tabs, Tag, Typography,
} from 'antd';
import { FileProtectOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { contractsApi } from 'api/client';
import { ContractDistribution } from 'components/ContractDistribution';
import type { ContractStatus, ExpenseContract, IncomeContract, UUID } from 'types';

const { Title, Text } = Typography;

const statusColors: Record<ContractStatus, string> = {
  DRAFT: 'default', ACTIVE: 'green', COMPLETED: 'blue', TERMINATED: 'red',
};

interface ContractsPageProps {
  projectId: UUID;
}

const ContractsPage: React.FC<ContractsPageProps> = ({ projectId }) => {
  const [income, setIncome] = useState<IncomeContract[]>([]);
  const [expense, setExpense] = useState<ExpenseContract[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedContractId, setSelectedContractId] = useState<UUID | undefined>();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [inc, exp] = await Promise.all([
        contractsApi.listIncome(projectId),
        contractsApi.listExpense(projectId),
      ]);
      setIncome(inc);
      setExpense(exp);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => { load(); }, [load]);

  const selectedContract = income.find((c) => c.id === selectedContractId);

  const contractCols: ColumnsType<IncomeContract | ExpenseContract> = [
    { title: '№ договора', dataIndex: 'number', key: 'number', width: 120 },
    { title: 'Наименование', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Контрагент', dataIndex: 'counterparty', key: 'counterparty', width: 200 },
    {
      title: 'Сумма', dataIndex: 'totalAmount', key: 'totalAmount', width: 150,
      render: (v: number) => v?.toLocaleString('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }),
    },
    {
      title: 'Статус', dataIndex: 'status', key: 'status', width: 120,
      render: (s: ContractStatus) => <Tag color={statusColors[s]}>{s}</Tag>,
    },
  ];

  return (
    <div>
      <Title level={4}><FileProtectOutlined /> Договоры</Title>

      <Tabs
        defaultActiveKey="distribution"
        items={[
          {
            key: 'distribution',
            label: 'Распределение ЛС → Договоры',
            children: (
              <Card size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text>Выберите доходный договор для распределения ЛС:</Text>
                  <Select
                    placeholder="Выберите доходный договор"
                    style={{ width: '100%', maxWidth: 500 }}
                    value={selectedContractId}
                    onChange={setSelectedContractId}
                    options={income.map((c) => ({
                      value: c.id,
                      label: `${c.number} — ${c.name} (${c.totalAmount?.toLocaleString('ru-RU')} ₽)`,
                    }))}
                    loading={loading}
                    allowClear
                  />
                  {selectedContract ? (
                    <ContractDistribution
                      projectId={projectId}
                      incomeContractId={selectedContract.id}
                      contractAmount={selectedContract.totalAmount}
                    />
                  ) : (
                    <Empty description="Выберите доходный договор для отображения распределения" />
                  )}
                </Space>
              </Card>
            ),
          },
          {
            key: 'income',
            label: `Доходные (${income.length})`,
            children: (
              <Table
                columns={contractCols} dataSource={income} rowKey="id"
                loading={loading} size="small" pagination={{ pageSize: 15 }}
              />
            ),
          },
          {
            key: 'expense',
            label: `Расходные (${expense.length})`,
            children: (
              <Table
                columns={contractCols} dataSource={expense} rowKey="id"
                loading={loading} size="small" pagination={{ pageSize: 15 }}
              />
            ),
          },
        ]}
      />
    </div>
  );
};

export default ContractsPage;
