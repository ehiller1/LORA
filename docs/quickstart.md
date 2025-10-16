# Quick Start Guide

## Installation

### Prerequisites

- Python 3.10+
- CUDA 11.8+ (for GPU support)
- 16GB+ RAM (32GB+ recommended for training)

### Install Dependencies

```bash
cd rmn-lora-system
pip install -r requirements.txt
```

### Configuration

```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your settings
```

## Basic Usage

### 1. Data Harmonization

Harmonize retailer data to RMIS format:

```bash
python -m src.agents.data_harmonizer \
  --retailer-mapping config/mappings/retailer_ABC.yaml \
  --input data/raw/retailer_ABC_export.parquet \
  --output data/harmonized/rmis_events.parquet
```

### 2. Budget Optimization

Optimize budget allocation:

```bash
# Create input file
cat > budget_input.json << EOF
{
  "total_budget": 2500000,
  "hierarchy": ["rmn", "placement", "audience"],
  "priors": [
    {
      "rmn": "retailer_A",
      "placement_type": "sponsored_product",
      "expected_incremental_roas": 3.2,
      "margin_pct": 0.25,
      "oos_probability": 0.05
    }
  ],
  "constraints": {
    "min_roas": 3.0,
    "reserve_for_experiments": 0.1
  },
  "objective": "maximize_incremental_margin"
}
EOF

# Run optimization
python -m src.agents.budget_optimizer \
  --method convex \
  --input budget_input.json \
  --output budget_output.json
```

### 3. Experiment Design

Design a lift experiment:

```bash
cat > experiment_input.json << EOF
{
  "goal": "incremental_revenue",
  "units": "geo",
  "power": 0.8,
  "min_detectable_effect": 0.10,
  "duration_weeks": 4,
  "covariates": ["store_size", "historical_sales"]
}
EOF

python -m src.agents.measurement design \
  --input experiment_input.json \
  --output experiment_design.json
```

### 4. Creative Generation

Generate compliant creative copy:

```bash
cat > creative_input.json << EOF
{
  "sku_id": "SKU12345",
  "attributes": {
    "name": "Premium Organic Coffee",
    "size": "12 oz",
    "benefits": ["100% Organic", "Fair Trade", "Rich Flavor"]
  },
  "retailer_specs": {
    "max_headline_length": 50,
    "max_body_length": 200,
    "disallowed_terms": ["guaranteed", "miracle"],
    "required_disclaimers": ["*Terms apply"],
    "placement_type": "sponsored_product"
  },
  "brand_tone": "Premium, authentic, environmentally conscious",
  "num_variants": 5
}
EOF

python -m src.agents.creative \
  --input creative_input.json \
  --output creative_output.json
```

### 5. Governance Checks

Check for PII and policy compliance:

```bash
# Check text for PII
python -m src.agents.governance check-pii \
  --text "Contact us at john.doe@example.com"

# Check creative compliance
cat > creative_check.json << EOF
{
  "creative_text": "Premium Coffee - Best Quality! *Terms apply",
  "disallowed_terms": ["guaranteed", "miracle"],
  "required_disclaimers": ["*Terms apply"],
  "placement_type": "sponsored_product"
}
EOF

python -m src.agents.governance check-creative \
  --input creative_check.json
```

## Training LoRA Adapters

### 1. Build Training Dataset

```bash
# Create synthetic dataset
python -m src.training.dataset_builder \
  --type synthetic \
  --example-type budgeting \
  --num-examples 1000 \
  --output data/training/budgeting_sft.jsonl
```

### 2. Train Adapter

```bash
python -m src.training.train_lora \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --dataset data/training/budgeting_sft.jsonl \
  --adapter-type task \
  --adapter-name budgeting \
  --output-dir models/adapters \
  --epochs 3 \
  --batch-size 4 \
  --learning-rate 2e-4
```

### 3. Evaluate Adapter

```bash
python -m src.training.evaluation \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --adapter models/adapters/task_budgeting \
  --test-dataset data/training/budgeting_test.jsonl \
  --output evaluation_results.json
```

## Multi-Tenant Runtime

### 1. Register Adapters

```bash
python -m src.runtime.adapter_manager \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --adapters-dir models/adapters \
  register \
  --path models/adapters/retailer_ABC \
  --type retailer \
  --name ABC \
  --tags retailer_ABC rmn_a
```

### 2. Start Runtime Server

```bash
python -m src.runtime.multi_tenant \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --adapters-dir models/adapters \
  --host 0.0.0.0 \
  --port 8000
```

### 3. Make Inference Request

```bash
curl -X POST http://localhost:8000/inference \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: tenant_example" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a budget optimization expert."},
      {"role": "user", "content": "Allocate $2M to maximize incremental margin with ROAS >= 3"}
    ],
    "retailer_id": "retailer_ABC",
    "task": "budgeting",
    "max_tokens": 1024,
    "temperature": 0.7
  }'
```

## Example Workflow

Run the complete example workflow:

```bash
python examples/example_workflow.py
```

This demonstrates:
- Data harmonization
- Budget optimization
- Experiment design
- Creative generation
- Governance checks
- Training dataset creation
- Planning workflow

## Next Steps

1. **Prepare Your Data**:
   - Create retailer mapping files for your RMNs
   - Export historical campaign data
   - Prepare product catalog and audience definitions

2. **Build Training Datasets**:
   - Collect schema mapping examples
   - Document policy Q&A
   - Capture tool usage patterns
   - Create preference pairs for DPO

3. **Train Adapters**:
   - Start with retailer adapters (schema mapping)
   - Add brand adapters (tone/compliance)
   - Train task adapters (budgeting, measurement, creative)

4. **Deploy Runtime**:
   - Configure multi-tenant settings
   - Set up monitoring and logging
   - Implement rate limiting and authentication
   - Connect to optimization services

5. **Integrate Services**:
   - Connect clean room endpoints
   - Integrate causal inference services
   - Set up experiment tracking
   - Configure monitoring dashboards

## Troubleshooting

### Out of Memory

If you encounter OOM errors during training:

```bash
# Reduce batch size
--batch-size 2

# Increase gradient accumulation
--gradient-accumulation-steps 8

# Use smaller LoRA rank
--lora-r 8
```

### Slow Inference

For faster inference:

```bash
# Use vLLM for serving
pip install vllm

# Or use 8-bit quantization
# Set in config.yaml:
# lora.use_4bit: false
# model.load_in_8bit: true
```

### Adapter Not Found

Ensure adapters are registered:

```bash
python -m src.runtime.adapter_manager \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --adapters-dir models/adapters \
  list
```

## Resources

- [Architecture Documentation](architecture.md)
- [RMIS Schema Reference](rmis_schema.md)
- [Training Guide](training_guide.md)
- [API Documentation](api_reference.md)
- [Evaluation Metrics](evaluation.md)

## Support

For issues and questions:
- GitHub Issues: [link]
- Documentation: [link]
- Community: [link]
