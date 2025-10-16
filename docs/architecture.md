# RMN LoRA System Architecture

## Overview

The Retail Media Network (RMN) LoRA system uses generative AI with Low-Rank Adaptation (LoRA) to optimize media spend and ROI across fragmented retail media networks.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Data Sources                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ RMN Logs │  │  Clean   │  │ Product  │  │  Sales   │           │
│  │          │  │  Rooms   │  │   Data   │  │   Data   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Harmonization Layer (RMIS)                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Data Harmonizer Agent                                        │  │
│  │  • Schema mapping (retailer → RMIS)                          │  │
│  │  • Tagging normalization                                     │  │
│  │  • Crosswalk resolution                                      │  │
│  │  • Anomaly detection                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Optimization Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Causal     │  │  Contextual  │  │  Forecasting │             │
│  │   Inference  │  │   Bandits    │  │   Services   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Generative AI Layer (Base LLM + LoRA)                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Base Model: Llama 3.1 8B (or similar)                       │  │
│  │  • Tool-calling capable                                       │  │
│  │  • Long context (8K+ tokens)                                 │  │
│  │  • Code/SQL generation                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Retailer    │  │    Brand     │  │     Task     │             │
│  │  Adapters    │  │   Adapters   │  │   Adapters   │             │
│  │              │  │              │  │              │             │
│  │ • Schema map │  │ • Tone/voice │  │ • Budgeting  │             │
│  │ • Policies   │  │ • Compliance │  │ • Measurement│             │
│  │ • API syntax │  │ • SKU phrases│  │ • Creative   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  RAG: Retailer policies, playbooks, specs                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Agentic Applications                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Planner  │  │  Budget  │  │Measurement│ │ Creative │           │
│  │  Agent   │  │Optimizer │  │   Agent   │ │  Agent   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                       │
│  ┌──────────┐  ┌──────────┐                                         │
│  │Governance│  │   Ops    │                                         │
│  │  Agent   │  │  Agent   │                                         │
│  └──────────┘  └──────────┘                                         │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. RMIS (Retail Media Interop Schema)

Canonical schema for normalizing data across retailers:

- **RMISEvent**: Impressions, clicks, conversions with standardized fields
- **RMISSKUDimension**: Product catalog with attributes and economics
- **RMISAudienceDimension**: Audience segments and behavioral data
- **RMISPolicyDimension**: Retailer policies, specs, and constraints

### 2. Data Harmonization Layer

**Data Harmonizer Agent** maps retailer-specific schemas to RMIS:

- Field-level mapping with transformations
- Tagging normalization for inconsistent placement types
- SKU crosswalks (UPC/EAN/GTIN)
- Attribution model normalization
- Validation and anomaly detection

### 3. Optimization Services

**Budget Optimizer Agent**:
- Contextual bandits with Thompson Sampling
- Convex optimization with constraints (ROAS, CPA, OOS)
- Hierarchical allocation (channel → RMN → placement → audience → SKU)

**Measurement Agent**:
- Experiment design (geo tests, switchbacks)
- Power analysis and sample size calculation
- Lift analysis with confidence intervals

### 4. Generative AI Layer

**Base Model + LoRA Adapters**:

- **Retailer Adapters**: Schema mappings, policy quirks, API templates
- **Brand Adapters**: Tone/voice, compliance constraints, SKU phrasing
- **Task Adapters**: Harmonization, budgeting, measurement, creative

**Adapter Composition**:
- Router selects retailer + brand + task adapters per request
- Sequential or additive composition
- Tenant isolation for multi-tenant deployments

### 5. Agentic Applications

**Planner Agent**:
- Orchestrates planning workflow
- Calls tools (query_clean_room, allocate_budget, design_experiment)
- Provides explainable rationale

**Creative Agent**:
- Generates policy-compliant copy variants
- Checks against retailer specs and disallowed terms
- Enforces brand tone and required disclaimers

**Governance Agent**:
- PII detection and redaction
- Policy compliance checking
- K-anonymity enforcement
- Differential privacy (optional)

### 6. Multi-Tenant Runtime

**Adapter Manager**:
- Discovers and loads LoRA adapters
- Manages adapter composition
- Caches loaded adapters

**Multi-Tenant Runtime**:
- Per-tenant adapter access control
- Rate limiting
- Request isolation
- FastAPI-based REST API

