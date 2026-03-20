/**
 * 8.5. InspectionBoard — предписания СДО.
 *
 * - Таблица предписаний с фильтрами по статусу
 * - Кнопка смены статуса + форма комментария
 * - Timeline истории изменений статуса (InspectionLog)
 * - Красная маркировка просроченных предписаний
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Button, Drawer, Form, Input, message, Modal, Select, Space, Table, Tag, Timeline, Typography,
} from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { inspectionsApi } from 'api/client';
import type { Inspection, InspectionLog, InspectionStatus, UUID } from 'types';

const { Text } = Typography;

interface InspectionBoardProps {
  projectId: UUID;
}

const statusOptions: { value: InspectionStatus; label: string }[] = [
  { value: 'OPEN', label: 'Открыто' },
  { value: 'IN_PROGRESS', label: 'В работе' },
  { value: 'FIXED', label: 'Устранено' },
  { value: 'CLOSED', label: 'Закрыто' },
];

const statusColors: Record<string, string> = {
  OPEN: 'red', IN_PROGRESS: 'orange', FIXED: 'blue', CLOSED: 'green',
};

function isOverdue(ins: Inspection): boolean {
  if (ins.status === 'CLOSED') return false;
  if (!ins.plannedFixDate) return false;
  return new Date(ins.plannedFixDate) < new Date();
}

const InspectionBoard: React.FC<InspectionBoardProps> = ({ projectId }) => {
  const [data, setData] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState<InspectionStatus | undefined>();
  const [selectedId, setSelectedId] = useState<UUID | null>(null);
  const [logs, setLogs] = useState<InspectionLog[]>([]);
  const [logDrawerOpen, setLogDrawerOpen] = useState(false);
  const [changeModalOpen, setChangeModalOpen] = useState(false);
  const [changeForm] = Form.useForm();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setData(await inspectionsApi.list(projectId));
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => { load(); }, [load]);

  const filtered = data.filter((d) => !filterStatus || d.status === filterStatus);

  const showLogs = async (id: UUID) => {
    setSelectedId(id);
    const result = await inspectionsApi.getLogs(id);
    setLogs(result);
    setLogDrawerOpen(true);
  };

  const openChangeStatus = (id: UUID) => {
    setSelectedId(id);
    changeForm.resetFields();
    setChangeModalOpen(true);
  };

  const handleChangeStatus = async () => {
    const values = await changeForm.validateFields();
    if (!selectedId) return;
    try {
      await inspectionsApi.changeStatus(selectedId, {
        newStatus: values.newStatus,
        comment: values.comment,
      });
      message.success('Статус обновлён');
      setChangeModalOpen(false);
      load();
    } catch {
      message.error('Ошибка обновления');
    }
  };

  const columns: ColumnsType<Inspection> = [
    { title: '№', dataIndex: 'number', key: 'number', width: 80 },
    {
      title: 'Описание', dataIndex: 'description', key: 'description', ellipsis: true,
      render: (text: string, record: Inspection) => (
        <Space>
          {isOverdue(record) && <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />}
          <Text>{text}</Text>
        </Space>
      ),
    },
    { title: 'Норматив', dataIndex: 'normReference', key: 'normReference', width: 180, ellipsis: true },
    { title: 'Плановый срок', dataIndex: 'plannedFixDate', key: 'plannedFixDate', width: 130 },
    { title: 'Факт. срок', dataIndex: 'actualFixDate', key: 'actualFixDate', width: 130 },
    {
      title: 'Статус', dataIndex: 'status', key: 'status', width: 120,
      render: (s: string) => <Tag color={statusColors[s]}>{s}</Tag>,
    },
    {
      title: 'Действия', key: 'actions', width: 200,
      render: (_: unknown, record: Inspection) => (
        <Space>
          <Button size="small" onClick={() => openChangeStatus(record.id)}>Статус</Button>
          <Button size="small" type="link" onClick={() => showLogs(record.id)}>История</Button>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="Фильтр по статусу" allowClear style={{ width: 180 }}
          options={statusOptions} onChange={(v) => setFilterStatus(v)}
        />
      </Space>

      <Table<Inspection>
        columns={columns}
        dataSource={filtered}
        rowKey="id"
        loading={loading}
        size="small"
        pagination={{ pageSize: 20 }}
        rowClassName={(record) => isOverdue(record) ? 'inspection-overdue' : ''}
      />

      {/* Timeline drawer */}
      <Drawer
        title="История изменений статуса"
        open={logDrawerOpen}
        onClose={() => setLogDrawerOpen(false)}
        width={400}
      >
        <Timeline
          items={logs.map((log) => ({
            color: statusColors[log.newStatus] || 'gray',
            children: (
              <div>
                <Text strong>{log.oldStatus} → {log.newStatus}</Text>
                <br />
                <Text type="secondary">{log.changedAt}</Text>
                {log.comment && <div style={{ marginTop: 4 }}>{log.comment}</div>}
                {log.changedBy && <div><Text type="secondary">Автор: {log.changedBy}</Text></div>}
              </div>
            ),
          }))}
        />
      </Drawer>

      {/* Change status modal */}
      <Modal
        title="Изменить статус предписания"
        open={changeModalOpen}
        onOk={handleChangeStatus}
        onCancel={() => setChangeModalOpen(false)}
        okText="Применить"
        cancelText="Отмена"
      >
        <Form form={changeForm} layout="vertical">
          <Form.Item name="newStatus" label="Новый статус" rules={[{ required: true }]}>
            <Select options={statusOptions} />
          </Form.Item>
          <Form.Item name="comment" label="Комментарий">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      <style>{`
        .inspection-overdue { background-color: #fff1f0 !important; }
      `}</style>
    </>
  );
};

export default InspectionBoard;
