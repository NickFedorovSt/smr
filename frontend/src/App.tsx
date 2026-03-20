/**
 * App.tsx — корневой компонент с маршрутизацией.
 *
 * Маршруты:
 *   /                       → перенаправление на /projects
 *   /projects               → список проектов
 *   /projects/:id           → дашборд проекта (сметы + быстрый ввод)
 *   /projects/:id/estimates → сметная иерархия
 *   /projects/:id/contracts → договоры
 *   /projects/:id/drawings  → чертежи
 *   /projects/:id/asbuilt   → исполнительная документация
 *   /projects/:id/inspections → предписания
 *   /projects/:id/reports   → отчёты
 */

import React from 'react';
import {
  BrowserRouter, Navigate, Route, Routes, useNavigate, useParams,
} from 'react-router-dom';
import { ConfigProvider, Layout, Menu, Typography, theme } from 'antd';
import ruRU from 'antd/locale/ru_RU';
import {
  AccountBookOutlined, AuditOutlined, FileExcelOutlined,
  FileImageOutlined, FileProtectOutlined, HomeOutlined,
  ProjectOutlined, SafetyOutlined,
} from '@ant-design/icons';

import ProjectsPage from 'pages/ProjectsPage';
import EstimatesPage from 'pages/EstimatesPage';
import ContractsPage from 'pages/ContractsPage';
import DrawingsPage from 'pages/DrawingsPage';
import AsBuiltPage from 'pages/AsBuiltPage';
import InspectionsPage from 'pages/InspectionsPage';
import ReportsPageWrapper from 'pages/ReportsPageWrapper';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

// ═══════════════════════════════════════════════════════════════
// Project layout — боковое меню внутри проекта
// ═══════════════════════════════════════════════════════════════

const ProjectLayout: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  if (!id) return <Navigate to="/projects" replace />;

  const menuItems = [
    { key: 'estimates', icon: <AccountBookOutlined />, label: 'Сметы' },
    { key: 'contracts', icon: <FileProtectOutlined />, label: 'Договоры' },
    { key: 'drawings', icon: <FileImageOutlined />, label: 'Чертежи' },
    { key: 'asbuilt', icon: <AuditOutlined />, label: 'Исп. документация' },
    { key: 'inspections', icon: <SafetyOutlined />, label: 'Предписания' },
    { key: 'reports', icon: <FileExcelOutlined />, label: 'Отчёты' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={220} theme="light" breakpoint="lg" collapsedWidth={60}>
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <Title level={5} style={{ margin: 0, cursor: 'pointer' }} onClick={() => navigate('/projects')}>
            <HomeOutlined /> СМР ПСД
          </Title>
        </div>
        <Menu
          mode="inline"
          defaultSelectedKeys={['estimates']}
          items={menuItems}
          onClick={({ key }) => navigate(`/projects/${id}/${key}`)}
        />
      </Sider>
      <Layout>
        <Content style={{ padding: 24 }}>
          <Routes>
            <Route index element={<EstimatesPage projectId={id} />} />
            <Route path="estimates" element={<EstimatesPage projectId={id} />} />
            <Route path="contracts" element={<ContractsPage projectId={id} />} />
            <Route path="drawings" element={<DrawingsPage projectId={id} />} />
            <Route path="asbuilt" element={<AsBuiltPage projectId={id} />} />
            <Route path="inspections" element={<InspectionsPage projectId={id} />} />
            <Route path="reports" element={<ReportsPageWrapper projectId={id} />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

// ═══════════════════════════════════════════════════════════════
// Root App
// ═══════════════════════════════════════════════════════════════

const App: React.FC = () => (
  <ConfigProvider locale={ruRU} theme={{ algorithm: theme.defaultAlgorithm }}>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/projects" replace />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/:id/*" element={<ProjectLayout />} />
      </Routes>
    </BrowserRouter>
  </ConfigProvider>
);

export default App;
