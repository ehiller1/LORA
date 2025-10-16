"""Streamlit Demo UI for RMN LoRA System."""

import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from demo.tools.warehouse import WarehouseManager
from demo.tools.optimizer import BudgetOptimizer
from demo.tools.policy import PolicyChecker
from demo.tools.creatives import CreativeGenerator
from demo.tools.experiments import ExperimentDesigner

# Page config
st.set_page_config(
    page_title="RMN LoRA Demo",
    page_icon="🎯",
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
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 0.75rem;
        border: 1px solid hsl(240, 5.9%, 90%);
    }
    
    /* Success/Warning/Error boxes */
    .stSuccess {
        background-color: hsla(142, 100%, 35%, 0.1);
        border-left: 4px solid hsl(142, 100%, 35%);
        border-radius: 0.75rem;
        animation: slideUp 0.5s ease-out forwards;
    }
    .stWarning {
        background-color: hsla(31, 100%, 50%, 0.1);
        border-left: 4px solid hsl(31, 100%, 50%);
        border-radius: 0.75rem;
        animation: slideUp 0.5s ease-out forwards;
    }
    .stError {
        background-color: hsla(4, 92%, 49%, 0.1);
        border-left: 4px solid hsl(4, 92%, 49%);
        border-radius: 0.75rem;
        animation: slideUp 0.5s ease-out forwards;
    }
    .stInfo {
        background-color: hsla(199, 100%, 50%, 0.1);
        border-left: 4px solid hsl(199, 100%, 50%);
        border-radius: 0.75rem;
        animation: slideUp 0.5s ease-out forwards;
    }
    
    /* Code blocks */
    code {
        border-radius: 0.5rem;
        padding: 0.2rem 0.4rem;
        background-color: hsl(240, 4.8%, 95.9%);
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background-color: hsl(142, 100%, 35%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'warehouse' not in st.session_state:
    st.session_state.warehouse = WarehouseManager()
if 'optimizer' not in st.session_state:
    st.session_state.optimizer = BudgetOptimizer()
if 'policy_checker' not in st.session_state:
    st.session_state.policy_checker = PolicyChecker()
if 'creative_gen' not in st.session_state:
    st.session_state.creative_gen = CreativeGenerator()
if 'experiment_designer' not in st.session_state:
    st.session_state.experiment_designer = ExperimentDesigner()
if 'harmonized' not in st.session_state:
    st.session_state.harmonized = False
if 'plan' not in st.session_state:
    st.session_state.plan = None

# Title
st.title("🎯 RMN LoRA System Demo")
st.markdown("**Composable LoRA Adapters for Retail Media Network Optimization**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    retailer_mode = st.radio(
        "Execution Mode",
        ["Manufacturer View", "Retailer Alpha Service", "Retailer Beta Service"],
        help="Toggle between manufacturer and retailer-hosted agent execution"
    )
    
    st.divider()
    
    st.subheader("Active Adapters")
    if retailer_mode == "Manufacturer View":
        st.success("✅ Base Model")
        st.info("🔧 Task: Planning")
        st.info("🔧 Task: Mapping")
    elif retailer_mode == "Retailer Alpha Service":
        st.success("✅ Base Model")
        st.warning("🏪 Retailer: Alpha")
        st.info("🔧 Task: Planning")
    else:
        st.success("✅ Base Model")
        st.warning("🏪 Retailer: Beta")
        st.info("🔧 Task: Planning")
    
    st.divider()
    
    st.subheader("📊 System Status")
    st.metric("Data Quality", "94%", "↑ 2%")
    st.metric("Active Campaigns", "18", "↑ 3")
    st.metric("Total Budget", "$2.5M", "")

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📥 Data", "📋 Plan", "💰 Optimize", "📊 Measure", "✨ Creative", "🔧 Ops"
])

