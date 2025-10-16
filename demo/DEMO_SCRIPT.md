# RMN LoRA System - 15-Minute Demo Script

## Pre-Demo Setup (5 minutes before)

```bash
# 1. Generate synthetic data
cd demo
python generate_synthetic_data.py

# 2. Start Streamlit app
streamlit run streamlit_app.py
```

**Browser**: Open http://localhost:8501

---

## Demo Flow (15 minutes)

### 🎬 INTRO (1 minute)

**Say**: 
> "Today I'll show you how LoRA adapters enable manufacturers to optimize Retail Media Network spend across multiple retailers with different schemas, policies, and APIs. We'll see data harmonization, AI planning, optimization, measurement design, and creative generation—all powered by composable LoRA adapters."

**Show**: Title screen with system architecture diagram

---

### 📥 PART 1: Data Harmonization (3 minutes)

**Navigate**: Click **"Data"** tab

**Say**:
> "We have two retailers with completely different data formats. Alpha uses CSV with US conventions, Beta uses JSONL with European formats. Watch how our Data Harmonizer Agent—using retailer-specific LoRA adapters—transforms both into our canonical RMIS schema."

**Actions**:
1. Click **"Load Alpha Data"**
   - ✅ Shows success message
   
2. Click **"Harmonize Alpha"**
   - Wait for spinner
   - **Point out**:
     - "10,000 rows harmonized"
     - "Enum coverage: 98%" (highlight this)
     - "Join success rate: 97%"
   
3. Click **"Preview Harmonized Data"** expander
   - **Say**: "Notice how 'sp' became 'sponsored_product', micros converted to dollars, CST to UTC"

4. Repeat for Beta:
   - Click **"Load Beta Data"**
   - Click **"Harmonize Beta"**
   - **Say**: "Beta had EUR currency, different field names, JSONL format—all normalized"

5. Scroll to **"Mapping Validation"**
   - Click **"View Mapping Gaps"** expander
   - **Say**: "The agent detected 3 mapping gaps and suggests fixes. In production, it would auto-apply these."

**Key Message**: "Different retailers, different schemas—one canonical format. This is the foundation for cross-RMN optimization."

---

### 📋 PART 2: AI Planning (3 minutes)

**Navigate**: Click **"Plan"** tab

**Say**:
> "Now let's create a campaign plan. The Planner Agent uses tool-calling to fetch metrics, get uplift priors, and call our optimizer—all orchestrated by the LLM with task-specific LoRA."

**Actions**:
1. **Show the brief** (already filled):
   ```
   Budget: $2,500,000
   Target ROAS: ≥ 3.0
   Experiment Reserve: 10%
   Exclude: SKUs with OOS probability > 5%
   ```

2. Click **"Draft Plan"** button
   - Wait for spinner (shows "🤖 Planner Agent working...")
   - **Say**: "The agent is calling tools: get_uplift_priors, fetch_metrics, allocate_budget"

3. **When plan appears**:
   - **Point to metrics**:
     - "Total Budget: $2.5M"
     - "Expected ROAS: 3.5x" (exceeds target)
     - "Incremental Revenue: $8.75M"
     - "Experiment Budget: $250K"
   
4. **Show allocation table**:
   - **Say**: "Look at the allocation—it's spread across both retailers, multiple placements, audiences, and SKUs. Notice the 🧪 emoji? Those are experiment cells."

5. Click **"Tool Call Trail"** expander
   - **Say**: "Here's the exact sequence of tool calls. Each one passed validation—SQL parsed, constraints checked."

6. Click **"Plan Rationale"** expander
   - **Read one bullet**: "Shift +12% from Beta Offsite to Alpha SP due to higher ICE at similar CPA"
   - **Say**: "The LLM explains its reasoning, citing uplift data and margin calculations."

**Key Message**: "This isn't just a spreadsheet—it's an AI agent that understands your business constraints and optimizes accordingly."

---

### 💰 PART 3: Interactive Optimization (2 minutes)

**Navigate**: Click **"Optimize"** tab

**Say**:
> "What if we tighten constraints? Let's see real-time what-if analysis."

**Actions**:
1. **Drag ROAS Floor slider** from 3.0 to 3.2
   - **Say**: "Increasing ROAS target to 3.2x"

