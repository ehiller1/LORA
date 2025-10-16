# RMN LoRA System - Unified UI Architecture

## Overview

Complete UI ecosystem with three integrated applications serving different user personas.

## Applications

### 1. Main Demo UI (`demo/streamlit_app.py`)

**Persona**: Brand Manager / Campaign Planner

**Purpose**: Day-to-day campaign management and optimization

**Tabs**:
1. **📥 Data** - Harmonize retailer exports to RMIS
2. **📋 Plan** - AI-powered campaign planning
3. **💰 Optimize** - Budget allocation with constraints
4. **📊 Measure** - Experiment design and measurement
5. **✨ Creative** - Policy-compliant ad copy generation
6. **🔧 Ops** - Adapter composition logs

**Key Features**:
- Real-time data harmonization
- AI planning with tool calling
- Interactive optimization (drag sliders, re-optimize)
- Experiment design (geo split, holdout, pacing)
- Creative generation with policy checks
- Adapter composition visibility

**Launch**:
```bash
cd demo
streamlit run streamlit_app.py
# Opens: http://localhost:8501
```

---

### 2. Admin Console (`src/ui/lora_admin.py`)

**Persona**: ML Engineer / System Administrator

**Purpose**: Train adapters, compose federations, manage datasets

**Tabs**:
1. **🚀 Training** - Create and monitor training jobs
2. **🔗 Federation** - Compose and test adapter federations
3. **📊 Datasets** - Manage training data and schema mappings
4. **📈 Analytics** - Monitor system health and performance

**Key Features**:
- Full training job configuration
- Real-time progress tracking
- Visual adapter composition
- Federation testing with sample prompts
- Dataset quality validation
- Schema mapping editor
- Performance monitoring

**Launch**:
```bash
streamlit run src/ui/lora_admin.py
# Opens: http://localhost:8501
```

---

### 3. RLHF Feedback UI (`src/ui/rlhf_app.py`)

**Persona**: Domain Expert / Quality Reviewer

**Purpose**: Collect human feedback for model improvement

**Features**:
- Thumbs up/down feedback
- 1-5 star ratings
- Pairwise preference comparisons
- Text corrections
- Feedback statistics dashboard
- DPO dataset export

**Launch**:
```bash
python -m src.ui.rlhf_app
# Opens: http://localhost:8001
```

---

### 4. NDE Rater IDE (`src/nde_rater/rater_app.py`)

**Persona**: Non-Domain Expert Rater

**Purpose**: Structured rating tasks for RLHF

**Features**:
- 6 task types with rubrics
- Golden set calibration
- Auto-checks (JSON/SQL validation)
- Rater reliability tracking
- Escalation workflow
- Active learning task selection

**Launch**:
```bash
python -m src.nde_rater.rater_app
# Opens: http://localhost:8002
```

---

## Unified Design System

### Color Palette

```css
/* Primary Colors */
--primary-blue: #3b82f6;
--primary-dark: #1f2937;

/* Semantic Colors */
--success-green: #10b981;
--warning-amber: #f59e0b;
--error-red: #ef4444;
--info-blue: #3b82f6;

/* Neutral Colors */
--gray-50: #f8f9fa;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-700: #374151;
--gray-900: #1f2937;

/* Background */
--bg-main: #f8f9fa;
--bg-card: #ffffff;
--bg-sidebar: #1f2937;
```

### Typography

```css
/* Headers */
h1 { font-size: 2rem; font-weight: 700; color: #1f2937; }
h2 { font-size: 1.5rem; font-weight: 600; color: #374151; }
h3 { font-size: 1.25rem; font-weight: 600; color: #4b5563; }

/* Body */
body { font-size: 1rem; font-weight: 400; color: #1f2937; }

/* Metrics */
.metric-value { font-size: 1.75rem; font-weight: 600; }
.metric-label { font-size: 0.875rem; font-weight: 500; color: #6b7280; }

/* Code */
code { font-family: 'Monaco', 'Courier New', monospace; }
```

### Components

**Cards**:
```css
.card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
}
```

**Buttons**:
```css
.btn-primary {
    background: #3b82f6;
    color: white;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-weight: 500;
}

.btn-secondary {
    background: white;
    color: #3b82f6;
    border: 1px solid #3b82f6;
    border-radius: 6px;
    padding: 0.5rem 1rem;
}
```

**Progress Bars**:
```css
.progress-bar {
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #3b82f6;
    transition: width 0.3s ease;
}
```

