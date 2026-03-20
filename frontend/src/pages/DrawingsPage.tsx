/**
 * Страница «Чертежи» — список чертежей проекта с фильтрами и управлением.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Button, Drawer, Form, Input, message, Popconfirm, Select, Space, Table, Tag, Typography,
} from 'antd';
import { DeleteOutlined, EditOutlined, FileImageOutlined, PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { drawingsApi } from 'api/client';
import type { Drawing, DrawingStatus, UUID } from 'types';

const { Title } = Typography;

const statusColors: Record<DrawingStatus, string> = {
  DRAFT: 'default', ISSUED: 'green', SUPERSEDED: 'red',
};
const statusLabels: Record<DrawingStatus, string> = {
  DRAFT: 'Черновик', ISSUED: 'Выдан в производство', SUPERSEDED: 'Заменён',
};

interface DrawingsPageProps {
  projectId: UUID;
}

const DrawingsPage: React.FC<DrawingsPageProps> = ({ projectId }) => {
  const [drawings, setDrawings] = useState<Drawing[]>([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingId, setEditingId] = useState<UUID | null>(null);
  const [form] = Form.useForm();
  const [filterStatus, setFilterStatus] = useState<DrawingStatus | undefined>();

  const load = useCallback(async () => {
    setLoading(true);
    try { setDrawings(await drawingsApi.list(projectId)); } finally { setLoading(false); }
  }, [projectId]);

  useEffect(() => { load(); }, [load]);

  const filtered = drawings.filter((d) => !filterStatus || d.status === filterStatus);

  const openCreate = () => {
    setEditingId(null);
    form.resetFields();
    form.setFieldValue('projectId', projectId);
    setDrawerOpen(true);
  };

  const openEdit = (record: Drawing) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setDrawerOpen(true);
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    try {
      if (editingId) {
        await drawingsApi.update(editingId, values);
        message.success('Чертёж обновлён');
      } else {
        await drawingsApi.create({ ...values, projectId });
        message.success('Чертёж добавлен');
      }
      setDrawerOpen(false);
      load();
    } catch {
      message.error('Ошибка сохранения');
    }
  };

  const handleDelete = async (id: UUID) => {
    try { await drawingsApi.delete(id); message.success('Удалено'); load(); }
    catch { message.error('Ошибка удаления'); }
  };

  const columns: ColumnsType<Drawing> = [
    { title: 'Марка', dataIndex: 'mark', key: 'mark', width: 100 },
    { title: 'Наименование', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Лист', dataIndex: 'sheetNumber', key: 'sheetNumber', width: 80 },
    { title: 'Ревизия', dataIndex: 'revision', key: 'revision', width: 80 },
    { title: 'Дата выдачи', dataIndex: 'issuedDate', key: 'issuedDate', width: 120 },
    {
      title: 'Статус', dataIndex: 'status', key: 'status', width: 160,
      render: (s: DrawingStatus) => <Tag color={statusColors[s]}>{statusLabels[s]}</Tag>,
    },
    {
      title: 'Действия', key: 'actions', width: 100,
      render: (_: unknown, record: Drawing) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
          <Popconfirm title="Удалить?" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={4} style={{ margin: 0 }}><FileImageOutlined /> Чертежи</Title>
        <Space>
          <Select
            allowClear placeholder="Фильтр по статусу" style={{ width: 200 }}
            options={Object.entries(statusLabels).map(([v, l]) => ({ value: v, label: l }))}
            onChange={(v) => setFilterStatus(v)}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Добавить</Button>
        </Space>
      </Space>

      <Table<Drawing>
        columns={columns} dataSource={filtered} rowKey="id" loading={loading}
        size="small" pagination={{ pageSize: 20 }}
      />

      <Drawer
        title={editingId ? 'Редактирование чертежа' : 'Новый чертёж'}
        open={drawerOpen} onClose={() => setDrawerOpen(false)} width={480}
        extra={<Button type="primary" onClick={handleSave}>Сохранить</Button>}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="mark" label="Марка" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="name" label="Наименование" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="sheetNumber" label="Номер листа"><Input /></Form.Item>
          <Form.Item name="revision" label="Ревизия"><Input /></Form.Item>
          <Form.Item name="status" label="Статус" initialValue="DRAFT">
            <Select options={Object.entries(statusLabels).map(([v, l]) => ({ value: v, label: l }))} />
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  );
};

export default DrawingsPage;