# TAB 1: DATA HARMONIZATION
with tab1:
    st.header("Data Harmonization")
    st.markdown("Upload retailer exports and harmonize to RMIS schema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retailer Alpha")
        st.markdown("**Format:** CSV | **Timezone:** CST | **Currency:** USD")
        
        if st.button("📂 Load Alpha Data", key="load_alpha"):
            with st.spinner("Loading Retailer Alpha data..."):
                success = st.session_state.warehouse.load_retailer_data("alpha")
                if success:
                    st.success("✅ Loaded Alpha data")
                else:
                    st.error("❌ Failed to load data")
        
        if st.button("🔄 Harmonize Alpha", key="harmonize_alpha"):
            with st.spinner("Harmonizing Alpha data to RMIS..."):
                result = st.session_state.warehouse.harmonize_retailer("alpha")
                if result['success']:
                    st.success(f"✅ Harmonized {result['rows']} rows")
                    st.session_state.harmonized = True
                    
                    # Show quality metrics
                    st.metric("Enum Coverage", f"{result['enum_coverage']}%")
                    st.metric("Join Success Rate", f"{result['join_rate']}%")
                    st.metric("Non-null Keys", f"{result['non_null_keys']}%")
                    
                    # Show preview
                    with st.expander("Preview Harmonized Data"):
                        st.dataframe(result['preview'])
    
    with col2:
        st.subheader("Retailer Beta")
        st.markdown("**Format:** JSONL | **Timezone:** PST | **Currency:** EUR")
        
        if st.button("📂 Load Beta Data", key="load_beta"):
            with st.spinner("Loading Retailer Beta data..."):
                success = st.session_state.warehouse.load_retailer_data("beta")
                if success:
                    st.success("✅ Loaded Beta data")
                else:
                    st.error("❌ Failed to load data")
        
        if st.button("🔄 Harmonize Beta", key="harmonize_beta"):
            with st.spinner("Harmonizing Beta data to RMIS..."):
                result = st.session_state.warehouse.harmonize_retailer("beta")
                if result['success']:
                    st.success(f"✅ Harmonized {result['rows']} rows")
                    
                    # Show quality metrics
                    st.metric("Enum Coverage", f"{result['enum_coverage']}%")
                    st.metric("Join Success Rate", f"{result['join_rate']}%")
                    st.metric("Non-null Keys", f"{result['non_null_keys']}%")
                    
                    # Show preview
                    with st.expander("Preview Harmonized Data"):
                        st.dataframe(result['preview'])
    
    st.divider()
    
    # Mapping validation
    st.subheader("📋 Mapping Validation")
    
    if st.session_state.harmonized:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Events", "18,000", "")
        with col2:
            st.metric("Validated Fields", "42/45", "")
        with col3:
            st.metric("Mapping Gaps", "3", "⚠️")
        
        with st.expander("🔍 View Mapping Gaps"):
            gaps = [
                {"Field": "inventory_type", "Issue": "Unknown enum 'partner'", "Suggestion": "Add to enum map"},
                {"Field": "attribution_model", "Issue": "Missing for 5% of rows", "Suggestion": "Default to 'last_click'"},
                {"Field": "device_type", "Issue": "Value 'unk' not in taxonomy", "Suggestion": "Map to 'unknown'"}
            ]
            st.dataframe(pd.DataFrame(gaps))

