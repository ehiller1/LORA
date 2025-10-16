# RMN LoRA System - Quick Start Guide

## Prerequisites

- Python 3.9+
- 8GB+ RAM (16GB+ recommended)
- GPU with 12GB+ VRAM (for training)
- PostgreSQL (optional, SQLite works for development)

## Installation (5 minutes)

### 1. Clone and Install Dependencies

```bash
cd rmn-lora-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### 2. Initialize Database

```bash
# Using SQLite (development)
python scripts/init_database.py --database-url sqlite:///rmn_system.db --sample-data

# Using PostgreSQL (production)
python scripts/init_database.py \
  --database-url postgresql://user:pass@localhost/rmn_db \
  --sample-data
```

This creates:
- 3 sample retailers (Amazon, Walmart, Target)
- 3 sample brands (ACME Corp, Globex Inc, Initech)
- Database schema for campaigns, SKUs, feedback, etc.

### 3. Configure Environment

```bash
# Copy example config
cp config/config.example.yaml config/config.yaml

# Edit with your settings
nano config/config.yaml
```

**Minimum required settings**:
```yaml
model:
  base_model: "meta-llama/Llama-3.1-8B-Instruct"

database:
  url: "sqlite:///rmn_system.db"

paths:
  data_dir: "./data"
  models_dir: "./models"
```

## Usage Examples

### Example 1: Data Harmonization (2 minutes)

Transform retailer-specific data to RMIS format:

```bash
# Create sample raw data
mkdir -p data/raw

# Harmonize data
python -m src.agents.data_harmonizer \
  --retailer-mapping config/mappings/retailer_ABC.yaml \
  --input data/raw/retailer_ABC_export.parquet \
  --output data/harmonized/retailer_ABC_rmis.parquet
```

**Python API**:
```python
from src.agents.data_harmonizer import DataHarmonizerAgent

agent = DataHarmonizerAgent("config/mappings/retailer_ABC.yaml")
stats = agent.harmonize("data/raw/input.parquet", "data/harmonized/output.parquet")
print(f"Processed {stats['input_rows']} rows")
```

### Example 2: Budget Optimization (1 minute)

Allocate budget across RMNs and placements:

```python
from src.agents.budget_optimizer import BudgetOptimizerAgent

optimizer = BudgetOptimizerAgent(method="convex")

result = optimizer.allocate(
    total_budget=100000,
    priors=[
        {
            "rmn": "amazon",
            "placement_type": "sponsored_product",
            "expected_roas": 3.2,
            "cost_per_unit": 1.5
        },
        {
            "rmn": "walmart",
            "placement_type": "display",
            "expected_roas": 2.8,
            "cost_per_unit": 2.0
        }
    ],
    constraints={
        "min_roas": 2.5,
        "max_cpa": 50.0,
        "reserve_for_experiments": 0.1
    }
)

print(f"Allocations: {result['allocations']}")
print(f"Expected ROAS: {result['expected_total_incremental_roas']}")
```

### Example 3: RLHF Feedback Collection (3 minutes)

Start the web UI for collecting human feedback:

```bash
# Start RLHF UI
python -m src.ui.rlhf_app

# Access at http://localhost:8001
```

**Features**:
1. Select your brand
2. Choose task type (budgeting, creative, measurement, planning)
3. Provide feedback:
   - 👍 👎 Simple thumbs up/down
   - ⭐ 1-5 star ratings
   - 🔄 Preference pairs (for DPO training)
4. View statistics dashboard
5. Export DPO datasets

### Example 4: Reflection & Decision Making (2 minutes)

Use the reflection framework for decision support:

```python
from src.agents.reflection import ReflectionEngine, Phase, BiasType

engine = ReflectionEngine(default_threshold=0.8)

# Create context
context = engine.create_context(
    task_type="budgeting",
    session_id="session_123"
)

# Add alternate perspectives
engine.add_alternate_frame(
    context,
    "Cost vs. benefit analysis"
)

# Assess risks
engine.assess_risk(
    context,
    factor="Market volatility",
    severity="medium",
    probability=0.6,
    impact="Budget efficiency may decrease 10-15%",
    mitigation="Reserve 15% for reallocation"
)

# Check for biases
engine.check_bias(
    context,
    BiasType.AVAILABILITY,
    "Anchoring on recent market fluctuations"
)

# Set confidence
engine.set_confidence(
    context,
    value=0.75,
    rationale="Historical patterns align with current trends",
    supporting=["Q3 data", "Market indicators"],
    contradicting=["Increased competition"]
)

# Check if should proceed
if engine.should_proceed(context):
    print("✅ Confidence threshold met, proceeding with decision")
    
    # Make decision
    engine.make_decision(
        context,
        decision={"allocate": 100000, "strategy": "balanced"},
        rationale="Balanced allocation based on historical performance"
    )
    
    # Save to database
    from src.storage.database import get_db
    db = get_db()
    with db.get_session() as session:
        engine.save_to_database(context, session)
else:
    print("⚠️ Confidence below threshold, need more data")
```

### Example 5: Multi-Tenant Runtime (5 minutes)

Start the inference server with LoRA adapters:

```bash
# Start server
python -m src.runtime.multi_tenant \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --adapters-dir models/adapters \
  --host 0.0.0.0 \
  --port 8000

# Or use Makefile
make serve
```

**Test inference**:
```bash
curl -X POST http://localhost:8000/inference \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: tenant_acme" \
  -d '{
    "messages": [
      {"role": "user", "content": "Allocate $100k across Amazon, Walmart, Target"}
    ],
    "retailer_id": "amazon",
    "brand_id": "acme_corp",
    "task": "budgeting",
    "max_tokens": 500
  }'
