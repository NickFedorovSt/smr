/** Axios клиент + типизированные API-вызовы для всех модулей. */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  UUID,
  Project, ProjectCreate, ProjectUpdate,
  EstimateTreeNode, BudgetSummaryItem, AlertItem, IDReadinessItem,
  SummaryEstimate, ObjectEstimate, LocalEstimateBase, LocalEstimate,
  EstimateItem, EstimateItemCreate,
  IncomeContract, ExpenseContract,
  LsIncomeContractLink, IncomeExpenseContractLink,
  Drawing, Specification,
  AsBuiltDoc, AsBuiltDocCreate,
  Progress, ProgressCreate,
  MaterialCertificate, M29Report, M29Line,
  Inspection, InspectionLog, InspectionChangeStatus,
  WorkJournal, JournalEntry,
  ReportType, ReportCacheItem,
} from 'types';

const API_BASE = process.env.REACT_APP_API_URL || '/api/v1';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// ── Helper ────────────────────────────────────────────────────

function unwrap<T>(res: AxiosResponse<T>): T {
  return res.data;
}

// ═══════════════════════════════════════════════════════════════
// Projects
// ═══════════════════════════════════════════════════════════════

export const projectsApi = {
  list: () => api.get<Project[]>('/projects').then(unwrap),
  get: (id: UUID) => api.get<Project>(`/projects/${id}`).then(unwrap),
  create: (data: ProjectCreate) => api.post<Project>('/projects', data).then(unwrap),
  update: (id: UUID, data: ProjectUpdate) => api.put<Project>(`/projects/${id}`, data).then(unwrap),
  delete: (id: UUID) => api.delete(`/projects/${id}`),
  getTree: (id: UUID) => api.get<EstimateTreeNode[]>(`/projects/${id}/tree`).then(unwrap),
  getBudgetSummary: (id: UUID) => api.get<BudgetSummaryItem[]>(`/projects/${id}/budget-summary`).then(unwrap),
  getAlerts: (id: UUID) => api.get<AlertItem[]>(`/projects/${id}/alerts`).then(unwrap),
  getIdReadiness: (id: UUID) => api.get<IDReadinessItem[]>(`/projects/${id}/id-readiness`).then(unwrap),
};

// ═══════════════════════════════════════════════════════════════
// Estimates
// ═══════════════════════════════════════════════════════════════

export const estimatesApi = {
  // ССР
  listSsr: (projectId: UUID) => api.get<SummaryEstimate[]>(`/estimates/ssr?project_id=${projectId}`).then(unwrap),
  createSsr: (data: Partial<SummaryEstimate>) => api.post<SummaryEstimate>('/estimates/ssr', data).then(unwrap),
  updateSsr: (id: UUID, data: Partial<SummaryEstimate>) => api.put<SummaryEstimate>(`/estimates/ssr/${id}`, data).then(unwrap),
  deleteSsr: (id: UUID) => api.delete(`/estimates/ssr/${id}`),
  // ОСР
  listOsr: (ssrId: UUID) => api.get<ObjectEstimate[]>(`/estimates/osr?summary_estimate_id=${ssrId}`).then(unwrap),
  createOsr: (data: Partial<ObjectEstimate>) => api.post<ObjectEstimate>('/estimates/osr', data).then(unwrap),
  updateOsr: (id: UUID, data: Partial<ObjectEstimate>) => api.put<ObjectEstimate>(`/estimates/osr/${id}`, data).then(unwrap),
  deleteOsr: (id: UUID) => api.delete(`/estimates/osr/${id}`),
  // ЛСР
  listLsr: (osrId: UUID) => api.get<LocalEstimateBase[]>(`/estimates/lsr?object_estimate_id=${osrId}`).then(unwrap),
  createLsr: (data: Partial<LocalEstimateBase>) => api.post<LocalEstimateBase>('/estimates/lsr', data).then(unwrap),
  updateLsr: (id: UUID, data: Partial<LocalEstimateBase>) => api.put<LocalEstimateBase>(`/estimates/lsr/${id}`, data).then(unwrap),
  deleteLsr: (id: UUID) => api.delete(`/estimates/lsr/${id}`),
  // ЛС
  listLs: (lsrId: UUID) => api.get<LocalEstimate[]>(`/estimates/ls?lsr_id=${lsrId}`).then(unwrap),
  createLs: (data: Partial<LocalEstimate>) => api.post<LocalEstimate>('/estimates/ls', data).then(unwrap),
  updateLs: (id: UUID, data: Partial<LocalEstimate>) => api.put<LocalEstimate>(`/estimates/ls/${id}`, data).then(unwrap),
  deleteLs: (id: UUID) => api.delete(`/estimates/ls/${id}`),
  // Сметные статьи
  listItems: (lsId: UUID) => api.get<EstimateItem[]>(`/estimates/items?ls_id=${lsId}`).then(unwrap),
  createItem: (data: EstimateItemCreate) => api.post<EstimateItem>('/estimates/items', data).then(unwrap),
  updateItem: (id: UUID, data: Partial<EstimateItemCreate>) => api.put<EstimateItem>(`/estimates/items/${id}`, data).then(unwrap),
  deleteItem: (id: UUID) => api.delete(`/estimates/items/${id}`),
};

