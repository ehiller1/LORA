"""Federation Demo Page - Shows clean room comparison and adapter composition."""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from demo.federation_workflow import run_federation_demo
from demo.components.federation_graph import (
    render_federation_graph,
    render_comparison_chart,
    render_adapter_details
)
import json

st.set_page_config(
    page_title="Federation Demo - RMN LoRA",
    page_icon="🔗",
    layout="wide"
)

# Header
st.title("🔗 Federated LoRA Demo")
st.markdown("""
This demo showcases the power of **federated LoRA adapters** compared to clean-room-only analytics.
See how combining Generic LLM + Industry LoRA + Manufacturer LoRA delivers superior results.
""")

# Value Attribution Section
st.markdown("---")
st.markdown("## 🎯 What You're Seeing")

st.markdown("""
This demo compares **three approaches** to RMN optimization:

1. **🟥 Generic LLM Only**: Base model with no specialized knowledge
2. **🟨 Clean Room + Industry LoRA**: Shared industry knowledge, but no proprietary data  
3. **🟩 Full Federation (Your Competitive Advantage)**: Generic + Industry + YOUR Manufacturer LoRA

Watch how each layer adds value:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%); 
                padding: 1.5rem; border-radius: 0.75rem; border: 2px solid #9E9E9E;">
        <h3 style="color: #616161;">🧠 Generic LLM</h3>
        <p style="font-weight: 600;">Provides:</p>
        <ul style="font-size: 0.9rem;">
            <li>Natural language understanding</li>
            <li>General reasoning</li>
            <li>Basic math/optimization</li>
        </ul>
        <hr style="border-color: #9E9E9E;">
        <p style="font-size: 1.2rem; color: #616161; font-weight: 700;">ROAS: 2.1x</p>
        <p style="font-size: 0.85rem; color: #757575;">Baseline performance</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                padding: 1.5rem; border-radius: 0.75rem; border: 2px solid #2196F3;">
        <h3 style="color: #1976D2;">🏢 Industry LoRA</h3>
        <p style="font-weight: 600;">Adds:</p>
        <ul style="font-size: 0.9rem;">
            <li>RMIS schema knowledge</li>
            <li>Retail media best practices</li>
            <li>Campaign structure</li>
        </ul>
        <hr style="border-color: #2196F3;">
        <p style="font-size: 1.2rem; color: #1976D2; font-weight: 700;">ROAS: 2.8x (+33%)</p>
        <p style="font-size: 0.85rem; color: #1976D2;">Shared industry knowledge</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                padding: 1.5rem; border-radius: 0.75rem; border: 2px solid #4CAF50;">
        <h3 style="color: #2E7D32;">🏭 Your LoRA</h3>
        <p style="font-weight: 600;">Your Advantage:</p>
        <ul style="font-size: 0.9rem;">
            <li><strong>Product affinities</strong></li>
            <li><strong>Margin optimization</strong></li>
            <li><strong>Historical performance</strong></li>
        </ul>
        <hr style="border-color: #4CAF50;">
        <p style="font-size: 1.2rem; color: #2E7D32; font-weight: 700;">ROAS: 3.5x (+25% more)</p>
        <p style="font-size: 0.85rem; color: #2E7D32; font-weight: 600;">🏆 Competitive advantage</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Demo Configuration")
    
    # Clean room toggle
    clean_room_mode = st.toggle(
        "🔒 Clean Room Mode Only",
        value=False,
        help="Enable to see results with clean room restrictions (limited data access)"
    )
    
    st.divider()
    
    # Budget settings
    st.subheader("Budget Settings")
    budget = st.number_input(
        "Total Budget ($)",
        min_value=100000,
        max_value=10000000,
        value=2500000,
        step=100000
    )
    
    roas_floor = st.slider(
        "Minimum ROAS",
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.1
    )
    
    exp_share = st.slider(
        "Experiment Budget %",
        min_value=0.0,
        max_value=0.3,
        value=0.1,
        step=0.05
    )
    
    st.divider()
    
    # Run demo button
    run_demo = st.button("▶️ Run Demo", type="primary", use_container_width=True)

# Main content
if run_demo or 'demo_results' in st.session_state:
    
    # Run demo if button clicked
    if run_demo:
        with st.spinner("Running federation demo..."):
            results = run_federation_demo(
                budget=budget,
                roas_floor=roas_floor,
                exp_share=exp_share
            )
            st.session_state.demo_results = results
    
    results = st.session_state.demo_results
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Comparison",
        "🔗 Federation Graph",
        "📋 Plan Details",
        "✨ Creatives"
    ])
    
    # Tab 1: Comparison
    with tab1:
        st.header("Clean Room vs Full Data Comparison")
        
        comparison = results["steps"]["comparison"]
        
        # Render comparison chart
        render_comparison_chart(comparison)
        
        # Key insights
        st.markdown("### 💡 Key Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            **With Federation (Full Data):**
            - ✅ Access to margin data for profitability optimization
            - ✅ Stock levels for out-of-stock avoidance
            - ✅ Promotional flags for timing optimization
            - ✅ Price elasticity modeling
            - ✅ {comparison['full_data_skus']} SKUs optimized
            """)
        
        with col2:
            st.warning(f"""
            **Clean Room Only:**
            - ❌ No margin visibility
            - ❌ No stock level data
            - ❌ No promotional timing
            - ❌ Limited to aggregated metrics
            - ⚠️ Only {comparison['clean_room_skus']} SKUs optimized
            """)
        
        # Performance delta
        st.markdown("### 📈 Performance Delta")
        
        delta_cols = st.columns(4)
        
        with delta_cols[0]:
            st.metric(
                "ROAS Improvement",
                f"{comparison['roas_delta_pct']:.1f}%",
                delta=f"+{comparison['roas_delta_pct']:.1f}%"
            )
        
        with delta_cols[1]:
            st.metric(
                "Revenue Improvement",
                f"{comparison['revenue_delta_pct']:.1f}%",
                delta=f"+{comparison['revenue_delta_pct']:.1f}%"
            )
        
        with delta_cols[2]:
            st.metric(
                "Accuracy Improvement",
                f"{comparison['accuracy_delta_pct']:.1f}%",
                delta=f"+{comparison['accuracy_delta_pct']:.1f}%"
            )
        
        with delta_cols[3]:
            st.metric(
                "SKU Coverage",
                f"{comparison['sku_delta_pct']:.1f}%",
                delta=f"+{comparison['sku_delta_pct']:.1f}%"
            )
    
    # Tab 2: Federation Graph
    with tab2:
        st.header("Adapter Composition Flow")
        
        viz_data = results["steps"]["visualization"]
        
        # Get adapters from full plan
        full_plan = results["steps"]["full_plan"]
        adapters = full_plan.get("adapters_used", [])
        
        # Render federation graph
        render_federation_graph(adapters, viz_data)
        
        # Adapter details
        st.markdown("---")
        st.subheader("📦 Adapter Details")
        
        # Load adapter metadata
        adapter_metadata = {}
        for adapter_id in adapters:
            metadata_path = Path(__file__).parent.parent / "mock_adapters" / adapter_id / "adapter_metadata.json"
            if metadata_path.exists():
                with open(metadata_path) as f:
                    adapter_metadata[adapter_id] = json.load(f)
        
        # Display in columns
        if adapter_metadata:
            cols = st.columns(len(adapter_metadata))
            for idx, (adapter_id, metadata) in enumerate(adapter_metadata.items()):
                with cols[idx]:
                    with st.expander(f"📦 {metadata.get('name', adapter_id)}", expanded=True):
                        st.markdown(f"**Type:** {metadata.get('adapter_type', 'unknown').title()}")
                        st.markdown(f"**Version:** {metadata.get('version', '1.0.0')}")
                        
                        caps = metadata.get('capabilities', [])
                        if caps:
                            st.markdown("**Capabilities:**")
                            for cap in caps[:3]:
                                st.markdown(f"- {cap}")
    
    # Tab 3: Plan Details
    with tab3:
        st.header("Campaign Plan Details")
        
        # Show both plans side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🟢 Full Data Plan")
            full_plan = results["steps"]["full_plan"]
            
            st.metric("Expected ROAS", f"{full_plan.get('expected_roas', 0):.2f}x")
            st.metric("Expected Revenue", f"${full_plan.get('incremental_revenue', 0):,.0f}")
            st.metric("Budget Allocated", f"${full_plan.get('budget_allocated', 0):,.0f}")
            
            if 'allocation' in full_plan:
                st.markdown("**Top Allocations:**")
                alloc = full_plan['allocation']
                if hasattr(alloc, 'head'):
                    st.dataframe(alloc.head(5), use_container_width=True)
        
        with col2:
            st.subheader("🟡 Clean Room Plan")
            clean_plan = results["steps"]["clean_room_plan"]
            
            st.metric("Expected ROAS", f"{clean_plan.get('expected_roas', 0):.2f}x")
            st.metric("Expected Revenue", f"${clean_plan.get('incremental_revenue', 0):,.0f}")
            st.metric("Budget Allocated", f"${clean_plan.get('budget_allocated', 0):,.0f}")
            
            if 'allocation' in clean_plan:
                st.markdown("**Top Allocations:**")
                alloc = clean_plan['allocation']
                if hasattr(alloc, 'head'):
                    st.dataframe(alloc.head(5), use_container_width=True)
    
    # Tab 4: Creatives
    with tab4:
        st.header("Generated Creatives")
        
        creatives_result = results["steps"]["creatives"]
        creatives = creatives_result.get("creatives", [])
        
        st.markdown(f"""
        **Adapters Used:** {', '.join(creatives_result.get('adapters_used', []))}  
        **Compliance Rate:** {creatives_result.get('compliance_rate', 0):.1%}
        """)
        
        for creative_set in creatives:
            sku = creative_set.get("sku")
            variants = creative_set.get("variants", [])
            
            with st.expander(f"📦 {sku}", expanded=True):
                for idx, variant in enumerate(variants):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Variant {idx + 1}:**")
                        st.info(variant.get("text", ""))
                    
                    with col2:
                        compliant = variant.get("compliant", True)
                        if compliant:
                            st.success("✅ Compliant")
                        else:
                            st.error("❌ Violations")
                            violations = variant.get("violations", [])
                            for v in violations:
                                st.caption(f"- {v}")

