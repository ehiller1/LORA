# RMN LoRA System - UI Visual Guide

## Complete UI Ecosystem

```
┌─────────────────────────────────────────────────────────────────────┐
│                     RMN LoRA System UIs                              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐
│   Main Demo UI    │  │  Admin Console    │  │   RLHF/NDE UI    │
│   (Port 8501)     │  │   (Port 8501)     │  │  (Ports 8001-2)  │
├───────────────────┤  ├───────────────────┤  ├──────────────────┤
│ Brand Managers    │  │ ML Engineers      │  │ Domain Experts   │
│ Campaign Planning │  │ Training/Ops      │  │ Quality Review   │
└───────────────────┘  └───────────────────┘  └──────────────────┘
```

---

## 1. Main Demo UI - Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🎯 RMN LoRA System Demo                                      [⚙️ Menu] │
│ Composable LoRA Adapters for Retail Media Network Optimization        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────────┐                                                        │
│ │ ⚙️ Config   │  [📥 Data] [📋 Plan] [💰 Optimize] [📊 Measure]      │
│ │             │  [✨ Creative] [🔧 Ops]                                │
│ │ Exec Mode:  │                                                        │
│ │ ● Mfr View  │  ┌──────────────────────────────────────────────────┐ │
│ │ ○ Alpha     │  │                                                   │ │
│ │ ○ Beta      │  │  TAB CONTENT AREA                                │ │
│ │             │  │                                                   │ │
│ │ Adapters:   │  │  • Data harmonization                            │ │
│ │ ✅ Base     │  │  • AI planning                                   │ │
│ │ 🔧 Planning │  │  • Budget optimization                           │ │
│ │ 🔧 Mapping  │  │  • Experiment design                             │ │
│ │             │  │  • Creative generation                           │ │
│ │ Status:     │  │  • Operations logs                               │ │
│ │ Quality 94% │  │                                                   │ │
│ │ Campaigns 18│  │                                                   │ │
│ │ Budget $2.5M│  │                                                   │ │
│ └─────────────┘  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### Data Tab Detail
```
┌────────────────────────────────────────────────────────────────────────┐
│ 📥 Data Harmonization                                                  │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────────────────────────┐  ┌─────────────────────────────────┐ │
│ │ Retailer Alpha              │  │ Retailer Beta                   │ │
│ │ Format: CSV | TZ: CST       │  │ Format: JSONL | TZ: PST        │ │
│ │ Currency: USD               │  │ Currency: EUR                   │ │
│ │                             │  │                                 │ │
│ │ [📂 Load Alpha Data]        │  │ [📂 Load Beta Data]            │ │
│ │ [🔄 Harmonize Alpha]        │  │ [🔄 Harmonize Beta]            │ │
│ │                             │  │                                 │ │
│ │ Status: ✅ Loaded           │  │ Status: ✅ Loaded              │ │
│ │ Rows: 10,000                │  │ Rows: 8,000                    │ │
│ │ Enum Coverage: 98%          │  │ Enum Coverage: 92%             │ │
│ │ Join Rate: 97%              │  │ Join Rate: 95%                 │ │
│ └─────────────────────────────┘  └─────────────────────────────────┘ │
│                                                                         │
│ Mapping Validation Summary:                                            │
│ ┌──────────────────────────────────────────────────────────────────┐  │
│ │ Total Events: 18,000 | Validated Fields: 42/45 | Gaps: 3 ⚠️     │  │
│ │                                                                   │  │
│ │ Mapping Gaps:                                                    │  │
│ │ • Field 'inventory_type' value 'partner' not in RMIS taxonomy   │  │
│ │ • Field 'audience_segment' missing for 5% of events             │  │
│ │ • Timezone conversion accuracy: 99.2%                            │  │
│ └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Admin Console - Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🎛️ LoRA Training & Management Console                       [⚙️ Menu] │
│ Train adapters, compose federations, manage datasets                   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────────┐                                                        │
│ │ 🎛️ Admin    │  [🚀 Training] [🔗 Federation] [📊 Datasets]          │
│ │             │  [📈 Analytics]                                        │
│ │ Status:     │                                                        │
│ │ Jobs: 2     │  ┌──────────────────────────────────────────────────┐ │
│ │ Adapters: 4 │  │                                                   │ │
│ │             │  │  TAB CONTENT AREA                                │ │
│ │ Actions:    │  │                                                   │ │
│ │ [🚀 Train]  │  │  • Training job management                       │ │
│ │ [🔗 Fed]    │  │  • Adapter federation                            │ │
│ │ [📊 Data]   │  │  • Dataset library                               │ │
│ │             │  │  • Schema mappings                               │ │
│ │ Resources:  │  │  • Analytics dashboard                           │ │
│ │ 📖 Docs     │  │                                                   │ │
│ │ 🎓 Guide    │  │                                                   │ │
│ │ 💬 Support  │  │                                                   │ │
│ └─────────────┘  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### Training Tab Detail
```
┌────────────────────────────────────────────────────────────────────────┐
│ 🚀 LoRA Training Management                                            │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────────────────────────────────────┐  ┌───────────────────┐   │
│ │ 🎯 Create Training Job                  │  │ 📊 Queue Status   │   │
│ │                                         │  │                   │   │
│ │ Adapter Type: [Retailer ▼]             │  │ Active: 2         │   │
│ │ Name: [amazon_schema_v2_______]        │  │ Completed: 15     │   │
│ │ Base Model: [Llama-3.1-8B ▼]           │  │ Queue: 0          │   │
│ │ Training Type: [SFT ▼]                 │  │                   │   │
│ │ Dataset: [datasets/amazon.jsonl___]    │  │ [🔄 Refresh]      │   │
│ │ Epochs: [===|===] 3                    │  └───────────────────┘   │
│ │                                         │                           │
│ │ ▼ Advanced Settings                    │                           │
│ │ LoRA Rank: 16    Batch: 4              │                           │
│ │ LoRA Alpha: 32   LR: 0.0002            │                           │
│ │ Quantization: [4-bit ▼]                │                           │
│ │                                         │                           │
│ │ [🚀 Start Training]                     │                           │
│ └─────────────────────────────────────────┘                           │
│                                                                         │
│ 🔄 Active & Recent Jobs                                                │
│ ┌──────────────────────────────────────────────────────────────────┐  │
│ │ ▶ amazon_schema_v1 - RUNNING                                     │  │
│ │   Job: job_001 | Type: Retailer | Started: 2024-10-15 10:30     │  │
│ │   Progress: [==============>        ] 65%                        │  │
│ │   Epoch: 2/3 | Loss: 1.234 | ETA: 45 min                        │  │
│ │                                                                   │  │
│ │   Config: rank=16, alpha=32, batch=4, lr=0.0002, quant=4bit     │  │
│ └──────────────────────────────────────────────────────────────────┘  │
│ ┌──────────────────────────────────────────────────────────────────┐  │
│ │ ✓ planning_v1 - COMPLETED                                        │  │
│ │   Job: job_002 | Completed: 2024-10-14 15:20                    │  │
│ │   Final Loss: 0.872 | Accuracy: 91.5% | Size: 12MB              │  │
│ └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### Federation Tab Detail
```
┌────────────────────────────────────────────────────────────────────────┐
│ 🔗 LoRA Federation & Composition                                       │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────────────────────────┐  ┌─────────────────────────────────┐ │
│ │ 🔗 Compose Federation       │  │ 🎯 Active Federation            │ │
│ │                             │  │                                 │ │
│ │ Base Model:                 │  │ ID: fed_20241015_103000         │ │
│ │ [Llama-3.1-8B ▼]            │  │ Created: 2024-10-15 10:30       │ │
│ │                             │  │                                 │ │
│ │ Retailer Adapter:           │  │ Composition Stack:              │ │
│ │ [amazon_schema_v1 ▼]        │  │ ┌─────────────────────────────┐ │ │
│ │                             │  │ │ Base: Llama-3.1-8B          │ │ │
│ │ Task Adapter:               │  │ └─────────────────────────────┘ │ │
│ │ [planning_v1 ▼]             │  │              ↓                  │ │
│ │                             │  │ ┌─────────────────────────────┐ │ │
│ │ Composition Method:         │  │ │ Retailer: amazon_schema_v1  │ │ │
│ │ ○ Additive (Sum)            │  │ │ (~15MB, rank=16)            │ │ │
│ │ ● Gated (Routing)           │  │ └─────────────────────────────┘ │ │
│ │ ○ Sequential (Chain)        │  │              ↓                  │ │
│ │                             │  │ ┌─────────────────────────────┐ │ │
│ │ [🔗 Create Federation]      │  │ │ Task: planning_v1           │ │ │
│ │                             │  │ │ (~12MB, rank=16)            │ │ │
│ └─────────────────────────────┘  │ └─────────────────────────────┘ │ │
│                                   │              ↓                  │ │
│                                   │ ┌─────────────────────────────┐ │ │
│                                   │ │ Federated Model (Ready)     │ │ │
│                                   │ └─────────────────────────────┘ │ │
│                                   │                                 │ │
│                                   │ Total Size: 8.2GB               │ │
│                                   │ Overhead: 27MB                  │ │
│                                   │ Method: Gated                   │ │
│                                   │ Status: Ready                   │ │
│                                   │                                 │ │
│                                   │ [🧪 Test] [💾 Save] [🗑️ Clear] │ │
│                                   └─────────────────────────────────┘ │
│                                                                         │
│ 🧪 Test Federation                                                     │
│ ┌──────────────────────────────────────────────────────────────────┐  │
│ │ Prompt: [Map 'adType' field with value 'sp' to RMIS schema___]  │  │
│ │                                                                   │  │
│ │ [▶️ Run Inference]                                                │  │
│ │                                                                   │  │
│ │ Response:                                                        │  │
│ │ > The field 'adType' with value 'sp' maps to 'placement_type'   │  │
│ │ > with canonical value 'sponsored_product' in RMIS schema.       │  │
│ │                                                                   │  │
│ │ Metrics: 32 tokens | 145ms latency | 2 adapters used            │  │
│ │ Adapters: ✅ amazon_schema_v1, ✅ planning_v1                    │  │
│ └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Color Palette Reference

```
┌─────────────────────────────────────────────────────────────┐
│ Primary Colors                                              │
├─────────────────────────────────────────────────────────────┤
│ ██ #3b82f6  Primary Blue    (Actions, Links, Selected)     │
│ ██ #1f2937  Dark Gray       (Sidebar, Headers)             │
├─────────────────────────────────────────────────────────────┤
│ Semantic Colors                                             │
├─────────────────────────────────────────────────────────────┤
│ ██ #10b981  Success Green   (Completed, Active, Pass)      │
│ ██ #f59e0b  Warning Amber   (In Progress, Attention)       │
│ ██ #ef4444  Error Red       (Failed, Errors, Critical)     │
│ ██ #3b82f6  Info Blue       (Information, Tips)            │
├─────────────────────────────────────────────────────────────┤
│ Neutral Colors                                              │
├─────────────────────────────────────────────────────────────┤
│ ██ #f8f9fa  Background      (Main area)                    │
│ ██ #ffffff  Card Background (Content cards)                │
│ ██ #e5e7eb  Border Gray     (Dividers, borders)            │
│ ██ #6b7280  Text Gray       (Secondary text)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Component Library

