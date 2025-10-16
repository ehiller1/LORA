# RMN LoRA System - UI Design Specification

## Overview

Professional business-grade UI system for LoRA training, federation management, and dataset administration.

## Design Principles

### 1. Professional Business Layout
- **Clean & Modern**: White backgrounds, subtle shadows, rounded corners
- **Consistent Spacing**: 8px grid system
- **Typography**: Clear hierarchy with weighted headers
- **Color Palette**:
  - Primary: #3b82f6 (Blue)
  - Success: #10b981 (Green)
  - Warning: #f59e0b (Amber)
  - Error: #ef4444 (Red)
  - Neutral: #1f2937 (Dark Gray)
  - Background: #f8f9fa (Light Gray)

### 2. Information Architecture
```
Admin Console
├── Training Management
│   ├── Create Training Job
│   ├── Active Jobs Monitor
│   └── Training History
├── Federation & Composition
│   ├── Adapter Selection
│   ├── Composition Builder
│   └── Federation Testing
├── Datasets & Mappings
│   ├── Dataset Library
│   ├── Schema Mappings
│   └── Data Browser
└── Analytics & Monitoring
    ├── Training Metrics
    ├── Performance Dashboard
    └── System Health
```

## UI Components

### 1. Training Management UI

**Purpose**: Train new LoRA adapters with full configuration control

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ 🚀 LoRA Training Management                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Create Training Job                  Training Queue    │
│  ┌────────────────────────┐          ┌───────────────┐ │
│  │ Adapter Type: [▼]      │          │ Active: 2     │ │
│  │ Adapter Name: [____]   │          │ Completed: 15 │ │
│  │ Base Model: [▼]        │          │ Queue: 0      │ │
│  │ Training Type: [▼]     │          └───────────────┘ │
│  │ Dataset Path: [____]   │                            │
│  │ Epochs: [===|===] 3    │                            │
│  │                        │                            │
│  │ Advanced Settings ▼    │                            │
│  │ LoRA Rank: 16          │                            │
│  │ Batch Size: 4          │                            │
│  │ Learning Rate: 0.0002  │                            │
│  │                        │                            │
│  │ [🚀 Start Training]    │                            │
│  └────────────────────────┘                            │
│                                                          │
│  Active & Recent Jobs                                   │
│  ┌────────────────────────────────────────────────────┐ │
│  │ ▶ amazon_schema_v1 - RUNNING                       │ │
│  │   Progress: [=========>        ] 65%               │ │
│  │   Epoch: 2/3 | Loss: 1.23 | ETA: 45 min           │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │ ✓ planning_v1 - COMPLETED                          │ │
│  │   Final Loss: 0.87 | Accuracy: 92%                │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- ✅ Form-based job creation
- ✅ Real-time progress tracking
- ✅ Loss curve visualization
- ✅ Job queue management
- ✅ Advanced hyperparameter tuning
- ✅ One-click job restart

**Interactions**:
1. User fills form → Click "Start Training"
2. Job added to queue → Status: "Running"
3. Progress bar updates in real-time
4. On completion → Adapter saved to registry
5. User can download or deploy adapter

### 2. Federation & Composition UI

**Purpose**: Compose multiple LoRA adapters with base model

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ 🔗 LoRA Federation & Composition                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Compose Federation              Active Federation      │
│  ┌────────────────────┐          ┌──────────────────┐  │
│  │ Base Model: [▼]    │          │ Federation ID:   │  │
│  │ Llama-3.1-8B       │          │ fed_20241015     │  │
│  │                    │          │                  │  │
│  │ Retailer Adapter:  │          │ Stack:           │  │
│  │ [▼] amazon_v1      │          │ ┌──────────────┐ │  │
│  │                    │          │ │ Base Model   │ │  │
│  │ Task Adapter:      │          │ └──────────────┘ │  │
│  │ [▼] planning_v1    │          │        ↓         │  │
│  │                    │          │ ┌──────────────┐ │  │
│  │ Composition:       │          │ │ amazon_v1    │ │  │
│  │ ○ Additive        │          │ │ (~15MB)      │ │  │
│  │ ● Gated           │          │ └──────────────┘ │  │
│  │ ○ Sequential      │          │        ↓         │  │
│  │                    │          │ ┌──────────────┐ │  │
│  │ [🔗 Create]        │          │ │ planning_v1  │ │  │
│  └────────────────────┘          │ │ (~12MB)      │ │  │
│                                   │ └──────────────┘ │  │
│                                   │        ↓         │  │
│                                   │ ┌──────────────┐ │  │
│                                   │ │ Federated    │ │  │
│                                   │ │ (Ready)      │ │  │
│                                   │ └──────────────┘ │  │
│                                   └──────────────────┘  │
│                                                          │
│  Test Federation                                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Prompt: [Map 'adType' field with value 'sp'...]   │ │
│  │                                                     │ │
│  │ [▶️ Run Inference]                                  │ │
│  │                                                     │ │
│  │ Response:                                           │ │
│  │ > The field 'adType' maps to 'placement_type'...  │ │
│  │                                                     │ │
│  │ Metrics: 32 tokens | 145ms | 2 adapters used      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- ✅ Visual adapter stacking
- ✅ Composition method selection
- ✅ Live inference testing
- ✅ Performance metrics
- ✅ Save/load federations
- ✅ A/B comparison

**Interactions**:
1. Select base model + adapters
2. Choose composition method
3. Click "Create Federation"
4. Visual stack shows layers
5. Test with sample prompts
6. View latency and accuracy
7. Save federation config

