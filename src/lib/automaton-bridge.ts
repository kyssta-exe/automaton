export type BridgeStatus = {
  configured: boolean
  reachable: boolean
  url: string | null
}

export type CommandRequest = {
  instruction: string
  projectId?: string
}

export type CommandReceipt = {
  commandId: string
  status: 'queued' | 'running' | 'failed'
}

const baseUrl = (import.meta.env.VITE_AUTOMATON_API_URL as string | undefined)?.replace(/\/$/, '') ?? ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (!baseUrl) throw new Error('VITE_AUTOMATON_API_URL is not configured')
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } })
  if (!response.ok) throw new Error(`Automaton API ${response.status}: ${await response.text()}`)
  return response.json() as Promise<T>
}

export const automatonBridge = {
  status(): BridgeStatus { return { configured: Boolean(baseUrl), reachable: false, url: baseUrl || null } },
  async health(): Promise<BridgeStatus> {
    if (!baseUrl) return this.status()
    try { await request<{ ok: boolean }>('/api/health'); return { configured: true, reachable: true, url: baseUrl } }
    catch { return { configured: true, reachable: false, url: baseUrl } }
  },
  listProjects<T = unknown>() { return request<T[]>('/api/projects') },
  listFootage<T = unknown>() { return request<T[]>('/api/footage') },
  listJobs<T = unknown>() { return request<T[]>('/api/jobs') },
  listCommands<T = unknown>() { return request<T[]>('/api/commands') },
  sendCommand(input: CommandRequest) { return request<CommandReceipt>('/api/commands', { method: 'POST', body: JSON.stringify(input) }) },
}