// ═══════════════════════════════════════════════════════════════
// Contracts
// ═══════════════════════════════════════════════════════════════

export const contractsApi = {
  listIncome: (projectId: UUID) => api.get<IncomeContract[]>(`/contracts/income?project_id=${projectId}`).then(unwrap),
  createIncome: (data: Partial<IncomeContract>) => api.post<IncomeContract>('/contracts/income', data).then(unwrap),
  updateIncome: (id: UUID, data: Partial<IncomeContract>) => api.put<IncomeContract>(`/contracts/income/${id}`, data).then(unwrap),
  deleteIncome: (id: UUID) => api.delete(`/contracts/income/${id}`),

  listExpense: (projectId: UUID) => api.get<ExpenseContract[]>(`/contracts/expense?project_id=${projectId}`).then(unwrap),
  createExpense: (data: Partial<ExpenseContract>) => api.post<ExpenseContract>('/contracts/expense', data).then(unwrap),
  updateExpense: (id: UUID, data: Partial<ExpenseContract>) => api.put<ExpenseContract>(`/contracts/expense/${id}`, data).then(unwrap),
  deleteExpense: (id: UUID) => api.delete(`/contracts/expense/${id}`),

  // ЛС ↔ Доходный договор
  getLsIncomeLinks: (contractId: UUID) => api.get<LsIncomeContractLink[]>(`/contracts/ls-income?income_contract_id=${contractId}`).then(unwrap),
  addLsIncome: (data: LsIncomeContractLink) => api.post('/contracts/ls-income', data),
  removeLsIncome: (lsId: UUID, contractId: UUID) => api.delete(`/contracts/ls-income/${lsId}/${contractId}`),

  // Доходный ↔ Расходный
  getIncomeExpenseLinks: (contractId: UUID) => api.get<IncomeExpenseContractLink[]>(`/contracts/income-expense?income_contract_id=${contractId}`).then(unwrap),
  addIncomeExpense: (data: IncomeExpenseContractLink) => api.post('/contracts/income-expense', data),
  removeIncomeExpense: (incId: UUID, expId: UUID) => api.delete(`/contracts/income-expense/${incId}/${expId}`),
};

// ═══════════════════════════════════════════════════════════════
// Drawings
// ═══════════════════════════════════════════════════════════════

export const drawingsApi = {
  list: (projectId: UUID) => api.get<Drawing[]>(`/drawings?project_id=${projectId}`).then(unwrap),
  get: (id: UUID) => api.get<Drawing>(`/drawings/${id}`).then(unwrap),
  create: (data: Partial<Drawing>) => api.post<Drawing>('/drawings', data).then(unwrap),
  update: (id: UUID, data: Partial<Drawing>) => api.put<Drawing>(`/drawings/${id}`, data).then(unwrap),
  delete: (id: UUID) => api.delete(`/drawings/${id}`),
  listSpecs: (drawingId: UUID) => api.get<Specification[]>(`/drawings/${drawingId}/specifications`).then(unwrap),
};