**Status Badges**:
```css
.badge-success { background: #d1fae5; color: #065f46; }
.badge-warning { background: #fef3c7; color: #92400e; }
.badge-error { background: #fee2e2; color: #991b1b; }
.badge-info { background: #dbeafe; color: #1e40af; }
```

---

## User Flows

### Flow 1: Train Adapter → Use in Demo

```
1. Admin Console (Training Tab)
   ↓ Create training job
   ↓ Monitor progress
   ↓ Adapter saved to registry
   
2. Admin Console (Federation Tab)
   ↓ Select base model
   ↓ Add trained adapter
   ↓ Create federation
   ↓ Test with sample prompt
   
3. Main Demo (Data Tab)
   ↓ Sidebar shows active adapters
   ↓ Use federation for harmonization
   ↓ Plan campaigns with composed model
```

### Flow 2: Collect Feedback → Retrain

```
1. Main Demo (Any Tab)
   ↓ User generates output
   ↓ Click feedback button
   
2. RLHF UI
   ↓ Rate output (thumbs/stars)
   ↓ Provide corrections
   ↓ Submit feedback
   
3. Admin Console (Datasets Tab)
   ↓ Export DPO dataset
   ↓ Validate quality
   
4. Admin Console (Training Tab)
   ↓ Train with DPO
   ↓ New adapter version created
```

### Flow 3: Manage Schema Mapping

```
1. Admin Console (Datasets → Mappings)
   ↓ View retailer mappings
   ↓ Check coverage metrics
   ↓ Identify gaps
   
2. Admin Console (Datasets → Browser)
   ↓ Browse raw retailer data
   ↓ Understand field semantics
   
3. Admin Console (Datasets → Mappings)
   ↓ Edit mapping YAML
   ↓ Add new field transformations
   ↓ Save and validate
   
4. Main Demo (Data Tab)
   ↓ Load retailer data
   ↓ Harmonize with updated mapping
   ↓ View improved coverage
```

---

## Integration Points

### 1. Shared State

All UIs share common data structures:

```python
# Adapters
{
    'name': 'amazon_schema_v1',
    'type': 'retailer',
    'base_model': 'llama-3.1-8b',
    'size_mb': 15,
    'accuracy': 92,
    'created_at': '2024-10-15 10:30:00'
}

# Federations
{
    'id': 'fed_20241015_103000',
    'base_model': 'llama-3.1-8b',
    'retailer_adapter': 'amazon_schema_v1',
    'task_adapter': 'planning_v1',
    'method': 'gated',
    'status': 'active'
}

# Training Jobs
{
    'id': 'job_001',
    'name': 'amazon_schema_v2',
    'status': 'running',
    'progress': 65,
    'loss': 1.23,
    'epochs': 3,
    'current_epoch': 2
}
```

### 2. API Endpoints

Common backend API for all UIs:

```python
# Training
POST   /api/training/jobs          # Create training job
GET    /api/training/jobs/{id}     # Get job status
DELETE /api/training/jobs/{id}     # Cancel job

# Adapters
GET    /api/adapters               # List adapters
GET    /api/adapters/{name}        # Get adapter details
POST   /api/adapters/{name}/load   # Load adapter

# Federations
POST   /api/federations            # Create federation
GET    /api/federations/{id}       # Get federation
POST   /api/federations/{id}/infer # Run inference

# Datasets
GET    /api/datasets               # List datasets
POST   /api/datasets/validate      # Validate dataset
GET    /api/datasets/{name}/stats  # Get statistics

# Feedback
POST   /api/feedback               # Submit feedback
GET    /api/feedback/stats         # Get statistics
POST   /api/feedback/export        # Export DPO dataset
```

### 3. Event System

Real-time updates across UIs:

```python
# Events
training_job_started
training_job_progress_updated
training_job_completed
adapter_registered
federation_created
federation_tested
dataset_uploaded
dataset_validated
feedback_submitted
```

---

## Deployment Architecture

### Development (Local)

```
┌─────────────────────────────────────────┐
│ Developer Machine                       │
├─────────────────────────────────────────┤
│                                         │
│  Port 8501: Main Demo                  │
│  Port 8501: Admin Console (alt)        │
│  Port 8001: RLHF UI                    │
│  Port 8002: NDE Rater IDE              │
│                                         │
│  Shared: SQLite DB                     │
│  Shared: Local file system             │
└─────────────────────────────────────────┘
```

### Production (Cloud)

