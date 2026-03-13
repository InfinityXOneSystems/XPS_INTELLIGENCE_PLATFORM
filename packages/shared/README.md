# Shared Utilities — XPS Intelligence Platform

> **Status:** ⬜ Pending Phase 1 setup

## Overview

Cross-package shared utilities, TypeScript types, and constants used by both the backend (via Python equivalents) and frontend.

## Directory Structure (Target)

```
packages/shared/
├── src/
│   ├── types/        ← Shared TypeScript types / Python dataclasses
│   ├── utils/        ← Shared utility functions
│   └── constants/    ← Shared constants (API paths, config keys, etc.)
├── package.json
└── tsconfig.json
```

## Usage

Before writing any new utility, **always check this package first** to avoid duplication.

```typescript
// Import from shared package
import { AgentStatus, ApiEndpoints } from '@xps/shared';
```

## Human Gate

This package will be populated during **Phase 1** alongside backend/frontend consolidation.
