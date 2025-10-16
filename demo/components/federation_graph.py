"""Federation graph visualization component."""

import streamlit as st
from typing import List, Dict, Any, Optional
import graphviz


def build_federation_graph(
    adapters: List[str],
    composition_data: Optional[Dict[str, Any]] = None
) -> graphviz.Digraph:
    """
    Build a graphviz graph showing adapter composition.
    
    Args:
        adapters: List of adapter IDs in composition order
        composition_data: Optional detailed composition data
        
    Returns:
        Graphviz Digraph object
    """
    graph = graphviz.Digraph(comment='LoRA Federation')
    graph.attr(rankdir='TB', bgcolor='transparent')
    graph.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    graph.attr('edge', color='#3b82f6', penwidth='2')
    
    # Base model
    graph.node('base', 
               'Generic LLM\n(Llama 3.1 8B)\n\n• General reasoning\n• Tool use\n• Schema comprehension',
               fillcolor='#f0f9ff', color='#0284c7', fontcolor='#0c4a6e')
    
    # Track previous node for edges
    prev_node = 'base'
    
    # Add adapter nodes
    adapter_configs = {
        'industry_retail_media': {
            'label': 'Industry LoRA\n(Retail Media)\n\n• RMIS schema\n• Clean room protocols\n• Campaign metrics',
            'fillcolor': '#dbeafe',
            'color': '#2563eb'
        },
        'manufacturer_brand_x': {
            'label': 'Manufacturer LoRA\n(Brand X)\n\n• Brand tone\n• Product hierarchies\n• Private metrics',
            'fillcolor': '#fef3c7',
            'color': '#f59e0b'
        },
        'task_planning': {
            'label': 'Task LoRA\n(Planning)\n\n• Budget allocation\n• Tool calling\n• Constraints',
            'fillcolor': '#dcfce7',
            'color': '#16a34a'
        },
        'task_creative': {
            'label': 'Task LoRA\n(Creative)\n\n• Copy generation\n• Policy compliance\n• Tone adaptation',
            'fillcolor': '#fce7f3',
            'color': '#db2777'
        }
    }
    
    for adapter_id in adapters:
        if adapter_id in adapter_configs:
            config = adapter_configs[adapter_id]
            node_id = adapter_id
            
            graph.node(node_id,
                      config['label'],
                      fillcolor=config['fillcolor'],
                      color=config['color'],
                      fontcolor='#1e293b')
            
            # Add edge from previous node
            graph.edge(prev_node, node_id)
            prev_node = node_id
    
    # Agent orchestrator
    graph.node('orchestrator',
               'Agent Orchestrator\n\n• Task routing\n• Tool execution\n• Result aggregation',
               fillcolor='#f3e8ff', color='#9333ea', fontcolor='#581c87')
    graph.edge(prev_node, 'orchestrator')
    
    return graph