else:
    # Initial state - show instructions
    st.info("""
    👈 Configure your demo settings in the sidebar and click **Run Demo** to see:
    
    1. **Clean Room vs Full Data Comparison** - See the performance delta
    2. **Federation Graph** - Visualize adapter composition
    3. **Plan Details** - Compare optimization results
    4. **Creative Generation** - Brand-compliant ad copy
    """)
    
    # Show example federation architecture
    st.markdown("### 🏗️ Federation Architecture")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Generic LLM**
        - Base reasoning
        - Tool use
        - Schema comprehension
        """)
    
    with col2:
        st.markdown("""
        **+ Industry LoRA**
        - RMIS schema
        - Clean room protocols
        - Campaign metrics
        """)
    
    with col3:
        st.markdown("""
        **+ Manufacturer LoRA**
        - Brand tone
        - Private metrics
        - Product hierarchies
        """)
    
    st.markdown("---")
    
    # Value proposition
    st.markdown("### 💎 Why Federation?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Clean Room Limitations:**
        - ❌ No margin/profitability data
        - ❌ No inventory levels
        - ❌ No promotional flags
        - ❌ Aggregated data only
        - ❌ Limited SKU coverage
        """)
    
    with col2:
        st.markdown("""
        **Federation Advantages:**
        - ✅ Full data access via manufacturer adapter
        - ✅ Stock-out avoidance
        - ✅ Promotional timing optimization
        - ✅ Margin-aware allocation
        - ✅ 50% more SKUs optimized
        """)