# TAB 2: PLANNING
with tab2:
    st.header("Campaign Planning")
    st.markdown("AI-powered planning with tool-calling agents")
    
    # Planning brief
    st.subheader("📝 Planning Brief")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        brief = st.text_area(
            "Objectives & Constraints",
            value="""Budget: $2,500,000
Target ROAS: ≥ 3.0
Experiment Reserve: 10%
Exclude: SKUs with OOS probability > 5%
Focus: Maximize incremental margin
Retailers: Alpha, Beta""",
            height=150
        )
    
    with col2:
        st.markdown("**Quick Constraints**")
        budget = st.number_input("Budget ($)", value=2500000, step=100000)
        roas_target = st.number_input("Min ROAS", value=3.0, step=0.1)
        exp_share = st.slider("Experiment %", 0, 20, 10)
    
    if st.button("🚀 Draft Plan", type="primary"):
        with st.spinner("🤖 Planner Agent working..."):
            # Simulate planning
            import time
            time.sleep(2)
            
            plan_result = st.session_state.optimizer.generate_plan(
                budget=budget,
                roas_floor=roas_target,
                exp_share=exp_share / 100
            )
            
            st.session_state.plan = plan_result
            st.success("✅ Plan generated!")
    
    # Show plan
    if st.session_state.plan:
        st.divider()
        st.subheader("📊 Recommended Allocation")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Budget", f"${st.session_state.plan['budget']:,.0f}")
        with col2:
            st.metric("Expected ROAS", f"{st.session_state.plan['expected_roas']:.2f}x")
        with col3:
            st.metric("Incremental Revenue", f"${st.session_state.plan['incremental_revenue']:,.0f}")
        with col4:
            st.metric("Experiment Budget", f"${st.session_state.plan['experiment_budget']:,.0f}")
        
        # Allocation table
        st.dataframe(
            st.session_state.plan['allocation'],
            use_container_width=True,
            hide_index=True
        )
        
        # Tool call trail
        with st.expander("🔧 Tool Call Trail"):
            for call in st.session_state.plan['tool_calls']:
                st.code(f"✅ {call['function']}({json.dumps(call['args'], indent=2)})", language="json")
        
        # Rationale
        with st.expander("💡 Plan Rationale"):
            for reason in st.session_state.plan['rationale']:
                st.markdown(f"- {reason}")

# TAB 3: OPTIMIZATION
with tab3:
    st.header("Budget Optimization")
    st.markdown("Interactive what-if analysis with constraint tuning")
    
    if not st.session_state.plan:
        st.warning("⚠️ Please generate a plan first in the Plan tab")
    else:
        st.subheader("🎛️ Constraint Tuning")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_roas = st.slider(
                "ROAS Floor",
                min_value=2.0,
                max_value=4.0,
                value=3.0,
                step=0.1,
                help="Minimum acceptable ROAS"
            )
            
            new_exp = st.slider(
                "Experiment Share (%)",
                min_value=0,
                max_value=20,
                value=10,
                step=1
            )
        
        with col2:
            oos_threshold = st.slider(
                "OOS Threshold (%)",
                min_value=0,
                max_value=20,
                value=5,
                step=1,
                help="Exclude SKUs with out-of-stock probability above this"
            )
            
            max_per_retailer = st.number_input(
                "Max per Retailer ($)",
                value=1500000,
                step=100000
            )
        
        if st.button("🔄 Re-optimize", type="primary"):
            with st.spinner("Re-running optimization..."):
                import time
                time.sleep(1.5)
                
                new_plan = st.session_state.optimizer.generate_plan(
                    budget=st.session_state.plan['budget'],
                    roas_floor=new_roas,
                    exp_share=new_exp / 100,
                    oos_threshold=oos_threshold / 100
                )
                
                st.success("✅ Optimization complete!")
                
                # Show delta
                st.subheader("📈 Changes vs Current Plan")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    delta_roas = new_plan['expected_roas'] - st.session_state.plan['expected_roas']
                    st.metric("ROAS", f"{new_plan['expected_roas']:.2f}x", f"{delta_roas:+.2f}x")
                with col2:
                    delta_rev = new_plan['incremental_revenue'] - st.session_state.plan['incremental_revenue']
                    st.metric("Incremental Revenue", f"${new_plan['incremental_revenue']:,.0f}", f"${delta_rev:+,.0f}")
                with col3:
                    st.metric("Reallocated SKUs", "12", "")
                
                # Update plan
                st.session_state.plan = new_plan
        
        # Sensitivity analysis
        st.divider()
        st.subheader("📊 Sensitivity Analysis")
        
        sensitivity_data = pd.DataFrame({
            'ROAS Floor': [2.5, 2.8, 3.0, 3.2, 3.5],
            'Expected ROAS': [3.8, 3.5, 3.2, 3.0, 2.8],
            'Incremental Revenue': [9500000, 8750000, 8000000, 7500000, 7000000],
            'Risk Level': ['Low', 'Low', 'Medium', 'High', 'High']
        })
        
        st.dataframe(sensitivity_data, use_container_width=True, hide_index=True)

