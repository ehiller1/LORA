# Quick Start: Federation Demo

Get the federated LoRA demo running in **5 minutes**.

## Prerequisites

- Python 3.9+
- 8GB RAM minimum
- Git

## Installation

```bash
# Clone repository (if not already done)
cd rmn-lora-system

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import crewai; print('CrewAI installed:', crewai.__version__)"
```

## Run the Demo

### Option 1: Streamlit UI (Recommended)

```bash
streamlit run demo/pages/federation_demo.py
```

Then:
1. Open browser to `http://localhost:8501`
2. Configure settings in sidebar (budget, ROAS floor, etc.)
3. Click **"▶️ Run Demo"**
4. Explore the 4 tabs:
   - **Comparison** - See clean room vs full data metrics
   - **Federation Graph** - Visualize adapter composition
   - **Plan Details** - Compare budget allocations
   - **Creatives** - View generated ad copy

### Option 2: Python Script

```python
from demo.federation_workflow import run_federation_demo

# Run demo
results = run_federation_demo(
    budget=2500000,      # $2.5M budget
    roas_floor=3.0,      # Minimum 3x ROAS
    exp_share=0.1        # 10% for experiments
)

# Print comparison
comp = results["steps"]["comparison"]
print(f"Full Data ROAS: {comp['full_data_roas']:.2f}x")
print(f"Clean Room ROAS: {comp['clean_room_roas']:.2f}x")
print(f"Improvement: {comp['roas_delta_pct']:.1f}%")
```

## What You'll See

### 1. Comparison Metrics

| Metric | Clean Room | Full Data | Delta |
|--------|-----------|-----------|-------|
| iROAS | 2.8x | 3.5x | **+25%** |
| Revenue | $7.0M | $8.75M | **+25%** |
| SKUs | 28 | 42 | **+50%** |

### 2. Federation Graph

```
Generic LLM (Llama 3.1)
    ↓
Industry LoRA (Retail Media)
    ↓
Manufacturer LoRA (Brand X)
    ↓
Task LoRA (Planning)
    ↓
Agent Orchestrator
```

### 3. Missing Capabilities (Clean Room)

- ❌ No margin optimization
- ❌ No stock-out avoidance
- ❌ No promotional timing
- ❌ Limited SKU coverage

### 4. Generated Creatives

Brand-compliant ad copy with policy checking.

## Key Files

```
rmn-lora-system/
├── src/
│   ├── services/
│   │   └── llm_federation.py       # Core federation service
│   ├── agents/
│   │   └── crewai_base.py          # CrewAI agents
│   └── schemas/
│       └── rmis.py                 # Enhanced models
├── demo/
│   ├── federation_workflow.py      # Demo orchestrator
│   ├── pages/
│   │   └── federation_demo.py      # Streamlit UI
│   ├── components/
│   │   └── federation_graph.py     # Visualization
│   ├── tools/
│   │   └── clean_room.py           # Clean room connector
│   └── mock_adapters/              # Adapter metadata
│       ├── industry_retail_media/
│       ├── manufacturer_brand_x/
│       ├── task_planning/
│       └── task_creative/
└── docs/
    └── FEDERATION_DEMO_GUIDE.md    # Full documentation
```

## Next Steps

1. ✅ Run the demo
2. 📖 Read `docs/FEDERATION_DEMO_GUIDE.md` for details
3. 🔧 Customize adapters in `demo/mock_adapters/`
4. 🚀 Integrate with your data
5. 📊 Deploy to production

## Troubleshooting

**Issue:** Module not found errors

```bash
pip install crewai>=0.28.0 crewai-tools>=0.2.0
```

**Issue:** Streamlit not starting

```bash
pip install streamlit
streamlit run demo/pages/federation_demo.py
```

**Issue:** No comparison shown

Make sure you clicked "Run Demo" button in the sidebar.

## Learn More

- **Full Guide:** `docs/FEDERATION_DEMO_GUIDE.md`
- **Implementation Plan:** `FEDERATION_IMPLEMENTATION_PLAN.md`
- **Gap Analysis:** `FEDERATION_GAP_ANALYSIS.md`

---

**Ready in 5 minutes. Superior results guaranteed.** 🚀
