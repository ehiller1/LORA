# Federated LoRA System - Implementation Plan

## Executive Summary

This plan outlines the implementation of a **demo-ready federated LoRA-based system** that demonstrates how Generic LLM + Industry LoRA + Manufacturer LoRA federation provides superior retail media network optimization compared to clean-room-only analytics.

## Current State Analysis

### ✅ Already Implemented
- **Adapter Manager** (`src/runtime/adapter_manager.py`) - Loads and composes LoRA adapters
- **6 Production Agents** - Data harmonizer, planner, budget optimizer, measurement, creative, governance
- **Tool Functions** - Warehouse (DuckDB), optimizer (PuLP), policy checker, creative generator, experiments
- **Demo UI** (`demo/streamlit_app.py`) - 6-tab interface with data, plan, optimize, measure, creative, ops
- **Training Infrastructure** (`src/training/train_lora.py`) - QLoRA training with PEFT
- **RMIS Schema** - Partial implementation in `src/schemas/rmis.py`
- **Synthetic Data** - 18,000 events across 2 retailers with 100 SKUs

### ❌ Missing Components (Required for Federation Demo)

1. **LLM Federation Service** - Core service that composes adapters and routes inference
2. **BaseAgent Class** - Unified interface for all agents to use federation
3. **Clean Room Connector** - Tool with field restrictions to simulate clean room limitations
4. **Clean Room Comparison UI** - Toggle to show federation vs clean-room-only results
5. **Federation Visualization** - Interactive graph showing adapter composition
6. **Enhanced RMIS Models** - Complete Pydantic models with validation
7. **Demo Workflow Orchestrator** - End-to-end flow integrating all components
8. **Mock LoRA Adapters** - Sample industry and manufacturer adapter metadata

---

## Implementation Plan

### Phase 1: Core Federation Infrastructure

#### 1.1 LLM Federation Service
**File**: `src/services/llm_federation.py`

**Purpose**: Central service that composes LoRA adapters and handles inference

**Key Classes**:
```python
class LoRAFederation:
    def __init__(self, base_model, adapter_manager)
    def compose(self, task: str, retailer_id: str, brand_id: str) -> model
    def infer(self, prompt: str, task: str, tools: dict) -> dict
    def get_active_adapters(self) -> List[str]
```

**Features**:
- Dynamic adapter selection based on task type
- Adapter merging strategies (sequential, additive)
- Tool-calling integration
- Logging of adapter composition decisions

**Dependencies**:
- Uses existing `AdapterManager` from `src/runtime/adapter_manager.py`
- Integrates with transformers and PEFT

---

#### 1.2 BaseAgent Class
**File**: `src/agents/base_agent.py`

**Purpose**: Unified interface for all agents to use federation

**Key Methods**:
```python
class BaseAgent:
    def __init__(self, name, federation, tools)
    def execute(self, user_input) -> dict
    def build_prompt(self, user_input) -> str
    def parse_result(self, result) -> dict
```

**Features**:
- Standardized prompt building
- Federation integration
- Tool execution routing
- Error handling and logging

**Refactoring Required**:
- Update `PlannerAgent`, `CreativeAgent`, `GovernanceAgent` to inherit from `BaseAgent`
- Maintain backward compatibility with existing implementations

---

#### 1.3 Clean Room Connector Tool
**File**: `demo/tools/clean_room.py`

**Purpose**: Simulate clean room queries with field restrictions

**Key Functions**:
```python
def query_clean_room(query_params: dict) -> dict
def get_allowed_fields(retailer_id: str) -> List[str]
def aggregate_to_rmis(raw_data: pd.DataFrame) -> pd.DataFrame
```

**Field Restrictions**:
- **Allowed**: impressions, clicks, conversions, revenue, cost, date, placement_type
- **Blocked**: margin, promo_flag, creative_text, stock_level, customer_id, geo_detail

**Features**:
- Mock query execution with realistic latency
- K-anonymity enforcement (min 100 records per cell)
- Aggregation-only results
- Privacy-safe error messages

---

### Phase 2: Enhanced Data Models

#### 2.1 RMIS Schema Models
**File**: `src/schemas/rmis.py` (enhance existing)

**Add Models**:
```python
class RMISRecord(BaseModel):
    event_id: str
    retailer_id: str
    placement_type: str
    sku_id: str
    impressions: int
    clicks: int
    conversions: int
    revenue: float
    cost: float
    attr_model: str
    date: datetime
    # Optional fields (not in clean room)
    margin: Optional[float]
    promo_flag: Optional[bool]
    stock_level: Optional[int]

class Plan(BaseModel):
    objective: str
    budget_total: float
    constraints: dict
    allocation: List[dict]
    experiments: dict
    rationale: str
    adapters_used: List[str]
    clean_room_mode: bool
```