### Metrics Display
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ GPU Util    │  │ Memory      │  │ Throughput  │
│             │  │             │  │             │
│    87%      │  │ 14.2/16 GB  │  │  12 tok/s   │
│    ↑ 5%    │  │             │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Progress Bar
```
┌────────────────────────────────────────────────────┐
│ Training Progress                                  │
│ [==============>                    ] 65%          │
│ Epoch 2/3 | Loss: 1.234 | ETA: 45 min            │
└────────────────────────────────────────────────────┘
```

### Status Badges
```
✅ Active    ⚠️ Warning    ❌ Error    🔵 Info
```

### Buttons
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ 🚀 Primary       │  │ Secondary        │  │ 🗑️ Danger        │
│ (Blue, Solid)    │  │ (Outlined)       │  │ (Red, Solid)     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### Cards
```
┌────────────────────────────────────────────────────┐
│ Card Title                                         │
├────────────────────────────────────────────────────┤
│                                                    │
│ Card content with white background,                │
│ subtle shadow, and rounded corners.                │
│                                                    │
│ [Action Button]                                    │
└────────────────────────────────────────────────────┘
```

---

## 5. Responsive Breakpoints

```
Desktop (>1200px)
┌─────────────────────────────────────────────────────┐
│ [Sidebar]  [Main Content - Full Width]             │
└─────────────────────────────────────────────────────┘

Tablet (768px - 1200px)
┌──────────────────────────────────────────────┐
│ [Collapsed]  [Main Content - Adjusted]       │
└──────────────────────────────────────────────┘

Mobile (<768px)
┌─────────────────────────┐
│ [☰ Menu]                │
│ [Main Content - Stack]  │
└─────────────────────────┘
```

