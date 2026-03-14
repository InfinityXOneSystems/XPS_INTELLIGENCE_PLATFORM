export interface ScrapeJob {
  id: string;
  targetUrl: string;
  status: 'pending' | 'running' | 'done' | 'failed';
  idempotencyKey: string;
  resultCount: number;
  error?: string;
  scheduled: boolean;
  createdAt: string;
  updatedAt: string;
}
