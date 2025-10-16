# Supabase Integration Guide

## Overview

The RMN LoRA system supports **hybrid data persistence**:
- **SQLAlchemy** (PostgreSQL/MySQL/SQLite) - Core business logic, complex queries
- **Supabase** (Optional) - Real-time features, auth, storage, edge functions

## Why Supabase?

### ✅ Perfect Fit for This System

1. **Real-Time Features**
   - Live task assignment for raters
   - Instant leaderboard updates
   - Collaborative rating sessions
   - Dashboard metrics without polling

2. **Built-in Authentication**
   - Rater login/signup
   - Brand tenant isolation
   - JWT tokens
   - Row-level security

3. **Storage for ML Assets**
   - Model artifacts (LoRA adapters)
   - Training datasets
   - Logs and exports

4. **Edge Functions**
   - Auto-checks (serverless)
   - Lightweight APIs
   - Webhook handlers

5. **Managed PostgreSQL**
   - No ops overhead
   - Auto-scaling
   - Connection pooling
   - Global CDN

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   SQLAlchemy     │         │    Supabase      │         │
│  │   (Core Data)    │         │  (Real-time)     │         │
│  └──────────────────┘         └──────────────────┘         │
│          │                             │                     │
│          ↓                             ↓                     │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   PostgreSQL     │         │  Supabase Cloud  │         │
│  │   (Self-hosted)  │         │  - Auth          │         │
│  │                  │         │  - Realtime      │         │
│  │  • Campaigns     │         │  - Storage       │         │
│  │  • SKUs          │         │  - Edge Funcs    │         │
│  │  • Performance   │         │                  │         │
│  │  • Judgments     │         │  • Live Tasks    │         │
│  │  • Reward Models │         │  • Rater Auth    │         │
│  └──────────────────┘         │  • Model Files   │         │
│                                └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Install Supabase Client

```bash
pip install supabase
```

Add to `requirements.txt`:
```
supabase>=2.0.0
```

### 2. Create Supabase Project

1. Go to https://supabase.com
2. Create new project
3. Get your credentials:
   - Project URL: `https://xxxxx.supabase.co`
   - Anon/Public Key: `eyJhbGc...`
   - Service Role Key: `eyJhbGc...` (for admin operations)

### 3. Configure Environment

Create `.env` file:
```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...  # Anon key for client
SUPABASE_SERVICE_KEY=eyJhbGc...  # Service role for admin

# Existing PostgreSQL (keep for core data)
DATABASE_URL=postgresql://user:pass@localhost/rmn_db
```

### 4. Initialize in Application

```python
from src.storage.database import init_db
from src.storage.supabase_client import init_supabase

# Initialize both
db = init_db(os.getenv("DATABASE_URL"))
supabase = init_supabase()

# Check availability
if supabase.is_available():
    print("✅ Supabase real-time features enabled")
else:
    print("⚠️  Supabase not configured, using SQLAlchemy only")
```

## Use Cases

### Use Case 1: Real-Time Task Assignment

**Problem**: Raters need instant notification of new tasks

**Solution**: Supabase real-time subscriptions

```python
from src.storage.supabase_client import get_supabase

supabase = get_supabase()

# Subscribe to new tasks
def assign_to_rater(task):
    print(f"New task available: {task['task_id']}")
    # Notify rater via WebSocket
    notify_rater(task)

channel = supabase.subscribe_to_new_tasks(assign_to_rater)
```

**Frontend (JavaScript)**:
```javascript
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// Listen for new tasks
supabase
  .channel('rating_tasks')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'rating_tasks' },
    (payload) => {
      console.log('New task:', payload.new)
      showTaskNotification(payload.new)
    }
  )
  .subscribe()
```

### Use Case 2: Rater Authentication

**Problem**: Need secure login for raters with tenant isolation

**Solution**: Supabase Auth + Row-Level Security

```python
from src.storage.supabase_client import get_supabase

supabase = get_supabase()

# Sign up new rater
response = supabase.sign_up_rater(
    email="rater@example.com",
    password="secure_password",
    metadata={
        "rater_id": "rater_001",
        "name": "John Doe",
        "tenant_id": "acme_corp"
    }
)

# Sign in
auth_response = supabase.sign_in_rater(
    email="rater@example.com",
    password="secure_password"
)

# Get JWT token
token = auth_response.session.access_token
```