### 3. Datasets & Mappings UI

**Purpose**: Manage training datasets and schema mappings

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ 📊 Datasets & Schema Mappings                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [📊 Datasets] [🗺️ Mappings] [📁 Browser]              │
│                                                          │
│  Training Datasets                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Name                Type   Size    Examples Quality│ │
│  ├────────────────────────────────────────────────────┤ │
│  │ retailer_amazon_sft SFT   2.3MB   2,847    [95%] │ │
│  │ task_planning_sft   SFT   4.1MB   5,123    [92%] │ │
│  │ policy_creative_dpo DPO   1.8MB   1,456    [97%] │ │
│  │ retailer_walmart_sft SFT  2.1MB   2,634    [93%] │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  [➕ Upload] [🔍 Validate] [📥 Export] [🗑️ Delete]      │
│                                                          │
│  Schema Mappings                                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Retailer   Version  Fields  Coverage  Status      │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ Amazon     v0.2.0   42      [98%]     Active      │ │
│  │ Walmart    v0.2.0   38      [95%]     Active      │ │
│  │ Target     v0.1.5   35      [92%]     Active      │ │
│  │ Instacart  v0.1.0   28      [85%]     Draft       │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  Field Mapping Preview (Amazon)                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Source Field  → Target Field    Transform   Status│ │
│  ├────────────────────────────────────────────────────┤ │
│  │ adType       → placement_type   enum_map    ✅    │ │
│  │ cost_micros  → cost             /1000000    ✅    │ │
│  │ timestamp    → ts               to_utc      ✅    │ │
│  │ conv_click_7d→ conversions      none        ✅    │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- ✅ Dataset library with metadata
- ✅ Quality score visualization
- ✅ Schema mapping editor
- ✅ Field-level transformation rules
- ✅ Coverage metrics
- ✅ Data browser with filters
- ✅ Export to multiple formats

**Interactions**:
1. View all datasets with stats
2. Click dataset → View details
3. Validate dataset → See quality report
4. Edit mapping → Visual field mapper
5. Test mapping → Preview results
6. Export dataset → Download JSONL/CSV

### 4. Analytics & Monitoring UI

**Purpose**: Monitor training progress and system health

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ 📈 Analytics & Monitoring                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Training Metrics                                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Loss Curve                                          │ │
│  │ 3.0 ┤                                               │ │
│  │ 2.5 ┤╮                                              │ │
│  │ 2.0 ┤ ╲                                             │ │
│  │ 1.5 ┤  ╲___                                         │ │
│  │ 1.0 ┤      ╲___                                     │ │
│  │ 0.5 ┤          ╲___                                 │ │
│  │ 0.0 ┼─────────────────────────────────────────────  │ │
│  │     0    500   1000  1500  2000  2500  Steps      │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  System Health                                          │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │ GPU Util │ Memory   │ Throughp │ Active Jobs      │ │
│  │ 87%      │ 14.2/16GB│ 12 tok/s │ 2 running        │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
│                                                          │
│  Adapter Performance                                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Adapter         Accuracy  Latency  Size  Requests │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ amazon_v1       92%       145ms    15MB   1,247   │ │
│  │ planning_v1     89%       132ms    12MB   2,891   │ │
│  │ creative_v1     94%       158ms    14MB   743     │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- ✅ Real-time loss curves
- ✅ GPU/memory monitoring
- ✅ Adapter performance comparison
- ✅ Request throughput tracking
- ✅ Error rate monitoring
- ✅ Cost tracking

## Technical Implementation

### Framework: Streamlit
- **Pros**: Rapid development, Python-native, great for ML/AI
- **Cons**: Less customizable than React, server-side rendering

### Alternative: FastAPI + React
- **Pros**: More control, better performance, modern UX
- **Cons**: More development time, separate frontend/backend

### Recommendation: Streamlit for MVP, React for Production

## File Structure

```
src/ui/
├── admin_app.py              # Main admin console
├── components/
│   ├── training_panel.py     # Training management
│   ├── federation_panel.py   # Federation builder
│   ├── dataset_panel.py      # Dataset management
│   └── analytics_panel.py    # Monitoring dashboard
├── templates/
│   ├── base.html
│   └── admin.html
└── static/
    ├── css/
    │   └── admin.css
    └── js/
        └── admin.js
```

## Next Steps

1. ✅ Implement Streamlit admin console
2. Add real-time WebSocket updates
3. Integrate with training pipeline
4. Add authentication (JWT)
5. Deploy behind reverse proxy
6. Add audit logging
7. Implement role-based access control

## User Flows

### Flow 1: Train New Adapter
1. Navigate to Training tab
2. Fill form (adapter type, name, dataset)
3. Configure hyperparameters
4. Click "Start Training"
5. Monitor progress in real-time
6. On completion, adapter appears in registry
7. Test adapter in Federation tab

### Flow 2: Create Federation
1. Navigate to Federation tab
2. Select base model
3. Choose retailer adapter
4. Choose task adapter
5. Select composition method
6. Click "Create Federation"
7. View visual stack
8. Test with sample prompt
9. Save federation config

### Flow 3: Manage Datasets
1. Navigate to Datasets tab
2. View dataset library
3. Click dataset → See details
4. Run validation → Quality report
5. Edit if needed
6. Export for training

---

**Status**: Design specification complete  
**Next**: Implement Streamlit UI components  
**Timeline**: 2-3 days for full implementation
