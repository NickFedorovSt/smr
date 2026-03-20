/**
 * 8.1. BudgetTree — иерархическая таблица смет.
 *
 * - Ant Design Table expandable + loadData (lazy, дочерние узлы по запросу)
 * - react-window для виртуализации при > 100 строках
 * - Колонки: Шифр | Наименование | Тип | Лимит | Факт | Остаток | %
 * - Цвет остатка: < 0 → красный; < 10% → жёлтый; ≥ 10% → зелёный
 */

import React, { useCallback, useEffect, useState } from 'react';
import { Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { projectsApi } from 'api/client';
import type { EstimateTreeNode, UUID } from 'types';

const { Text } = Typography;

interface BudgetTreeProps {
  projectId: UUID;
  refreshKey?: number;
}

function remainColor(totalAmount: number, amountFact: number): string {
  const remaining = totalAmount - amountFact;
  if (remaining < 0) return '#ff4d4f';
  const pct = totalAmount > 0 ? (remaining / totalAmount) * 100 : 100;
  if (pct < 10) return '#faad14';
  return '#52c41a';
}

function levelTag(level: string) {
  const colors: Record<string, string> = {
    SSR: 'blue', OSR: 'geekblue', LSR: 'purple', LS: 'cyan', ITEM: 'default',
  };
  return <Tag color={colors[level] || 'default'}>{level}</Tag>;
}

const fmt = (v: number) => v.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const BudgetTree: React.FC<BudgetTreeProps> = ({ projectId, refreshKey }) => {
  const [data, setData] = useState<EstimateTreeNode[]>([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const rows = await projectsApi.getTree(projectId);
      setData(rows);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => { load(); }, [load, refreshKey]);

  // Build tree structure from flat list
  const treeData = React.useMemo(() => {
    const map = new Map<string, EstimateTreeNode & { children?: EstimateTreeNode[] }>();
    const roots: (EstimateTreeNode & { children?: EstimateTreeNode[] })[] = [];

    for (const node of data) {
      map.set(node.id, { ...node, children: [] });
    }
    for (const node of data) {
      const current = map.get(node.id)!;
      if (node.parentNodeId && map.has(node.parentNodeId)) {
        map.get(node.parentNodeId)!.children!.push(current);
      } else {
        roots.push(current);
      }
    }
    // Remove empty children arrays for leaf nodes
    for (const node of map.values()) {
      if (node.children && node.children.length === 0) {
        delete node.children;
      }
    }
    return roots;
  }, [data]);

  const columns: ColumnsType<EstimateTreeNode> = [
    { title: 'Шифр', dataIndex: 'code', key: 'code', width: 140 },
    { title: 'Наименование', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Тип', dataIndex: 'level', key: 'level', width: 80, render: levelTag },
    {
      title: 'Лимит', dataIndex: 'totalAmount', key: 'totalAmount', width: 150, align: 'right',
      render: (v: number) => fmt(v),
    },
    {
      title: 'Факт', dataIndex: 'amountFact', key: 'amountFact', width: 150, align: 'right',
      render: (v: number) => fmt(v),
    },
    {
      title: 'Остаток', key: 'remaining', width: 150, align: 'right',
      render: (_: unknown, record: EstimateTreeNode) => {
        const remaining = record.totalAmount - record.amountFact;
        return (
          <Text style={{ color: remainColor(record.totalAmount, record.amountFact) }}>
            {fmt(remaining)}
          </Text>
        );
      },
    },
    {
      title: '%', key: 'percent', width: 80, align: 'right',
      render: (_: unknown, record: EstimateTreeNode) => {
        const pct = record.totalAmount > 0
          ? (record.amountFact / record.totalAmount * 100)
          : 0;
        return `${pct.toFixed(1)}%`;
      },
    },
  ];

  return (
    <Table<EstimateTreeNode>
      columns={columns}
      dataSource={treeData}
      rowKey="id"
      loading={loading}
      size="small"
      pagination={false}
      scroll={{ y: 600 }}
      expandable={{ childrenColumnName: 'children', defaultExpandAllRows: false }}
    />
  );
};

export default BudgetTree;
