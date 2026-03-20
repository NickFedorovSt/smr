/**
 * 8.6. QuickProgressForm — быстрый ввод факта прямо с дашборда.
 *
 * - Форма: выбор ЛС → выбор статьи → месяц/год → объём → сумма
 * - Без перехода в глубину дерева (наиболее частая операция ПТО)
 * - После сохранения: обновить BudgetTree и AlertsPanel (через onSaved callback)
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Button, Card, DatePicker, Form, InputNumber, message, Select, Space, Typography,
} from 'antd';
import { SaveOutlined, ThunderboltOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { estimatesApi, progressApi } from 'api/client';
import type { EstimateItem, LocalEstimate, ProgressCreate, UUID } from 'types';

const { Title } = Typography;

interface QuickProgressFormProps {
  projectId: UUID;
  /** Список ЛС, переданный из родителя (чтобы не дублировать запрос). */
  localEstimates?: LocalEstimate[];
  /** Вызывается после успешного сохранения — обновить BudgetTree, AlertsPanel и т.д. */
  onSaved?: () => void;
}

const QuickProgressForm: React.FC<QuickProgressFormProps> = ({
  projectId,
  localEstimates: externalLs,
  onSaved,
}) => {
  const [form] = Form.useForm();
  const [lsList, setLsList] = useState<LocalEstimate[]>(externalLs ?? []);
  const [items, setItems] = useState<EstimateItem[]>([]);
  const [loadingItems, setLoadingItems] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Если ЛС не переданы снаружи — загружаем сами (плоский список по проекту).
  // API может не поддерживать flat-list, поэтому fallback: показать пустой селект.
  useEffect(() => {
    if (externalLs && externalLs.length > 0) {
      setLsList(externalLs);
    }
  }, [externalLs]);

  const onLsChange = useCallback(async (lsId: UUID) => {
    form.setFieldValue('estimateItemId', undefined);
    setItems([]);
    if (!lsId) return;
    setLoadingItems(true);
    try {
      const result = await estimatesApi.listItems(lsId);
      setItems(result);
    } finally {
      setLoadingItems(false);
    }
  }, [form]);

  const onFinish = useCallback(async (values: {
    lsId: UUID;
    estimateItemId: UUID;
    period: dayjs.Dayjs;
    volumeFact: number;
    amountFact: number;
    ks2Number?: string;
  }) => {
    setSubmitting(true);
    try {
      const payload: ProgressCreate = {
        estimateItemId: values.estimateItemId,
        year: values.period.year(),
        month: values.period.month() + 1, // dayjs month is 0-based
        volumeFact: values.volumeFact,
        amountFact: values.amountFact,
        ks2Number: values.ks2Number,
      };
      await progressApi.create(payload);
      message.success('Факт сохранён');
      form.resetFields();
      setItems([]);
      onSaved?.();
    } catch {
      message.error('Ошибка сохранения факта');
    } finally {
      setSubmitting(false);
    }
  }, [form, onSaved]);

  return (
    <Card
      title={
        <Space>
          <ThunderboltOutlined />
          <Title level={5} style={{ margin: 0 }}>Быстрый ввод факта</Title>
        </Space>
      }
      size="small"
    >
      <Form form={form} layout="vertical" onFinish={onFinish}>
        {/* Выбор ЛС */}
        <Form.Item
          name="lsId" label="Локальная смета (ЛС)"
          rules={[{ required: true, message: 'Выберите ЛС' }]}
        >
          <Select
            showSearch
            placeholder="Выберите ЛС"
            optionFilterProp="label"
            onChange={onLsChange}
            options={lsList.map((ls) => ({
              value: ls.id,
              label: `${ls.code} — ${ls.name}`,
            }))}
          />
        </Form.Item>

        {/* Выбор сметной статьи */}
        <Form.Item
          name="estimateItemId" label="Сметная статья"
          rules={[{ required: true, message: 'Выберите статью' }]}
        >
          <Select
            showSearch
            placeholder="Выберите статью"
            optionFilterProp="label"
            loading={loadingItems}
            options={items.map((item) => ({
              value: item.id,
              label: `${item.code} — ${item.name} (${item.unit})`,
            }))}
          />
        </Form.Item>

        {/* Период: месяц/год */}
        <Form.Item
          name="period" label="Период (месяц/год)"
          rules={[{ required: true, message: 'Выберите период' }]}
        >
          <DatePicker picker="month" style={{ width: '100%' }} />
        </Form.Item>

        {/* Объём и сумма */}
        <Space style={{ width: '100%' }} size="middle">
          <Form.Item
            name="volumeFact" label="Объём (факт)"
            rules={[{ required: true, message: 'Введите объём' }]}
            style={{ flex: 1 }}
          >
            <InputNumber min={0} step={0.01} style={{ width: '100%' }} placeholder="0.00" />
          </Form.Item>

          <Form.Item
            name="amountFact" label="Сумма (факт), ₽"
            rules={[{ required: true, message: 'Введите сумму' }]}
            style={{ flex: 1 }}
          >
            <InputNumber
              min={0} step={100} style={{ width: '100%' }} placeholder="0.00"
              formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')}
              parser={(v) => Number((v ?? '').replace(/\s/g, '')) as unknown as 0}
            />
          </Form.Item>
        </Space>

        {/* Номер КС-2 (необязательно) */}
        <Form.Item name="ks2Number" label="Номер КС-2 (необязательно)">
          <Select
            allowClear
            placeholder="Связать с КС-2 (необязательно)"
            options={[]}
            notFoundContent="Введите номер вручную или оставьте пустым"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={submitting}
            icon={<SaveOutlined />}
            block
          >
            Сохранить факт
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default QuickProgressForm;
