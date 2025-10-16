# Data Persistence Strategy - Complete Guide

## TL;DR

**You have 3 options**:

1. **SQLAlchemy Only** (Current) - ✅ Works now, no additional setup
2. **Hybrid** (Recommended) - SQLAlchemy + Supabase for real-time
3. **Supabase Only** - Full migration (not recommended)

**Recommendation**: Start with SQLAlchemy, add Supabase when you need real-time features.

---

## Current Setup (Already Working)

### ✅ SQLAlchemy + PostgreSQL/MySQL/SQLite

**What's implemented**:
- Complete database models (16 tables)
- Connection pooling
- Session management
- Migrations support (Alembic)
- Multi-database support

**Location**: `src/storage/database.py`, `src/storage/models.py`

**Usage**:
```python
from src.storage.database import init_db, get_db

# Initialize
db = init_db("postgresql://user:pass@localhost/rmn_db")

# Use
with db.get_session() as session:
    campaigns = session.query(Campaign).all()
```

**Pros**:
- ✅ Full control
- ✅ No vendor lock-in
- ✅ Mature ORM
- ✅ Complex queries
- ✅ ACID transactions

**Cons**:
- ❌ No real-time features
- ❌ Manual auth implementation
- ❌ No built-in storage
- ❌ Ops overhead

---

## Option 1: Keep SQLAlchemy Only

**When to choose**:
- You already have PostgreSQL infrastructure
- Don't need real-time features immediately
- Want full database control
- Have DevOps resources

**Setup**: Already done! ✅

**Cost**: $50-200/month (server) + ops time

**What you get**:
- All core functionality
- Campaign management
- Performance tracking
- Reward model training
- Analytics

**What you miss**:
- Real-time task assignment
- Live leaderboards
- Instant notifications
- Built-in auth
- File storage

---

## Option 2: Hybrid (Recommended) ⭐

**When to choose**:
- Want real-time features for Rater IDE
- Need simplified auth
- Want file storage for models
- Keep core data control

### Architecture

```
┌─────────────────────────────────────────┐
│         Application Layer               │
├─────────────────────────────────────────┤
│                                          │
│  SQLAlchemy          Supabase           │
│  (Core Data)         (Enhancements)     │
│                                          │
│  • Campaigns         • Real-time        │
│  • SKUs              • Auth             │
│  • Performance       • Storage          │
│  • Judgments         • Edge Functions   │
│  • Analytics                             │
│                                          │
└─────────────────────────────────────────┘
```

### What Goes Where

#### SQLAlchemy (Keep)
- ✅ Campaign data
- ✅ SKU catalogs
- ✅ Performance metrics
- ✅ Judgments (core data)
- ✅ Reward models
- ✅ Complex analytics
- ✅ Transactions

#### Supabase (Add)
- ✅ Real-time task assignment
- ✅ Rater authentication
- ✅ Live statistics
- ✅ Model artifact storage
- ✅ Training datasets
- ✅ WebSocket notifications

### Setup

**1. Install Supabase**:
```bash
pip install supabase
```

**2. Create Supabase Project**:
- Go to https://supabase.com
- Create project (free tier available)
- Get credentials

**3. Configure**:
```bash
# .env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
```

**4. Initialize**:
```python
from src.storage.database import init_db
from src.storage.supabase_client import init_supabase

# Both systems
db = init_db("postgresql://...")
supabase = init_supabase()  # Optional, graceful fallback

# Check availability
if supabase.is_available():
    print("✅ Real-time enabled")
```

### Example: Hybrid Workflow

```python
class RaterApp:
    def __init__(self):
        self.db = get_db()  # SQLAlchemy
        self.supabase = get_supabase()  # Supabase
    
    def assign_task(self, rater_id):
        # Complex query in PostgreSQL
        with self.db.get_session() as session:
            task = session.query(RatingTask)\
                .join(GoldenSetItem)\
                .filter(...)\
                .order_by(...)\
                .first()
            
            task.status = 'in_progress'
            session.commit()
        
        # Broadcast via Supabase real-time
        if self.supabase.is_available():
            self.supabase.update_task_status(
                task.task_id,
                'in_progress'
            )
        
        return task
```