# TAB 4: MEASUREMENT
with tab4:
    st.header("Measurement & Experimentation")
    st.markdown("Design experiments and generate lift readout SQL")
    
    st.subheader("🧪 Experiment Design")
    
    col1, col2 = st.columns(2)
    
    with col1:
        exp_type = st.selectbox(
            "Experiment Type",
            ["Geo Split Test", "Audience Holdout", "Budget Pacing Test"]
        )
        
        min_cells = st.number_input("Minimum Cells", value=2, min_value=2, max_value=10)
        power_target = st.slider("Statistical Power", 0.7, 0.95, 0.8, 0.05)
    
    with col2:
        mde = st.number_input("Minimum Detectable Effect (%)", value=10, min_value=5, max_value=50)
        duration_days = st.number_input("Duration (days)", value=14, min_value=7, max_value=90)
    
    if st.button("🎯 Design Experiment"):
        with st.spinner("Designing experiment..."):
            import time
            time.sleep(1)
            
            design = st.session_state.experiment_designer.design_experiment(
                exp_type=exp_type,
                min_cells=min_cells,
                power=power_target,
                mde=mde / 100
            )
            
            st.success("✅ Experiment designed!")
            
            # Show design
            st.subheader("📋 Experiment Plan")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Treatment Cells", design['cells'])
            with col2:
                st.metric("Sample Size per Cell", design['sample_size'])
            with col3:
                st.metric("Expected Power", f"{design['power']:.1%}")
            
            # Cell assignment
            st.subheader("🗺️ Cell Assignment")
            st.dataframe(design['cell_assignment'], use_container_width=True)
            
            # SQL for readout
            st.subheader("📝 Lift Readout SQL")
            st.code(design['sql'], language="sql")
            
            with st.expander("💡 Interpretation Guide"):
                st.markdown("""
                **How to read results:**
                1. Wait for experiment duration to complete
                2. Run the SQL query above
                3. Compare treatment vs control metrics
                4. Check if lift is statistically significant (p < 0.05)
                5. Calculate incremental ROAS
                """)

# TAB 5: CREATIVE
with tab5:
    st.header("Creative Generation")
    st.markdown("AI-generated ad copy with policy compliance checking")
    
    st.subheader("🎨 Generate Creative")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_skus = st.multiselect(
            "Select SKUs",
            options=[f"SKU-{i:03d}" for i in range(1, 21)],
            default=[f"SKU-{i:03d}" for i in range(1, 4)]
        )
        
        retailer_for_creative = st.selectbox(
            "Target Retailer",
            ["Alpha", "Beta"]
        )
        
        tone = st.selectbox(
            "Tone",
            ["Professional", "Casual", "Urgent", "Premium"]
        )
    
    with col2:
        st.markdown("**Retailer Specs**")
        if retailer_for_creative == "Alpha":
            st.info("Max headline: 80 chars")
            st.info("Max body: 250 chars")
            st.warning("Disallowed: 'guaranteed', 'miracle'")
        else:
            st.info("Max headline: 60 chars")
            st.info("Max body: 200 chars")
            st.warning("Disallowed: 'best', 'free'")
    
    if st.button("✨ Generate Copy", type="primary"):
        with st.spinner("🤖 Creative Agent working..."):
            import time
            time.sleep(1.5)
            
            creatives = st.session_state.creative_gen.generate(
                skus=selected_skus,
                retailer=retailer_for_creative.lower(),
                tone=tone.lower()
            )
            
            st.success(f"✅ Generated {len(creatives)} creative variants")
            
            # Show creatives
            for i, creative in enumerate(creatives):
                with st.expander(f"Variant {i+1} - {creative['sku']} - {'✅ PASS' if creative['policy_pass'] else '❌ FAIL'}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Headline:** {creative['headline']}")
                        st.markdown(f"**Body:** {creative['body']}")
                        st.caption(f"Headline: {len(creative['headline'])} chars | Body: {len(creative['body'])} chars")
                    
                    with col2:
                        if creative['policy_pass']:
                            st.success("✅ Policy Check PASS")
                        else:
                            st.error("❌ Policy Check FAIL")
                            for reason in creative['policy_reasons']:
                                st.caption(f"• {reason}")
                            
                            if st.button(f"🔧 Fix", key=f"fix_{i}"):
                                st.info("Auto-fixing violations...")
                                # Simulate fix
                                creative['policy_pass'] = True
                                creative['policy_reasons'] = []
                                st.rerun()

