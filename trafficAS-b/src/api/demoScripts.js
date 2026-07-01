import { apiClient } from './client'

const BASE = '/api/demo/scripts'

export function runDemoScript(scriptId, { dataSource = 'REAL' } = {}) {
  return apiClient
    .post(`${BASE}/${scriptId}/run`, { dataSource }, { timeout: 120000 })
    .then((response) => response.data?.data)
}