### Cost

**Free Tier** (Perfect for pilot):
- 500MB database
- 1GB storage
- 2GB bandwidth
- Real-time, auth, storage
- **$0/month**

**Pro Tier** (Production):
- 8GB database
- 100GB storage
- 250GB bandwidth
- Daily backups
- **$25/month**

**Total with self-hosted PostgreSQL**:
- PostgreSQL: $100/month
- Supabase Pro: $25/month
- **Total: $125/month**

### Migration Path

**Phase 1**: Add Supabase (no breaking changes)
- Install client
- Configure credentials
- Keep all SQLAlchemy code
- ✅ Zero risk

**Phase 2**: Enable real-time
- Add subscriptions to Rater IDE
- Live leaderboards
- WebSocket notifications

**Phase 3**: Move auth
- Migrate to Supabase Auth
- JWT tokens
- Row-level security

**Phase 4**: Offload storage
- Model artifacts to Supabase Storage
- Training datasets
- Exports and logs

---

## Option 3: Supabase Only

**When to choose**:
- Starting from scratch
- Want fully managed solution
- Don't need complex queries
- Prefer simplicity over control

**Not recommended for this system** because:
- ❌ Complex analytics queries
- ❌ Reward model training needs
- ❌ Large-scale data processing
- ❌ Vendor lock-in risk

---

## Comparison Table

| Feature | SQLAlchemy Only | Hybrid | Supabase Only |
|---------|----------------|--------|---------------|
| **Setup Complexity** | Medium | Medium | Low |
| **Real-time** | ❌ | ✅ | ✅ |
| **Auth** | Manual | ✅ | ✅ |
| **Storage** | Manual | ✅ | ✅ |
| **Complex Queries** | ✅ | ✅ | ⚠️ Limited |
| **Transactions** | ✅ | ✅ | ⚠️ Limited |
| **Vendor Lock-in** | ✅ None | ⚠️ Partial | ❌ High |
| **Cost (pilot)** | $50-100 | $0-25 | $0-25 |
| **Cost (production)** | $100-200 | $125 | $25-100 |
| **Ops Overhead** | High | Low | Very Low |

---

## Recommendation by Use Case

### For Development/Pilot
**Use**: SQLAlchemy + SQLite
- Zero cost
- No setup
- Perfect for testing

```python
db = init_db("sqlite:///rmn_system.db")
```

### For Production (Small Scale)
**Use**: Hybrid (PostgreSQL + Supabase Free)
- Core data in PostgreSQL
- Real-time via Supabase
- $100/month total

### For Production (Large Scale)
**Use**: Hybrid (PostgreSQL + Supabase Pro)
- Dedicated PostgreSQL
- Supabase Pro for real-time
- $125/month total

### For Enterprise
**Use**: Hybrid (Managed PostgreSQL + Supabase Team)
- AWS RDS or similar
- Supabase Team plan
- $500+/month

---

## Quick Start Guide

### Current Setup (No Changes Needed)

```bash
# 1. Install dependencies (already in requirements.txt)
pip install -r requirements.txt

# 2. Initialize database
python scripts/init_database.py \
  --database-url postgresql://user:pass@localhost/rmn_db \
  --sample-data

# 3. Start applications
python -m src.runtime.multi_tenant --port 8000
python -m src.ui.rlhf_app  # Port 8001
python -m src.nde_rater.rater_app  # Port 8002
```

**✅ System works perfectly with SQLAlchemy only!**

### Add Supabase (Optional Enhancement)