2. **Drag Experiment Share** from 10% to 15%
   - **Say**: "And reserving more budget for testing"

3. Click **"Re-optimize"** button
   - Wait for spinner
   
4. **When results appear**:
   - **Point to deltas**:
     - "ROAS: 3.2x (+0.2x)" (green)
     - "Incremental Revenue: $8.0M (-$750K)" (red)
     - "Reallocated SKUs: 12"
   
   - **Say**: "Higher ROAS target means we're more selective—revenue drops slightly but efficiency improves. The optimizer reallocated 12 SKUs to meet the new constraint."

5. **Scroll to Sensitivity Analysis**
   - **Say**: "Here's how the plan changes across different ROAS targets. At 3.5x, we're in high-risk territory."

**Key Message**: "Instant what-if analysis. No spreadsheets, no manual reallocation—just drag and re-optimize."

---

### 📊 PART 4: Measurement Design (2 minutes)

**Navigate**: Click **"Measure"** tab

**Say**:
> "Before we launch, let's design an experiment to measure true incrementality."

**Actions**:
1. **Show experiment settings**:
   - Type: "Geo Split Test" (already selected)
   - Minimum Cells: 2
   - Statistical Power: 80%
   - MDE: 10%

2. Click **"Design Experiment"** button
   - Wait for spinner

3. **When design appears**:
   - **Point to metrics**:
     - "Treatment Cells: 2"
     - "Sample Size per Cell: 1,600"
     - "Expected Power: 80%"
   
4. **Show Cell Assignment table**:
   - **Say**: "We've balanced DMAs by population—Treatment vs Control. This ensures apples-to-apples comparison."

5. **Scroll to SQL**:
   - **Say**: "Here's the exact SQL to read out results after 14 days. It calculates lift, ROAS by cell, and runs a t-test for significance."
   - **Don't read it all—just point**

6. Click **"Interpretation Guide"** expander
   - **Say**: "The agent even provides interpretation guidance for non-technical users."

**Key Message**: "Rigorous measurement design, generated automatically. No more guessing if your campaigns actually worked."

---

### ✨ PART 5: Creative Generation (2 minutes)

**Navigate**: Click **"Creative"** tab

**Say**:
> "Finally, let's generate ad copy. The Creative Agent knows each retailer's policies—max lengths, disallowed terms, required disclaimers."

**Actions**:
1. **Select SKUs**: Already selected (SKU-001, SKU-002, SKU-003)

2. **Target Retailer**: Select "Alpha"

3. **Tone**: Select "Professional"

4. Click **"Generate Copy"** button
   - Wait for spinner
   - **Say**: "Generating 6 variants—2 per SKU"

5. **When creatives appear**:
   - **Expand first variant** (should be ✅ PASS)
     - **Read headline**: "Premium Wireless Headphones - Quality You Can Trust"
     - **Say**: "80 chars—within Alpha's limit. No disallowed terms. Policy check: PASS."
   
6. **Expand a FAIL variant** (if any, or simulate):
   - **Say**: "This one failed—contains 'guaranteed', which Alpha prohibits."
   - Click **"Fix"** button
   - **Say**: "Watch—the agent auto-fixes violations and re-checks. Now it passes."

7. **Change retailer to Beta**:
   - Click **"Generate Copy"** again
   - **Say**: "Notice the copy is shorter—Beta has stricter length limits. Different policies, same agent."

**Key Message**: "Policy-compliant creative at scale. No more manual reviews, no more rejections."

---

### 🔧 PART 6: Ops & Observability (1 minute)

**Navigate**: Click **"Ops"** tab

**Say**:
> "Behind the scenes, here's what's happening."

**Actions**:
1. **Point to System Health**:
   - "System Health: Healthy"
   - "API Latency: 145ms"
   - "Error Rate: 0.02%"

2. **Show Adapter Composition Log**:
   - **Say**: "Every task loads the right LoRA adapters. For planning, we load base + task_planning + retailer_alpha. For creative, we swap in task_policy_creative."
   - **Point to a row**: "See? Adapters compose dynamically."

3. **Show Tool Call Log**:
   - **Say**: "Every tool call is logged with arguments, results, and duration. Full observability."