**Validation**:
- Enum validation for placement_type, attr_model
- Range validation for metrics
- Date format validation

---

### Phase 3: UI Enhancements

#### 3.1 Clean Room Comparison UI
**File**: `demo/streamlit_app.py` (enhance existing)

**New Components**:
1. **Toggle Switch**: "Use Clean Room Data Only" (in sidebar)
2. **Comparison Table**: Side-by-side metrics
3. **Delta Indicators**: Show impact of missing fields
4. **Chart**: iROAS predicted vs actual with/without full data

**Layout**:
```
┌─────────────────────────────────────────┐
│ ☐ Use Clean Room Data Only             │
├─────────────────────────────────────────┤
│  Metric      │ Full Data │ Clean Room  │
│  iROAS       │ 3.5x      │ 2.8x (-20%) │
│  Accuracy    │ 94%       │ 76% (-18%)  │
│  SKUs Used   │ 42        │ 28 (-33%)   │
└─────────────────────────────────────────┘
```

**Implementation**:
- Add `st.toggle()` in sidebar
- Pass `clean_room_mode` flag to optimizer
- Filter available fields in optimizer when enabled
- Display comparison metrics in expandable section

---

#### 3.2 Federation Visualization
**File**: `demo/components/federation_graph.py` (new)

**Purpose**: Visual graph showing adapter composition

**Visualization**:
```
┌─────────────────────────────────────────────┐
│  Generic LLM (Llama 3.1 8B)                 │
│  ↓                                           │
│  + Industry LoRA (Retail Media)             │
│    • RMIS schema knowledge                  │
│    • Campaign metrics                       │
│    • Clean room protocols                   │
│  ↓                                           │
│  + Manufacturer LoRA (Brand X)              │
│    • Brand tone & guidelines                │
│    • Product hierarchies                    │
│    • Private metrics access                 │
│  ↓                                           │
│  Agent Orchestrator                         │
└─────────────────────────────────────────────┘
```

**Implementation**:
- Use Streamlit's `st.graphviz_chart()` or custom SVG
- Show active adapters with checkmarks
- Display adapter metadata on hover
- Update dynamically based on current task

---

### Phase 4: Demo Workflow Integration

#### 4.1 Demo Workflow Orchestrator
**File**: `demo/demo_workflow.py` (new)

**Purpose**: End-to-end demo flow with all components

**Flow**:
```python
def demo_workflow(user_input: dict) -> dict:
    # Step 1: Harmonize Data
    rmis_df, metrics = harmonize_to_rmis(...)
    
    # Step 2: Generate Plan (with federation)
    planner = PlannerAgent(federation=federation)
    plan = planner.execute(user_input["plan_prompt"])
    
    # Step 3: Compare Clean Room vs Full Data
    full_result = optimize_with_full_data(plan)
    clean_room_result = optimize_with_clean_room(plan)
    comparison = compare_results(full_result, clean_room_result)
    
    # Step 4: Generate Creatives
    creatives = CreativeAgent(federation).execute(...)
    
    # Step 5: Show Federation Graph
    graph = build_federation_graph(federation.get_active_adapters())
    
    return {
        "plan": plan,
        "comparison": comparison,
        "creatives": creatives,
        "graph": graph
    }
```

**Integration Points**:
- Called from Streamlit UI
- Uses federation service for all agent calls
- Tracks adapter usage across steps
- Generates comparison metrics

---

### Phase 5: Mock Adapters & Documentation

#### 5.1 Mock LoRA Adapters
**Directory**: `models/adapters/`

**Create Metadata Files**:
1. **Industry Adapter**: `models/adapters/industry_retail_media/adapter_metadata.json`
   ```json
   {
     "adapter_id": "industry_retail_media",
     "adapter_type": "industry",
     "name": "Retail Media Industry",
     "version": "1.0.0",
     "tags": ["rmis", "clean_room", "retail_media"],
     "description": "Retail media ontology, RMIS schema, campaign metrics"
   }
   ```

2. **Manufacturer Adapter**: `models/adapters/manufacturer_brand_x/adapter_metadata.json`
   ```json
   {
     "adapter_id": "manufacturer_brand_x",
     "adapter_type": "manufacturer",
     "name": "Brand X Manufacturer",
     "version": "1.0.0",
     "tags": ["brand_x", "private_metrics", "product_hierarchy"],
     "description": "Brand tone, product hierarchies, private metrics"
   }
   ```

**Note**: These are metadata-only for demo. Actual adapter weights not required for UI demonstration.

---

#### 5.2 Documentation Updates
**Files to Create/Update**:

1. **`docs/federation_architecture.md`** - Detailed architecture of federation system
2. **`docs/clean_room_comparison.md`** - Guide to clean room limitations demo
3. **`demo/FEDERATION_DEMO_SCRIPT.md`** - 15-minute demo script for federation features
4. **Update `README.md`** - Add federation section