def render_federation_graph(
    adapters: List[str],
    composition_data: Optional[Dict[str, Any]] = None,
    show_metrics: bool = True
) -> None:
    """
    Render federation graph in Streamlit.
    
    Args:
        adapters: List of adapter IDs
        composition_data: Optional composition metadata
        show_metrics: Whether to show performance metrics
    """
    st.subheader("🔗 Federation Composition")
    
    # Build and display graph
    graph = build_federation_graph(adapters, composition_data)
    st.graphviz_chart(graph)
    
    # Show active adapters
    st.markdown("### Active Adapters")
    cols = st.columns(len(adapters) if adapters else 1)
    
    adapter_info = {
        'industry_retail_media': {
            'name': 'Industry LoRA',
            'icon': '🏢',
            'color': '#2563eb'
        },
        'manufacturer_brand_x': {
            'name': 'Manufacturer LoRA',
            'icon': '🏭',
            'color': '#f59e0b'
        },
        'task_planning': {
            'name': 'Planning Task',
            'icon': '📊',
            'color': '#16a34a'
        },
        'task_creative': {
            'name': 'Creative Task',
            'icon': '✨',
            'color': '#db2777'
        }
    }
    
    for idx, adapter_id in enumerate(adapters):
        if adapter_id in adapter_info:
            info = adapter_info[adapter_id]
            with cols[idx]:
                st.markdown(f"""
                <div style="
                    padding: 1rem;
                    border-radius: 0.5rem;
                    border: 2px solid {info['color']};
                    background: white;
                    text-align: center;
                ">
                    <div style="font-size: 2rem;">{info['icon']}</div>
                    <div style="font-weight: 600; color: {info['color']};">{info['name']}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">✓ Active</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Show metrics if available
    if show_metrics and composition_data:
        st.markdown("### Composition Metrics")
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            st.metric(
                "Total Parameters",
                composition_data.get("total_parameters", "8.5B")
            )
        
        with metric_cols[1]:
            st.metric(
                "LoRA Parameters",
                composition_data.get("lora_parameters", "67M")
            )
        
        with metric_cols[2]:
            st.metric(
                "Composition Time",
                f"{composition_data.get('composition_time_ms', 1850)}ms"
            )
        
        with metric_cols[3]:
            st.metric(
                "Strategy",
                composition_data.get("composition_strategy", "Sequential").title()
            )


def render_comparison_chart(comparison: Dict[str, Any]) -> None:
    """
    Render clean room vs full data comparison chart.
    
    Args:
        comparison: Comparison result dict
    """
    st.subheader("📊 Clean Room vs Federation Comparison")
    
    # Metrics comparison
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### iROAS")
        st.metric(
            "Full Data",
            f"{comparison.get('full_data_roas', 0):.2f}x",
            delta=f"{comparison.get('roas_delta_pct', 0):.1f}%",
            delta_color="normal"
        )
        st.metric(
            "Clean Room Only",
            f"{comparison.get('clean_room_roas', 0):.2f}x"
        )
    
    with col2:
        st.markdown("#### Revenue")
        st.metric(
            "Full Data",
            f"${comparison.get('full_data_revenue', 0):,.0f}",
            delta=f"{comparison.get('revenue_delta_pct', 0):.1f}%",
            delta_color="normal"
        )
        st.metric(
            "Clean Room Only",
            f"${comparison.get('clean_room_revenue', 0):,.0f}"
        )
    
    with col3:
        st.markdown("#### SKUs Optimized")
        st.metric(
            "Full Data",
            comparison.get('full_data_skus', 0),
            delta=f"{comparison.get('sku_delta_pct', 0):.1f}%",
            delta_color="normal"
        )
        st.metric(
            "Clean Room Only",
            comparison.get('clean_room_skus', 0)
        )
    
    # Missing capabilities
    st.markdown("### 🚫 Capabilities Unavailable in Clean Room")
    missing = comparison.get('missing_capabilities', [])
    
    if missing:
        cols = st.columns(2)
        for idx, capability in enumerate(missing):
            with cols[idx % 2]:
                st.markdown(f"- ❌ {capability}")
    
    # Blocked fields
    blocked = comparison.get('blocked_fields', [])
    if blocked:
        with st.expander("🔒 Blocked Fields in Clean Room"):
            st.markdown("The following fields are not accessible in clean room mode:")
            for field in blocked:
                st.code(field, language="text")


def render_adapter_details(adapter_id: str, metadata: Dict[str, Any]) -> None:
    """
    Render detailed adapter information.
    
    Args:
        adapter_id: Adapter identifier
        metadata: Adapter metadata
    """
    st.markdown(f"### {metadata.get('name', adapter_id)}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Type:** {metadata.get('adapter_type', 'unknown').title()}")
        st.markdown(f"**Version:** {metadata.get('version', '1.0.0')}")
        st.markdown(f"**Description:** {metadata.get('description', 'No description')}")
        
        # Capabilities
        capabilities = metadata.get('capabilities', [])
        if capabilities:
            st.markdown("**Capabilities:**")
            for cap in capabilities:
                st.markdown(f"- {cap}")
    
    with col2:
        # Performance metrics
        perf = metadata.get('performance', {})
        if perf:
            st.markdown("**Performance:**")
            for key, value in perf.items():
                if isinstance(value, float):
                    if value < 1:
                        st.metric(key.replace('_', ' ').title(), f"{value:.2%}")
                    else:
                        st.metric(key.replace('_', ' ').title(), f"{value:.1f}ms")
                else:
                    st.metric(key.replace('_', ' ').title(), value)