4. **Show Data Quality Metrics**:
   - **Say**: "Enum coverage, join rates—all monitored in real-time. If quality drops, we alert."

**Key Message**: "Production-grade observability. You know exactly what the system is doing and why."

---

### 🏪 BONUS: Retailer Leasing (1 minute, if time)

**Navigate**: Sidebar

**Say**:
> "One more thing—the 'retailer leases agents' model."

**Actions**:
1. **In sidebar**, change **"Execution Mode"** to **"Retailer Alpha Service"**

2. **Point to Active Adapters**:
   - **Say**: "Now we're running at Retailer Alpha's service. They host the agent, load their LoRA, and return only aggregated results—no raw data leaves their environment."

3. **Go back to Plan tab**:
   - **Say**: "The manufacturer gets the same plan, but it's computed at the retailer. This is multi-tenant, privacy-preserving AI."

**Key Message**: "Retailers can lease agents to manufacturers without exposing raw data. Win-win."

---

## 🎬 CLOSING (1 minute)

**Say**:
> "So what did we just see?
> 
> 1. **Data harmonization** across retailers with different schemas
> 2. **AI planning** with tool-calling and constraint optimization
> 3. **Interactive what-if** analysis with real-time re-optimization
> 4. **Experiment design** with statistical rigor
> 5. **Policy-compliant creative** generation
> 6. **Full observability** with adapter composition logs
> 
> All powered by composable LoRA adapters—retailer adapters for schema/policy knowledge, task adapters for planning/creative/measurement.
> 
> This is production-ready. We can onboard a new retailer in days, not months. And manufacturers get a single interface to optimize across all their RMN spend.
> 
> Questions?"

---

## Backup Slides (if needed)

### Technical Architecture
- Base model: Llama-3.1-8B-Instruct
- LoRA adapters: 16-rank, ~10MB each
- Warehouse: DuckDB (in-memory)
- Optimizer: PuLP (linear programming)
- UI: Streamlit

### Data Flow
```
Raw Retailer Data → Harmonization (LoRA) → RMIS Schema → 
Planner Agent (LoRA) → Optimizer (LP) → Allocation Plan → 
Creative Agent (LoRA) → Policy Check → Approved Copy
```

### Adapter Composition
```python
# Pseudocode
adapters = [
    base_model,
    load_lora("retailer_alpha"),  # Schema knowledge
    load_lora("task_planning")     # Tool calling
]
response = model.generate(prompt, adapters=adapters)
```

---

## Troubleshooting

**If data doesn't load**:
- Check `demo/data/` directory exists
- Re-run `python generate_synthetic_data.py`

**If Streamlit crashes**:
- Check Python version (3.11+)
- Install dependencies: `pip install streamlit pandas numpy duckdb`

**If optimizer is slow**:
- It's using simplified heuristic (PuLP not installed)
- Install: `pip install pulp`

---

## Post-Demo Q&A Prep

**Q: How long to train adapters?**  
A: 1-3 hours per adapter on a single GPU. We use QLoRA for efficiency.

**Q: How much data needed?**  
A: 1-3k examples per adapter (SFT) + 1-2k preference pairs (DPO). Quality over quantity.

**Q: Can it handle more retailers?**  
A: Yes—just add new retailer LoRA. No retraining of base model.

**Q: What about data privacy?**  
A: Retailers can host agents in their environment. Only aggregated results leave.

**Q: Cost?**  
A: Inference: ~$0.001/request. Training: ~$50/adapter. Hosting: $200-500/month.

**Q: Integration with existing systems?**  
A: FastAPI endpoints. Plug into your MMM, DSP, or BI tools.

---

## Success Metrics

**Demo is successful if audience understands**:
1. ✅ LoRA adapters enable retailer-specific customization
2. ✅ Composable adapters (retailer + task) work together
3. ✅ System handles real constraints (ROAS, budget, OOS)
4. ✅ Output is production-grade (SQL, policy checks, experiments)
5. ✅ Retailer leasing model preserves privacy

**Next steps after demo**:
- Pilot with 1 retailer, 1 manufacturer
- Collect real data for adapter training
- Deploy behind API
- Measure lift vs manual planning
