/**
 * 支付 API 前端调用封装
 * 基于 openapi.yaml 生成的类型，零手写
 */
import type { paths } from '../types/api';

type CreatePaymentRequest = paths['/api/pay/create.php']['post']['requestBody']['content']['application/json'];
type CreatePaymentResponse = paths['/api/pay/create.php']['post']['responses']['200']['content']['application/json'];
type QueryPaymentResponse = paths['/api/pay/query.php']['get']['responses']['200']['content']['application/json'];
type RefundRequest = paths['/api/pay/refund.php']['post']['requestBody']['content']['application/json'];

const API_BASE = import.meta.env.VITE_API_BASE || '/api';

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('sti_auth');
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  return fetch(url, { ...options, headers, credentials: 'include' });
}

export const paymentsApi = {
  /** 创建支付订单 */
  async create(data: CreatePaymentRequest): Promise<CreatePaymentResponse> {
    const res = await fetchWithAuth(`${API_BASE}/pay/create.php`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  /** 查询订单状态 */
  async query(orderId: string): Promise<QueryPaymentResponse> {
    const res = await fetchWithAuth(`${API_BASE}/pay/query.php?orderId=${orderId}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  /** 申请退款 */
  async refund(data: RefundRequest): Promise<{ success: boolean }> {
    const res = await fetchWithAuth(`${API_BASE}/pay/refund.php`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
};
