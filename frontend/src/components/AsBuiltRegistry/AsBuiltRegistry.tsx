/**
 * 8.3. AsBuiltRegistry — таблица АОСР/АООК.
 *
 * - Фильтры: тип, статус, дата, марка чертежа
 * - Форма создания: мультиселект чертежей и спецификаций
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Button, DatePicker, Drawer, Form, Input, message, Select, Space, Table, Tag,
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { asbuiltApi, drawingsApi } from 'api/client';
import type { AsBuiltDoc, AsBuiltDocCreate, AsBuiltDocStatus, AsBuiltDocType, Drawing, UUID } from 'types';

interface AsBuiltRegistryProps {
  projectId: UUID;
}

const typeOptions = [
  { value: 'AOSR', label: 'АОСР' },
  { value: 'AOOK', label: 'АООК' },
  { value: 'OTHER', label: 'Прочее' },
];

const statusOptions = [
  { value: 'DRAFT', label: 'Черновик' },
  { value: 'SIGNED', label: 'Подписан' },
  { value: 'REJECTED', label: 'Отклонён' },
];

const statusColors: Record<string, string> = {
  DRAFT: 'default', SIGNED: 'success', REJECTED: 'error',
};

const AsBuiltRegistry: React.FC<AsBuiltRegistryProps> = ({ projectId }) => {
  const [docs, setDocs] = useState<AsBuiltDoc[]>([]);
  const [loading, setLoading] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawings, setDrawings] = useState<Drawing[]>([]);
  const [filterType, setFilterType] = useState<AsBuiltDocType | undefined>();
  const [filterStatus, setFilterStatus] = useState<AsBuiltDocStatus | undefined>();
  const [form] = Form.useForm();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const all = await asbuiltApi.list(projectId);
      setDocs(all);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => { load(); }, [load]);

  const openCreate = async () => {
    const drws = await drawingsApi.list(projectId);
    setDrawings(drws);
    form.resetFields();
    setDrawerOpen(true);
  };

  const handleCreate = async () => {
    const values = await form.validateFields();
    const data: AsBuiltDocCreate = {
      ...values,
      projectId,
      workDate: values.workDate?.format('YYYY-MM-DD'),
      signDate: values.signDate?.format('YYYY-MM-DD'),
    };
    try {
      await asbuiltApi.create(data);
      message.success('Акт создан');
      setDrawerOpen(false);
      load();
    } catch {
      message.error('Ошибка создания');
    }
  };

  const filteredDocs = docs.filter((d) => {
    if (filterType && d.type !== filterType) return false;
    if (filterStatus && d.status !== filterStatus) return false;
    return true;
  });

  const columns: ColumnsType<AsBuiltDoc> = [
    { title: '№', dataIndex: 'number', key: 'number', width: 100 },
    { title: 'Тип', dataIndex: 'type', key: 'type', width: 80, render: (t: string) => <Tag>{t}</Tag> },
    { title: 'Наименование', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Дата работ', dataIndex: 'workDate', key: 'workDate', width: 120 },
    { title: 'Дата подп.', dataIndex: 'signDate', key: 'signDate', width: 120 },
    { title: 'Прораб', dataIndex: 'foreman', key: 'foreman', width: 150 },
    { title: 'Технадзор', dataIndex: 'supervisor', key: 'supervisor', width: 150 },
    {
      title: 'Статус', dataIndex: 'status', key: 'status', width: 110,
      render: (s: string) => <Tag color={statusColors[s]}>{s}</Tag>,
    },
  ];

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="Тип" allowClear style={{ width: 120 }}
          options={typeOptions} onChange={(v) => setFilterType(v)}
        />
        <Select
          placeholder="Статус" allowClear style={{ width: 140 }}
          options={statusOptions} onChange={(v) => setFilterStatus(v)}
        />
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          Создать акт
        </Button>
      </Space>

      <Table<AsBuiltDoc>
        columns={columns}
        dataSource={filteredDocs}
        rowKey="id"
        loading={loading}
        size="small"
        pagination={{ pageSize: 20 }}
      />

      <Drawer
        title="Новый акт ИД"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={480}
        extra={<Button type="primary" onClick={handleCreate}>Сохранить</Button>}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="number" label="Номер" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="name" label="Наименование" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="type" label="Тип" rules={[{ required: true }]}>
            <Select options={typeOptions} />
          </Form.Item>
          <Form.Item name="workDate" label="Дата работ">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="signDate" label="Дата подписания">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="foreman" label="Прораб">
            <Input />
          </Form.Item>
          <Form.Item name="supervisor" label="Технадзор">
            <Input />
          </Form.Item>
          <Form.Item name="status" label="Статус" initialValue="DRAFT">
            <Select options={statusOptions} />
          </Form.Item>
          <Form.Item name="drawingIds" label="Чертежи">
            <Select
              mode="multiple"
              placeholder="Выберите чертежи"
              options={drawings.map((d) => ({ value: d.id, label: `${d.mark} — ${d.name}` }))}
            />
          </Form.Item>
        </Form>
      </Drawer>
    </>
  );
};

export default AsBuiltRegistry;