**Row-Level Security (RLS) in Supabase**:
```sql
-- Only allow raters to see their own judgments
CREATE POLICY "Raters can view own judgments"
ON judgments FOR SELECT
USING (auth.uid() = rater_id);

-- Only allow raters to insert their own judgments
CREATE POLICY "Raters can insert own judgments"
ON judgments FOR INSERT
WITH CHECK (auth.uid() = rater_id);
```

### Use Case 3: Live Leaderboard

**Problem**: Show real-time rater statistics

**Solution**: Supabase real-time + materialized views

```python
# Subscribe to rater stats updates
def update_leaderboard(rater_data):
    print(f"Rater {rater_data['name']}: {rater_data['total_judgments']} judgments")

supabase.subscribe_to_rater_stats("rater_001", update_leaderboard)
```

**Frontend**:
```javascript
// Live leaderboard
supabase
  .channel('leaderboard')
  .on('postgres_changes',
    { event: 'UPDATE', schema: 'public', table: 'rater_profiles' },
    (payload) => {
      updateLeaderboardRow(payload.new)
    }
  )
  .subscribe()
```

### Use Case 4: Model Artifact Storage

**Problem**: Store LoRA adapters and training data

**Solution**: Supabase Storage

```python
from src.storage.supabase_client import get_supabase

supabase = get_supabase()

# Upload LoRA adapter
with open("models/adapters/amazon_v1.safetensors", "rb") as f:
    supabase.upload_model_artifact(
        bucket="model-artifacts",
        path="adapters/amazon/v1.safetensors",
        f.read()
    )

# Get public URL
url = supabase.get_public_url(
    "model-artifacts",
    "adapters/amazon/v1.safetensors"
)

# Download for inference
model_bytes = supabase.download_model_artifact(
    "model-artifacts",
    "adapters/amazon/v1.safetensors"
)
```

**Create Storage Buckets in Supabase**:
```sql
-- Create buckets
INSERT INTO storage.buckets (id, name, public)
VALUES 
  ('model-artifacts', 'model-artifacts', false),
  ('training-data', 'training-data', false),
  ('exports', 'exports', true);

-- Set policies
CREATE POLICY "Authenticated users can upload models"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'model-artifacts');
```

### Use Case 5: Edge Functions for Auto-Checks

**Problem**: Run auto-checks without spinning up servers

**Solution**: Supabase Edge Functions (Deno)

**Create Edge Function** (`supabase/functions/auto-check/index.ts`):
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { task_type, candidate_a, candidate_b } = await req.json()
  
  // Run auto-checks
  const results = {
    candidate_a: runChecks(task_type, candidate_a),
    candidate_b: runChecks(task_type, candidate_b)
  }
  
  return new Response(
    JSON.stringify(results),
    { headers: { "Content-Type": "application/json" } }
  )
})

function runChecks(taskType: string, candidate: any) {
  // JSON validation, SQL parsing, etc.
  return {
    json_valid: true,
    sql_valid: true,
    // ...
  }
}
```

**Invoke from Python**:
```python
supabase = get_supabase()

results = supabase.invoke_edge_function(
    "auto-check",
    {
        "task_type": "tool_call_qa",
        "candidate_a": {...},
        "candidate_b": {...}
    }
)
```

## Data Distribution Strategy

### What Goes Where?

#### SQLAlchemy (Core PostgreSQL)
✅ **Use for**:
- Campaign data
- SKU catalogs
- Performance metrics
- Historical data
- Complex joins
- Transactions
- Analytics queries
- Reward model training

**Why**: Complex business logic, ACID transactions, mature ORM

#### Supabase
✅ **Use for**:
- Real-time task assignment
- Rater authentication
- Live statistics
- Model artifact storage
- Training dataset files
- Webhook handlers
- Lightweight APIs

**Why**: Real-time, auth, storage, serverless functions

## Migration Path

### Phase 1: Add Supabase (No Breaking Changes)

1. Install Supabase client
2. Configure credentials
3. Keep all existing SQLAlchemy code
4. Add Supabase for new features only

**No changes to existing code!**

### Phase 2: Enable Real-Time Features

1. Add real-time subscriptions to Rater IDE
2. Implement live leaderboards
3. Add WebSocket notifications

### Phase 3: Move Auth to Supabase

1. Migrate rater authentication
2. Implement JWT tokens
3. Add row-level security

### Phase 4: Offload Storage

1. Move model artifacts to Supabase Storage
2. Store training datasets
3. Archive old data

## Example: Hybrid Rater App

```python
from src.storage.database import get_db
from src.storage.supabase_client import get_supabase