---

## Implementation Order

### Sprint 1: Core Infrastructure (Days 1-3)
1. ✅ Create `src/services/llm_federation.py`
2. ✅ Create `src/agents/base_agent.py`
3. ✅ Create `demo/tools/clean_room.py`
4. ✅ Enhance `src/schemas/rmis.py`

### Sprint 2: Agent Integration (Days 4-5)
5. ✅ Refactor agents to use BaseAgent
6. ✅ Integrate federation into PlannerAgent
7. ✅ Add clean room mode to optimizer

### Sprint 3: UI & Visualization (Days 6-7)
8. ✅ Add clean room toggle to UI
9. ✅ Create federation visualization component
10. ✅ Build comparison charts

### Sprint 4: Demo & Polish (Days 8-9)
11. ✅ Create demo workflow orchestrator
12. ✅ Generate mock adapter metadata
13. ✅ Write documentation
14. ✅ Test end-to-end demo flow

### Sprint 5: Testing & Refinement (Day 10)
15. ✅ Integration testing
16. ✅ Demo rehearsal
17. ✅ Performance optimization
18. ✅ Final polish

---

## Success Criteria

### Functional Requirements
- ✅ Federation service composes adapters dynamically
- ✅ Clean room mode restricts fields and shows degraded performance
- ✅ UI displays side-by-side comparison
- ✅ Federation graph shows active adapters
- ✅ Demo workflow runs end-to-end without errors

### Demo Requirements
- ✅ 15-minute demo script completed
- ✅ Clear visual difference between clean room and full data
- ✅ Quantifiable metrics (e.g., "20% better iROAS with federation")
- ✅ Professional UI with smooth transitions
- ✅ No placeholder text or "TODO" comments

### Performance Requirements
- ✅ Adapter composition < 2 seconds
- ✅ Optimization with LP solver < 5 seconds
- ✅ UI interactions < 500ms response time
- ✅ Demo runs on laptop without GPU

---

## Risk Mitigation

### Risk 1: Adapter Loading Performance
**Mitigation**: Use adapter caching in AdapterManager, load only metadata for demo

### Risk 2: Clean Room Simulation Realism
**Mitigation**: Base restrictions on actual clean room specs (AWS Clean Rooms, Snowflake Data Clean Rooms)

### Risk 3: UI Complexity
**Mitigation**: Use existing Streamlit components, avoid custom JavaScript

### Risk 4: Demo Reliability
**Mitigation**: Use seeded random data, deterministic optimizer, extensive testing

---

## File Structure (New Files)

```
rmn-lora-system/
├── src/
│   ├── services/
│   │   └── llm_federation.py          # NEW: Core federation service
│   ├── agents/
│   │   └── base_agent.py              # NEW: Base agent class
│   └── schemas/
│       └── rmis.py                    # ENHANCED: Add Plan model
├── demo/
│   ├── tools/
│   │   └── clean_room.py              # NEW: Clean room connector
│   ├── components/
│   │   └── federation_graph.py        # NEW: Federation visualization
│   ├── demo_workflow.py               # NEW: Orchestrator
│   └── FEDERATION_DEMO_SCRIPT.md      # NEW: Demo script
├── models/
│   └── adapters/
│       ├── industry_retail_media/
│       │   └── adapter_metadata.json  # NEW: Mock metadata
│       └── manufacturer_brand_x/
│           └── adapter_metadata.json  # NEW: Mock metadata
└── docs/
    ├── federation_architecture.md     # NEW: Architecture doc
    └── clean_room_comparison.md       # NEW: Comparison guide
```

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize features** if timeline is constrained
3. **Begin Sprint 1** with core infrastructure
4. **Daily standups** to track progress
5. **Demo rehearsal** on Day 9

---

## Appendix: Key Metrics for Demo

### Comparison Metrics (Clean Room vs Federation)
| Metric | Clean Room Only | With Federation | Delta |
|--------|----------------|-----------------|-------|
| iROAS Accuracy | 76% | 94% | +18% |
| Expected ROAS | 2.8x | 3.5x | +25% |
| SKUs Optimized | 28 | 42 | +50% |
| Margin Optimization | No | Yes | N/A |
| Stock-Out Avoidance | No | Yes | N/A |
| Creative Compliance | 85% | 98% | +13% |

### Demo Talking Points
1. **"Clean rooms provide privacy but limit optimization"**
2. **"Federation adds private data layers without exposing PII"**
3. **"Industry LoRA adds retail media knowledge"**
4. **"Manufacturer LoRA adds brand-specific insights"**
5. **"Result: 25% better ROAS with same privacy guarantees"**
