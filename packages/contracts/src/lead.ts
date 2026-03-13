export interface LeadRaw {
  id: string;
  sourceUrl: string;
  rawData: Record<string, unknown>;
  status: 'raw' | 'normalized' | 'scored' | 'invalid';
  idempotencyKey: string;
  createdAt: string;
}

export interface LeadNormalized extends LeadRaw {
  normalizedData: {
    name?: string;
    email?: string;
    phone?: string;
    company?: string;
    website?: string;
  };
}

export interface LeadScored extends LeadNormalized {
  score: number;
}