class HybridRaterApp:
    def __init__(self):
        self.db = get_db()  # SQLAlchemy
        self.supabase = get_supabase()  # Supabase
    
    def assign_task(self, rater_id: str):
        # Get task from PostgreSQL (complex query)
        with self.db.get_session() as session:
            task = session.query(RatingTask)\
                .filter(RatingTask.status == 'pending')\
                .order_by(RatingTask.priority.desc())\
                .first()
        
        if not task:
            return None
        
        # Update in PostgreSQL
        task.status = 'in_progress'
        task.assigned_at = datetime.utcnow()
        session.commit()
        
        # Broadcast via Supabase real-time
        if self.supabase.is_available():
            self.supabase.update_task_status(
                task.task_id,
                'in_progress',
                assigned_to=rater_id
            )
        
        return task
    
    def submit_judgment(self, judgment_data: dict):
        # Save to PostgreSQL (core data)
        with self.db.get_session() as session:
            judgment = Judgment(**judgment_data)
            session.add(judgment)
            session.commit()
        
        # Broadcast via Supabase (real-time update)
        if self.supabase.is_available():
            self.supabase.insert_judgment_realtime(judgment_data)
        
        return judgment
    
    def subscribe_to_tasks(self, callback):
        # Real-time subscription (Supabase only)
        if self.supabase.is_available():
            return self.supabase.subscribe_to_new_tasks(callback)
        else:
            # Fallback: polling
            return self._poll_tasks(callback)
```

## Cost Comparison

### Self-Hosted PostgreSQL
- **Pros**: Full control, no vendor lock-in
- **Cons**: Ops overhead, no real-time, no auth, no storage
- **Cost**: $50-200/month (server) + ops time

### Supabase Free Tier
- **Includes**:
  - 500MB database
  - 1GB file storage
  - 2GB bandwidth
  - Real-time, auth, storage
- **Cost**: **$0/month**
- **Perfect for**: Development, pilot

### Supabase Pro ($25/month)
- **Includes**:
  - 8GB database
  - 100GB file storage
  - 250GB bandwidth
  - Daily backups
  - Email support
- **Cost**: **$25/month**
- **Perfect for**: Production (5 retailers, 25k judgments/month)

### Hybrid Approach (Recommended)
- Self-hosted PostgreSQL: $100/month
- Supabase Pro: $25/month
- **Total**: $125/month
- **Get**: Core data control + real-time features

## Security Considerations

### Row-Level Security (RLS)

Enable RLS for multi-tenant isolation:

```sql
-- Enable RLS
ALTER TABLE rating_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE judgments ENABLE ROW LEVEL SECURITY;

-- Raters can only see tasks assigned to them
CREATE POLICY "Raters see assigned tasks"
ON rating_tasks FOR SELECT
USING (
  assigned_to = auth.jwt() ->> 'rater_id'
  OR status = 'pending'
);

-- Brands can only see their own data
CREATE POLICY "Brands see own campaigns"
ON campaigns FOR SELECT
USING (brand_id = auth.jwt() ->> 'brand_id');
```

### API Keys

- **Anon Key**: Use in frontend (public)
- **Service Role Key**: Use in backend (private, admin access)

```python
# Backend (full access)
supabase = init_supabase(
    url=SUPABASE_URL,
    key=SUPABASE_SERVICE_KEY  # Service role
)

# Frontend (restricted)
const supabase = createClient(
  SUPABASE_URL,
  SUPABASE_ANON_KEY  // Anon key
)
```

## Recommendation

### ✅ Use Hybrid Approach

**Start with**:
1. Keep SQLAlchemy for core data (already implemented)
2. Add Supabase for real-time features (optional enhancement)
3. Use Supabase Storage for model artifacts
4. Implement auth with Supabase (easier than custom JWT)

**Benefits**:
- ✅ No breaking changes to existing code
- ✅ Real-time features when needed
- ✅ Managed auth and storage
- ✅ Can remove Supabase later if needed
- ✅ Best of both worlds

**Quick Start**:
```bash
# 1. Install
pip install supabase

# 2. Configure
echo "SUPABASE_URL=https://xxx.supabase.co" >> .env
echo "SUPABASE_KEY=eyJhbGc..." >> .env

# 3. Initialize (optional, graceful fallback)
from src.storage.supabase_client import init_supabase
supabase = init_supabase()

# 4. Use real-time features if available
if supabase.is_available():
    supabase.subscribe_to_new_tasks(handle_task)
```

**You don't need Supabase immediately**, but it's highly recommended for:
- Real-time rater IDE
- Live leaderboards
- Model artifact storage
- Simplified auth

The system works fine with just SQLAlchemy + PostgreSQL!
