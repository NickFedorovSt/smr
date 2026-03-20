/**
 * Страница «Исполнительная документация» — AsBuiltRegistry + IDReadinessDashboard.
 */

import React from 'react';
import { Col, Row, Typography } from 'antd';
import { AuditOutlined } from '@ant-design/icons';
import { AsBuiltRegistry } from 'components/AsBuiltRegistry';
import { IDReadinessDashboard } from 'components/IDReadinessDashboard';
import type { UUID } from 'types';

const { Title } = Typography;

interface AsBuiltPageProps {
  projectId: UUID;
}

const AsBuiltPage: React.FC<AsBuiltPageProps> = ({ projectId }) => (
  <div>
    <Title level={4}><AuditOutlined /> Исполнительная документация</Title>
    <Row gutter={[24, 24]}>
      <Col xs={24} xl={16}>
        <AsBuiltRegistry projectId={projectId} />
      </Col>
      <Col xs={24} xl={8}>
        <IDReadinessDashboard projectId={projectId} />
      </Col>
    </Row>
  </div>
);

export default AsBuiltPage;
