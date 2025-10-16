# RMN LoRA Admin Console - User Guide

## Overview

Professional admin interface for managing LoRA training, adapter federation, and dataset operations.

## Quick Start

```bash
# Launch admin console
streamlit run src/ui/lora_admin.py
```

**Opens**: http://localhost:8501

## Features

### 1. 🚀 Training Management

**Purpose**: Train new LoRA adapters with full configuration control

**Workflow**:
1. Select adapter type (Retailer/Task/Domain)
2. Name your adapter (e.g., `amazon_schema_v2`)
3. Choose base model (Llama-3.1-8B or Mistral-7B)
4. Select training type (SFT/DPO/QLoRA)
5. Specify dataset path
6. Configure hyperparameters (rank, alpha, batch size, learning rate)
7. Click "Start Training"
8. Monitor progress in real-time
9. On completion, adapter appears in registry

**Key Features**:
- ✅ Real-time progress tracking with loss curves
- ✅ Advanced hyperparameter tuning
- ✅ Job queue management
- ✅ Automatic adapter registration on completion
- ✅ Training history with metrics

**Example Configuration**:
```yaml
Adapter Type: Retailer
Name: amazon_schema_v2
Base Model: meta-llama/Llama-3.1-8B-Instruct
Training Type: SFT
Dataset: datasets/sft/retailer_amazon.jsonl
Epochs: 3
LoRA Rank: 16
LoRA Alpha: 32
Batch Size: 4
Learning Rate: 0.0002
Quantization: 4-bit
```

### 2. 🔗 Federation & Composition

**Purpose**: Compose multiple LoRA adapters with base model

**Workflow**:
1. Select base model
2. Choose retailer adapter (optional)
3. Choose task adapter (optional)
4. Select composition method:
   - **Additive**: Sum adapter weights
   - **Gated**: Learned routing between adapters
   - **Sequential**: Chain adapters in sequence
5. Click "Create Federation"
6. View visual composition stack
7. Test with sample prompts
8. Monitor latency and accuracy
9. Save federation config

**Visual Stack Example**:
```
┌─────────────────────────────┐
│ Base: Llama-3.1-8B-Instruct │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│ Retailer: amazon_schema_v1  │
│ (~15MB, rank=16)            │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│ Task: planning_v1           │
│ (~12MB, rank=16)            │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│ Federated Model (Ready)     │
└─────────────────────────────┘
```

**Testing**:
- Enter test prompt
- Click "Run Inference"
- View response, token count, latency
- See which adapters were used

**Metrics Tracked**:
- Total model size (base + adapters)
- Adapter overhead
- Inference latency
- Tokens generated
- Adapters activated

### 3. 📊 Datasets & Mappings

**Purpose**: Manage training datasets and schema mappings

#### 3.1 Dataset Library

**Features**:
- View all training datasets with metadata
- Quality scores (0-100%)
- Example counts
- File sizes
- Dataset types (SFT/DPO)

**Actions**:
- ➕ Upload new dataset
- 🔍 Validate dataset quality
- 📥 Export to different formats
- 🗑️ Delete dataset

**Quality Metrics**:
- **95-100%**: Excellent - Ready for production training
- **90-94%**: Good - Minor issues, safe to use
- **85-89%**: Fair - Review issues before training
- **<85%**: Poor - Needs cleanup

#### 3.2 Schema Mappings

**Features**:
- View retailer-to-RMIS mappings
- Field coverage percentages
- Mapping versions
- Status (Active/Draft)

**Mapping Details**:
- Source field → Target field
- Transformation rules
- Validation status
- Coverage metrics

**Example Mapping**:
```yaml
Source Field: adType
Target Field: placement_type
Transform: enum_map
  sp → sponsored_product
  sd → sponsored_display
  onsite_disp → onsite_display
Status: ✅ Active
```

#### 3.3 Data Browser

**Features**:
- Browse raw retailer data
- Apply filters (date, retailer, type)
- Preview data before harmonization
- Export filtered results

**Data Sources**:
- Retailer Alpha Events (CSV)
- Retailer Beta Events (JSONL)
- SKU Catalog
- Uplift Priors
- Performance Metrics

### 4. 📈 Analytics & Monitoring

**Purpose**: Monitor training progress and system health