```

### Example 6: Train LoRA Adapter (30 minutes)

Train a task-specific LoRA adapter:

```bash
# 1. Create training dataset
python -m src.training.dataset_builder \
  --type synthetic \
  --example-type budgeting \
  --num-examples 1000 \
  --output data/training/budgeting_sft.jsonl

# 2. Train adapter
python -m src.training.train_lora \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --dataset data/training/budgeting_sft.jsonl \
  --adapter-type task \
  --adapter-name budgeting \
  --output-dir models/adapters/task_budgeting \
  --num-epochs 3 \
  --batch-size 4

# 3. Evaluate adapter
python -m src.training.evaluation \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --adapter-path models/adapters/task_budgeting \
  --test-dataset data/training/budgeting_test.jsonl
```

## Common Workflows

### Workflow 1: End-to-End Campaign Planning

```python
from src.agents.planner import PlannerAgent
from src.agents.reflection import ReflectionEngine

# Initialize
planner = PlannerAgent("meta-llama/Llama-3.1-8B-Instruct")
reflection = ReflectionEngine()

# Create reflection context
context = reflection.create_context("planning", "campaign_001")

# Generate plan
plan = planner.plan(
    objective="Launch new product with $200k budget across 3 RMNs",
    context={
        "product": "Organic Snack Bar",
        "target_audience": "health-conscious millennials",
        "launch_date": "2024-Q4"
    },
    constraints={
        "min_roas": 3.0,
        "max_cpa": 40.0
    }
)

# Assess plan confidence
reflection.set_confidence(
    context,
    value=0.85,
    rationale="Strong historical performance for similar products"
)

if reflection.should_proceed(context):
    # Execute plan
    result = planner.execute_tool_call(plan)
    print(f"Plan executed: {result}")
```

### Workflow 2: Collect Feedback & Train DPO

```bash
# 1. Collect feedback via UI
python -m src.ui.rlhf_app
# Users provide preference pairs at http://localhost:8001

# 2. Export DPO dataset
curl http://localhost:8001/feedback/export-dpo?brand_id=acme_corp > dpo_dataset.json

# 3. Train DPO adapter
python -m src.training.train_lora \
  --base-model meta-llama/Llama-3.1-8B-Instruct \
  --dataset dpo_dataset.json \
  --training-type dpo \
  --adapter-name brand_acme_dpo \
  --output-dir models/adapters/brand_acme_dpo
```

### Workflow 3: Data Harmonization Pipeline

```python
from pathlib import Path
from src.agents.data_harmonizer import DataHarmonizerAgent
from src.storage.database import get_db
from src.storage.models import Campaign, PerformanceMetric

# Harmonize data from multiple retailers
retailers = ["amazon", "walmart", "target"]

for retailer in retailers:
    agent = DataHarmonizerAgent(f"config/mappings/{retailer}.yaml")
    
    stats = agent.harmonize(
        input_path=f"data/raw/{retailer}_export.parquet",
        output_path=f"data/harmonized/{retailer}_rmis.parquet"
    )
    
    print(f"{retailer}: {stats['input_rows']} rows processed")

# Load into database
db = get_db()
with db.get_session() as session:
    # Import harmonized data
    import polars as pl
    
    for retailer in retailers:
        df = pl.read_parquet(f"data/harmonized/{retailer}_rmis.parquet")
        
        # Convert to performance metrics
        for row in df.iter_rows(named=True):
            metric = PerformanceMetric(
                campaign_id=row["campaign_id"],
                date=row["date"],
                placement_type=row["placement_type"],
                impressions=row["impressions"],
                clicks=row["clicks"],
                spend=row["cost"]
            )
            session.add(metric)
    
    session.commit()
```

## Troubleshooting

### Issue: Import errors

**Solution**: Ensure you're in the project root and have activated the virtual environment:
```bash
cd rmn-lora-system
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Database connection errors

**Solution**: Check database URL and ensure database exists:
```bash
# For PostgreSQL
createdb rmn_db

# Verify connection
python -c "from src.storage.database import init_db; db = init_db('postgresql://user:pass@localhost/rmn_db'); print('✅ Connected')"
```

### Issue: Out of memory during training

**Solution**: Reduce batch size and enable gradient accumulation:
```bash
python -m src.training.train_lora \
  --batch-size 1 \
  --gradient-accumulation-steps 8 \
  --use-8bit  # Enable 8-bit quantization
```

### Issue: RLHF UI not loading

**Solution**: Check if port 8001 is available and database is initialized:
```bash
# Check port
lsof -i :8001

# Initialize database with sample data
python scripts/init_database.py --sample-data
```

## Next Steps

1. **Configure Retailer Mappings**: Create YAML mappings for your RMNs in `config/mappings/`
2. **Collect Training Data**: Use RLHF UI to gather feedback from domain experts
3. **Train Adapters**: Train retailer, brand, and task-specific LoRA adapters
4. **Deploy Runtime**: Set up multi-tenant runtime with authentication
5. **Monitor Performance**: Set up Prometheus/Grafana for monitoring

## Resources

- **Full Documentation**: `docs/architecture.md`, `docs/quickstart.md`
- **Gap Analysis**: `GAP_ANALYSIS.md`
- **API Reference**: Start server and visit `/docs` endpoint
- **Examples**: `examples/example_workflow.py`
- **Tests**: `tests/` directory

## Support

For issues and questions:
1. Check `GAP_ANALYSIS.md` for known issues
2. Review test files in `tests/` for usage examples
3. Run example workflow: `python examples/example_workflow.py`
