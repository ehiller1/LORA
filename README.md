# Retail Media Network LoRA Optimization System

A complete generative AI + LoRA adapter system for optimizing Retail Media Network (RMN) spend and ROI.

## Overview

This system uses a base LLM with composable LoRA adapters to:
- **Harmonize** fragmented RMN data across multiple retailers
- **Optimize** budget allocation using causal inference and contextual bandits
- **Measure** incremental lift through experiment design
- **Generate** compliant creative copy
- **Enforce** privacy and policy guardrails

## Architecture

```
Data Sources → Harmonization Layer → Optimization Services → Generative AI Layer → Agentic Apps
```

### Components

1. **RMIS (Retail Media Interop Schema)**: Canonical data model
2. **Data Harmonizer Agent**: Maps retailer schemas → RMIS
3. **Planner Agent**: Orchestrates planning and tool calls
4. **Budget Optimizer Agent**: Allocates spend via contextual bandits
5. **Measurement Agent**: Designs and analyzes lift experiments
6. **Creative Agent**: Generates policy-compliant copy
7. **Governance Agent**: Enforces PII/policy guardrails
8. **LoRA Training Infrastructure**: SFT/DPO/QLoRA pipelines
9. **Multi-Tenant Runtime**: Adapter composition and isolation

## ✨ What's New

### Complete Production System
- ✅ **Data Storage Layer**: Full database models for campaigns, SKUs, feedback, and more
- ✅ **RLHF UI**: Web interface for non-technical users to provide feedback
- ✅ **Reflection Framework**: Decision support with confidence scoring, risk assessment, and bias detection
- ✅ **Real Integrations**: All mock implementations replaced with actual agent calls
- ✅ **Setup Scripts**: Automated database initialization and sample data creation

### Key Features
- 🎯 **6 Production Agents**: Data harmonizer, planner, budget optimizer, measurement, creative, governance
- 🗄️ **Complete Storage**: PostgreSQL/MySQL/SQLite support with SQLAlchemy ORM
- 🎨 **RLHF Interface**: Collect thumbs up/down, ratings, and preference pairs for DPO training
- 🧠 **Decision Support**: Confidence scoring, risk assessment, bias detection, alternate framing
- 🔌 **Real APIs**: HTTP client for clean room queries, direct agent integrations
- 📊 **Analytics Dashboard**: View feedback statistics and export DPO datasets

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your settings
```

### Run Data Harmonization

```bash
python -m src.agents.data_harmonizer \
  --retailer-mapping config/mappings/retailer_ABC.yaml \
  --input data/raw/retailer_ABC_export.parquet \
  --output data/harmonized/rmis_events.parquet
```

### Run Planner Agent

```bash
python -m src.agents.planner \
  --objective "Allocate $2.5M to maximize incremental margin with ROAS >= 3" \
  --adapters retailer_ABC,brand_XYZ,task_budgeting
```

### Train LoRA Adapters

```bash
python -m src.training.train_lora \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --adapter-type retailer \
  --dataset data/training/retailer_ABC_sft.jsonl \
  --output models/adapters/retailer_ABC
```

## Project Structure

```
rmn-lora-system/
├── config/                    # Configuration files
│   ├── mappings/             # Retailer → RMIS mappings
│   └── policies/             # Retailer policies and specs
├── data/                      # Data storage
│   ├── raw/                  # Raw retailer exports
│   ├── harmonized/           # RMIS-normalized data
│   └── training/             # Training datasets
├── models/                    # Model artifacts
│   ├── base/                 # Base LLM
│   └── adapters/             # LoRA adapters
├── src/                       # Source code
│   ├── agents/               # Agent implementations
│   ├── schemas/              # RMIS and tool schemas
│   ├── services/             # Optimization services
│   ├── training/             # LoRA training infrastructure
│   ├── runtime/              # Multi-tenant runtime
│   └── evaluation/           # Evaluation harness
├── tests/                     # Test suite
└── docs/                      # Documentation
```

## Key Features

### LoRA Adapter Strategy

- **Retailer Adapters**: Schema mapping, policy quirks, API templates
- **Brand Adapters**: Tone, compliance, SKU phrasing
- **Task Adapters**: Harmonization, measurement, budgeting, creative

### Optimization Stack

- **Causal Inference**: Uplift models (T/X/DR-learners)
- **Contextual Bandits**: Budget allocation with constraints
- **Experiment Design**: Geo tests, switchbacks
- **Forecasting**: Stock, price elasticity

### Privacy & Governance

- Clean-room only data access
- Differential privacy / k-anonymity
- Per-tenant adapter isolation
- Policy verification

## Documentation

- [RMIS Schema Reference](docs/rmis_schema.md)
- [Agent API Documentation](docs/agents.md)
- [LoRA Training Guide](docs/lora_training.md)
- [Retailer Mapping Guide](docs/mapping_guide.md)
- [Evaluation Metrics](docs/evaluation.md)

## License

MIT License