```bash
# 1. Install Supabase client
pip install supabase

# 2. Create project at supabase.com

# 3. Configure
cp .env.example .env
# Edit .env with Supabase credentials

# 4. Initialize (graceful fallback if not configured)
python -c "from src.storage.supabase_client import init_supabase; init_supabase()"

# 5. Enable real-time features
# - Rater IDE gets live updates
# - Leaderboards update instantly
# - Model storage available
```

---

## What Each System Handles

### SQLAlchemy (Core Business Logic)

**Tables**:
1. `retailers` - Retailer configs
2. `brands` - Brand/manufacturer entities
3. `campaigns` - Campaign data
4. `sku_catalog` - Product catalog
5. `audience_segments` - Audience definitions
6. `performance_metrics` - Time-series data
7. `feedback` - RLHF feedback
8. `reflection_logs` - Decision audit trail
9. `rater_profiles` - Rater reliability
10. `rating_tasks` - Rating tasks
11. `judgments` - Rater judgments
12. `golden_set_items` - Calibration tasks
13. `reward_models` - Trained models
14. `rlhf_metrics` - Business KPIs

**Operations**:
- Complex joins
- Aggregations
- Transactions
- Analytics
- Reporting

### Supabase (Real-time & Enhancements)

**Features**:
1. **Real-time subscriptions**
   - New task notifications
   - Live leaderboards
   - Status updates

2. **Authentication**
   - Rater login/signup
   - JWT tokens
   - Row-level security

3. **Storage**
   - Model artifacts (LoRA adapters)
   - Training datasets
   - Exports

4. **Edge Functions**
   - Auto-checks (serverless)
   - Webhooks
   - Lightweight APIs

---

## Security Considerations

### SQLAlchemy
- Connection string encryption
- SSL/TLS for connections
- Application-level access control
- Prepared statements (SQL injection protection)

### Supabase
- Row-level security (RLS)
- JWT authentication
- API key management
- Bucket policies for storage

**Example RLS Policy**:
```sql
-- Raters can only see their own judgments
CREATE POLICY "Raters view own judgments"
ON judgments FOR SELECT
USING (auth.uid() = rater_id);
```

---

## Performance Considerations

### SQLAlchemy
- Connection pooling (10-20 connections)
- Query optimization
- Indexes on foreign keys
- Materialized views for analytics

### Supabase
- Real-time: ~1000 concurrent connections
- Storage: CDN-backed, global
- Database: Auto-scaling
- Edge Functions: <50ms cold start

---

## Final Recommendation

### ✅ Start with SQLAlchemy Only

**Why**:
- Already implemented ✅
- Zero additional cost
- No vendor dependencies
- Full control

**Then add Supabase when you need**:
- Real-time task assignment
- Live leaderboards
- Simplified auth
- Model storage

### Migration is Easy

```python
# Day 1: SQLAlchemy only
db = init_db("postgresql://...")

# Day 30: Add Supabase (no breaking changes)
supabase = init_supabase()  # Optional

# Code works with or without Supabase!
if supabase.is_available():
    supabase.subscribe_to_new_tasks(callback)
else:
    # Fallback to polling
    poll_for_new_tasks()
```

---

## Summary

**Current Status**: ✅ **Fully functional with SQLAlchemy**

**Supabase**: Optional enhancement for:
- Real-time features
- Simplified auth
- File storage
- Serverless functions

**Cost**:
- SQLAlchemy only: $50-200/month
- Hybrid (recommended): $125/month
- Supabase only: $25-100/month (not recommended)

**Next Steps**:
1. ✅ Use current SQLAlchemy setup
2. Deploy pilot with PostgreSQL
3. Add Supabase when you need real-time
4. No rush - system works great as-is!

**Files Created**:
- `src/storage/supabase_client.py` - Supabase integration
- `SUPABASE_INTEGRATION.md` - Complete guide
- `.env.example` - Configuration template

**You're ready to deploy with SQLAlchemy!** Supabase is there when you need it.