## Data Flow

### Example: Budget Allocation Workflow

1. **User Request**: "Allocate $2.5M to maximize incremental margin with ROAS ≥ 3"

2. **Planner Agent**:
   - Loads retailer + brand + task adapters
   - Parses objective and constraints
   - Generates tool calls

3. **Query Clean Room**:
   - Fetches aggregated performance data (RMIS format)
   - Applies k-anonymity and privacy thresholds
   - Returns uplift metrics by placement/audience/SKU

4. **Budget Optimizer**:
   - Receives priors (expected ROAS, margin, OOS probability)
   - Applies constraints (min ROAS, experiment reserve, OOS threshold)
   - Solves convex optimization problem
   - Returns allocations with rationale

5. **Response**:
   - Structured allocation plan
   - Expected incremental ROAS and margin
   - Monitoring plan (pacing, re-optimization cadence)

## LoRA Training Strategy

### Adapter Types

**Retailer Adapters**:
- **Training data**: Schema mapping examples, policy Q&A, API templates
- **Objective**: Map native RMN data → RMIS, enforce retailer policies

**Brand Adapters**:
- **Training data**: Brand voice examples, product descriptions, compliance cases
- **Objective**: Generate on-brand copy, enforce regulated claims

**Task Adapters**:
- **Training data**: Tool usage examples, reasoning chains, solver orchestration
- **Objective**: Reliable function calling, constraint satisfaction

### Training Recipe

1. **SFT (Supervised Fine-Tuning)**:
   - Curated transcripts: objectives → plans → tool calls → results
   - Policy-aware responses with refusal patterns
   - Toolformer-style augmentation (real tool I/O)

2. **DPO (Direct Preference Optimization)**:
   - Good vs bad planning examples
   - Incremental optimization vs last-click
   - Constraint satisfaction vs violations

3. **QLoRA Settings**:
   - r=16, α=32, dropout=0.05
   - 4-bit quantization for training and serving
   - Target modules: attention + MLP projections

## Privacy & Governance

### Data Access

- **Clean rooms only**: No raw user-level data extraction
- **Aggregation required**: All queries must use GROUP BY or aggregation functions
- **K-anonymity**: Minimum cell size (default 50)
- **Differential privacy**: Optional Laplace noise for sensitive metrics

### PII Protection

- Regex-based detection (email, phone, SSN, credit card)
- Automatic redaction in outputs
- Hashed identifiers for cross-system joins

### Policy Enforcement

- Disallowed terms checking
- Required disclaimers validation
- Creative specs compliance (length, format)
- Query allow-lists for data access

## Deployment Models

### Manufacturer-Side (Multi-RMN Copilot)

- Host base model + retailer/brand adapters
- RAG over retailer policies and internal playbooks
- Data stays in manufacturer's control
- Clean-room connectors for RMN joins

### Retailer-Side (Agent Leasing)

- Retailer hosts base model + retailer adapter
- Per-manufacturer brand adapters loaded into isolated runtimes
- Manufacturers "lease" agents within retailer enclave
- No raw data extraction, only aggregated outputs
- Performance-linked pricing model

## Technology Stack

- **ML Framework**: PyTorch, Transformers, PEFT, bitsandbytes
- **Data Processing**: Polars, Pandas, DuckDB
- **Optimization**: CVXPY, scikit-learn, econML
- **API**: FastAPI, Uvicorn
- **Monitoring**: Prometheus, OpenTelemetry
- **Storage**: PostgreSQL, Redis, ChromaDB (vector store)

## Scalability Considerations

- **Model Serving**: vLLM or TGI for efficient inference
- **Adapter Loading**: Dynamic loading/unloading based on request patterns
- **Distributed Training**: DeepSpeed or FSDP for large-scale adapter training
- **Caching**: Redis for adapter metadata and request results
- **Load Balancing**: Multiple runtime instances behind load balancer

## Security

- **Tenant Isolation**: Separate adapter namespaces, signed artifacts
- **API Authentication**: JWT tokens, API keys
- **Encryption**: TLS for API, encrypted storage for adapters
- **Audit Logging**: All requests, tool calls, and data access logged
- **TEE (Trusted Execution Environments)**: Optional for clean-room joins
