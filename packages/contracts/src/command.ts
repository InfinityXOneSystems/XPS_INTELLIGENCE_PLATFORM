import { Artifact } from './artifact';

export type CommandType =
  | 'scrape'
  | 'ingest'
  | 'normalize'
  | 'score'
  | 'generate'
  | 'analyze'
  | 'browse'
  | 'create_system';

export interface Command {
  id: string;
  type: CommandType;
  payload: Record<string, unknown>;
  idempotencyKey: string;
  createdAt: string;
}

export interface CommandResult {
  commandId: string;
  status: 'pending' | 'running' | 'done' | 'failed';
  result?: Record<string, unknown>;
  error?: string;
  artifacts: Artifact[];
}