// ═══════════════════════════════════════════════════════════════
// AsBuilt
// ═══════════════════════════════════════════════════════════════

export const asbuiltApi = {
  list: (projectId: UUID) => api.get<AsBuiltDoc[]>(`/asbuilt?project_id=${projectId}`).then(unwrap),
  get: (id: UUID) => api.get<AsBuiltDoc>(`/asbuilt/${id}`).then(unwrap),
  create: (data: AsBuiltDocCreate) => api.post<AsBuiltDoc>('/asbuilt', data).then(unwrap),
  update: (id: UUID, data: Partial<AsBuiltDocCreate>) => api.put<AsBuiltDoc>(`/asbuilt/${id}`, data).then(unwrap),
  delete: (id: UUID) => api.delete(`/asbuilt/${id}`),
};

// ═══════════════════════════════════════════════════════════════
// Progress
// ═══════════════════════════════════════════════════════════════

export const progressApi = {
  list: (params?: Record<string, string>) => api.get<Progress[]>('/progress', { params }).then(unwrap),
  create: (data: ProgressCreate) => api.post<Progress>('/progress', data).then(unwrap),
  update: (id: UUID, data: Partial<ProgressCreate>) => api.put<Progress>(`/progress/${id}`, data).then(unwrap),
  delete: (id: UUID) => api.delete(`/progress/${id}`),
};

// ═══════════════════════════════════════════════════════════════
// Materials
// ═══════════════════════════════════════════════════════════════

export const materialsApi = {
  listCerts: (projectId: UUID) => api.get<MaterialCertificate[]>(`/materials/certificates?project_id=${projectId}`).then(unwrap),
  createCert: (data: Partial<MaterialCertificate>) => api.post<MaterialCertificate>('/materials/certificates', data).then(unwrap),
  deleteCert: (id: UUID) => api.delete(`/materials/certificates/${id}`),

  listM29: (projectId: UUID) => api.get<M29Report[]>(`/materials/m29?project_id=${projectId}`).then(unwrap),
  createM29: (data: Partial<M29Report>) => api.post<M29Report>('/materials/m29', data).then(unwrap),
  listM29Lines: (reportId: UUID) => api.get<M29Line[]>(`/materials/m29/${reportId}/lines`).then(unwrap),
};

// ═══════════════════════════════════════════════════════════════
// Inspections
// ═══════════════════════════════════════════════════════════════

export const inspectionsApi = {
  list: (projectId: UUID) => api.get<Inspection[]>(`/inspections?project_id=${projectId}`).then(unwrap),
  get: (id: UUID) => api.get<Inspection>(`/inspections/${id}`).then(unwrap),
  create: (data: Partial<Inspection>) => api.post<Inspection>('/inspections', data).then(unwrap),
  update: (id: UUID, data: Partial<Inspection>) => api.put<Inspection>(`/inspections/${id}`, data).then(unwrap),
  delete: (id: UUID) => api.delete(`/inspections/${id}`),
  changeStatus: (id: UUID, data: InspectionChangeStatus) => api.post(`/inspections/${id}/change-status`, data),
  getLogs: (id: UUID) => api.get<InspectionLog[]>(`/inspections/${id}/logs`).then(unwrap),
};

// ═══════════════════════════════════════════════════════════════
// Reports
// ═══════════════════════════════════════════════════════════════

export const reportsApi = {
  generate: (params: Record<string, string>) =>
    api.get('/reports/generate', { params, responseType: 'blob' }).then((res) => res),
  list: (projectId?: UUID) =>
    api.get<ReportCacheItem[]>('/reports/list', { params: projectId ? { project_id: projectId } : {} }).then(unwrap),
  delete: (id: UUID) => api.delete(`/reports/${id}`),
};

export default api;