**Metrics**:
- **GPU Utilization**: Current GPU usage %
- **Memory**: Used/Total VRAM
- **Throughput**: Tokens per second
- **Active Jobs**: Currently training

**Visualizations**:
- **Loss Curves**: Training loss over time
- **Adapter Performance**: Accuracy and latency by adapter
- **System Health**: Resource utilization trends

**Performance Benchmarks**:
- Training throughput: 10-20 req/sec (single GPU)
- Inference latency: 100-200ms (8B model)
- Memory overhead per adapter: 10-20MB
- GPU utilization target: 80-90%

## UI Design Principles

### Professional Business Layout

**Color Palette**:
- Primary: #3b82f6 (Blue) - Actions, selected states
- Success: #10b981 (Green) - Completed, active
- Warning: #f59e0b (Amber) - In progress, attention
- Error: #ef4444 (Red) - Failed, errors
- Neutral: #1f2937 (Dark Gray) - Sidebar, headers
- Background: #f8f9fa (Light Gray) - Main area

**Typography**:
- Headers: Bold, hierarchical (H1 > H2 > H3)
- Body: Regular weight, readable size
- Metrics: Large, bold numbers
- Code: Monospace for technical details

**Spacing**:
- 8px grid system
- Consistent padding and margins
- White space for clarity

**Components**:
- Cards with subtle shadows
- Rounded corners (6-8px)
- Progress bars for status
- Expandable sections for details

### Information Hierarchy

```
Level 1: Page Title (H1)
  Level 2: Section Headers (H2)
    Level 3: Subsections (H3)
      Level 4: Metrics and Details
        Level 5: Fine print and metadata
```

### Interaction Patterns

**Forms**:
- Clear labels above inputs
- Placeholder text for examples
- Validation on submit
- Success/error feedback

**Tables**:
- Sortable columns
- Progress bars for percentages
- Status badges (✅ ⚠️ ❌)
- Hover effects for rows

**Buttons**:
- Primary: Solid blue for main actions
- Secondary: Outlined for alternatives
- Danger: Red for destructive actions
- Icon + text for clarity

**Feedback**:
- Success: Green banner with checkmark
- Error: Red banner with X
- Info: Blue banner with i
- Warning: Amber banner with !

## Integration with Main Demo

The admin console complements the main demo:

**Main Demo** (`demo/streamlit_app.py`):
- End-user facing
- Campaign planning and optimization
- Data harmonization
- Creative generation
- Measurement design

**Admin Console** (`src/ui/lora_admin.py`):
- Admin/developer facing
- Train new adapters
- Compose federations
- Manage datasets
- Monitor system health

**Workflow**:
1. Use **Admin Console** to train retailer adapters
2. Use **Admin Console** to compose federation
3. Use **Main Demo** to run campaigns with trained adapters
4. Use **Admin Console** to monitor performance
5. Use **Admin Console** to retrain with new data

## Advanced Features

### 1. Batch Training

Train multiple adapters in sequence:

```python
# In training form, add multiple jobs
jobs = [
    {'name': 'amazon_v2', 'dataset': 'datasets/amazon.jsonl'},
    {'name': 'walmart_v2', 'dataset': 'datasets/walmart.jsonl'},
    {'name': 'target_v2', 'dataset': 'datasets/target.jsonl'}
]

for job in jobs:
    submit_training_job(job)
```

### 2. Federation A/B Testing

Compare two federations:

```python
# Federation A: Base + Amazon + Planning
fed_a = compose_federation(
    base='llama-3.1-8b',
    retailer='amazon_v1',
    task='planning_v1'
)

# Federation B: Base + Amazon + Creative
fed_b = compose_federation(
    base='llama-3.1-8b',
    retailer='amazon_v1',
    task='creative_v1'
)

# Run same prompt on both
results_a = fed_a.infer(prompt)
results_b = fed_b.infer(prompt)

# Compare accuracy, latency
```

### 3. Dataset Validation

Automated quality checks:

```python
validation_results = validate_dataset('datasets/amazon.jsonl')

# Checks:
# - JSON format validity
# - Required fields present
# - Field types correct
# - No duplicate examples
# - Balanced distribution
# - No PII leakage

if validation_results['quality_score'] >= 90:
    approve_for_training()
```

