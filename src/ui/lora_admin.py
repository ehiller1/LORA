"""LoRA Admin Console - Training, Federation, and Dataset Management."""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="RMN LoRA Admin",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS - Integrated from index.css and App.css
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600;700&display=swap');
    
    /* Base styles */
    * {
        font-family: 'Archivo', sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    .main { 
        background-color: #ffffff;
        max-width: 1280px;
        margin: 0 auto;
    }
    
    /* Card styles */
    .stMetric, .card { 
        background: white;
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid rgba(240, 240, 240, 0.5);
    }
    
    /* Typography */
    h1 { 
        color: hsl(240, 10%, 3.9%);
        font-weight: 700;
        animation: fadeIn 0.6s ease-out forwards;
    }
    h2 { 
        color: hsl(240, 10%, 3.9%);
        font-weight: 600;
        margin-top: 2rem;
        animation: slideUp 0.5s ease-out forwards;
    }
    h3 {
        color: hsl(240, 10%, 3.9%);
        font-weight: 500;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: white;
        padding: 8px;
        border-radius: 0.75rem;
        border: 1px solid hsl(240, 5.9%, 90%);
    }
    .stTabs [data-baseweb="tab"] { 
        height: 50px;
        padding: 0 24px;
        background-color: hsl(240, 4.8%, 95.9%);
        border-radius: 0.75rem;
        font-weight: 500;
        transition: all 300ms;
    }
    .stTabs [aria-selected="true"] { 
        background-color: hsl(142, 100%, 35%);
        color: white;
    }
    
    /* Buttons */
    .stButton > button { 
        border-radius: 0.75rem;
        font-weight: 500;
        transition: all 300ms;
        font-family: 'Archivo', sans-serif;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: hsl(240, 10%, 3.9%);
    }
    [data-testid="stSidebar"] * { 
        color: white !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes scaleIn {
        from {
            transform: scale(0.95);
            opacity: 0;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* Glass morphism effect */
    .glass {
        background: white;
        border: 1px solid rgba(240, 240, 240, 0.5);
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background-color: hsl(142, 100%, 35%);
        border-radius: 0.75rem;
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 0.75rem;
        animation: scaleIn 0.4s ease-out forwards;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        border-radius: 0.75rem;
        font-weight: 500;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        border-radius: 0.75rem;
        border: 1px solid hsl(240, 5.9%, 90%);
    }
    
    /* Success/Warning/Error boxes */
    .stSuccess {
        background-color: hsl(142, 100%, 35%, 0.1);
        border-left: 4px solid hsl(142, 100%, 35%);
        border-radius: 0.75rem;
    }
    .stWarning {
        background-color: hsl(31, 100%, 50%, 0.1);
        border-left: 4px solid hsl(31, 100%, 50%);
        border-radius: 0.75rem;
    }
    .stError {
        background-color: hsl(4, 92%, 49%, 0.1);
        border-left: 4px solid hsl(4, 92%, 49%);
        border-radius: 0.75rem;
    }
    .stInfo {
        background-color: hsl(199, 100%, 50%, 0.1);
        border-left: 4px solid hsl(199, 100%, 50%);
        border-radius: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'training_jobs' not in st.session_state:
    st.session_state.training_jobs = []
if 'adapters' not in st.session_state:
    st.session_state.adapters = [
        {'name': 'amazon_schema_v1', 'type': 'Retailer', 'size_mb': 15, 'accuracy': 92},
        {'name': 'walmart_schema_v1', 'type': 'Retailer', 'size_mb': 14, 'accuracy': 89},
        {'name': 'planning_v1', 'type': 'Task', 'size_mb': 12, 'accuracy': 91},
        {'name': 'creative_v1', 'type': 'Task', 'size_mb': 13, 'accuracy': 94}
    ]
if 'active_federation' not in st.session_state:
    st.session_state.active_federation = None

# Sidebar
with st.sidebar:
    st.title("🎛️ LoRA Admin")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Jobs", len([j for j in st.session_state.training_jobs if j.get('status') == 'running']))
    with col2:
        st.metric("Adapters", len(st.session_state.adapters))
    
    st.markdown("---")
    st.subheader("Quick Actions")
    
    if st.button("🚀 New Training", use_container_width=True):
        st.session_state.active_tab = 0
    if st.button("🔗 Federation", use_container_width=True):
        st.session_state.active_tab = 1
    if st.button("📊 Datasets", use_container_width=True):
        st.session_state.active_tab = 2

# Header
st.title("🎛️ LoRA Training & Management Console")
st.markdown("**Train adapters, compose federations, manage datasets**")

# Main tabs
tabs = st.tabs(["🚀 Training", "🔗 Federation", "📊 Datasets", "📈 Analytics"])

# ============================================================================
# TAB 1: TRAINING
# ============================================================================
with tabs[0]:
    st.header("LoRA Training Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Create Training Job")
        
        with st.form("training_form"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                adapter_type = st.selectbox("Adapter Type", ["Retailer", "Task", "Domain"])
                adapter_name = st.text_input("Name", placeholder="e.g., amazon_schema_v2")
                base_model = st.selectbox("Base Model", [
                    "meta-llama/Llama-3.1-8B-Instruct",
                    "mistralai/Mistral-7B-Instruct-v0.2"
                ])
            
            with col_b:
                training_type = st.selectbox("Training Type", ["SFT", "DPO", "QLoRA"])
                dataset_path = st.text_input("Dataset", placeholder="datasets/sft/retailer_amazon.jsonl")
                num_epochs = st.slider("Epochs", 1, 10, 3)
            
            with st.expander("Advanced Settings"):
                col_c, col_d, col_e = st.columns(3)
                with col_c:
                    lora_r = st.number_input("LoRA Rank", 8, 64, 16)
                    lora_alpha = st.number_input("LoRA Alpha", 8, 128, 32)
                with col_d:
                    batch_size = st.number_input("Batch Size", 1, 32, 4)
                    learning_rate = st.number_input("Learning Rate", 0.00001, 0.001, 0.0002, format="%.5f")
                with col_e:
                    quantization = st.selectbox("Quantization", ["None", "4-bit", "8-bit"])
                    gradient_checkpointing = st.checkbox("Gradient Checkpointing", True)
            
            submitted = st.form_submit_button("🚀 Start Training", type="primary", use_container_width=True)
            
            if submitted and adapter_name and dataset_path:
                job = {
                    'id': f"job_{len(st.session_state.training_jobs) + 1:03d}",
                    'name': adapter_name,
                    'type': adapter_type,
                    'status': 'running',
                    'progress': 0,
                    'epochs': num_epochs,
                    'current_epoch': 0,
                    'loss': 2.5,
                    'started_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.training_jobs.append(job)
                st.success(f"✅ Training job '{adapter_name}' started!")
                st.rerun()
    
    with col2:
        st.subheader("📊 Queue Status")
        active = len([j for j in st.session_state.training_jobs if j.get('status') == 'running'])
        completed = len([j for j in st.session_state.training_jobs if j.get('status') == 'completed'])
        
        st.metric("Active", active)
        st.metric("Completed", completed)
        st.metric("Queue", 0)
        
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Active jobs
    if st.session_state.training_jobs:
        st.markdown("---")
        st.subheader("🔄 Active & Recent Jobs")
        
        for job in reversed(st.session_state.training_jobs[-5:]):
            with st.expander(f"{job['name']} - {job.get('status', 'unknown').upper()}", 
                           expanded=(job.get('status') == 'running')):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"**ID:** {job['id']}")
                    st.markdown(f"**Type:** {job['type']}")
                with col2:
                    st.markdown(f"**Started:** {job['started_at']}")
                with col3:
                    st.markdown(f"**Epoch:** {job['current_epoch']}/{job['epochs']}")
                    st.markdown(f"**Loss:** {job.get('loss', 0):.3f}")
                with col4:
                    if job.get('status') == 'running':
                        progress = min(job['progress'] + np.random.randint(5, 15), 100)
                        job['progress'] = progress
                        job['current_epoch'] = int(progress / 100 * job['epochs'])
                        job['loss'] = max(0.5, 2.5 - (progress / 100) * 2.0)
                        
                        st.progress(progress / 100)
                        st.markdown(f"**{progress}%**")
                        
                        if progress >= 100:
                            job['status'] = 'completed'
                            st.session_state.adapters.append({
                                'name': job['name'],
                                'type': job['type'],
                                'size_mb': np.random.randint(10, 20),
                                'accuracy': np.random.uniform(85, 95)
                            })
                    else:
                        st.success("✅ Done")

# ============================================================================
# TAB 2: FEDERATION
# ============================================================================
with tabs[1]:
    st.header("LoRA Federation & Composition")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔗 Compose Federation")
        
        base_model = st.selectbox("Base Model", [
            "meta-llama/Llama-3.1-8B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.2"
        ], key="fed_base")
        
        retailer_adapters = [a['name'] for a in st.session_state.adapters if a['type'] == 'Retailer']
        task_adapters = [a['name'] for a in st.session_state.adapters if a['type'] == 'Task']
        
        st.markdown("**Retailer Adapter:**")
        retailer_adapter = st.selectbox("Select", ["None"] + retailer_adapters, key="fed_retailer")
        
        st.markdown("**Task Adapter:**")
        task_adapter = st.selectbox("Select", ["None"] + task_adapters, key="fed_task")
        
        st.markdown("**Composition Method:**")
        composition_method = st.radio("Method", 
            ["Additive (Sum)", "Gated (Routing)", "Sequential (Chain)"], key="fed_method")
        
        if st.button("🔗 Create Federation", type="primary", use_container_width=True):
            if retailer_adapter != "None" or task_adapter != "None":
                st.session_state.active_federation = {
                    'id': f"fed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'base_model': base_model,
                    'retailer': retailer_adapter if retailer_adapter != "None" else None,
                    'task': task_adapter if task_adapter != "None" else None,
                    'method': composition_method,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("✅ Federation created!")
                st.rerun()
    
    with col2:
        st.subheader("🎯 Active Federation")
        
        if st.session_state.active_federation:
            fed = st.session_state.active_federation
            
            st.markdown(f"**ID:** `{fed['id']}`")
            st.markdown(f"**Created:** {fed['created_at']}")
            st.markdown("---")
            
            # Visual stack
            st.markdown("**Composition Stack:**")
            st.code(f"""
┌─────────────────────────────┐
│ Base: {fed['base_model'][:20]}...
└─────────────────────────────┘
              ↓""")
            
            if fed['retailer']:
                st.code(f"""
┌─────────────────────────────┐
│ Retailer: {fed['retailer']}
│ (~15MB, rank=16)
└─────────────────────────────┘
              ↓""")
            
            if fed['task']:
                st.code(f"""
┌─────────────────────────────┐
│ Task: {fed['task']}
│ (~12MB, rank=16)
└─────────────────────────────┘
              ↓""")
            
            st.code("""
┌─────────────────────────────┐
│ Federated Model (Ready)
└─────────────────────────────┘""")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Size", "8.2GB")
                st.metric("Overhead", "27MB")
            with col_b:
                st.metric("Method", fed['method'].split()[0])
                st.metric("Status", "Ready")
            
            if st.button("🧪 Test", use_container_width=True):
                st.info("Running test...")
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.active_federation = None
                st.rerun()
        else:
            st.info("No active federation")
    
    # Testing section
    if st.session_state.active_federation:
        st.markdown("---")
        st.subheader("🧪 Test Federation")
        
        test_prompt = st.text_area("Prompt", 
            value="Map 'adType' field with value 'sp' to RMIS schema", height=100)
        
        if st.button("▶️ Run Inference", type="primary"):
            with st.spinner("Running..."):
                import time
                time.sleep(1)
                
                st.success("✅ Complete!")
                st.markdown("**Response:**")
                st.markdown("> The field 'adType' with value 'sp' maps to 'placement_type' = 'sponsored_product'")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Tokens", 32)
                with col2:
                    st.metric("Latency", "145ms")
                with col3:
                    adapters_used = sum([1 for x in [st.session_state.active_federation['retailer'], 
                                                      st.session_state.active_federation['task']] if x])
                    st.metric("Adapters", adapters_used)

# ============================================================================
# TAB 3: DATASETS
# ============================================================================
with tabs[2]:
    st.header("Datasets & Schema Mappings")
    
    subtabs = st.tabs(["📊 Datasets", "🗺️ Mappings", "📁 Browser"])
    
    # Datasets
    with subtabs[0]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📊 Training Datasets")
            
            datasets = [
                {'Name': 'retailer_amazon_sft', 'Type': 'SFT', 'Size': '2.3MB', 'Examples': 2847, 'Quality': 95},
                {'Name': 'task_planning_sft', 'Type': 'SFT', 'Size': '4.1MB', 'Examples': 5123, 'Quality': 92},
                {'Name': 'policy_creative_dpo', 'Type': 'DPO', 'Size': '1.8MB', 'Examples': 1456, 'Quality': 97},
                {'Name': 'retailer_walmart_sft', 'Type': 'SFT', 'Size': '2.1MB', 'Examples': 2634, 'Quality': 93}
            ]
            
            df = pd.DataFrame(datasets)
            st.dataframe(df, use_container_width=True, hide_index=True,
                column_config={'Quality': st.column_config.ProgressColumn('Quality', format='%d%%', max_value=100)})
            
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.button("➕ Upload", use_container_width=True)
            with col_b:
                st.button("🔍 Validate", use_container_width=True)
            with col_c:
                st.button("📥 Export", use_container_width=True)
            with col_d:
                st.button("🗑️ Delete", use_container_width=True)
        
        with col2:
            st.subheader("📈 Statistics")
            st.metric("Total Datasets", len(datasets))
            st.metric("Total Examples", sum(d['Examples'] for d in datasets))
            st.metric("Avg Quality", f"{np.mean([d['Quality'] for d in datasets]):.0f}%")
    
    # Mappings
    with subtabs[1]:
        st.subheader("🗺️ Schema Mappings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mappings = [
                {'Retailer': 'Amazon', 'Version': 'v0.2.0', 'Fields': 42, 'Coverage': 98, 'Status': 'Active'},
                {'Retailer': 'Walmart', 'Version': 'v0.2.0', 'Fields': 38, 'Coverage': 95, 'Status': 'Active'},
                {'Retailer': 'Target', 'Version': 'v0.1.5', 'Fields': 35, 'Coverage': 92, 'Status': 'Active'},
                {'Retailer': 'Instacart', 'Version': 'v0.1.0', 'Fields': 28, 'Coverage': 85, 'Status': 'Draft'}
            ]
            
            df_map = pd.DataFrame(mappings)
            st.dataframe(df_map, use_container_width=True, hide_index=True,
                column_config={'Coverage': st.column_config.ProgressColumn('Coverage', format='%d%%', max_value=100)})
        
        with col2:
            selected = st.selectbox("Select Retailer", [m['Retailer'] for m in mappings])
            sel_map = next(m for m in mappings if m['Retailer'] == selected)
            
            st.markdown(f"**Retailer:** {sel_map['Retailer']}")
            st.markdown(f"**Version:** {sel_map['Version']}")
            st.markdown(f"**Status:** {sel_map['Status']}")
            st.metric("Fields", sel_map['Fields'])
            st.metric("Coverage", f"{sel_map['Coverage']}%")
            
            st.button("📝 Edit", use_container_width=True)
            st.button("📥 Download", use_container_width=True)
        
        st.markdown("---")
        st.subheader("📋 Field Mapping Preview")
        
        field_map = pd.DataFrame([
            {'Source': 'adType', 'Target': 'placement_type', 'Transform': 'enum_map', 'Status': '✅'},
            {'Source': 'cost_micros', 'Target': 'cost', 'Transform': '/1000000', 'Status': '✅'},
            {'Source': 'timestamp', 'Target': 'ts', 'Transform': 'to_utc', 'Status': '✅'},
            {'Source': 'conv_click_7d', 'Target': 'conversions', 'Transform': 'none', 'Status': '✅'}
        ])
        st.dataframe(field_map, use_container_width=True, hide_index=True)
    
    # Browser
    with subtabs[2]:
        st.subheader("📁 Data Browser")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            source = st.radio("Source", [
                "Alpha Events",
                "Beta Events",
                "SKU Catalog",
                "Uplift Priors"
            ])
            
            st.markdown("---")
            st.markdown("**Filters:**")
            st.date_input("Date Range", [])
            st.multiselect("Retailer", ["alpha", "beta"])
            st.button("🔍 Apply", use_container_width=True)
        
        with col2:
            st.markdown(f"**Viewing: {source}**")
            
            sample = pd.DataFrame({
                'id': [f'evt_{i:06d}' for i in range(10)],
                'ts': pd.date_range('2024-01-01', periods=10),
                'type': np.random.choice(['sponsored_product', 'display'], 10),
                'cost': np.random.uniform(10, 100, 10).round(2),
                'impressions': np.random.randint(100, 1000, 10)
            })
            
            st.dataframe(sample, use_container_width=True, hide_index=True)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Rows", "10,000")
            with col_b:
                st.metric("Columns", 15)
            with col_c:
                st.metric("Size", "2.3MB")

# ============================================================================
# TAB 4: ANALYTICS
# ============================================================================
with tabs[3]:
    st.header("Analytics & Monitoring")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("GPU Util", "87%", "↑ 5%")
    with col2:
        st.metric("Memory", "14.2/16GB", "")
    with col3:
        st.metric("Throughput", "12 tok/s", "")
    with col4:
        st.metric("Active Jobs", len([j for j in st.session_state.training_jobs if j.get('status') == 'running']), "")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📉 Training Loss Curve")
        
        # Generate sample loss curve
        steps = np.arange(0, 2500, 10)
        loss = 2.5 * np.exp(-steps / 800) + 0.5 + np.random.normal(0, 0.05, len(steps))
        
        df_loss = pd.DataFrame({'Step': steps, 'Loss': loss})
        st.line_chart(df_loss.set_index('Step'))
    
    with col2:
        st.subheader("🎯 Adapter Performance")
        
        perf = pd.DataFrame([
            {'Adapter': 'amazon_v1', 'Accuracy': 92, 'Latency': '145ms'},
            {'Adapter': 'planning_v1', 'Accuracy': 89, 'Latency': '132ms'},
            {'Adapter': 'creative_v1', 'Accuracy': 94, 'Latency': '158ms'}
        ])
        
        st.dataframe(perf, use_container_width=True, hide_index=True)