# TAB 6: OPS
with tab6:
    st.header("Operations & Observability")
    st.markdown("System logs, adapter composition, and quality checks")
    
    # System status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Health", "Healthy", "")
        st.metric("API Latency", "145ms", "-12ms")
    
    with col2:
        st.metric("Active Adapters", "4", "")
        st.metric("Tool Calls (24h)", "1,247", "+89")
    
    with col3:
        st.metric("Data Freshness", "2 min", "")
        st.metric("Error Rate", "0.02%", "-0.01%")
    
    st.divider()
    
    # Adapter composition log
    st.subheader("🔧 Adapter Composition Log")
    
    adapter_log = pd.DataFrame([
        {"Timestamp": "2024-10-15 16:45:23", "Task": "Planning", "Adapters": "base + task_planning + retailer_alpha", "Status": "✅"},
        {"Timestamp": "2024-10-15 16:45:18", "Task": "Mapping", "Adapters": "base + task_mapping + retailer_beta", "Status": "✅"},
        {"Timestamp": "2024-10-15 16:44:52", "Task": "Creative", "Adapters": "base + task_policy_creative + retailer_alpha", "Status": "✅"},
        {"Timestamp": "2024-10-15 16:44:31", "Task": "Optimization", "Adapters": "base + task_planning", "Status": "✅"},
    ])
    
    st.dataframe(adapter_log, use_container_width=True, hide_index=True)
    
    # Tool call log
    st.subheader("📞 Recent Tool Calls")
    
    tool_log = pd.DataFrame([
        {"Time": "16:45:23", "Function": "allocate_budget", "Args": "budget=2500000, roas_floor=3.0", "Result": "✅ Success", "Duration": "234ms"},
        {"Time": "16:45:20", "Function": "fetch_metrics", "Args": "rmn=alpha, window=30d", "Result": "✅ Success", "Duration": "89ms"},
        {"Time": "16:45:18", "Function": "get_uplift_priors", "Args": "granularity=sku", "Result": "✅ Success", "Duration": "45ms"},
        {"Time": "16:44:52", "Function": "policy_check", "Args": "retailer=alpha", "Result": "⚠️ 1 violation", "Duration": "12ms"},
    ])
    
    st.dataframe(tool_log, use_container_width=True, hide_index=True)
    
    # Data quality
    st.subheader("📊 Data Quality Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Enum Coverage**")
        enum_data = pd.DataFrame({
            'Field': ['placement_type', 'device_type', 'inventory_type', 'attribution_model'],
            'Coverage': [100, 98, 92, 95],
            'Status': ['✅', '✅', '⚠️', '✅']
        })
        st.dataframe(enum_data, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Join Success Rates**")
        join_data = pd.DataFrame({
            'Join': ['events → campaigns', 'events → skus', 'conversions → events', 'events → audiences'],
            'Rate': [99.8, 97.2, 98.5, 94.1],
            'Status': ['✅', '✅', '✅', '⚠️']
        })
        st.dataframe(join_data, use_container_width=True, hide_index=True)

# Footer
st.divider()
st.caption("🎯 RMN LoRA System Demo | Powered by Composable LoRA Adapters")