### 4. Mapping Editor

Visual schema mapping tool:

```
Source (Retailer)     Transform        Target (RMIS)
┌─────────────────┐                   ┌─────────────────┐
│ adType          │ ─── enum_map ───> │ placement_type  │
│ cost_micros     │ ─── /1000000 ───> │ cost            │
│ timestamp       │ ─── to_utc   ───> │ ts              │
│ conv_click_7d   │ ─── none     ───> │ conversions     │
└─────────────────┘                   └─────────────────┘
```

## Troubleshooting

### Training Job Stuck

**Symptoms**: Progress bar not moving, no loss updates

**Solutions**:
1. Check GPU availability: `nvidia-smi`
2. Review job logs in expander
3. Verify dataset path exists
4. Check memory usage (may be OOM)
5. Restart training with smaller batch size

### Federation Not Loading

**Symptoms**: "No active federation" message

**Solutions**:
1. Ensure at least one adapter selected
2. Check adapter registry has adapters
3. Verify base model is available
4. Clear session state and retry

### Dataset Upload Failing

**Symptoms**: Upload button does nothing

**Solutions**:
1. Check file format (must be JSONL for SFT/DPO)
2. Verify file size (<100MB for demo)
3. Validate JSON structure
4. Check file permissions

### Slow Inference

**Symptoms**: Test inference takes >5 seconds

**Solutions**:
1. Check GPU utilization
2. Reduce batch size
3. Use quantization (4-bit/8-bit)
4. Clear model cache
5. Restart Streamlit app

## Best Practices

### Training

1. **Start small**: Train on 1K examples first, validate, then scale
2. **Monitor loss**: Should decrease smoothly, plateau indicates convergence
3. **Use validation set**: Hold out 10-20% for evaluation
4. **Experiment with hyperparameters**: Try different ranks, alphas, learning rates
5. **Save checkpoints**: Enable checkpoint saving every N steps

### Federation

1. **Test incrementally**: Add one adapter at a time
2. **Measure overhead**: Track latency increase per adapter
3. **Use gating for multiple adapters**: Better than simple addition
4. **Cache federations**: Save successful compositions
5. **Version control**: Track which adapters work well together

### Datasets

1. **Validate before training**: Run quality checks
2. **Balance distribution**: Ensure diverse examples
3. **Remove PII**: Scan for sensitive data
4. **Version datasets**: Track changes over time
5. **Document transformations**: Record all preprocessing steps

### Monitoring

1. **Set alerts**: GPU >95%, memory >90%, loss plateau
2. **Track trends**: Compare adapter performance over time
3. **Log all changes**: Audit trail for debugging
4. **Regular backups**: Save trained adapters
5. **Performance baselines**: Establish expected metrics

## API Integration

The admin console can be integrated with the main system:

```python
from src.ui.lora_admin import (
    submit_training_job,
    compose_federation,
    validate_dataset
)

# Submit training job programmatically
job_id = submit_training_job(
    adapter_type='retailer',
    adapter_name='amazon_v3',
    dataset_path='datasets/amazon_v3.jsonl',
    config={
        'lora_r': 16,
        'lora_alpha': 32,
        'batch_size': 4,
        'learning_rate': 0.0002
    }
)

# Monitor job status
status = get_job_status(job_id)

# On completion, create federation
if status == 'completed':
    federation = compose_federation(
        base_model='llama-3.1-8b',
        retailer_adapter='amazon_v3',
        task_adapter='planning_v1',
        method='gated'
    )
    
    # Test federation
    result = test_federation(federation, test_prompt)
```

## Future Enhancements

### Phase 1 (Current)
- ✅ Training job management
- ✅ Federation composition
- ✅ Dataset library
- ✅ Basic monitoring

### Phase 2 (Next)
- [ ] Real-time WebSocket updates
- [ ] Distributed training support
- [ ] Advanced mapping editor
- [ ] A/B testing framework

### Phase 3 (Future)
- [ ] AutoML for hyperparameter tuning
- [ ] Federated learning across retailers
- [ ] Continuous training pipeline
- [ ] Production deployment automation

---

**Status**: ✅ Production Ready  
**Version**: 1.0  
**Last Updated**: 2024-10-15