```
┌─────────────────────────────────────────────────────┐
│ Load Balancer (HTTPS)                               │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│ Kubernetes Cluster                                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Pod 1: Main Demo (3 replicas)                     │
│  Pod 2: Admin Console (1 replica)                  │
│  Pod 3: RLHF UI (2 replicas)                       │
│  Pod 4: NDE Rater IDE (2 replicas)                 │
│  Pod 5: API Backend (5 replicas)                   │
│                                                      │
│  Shared: PostgreSQL (RDS)                          │
│  Shared: S3 (model artifacts, datasets)            │
│  Shared: Redis (session state, cache)              │
└─────────────────────────────────────────────────────┘
```

---

## Access Control

### Role-Based Permissions

**Brand Manager**:
- ✅ Main Demo (all tabs)
- ❌ Admin Console
- ✅ RLHF UI (submit feedback)
- ❌ NDE Rater IDE

**ML Engineer**:
- ✅ Main Demo (all tabs)
- ✅ Admin Console (all tabs)
- ✅ RLHF UI (view stats)
- ❌ NDE Rater IDE

**System Admin**:
- ✅ All UIs (full access)

**NDE Rater**:
- ❌ Main Demo
- ❌ Admin Console
- ❌ RLHF UI
- ✅ NDE Rater IDE (rating tasks only)

**Domain Expert**:
- ✅ Main Demo (read-only)
- ❌ Admin Console
- ✅ RLHF UI (all features)
- ✅ NDE Rater IDE (golden set creation)

---

## Performance Targets

### Main Demo
- Page load: <2 seconds
- Data harmonization: <3 seconds (10K rows)
- Plan generation: <3 seconds
- Optimization: <2 seconds
- Creative generation: <2 seconds

### Admin Console
- Training job submission: <1 second
- Progress updates: Real-time (WebSocket)
- Federation creation: <1 second
- Dataset validation: <5 seconds (1K examples)

### RLHF UI
- Feedback submission: <500ms
- Dashboard load: <2 seconds
- Export DPO dataset: <10 seconds (10K examples)

### NDE Rater IDE
- Task load: <1 second
- Judgment submission: <500ms
- Auto-checks: <200ms
- Calibration: <2 seconds

---

## Monitoring & Observability

### Metrics to Track

**Usage**:
- Active users per UI
- Page views per tab
- Actions per session
- Session duration

**Performance**:
- Page load times
- API response times
- Training job duration
- Inference latency

**Quality**:
- Feedback submission rate
- Rater agreement rate
- Dataset quality scores
- Adapter accuracy

**System Health**:
- GPU utilization
- Memory usage
- Disk I/O
- Network throughput

### Dashboards

**Operations Dashboard**:
- All UIs uptime
- Request rates
- Error rates
- Resource utilization

**Training Dashboard**:
- Active jobs
- Queue depth
- Success/failure rates
- Average training time

**Quality Dashboard**:
- Feedback volume
- Rating distributions
- Adapter performance trends
- Dataset quality trends

---

## Future Enhancements

### Phase 1 (Current)
- ✅ Main Demo with 6 tabs
- ✅ Admin Console with 4 tabs
- ✅ RLHF UI
- ✅ NDE Rater IDE
- ✅ Unified design system

### Phase 2 (Q1 2025)
- [ ] Real-time WebSocket updates
- [ ] Advanced mapping editor (drag-and-drop)
- [ ] A/B testing framework
- [ ] Automated hyperparameter tuning
- [ ] Multi-user collaboration

### Phase 3 (Q2 2025)
- [ ] Mobile-responsive design
- [ ] Dark mode
- [ ] Internationalization (i18n)
- [ ] Advanced analytics (Looker/Tableau)
- [ ] API playground

### Phase 4 (Q3 2025)
- [ ] Voice interface
- [ ] Natural language queries
- [ ] Automated report generation
- [ ] Slack/Teams integration
- [ ] Embedded widgets

---

## Summary

**4 Integrated UIs**:
1. **Main Demo** - Campaign management (Brand Managers)
2. **Admin Console** - Training & federation (ML Engineers)
3. **RLHF UI** - Feedback collection (Domain Experts)
4. **NDE Rater IDE** - Structured rating (NDE Raters)

**Unified Design**:
- Consistent color palette
- Professional business layout
- Shared component library
- Common interaction patterns

**Integration**:
- Shared data structures
- Common API backend
- Real-time event system
- Role-based access control

**Production Ready**:
- Scalable architecture
- Performance optimized
- Monitoring & observability
- Security & compliance

---

**Status**: ✅ Complete  
**Version**: 1.0  
**Last Updated**: 2024-10-15