---

## 6. User Journey Map

```
Brand Manager Journey
┌─────────────────────────────────────────────────────────┐
│ 1. Open Main Demo                                       │
│    ↓                                                    │
│ 2. Load retailer data (Data Tab)                       │
│    ↓                                                    │
│ 3. Harmonize to RMIS                                   │
│    ↓                                                    │
│ 4. Generate campaign plan (Plan Tab)                   │
│    ↓                                                    │
│ 5. Adjust constraints (Optimize Tab)                   │
│    ↓                                                    │
│ 6. Design experiment (Measure Tab)                     │
│    ↓                                                    │
│ 7. Generate creatives (Creative Tab)                   │
│    ↓                                                    │
│ 8. Review logs (Ops Tab)                               │
└─────────────────────────────────────────────────────────┘

ML Engineer Journey
┌─────────────────────────────────────────────────────────┐
│ 1. Open Admin Console                                   │
│    ↓                                                    │
│ 2. Create training job (Training Tab)                  │
│    ↓                                                    │
│ 3. Monitor progress                                     │
│    ↓                                                    │
│ 4. Compose federation (Federation Tab)                 │
│    ↓                                                    │
│ 5. Test inference                                       │
│    ↓                                                    │
│ 6. Validate datasets (Datasets Tab)                    │
│    ↓                                                    │
│ 7. Monitor analytics (Analytics Tab)                   │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Integration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Complete System Flow                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌──────────────┐
│ Admin Console │────>│ Adapter       │<────│ Main Demo    │
│               │     │ Registry      │     │              │
│ • Train       │     │               │     │ • Use        │
│ • Compose     │     │ • Retailers   │     │ • Plan       │
│ • Manage      │     │ • Tasks       │     │ • Optimize   │
└───────────────┘     │ • Federations │     └──────────────┘
        │             └───────────────┘             │
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌───────────────────┐
                    │ Feedback Loop     │
                    │                   │
                    │ • RLHF UI         │
                    │ • NDE Rater       │
                    │ • DPO Export      │
                    └───────────────────┘
```

---

**Status**: ✅ Complete Visual Guide  
**Purpose**: Reference for UI design and layout  
**Use**: Share with designers, developers, stakeholders
