export type ArtifactType =
  | 'image'
  | 'video'
  | 'music'
  | 'template'
  | 'chart'
  | 'lead'
  | 'web_browse'
  | 'system'
  | 'text';

export interface Artifact {
  id: string;
  artifactType: ArtifactType;
  title: string;
  content: Record<string, unknown>;
  storageUrl?: string;
  jobId?: string;
  createdAt: string;
}

export interface ArtifactCreate {
  artifactType: ArtifactType;
  title: string;
  content: Record<string, unknown>;
  storageUrl?: string;
  jobId?: string;
}
