"""Welcome & Onboarding Screen - Communicates the Proprietary LoRA Federation Value Story."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="Build Your Proprietary AI",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Archivo', sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    .main { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .hero-section {
        background: white;
        padding: 4rem 2rem;
        border-radius: 1rem;
        margin: 2rem auto;
        max-width: 1200px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    .value-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #667eea;
        margin: 1rem 0;
        transition: transform 0.3s;
    }
    
    .value-card:hover {
        transform: translateY(-5px);
    }
    
    .cta-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .cta-button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .feature-badge {
        display: inline-block;
        background: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        font-size: 1.5rem;
        color: #555;
        font-weight: 400;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown('<div class="hero-section">', unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("<h1>🚀 Build Your Proprietary AI for RMN Optimization</h1>", unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Without Training a Model From Scratch</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ### The Power of Federated LoRA
    
    Combine three powerful layers to create your competitive advantage:
    
    <div style="margin: 1.5rem 0;">
        <div class="feature-badge">🧠 Generic LLM</div>
        <span style="font-size: 1.5rem; margin: 0 1rem;">+</span>
        <div class="feature-badge">🏢 Industry LoRA</div>
        <span style="font-size: 1.5rem; margin: 0 1rem;">+</span>
        <div class="feature-badge">🏭 YOUR Manufacturer LoRA</div>
    </div>
    
    <div style="margin: 2rem 0;">
        <div class="feature-badge" style="background: #FF9800;">= State-of-the-Art RMN Optimization</div>
    </div>
    
    **Result**: An AI trained on YOUR data, optimized for YOUR products, delivering YOUR competitive advantage.
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("🎯 Start Building Your Model", type="primary", use_container_width=True):
            st.switch_page("pages/1_build_your_model.py")
    
    with col_b:
        if st.button("📊 See Live Demo", use_container_width=True):
            st.switch_page("streamlit_app.py")

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; 
                border-radius: 1rem; 
                color: white;
                text-align: center;">
        <h2 style="color: white; margin-top: 0;">⚡ Fast Facts</h2>
        <div style="font-size: 2.5rem; font-weight: 700; margin: 1rem 0;">2 Hours</div>
        <p>From Data to Deployed AI</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <div style="font-size: 2.5rem; font-weight: 700; margin: 1rem 0;">$127</div>
        <p>Training Cost (vs $42,000)</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <div style="font-size: 2.5rem; font-weight: 700; margin: 1rem 0;">+67%</div>
        <p>Average ROAS Improvement</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Value Proposition Metrics
st.markdown("---")
st.markdown("## 💰 Why Build a Proprietary LoRA?")
st.markdown("**See the incremental value of each layer:**")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🏆 Performance",
        "+67% ROAS",
        "vs generic models",
        help="Manufacturers using proprietary LoRA see 67% better ROAS on average"
    )

with col2:
    st.metric(
        "💸 Cost Savings",
        "99.8%",
        "vs full training",
        help="LoRA training costs <0.2% of training a model from scratch"
    )

with col3:
    st.metric(
        "⚡ Speed",
        "2 hours",
        "vs 6 months",
        help="Deploy your proprietary AI in hours, not months"
    )

with col4:
    st.metric(
        "🔒 Privacy",
        "100%",
        "Your data, your IP",
        help="Your training data and resulting LoRA are YOUR intellectual property"
    )

# How it Works - Interactive Visualization
st.markdown("---")
st.markdown("## 🔧 How Federation Creates Value")
st.markdown("**Each layer adds capabilities. YOUR layer adds competitive advantage.**")

# Interactive Plotly chart showing cumulative value
fig = go.Figure()

categories = ['ROAS', 'Prediction Accuracy', 'SKU Coverage', 'Margin Optimization']
generic_llm = [2.1, 45, 60, 30]
plus_industry = [2.8, 67, 85, 55]
plus_manufacturer = [3.5, 89, 98, 87]

# Calculate incremental values
industry_increment = [plus_industry[i] - generic_llm[i] for i in range(len(categories))]
manufacturer_increment = [plus_manufacturer[i] - plus_industry[i] for i in range(len(categories))]

fig.add_trace(go.Bar(
    name='🧠 Generic LLM Only',
    x=categories,
    y=generic_llm,
    marker_color='#9E9E9E',
    text=[f'{v}{"x" if i==0 else "%"}' for i, v in enumerate(generic_llm)],
    textposition='inside',
    hovertemplate='<b>Generic LLM</b><br>%{x}: %{y}<extra></extra>'
))

fig.add_trace(go.Bar(
    name='🏢 + Industry LoRA',
    x=categories,
    y=industry_increment,
    marker_color='#2196F3',
    text=[f'+{v}{"x" if i==0 else "%"}' for i, v in enumerate(industry_increment)],
    textposition='inside',
    hovertemplate='<b>Industry LoRA Adds</b><br>%{x}: +%{y}<extra></extra>',
    base=generic_llm
))

fig.add_trace(go.Bar(
    name='🏭 + YOUR Manufacturer LoRA',
    x=categories,
    y=manufacturer_increment,
    marker_color='#4CAF50',
    text=[f'+{v}{"x" if i==0 else "%"}' for i, v in enumerate(manufacturer_increment)],
    textposition='inside',
    hovertemplate='<b>YOUR LoRA Adds</b><br>%{x}: +%{y}<extra></extra>',
    base=plus_industry
))

fig.update_layout(
    barmode='stack',
    title={
        'text': 'Cumulative Value of Each LoRA Layer',
        'font': {'size': 20, 'family': 'Archivo'}
    },
    xaxis_title='Capability',
    yaxis_title='Performance',
    height=500,
    font=dict(family="Archivo", size=14),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# Detailed Value Breakdown
st.markdown("---")
st.markdown("## 💡 What Each Layer Provides")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="value-card">
        <h3 style="color: #9E9E9E;">🧠 Generic LLM</h3>
        <p><strong>Foundation Capabilities</strong></p>
        <ul>
            <li>Natural language understanding</li>
            <li>General reasoning & logic</li>
            <li>Basic math & optimization</li>
            <li>Code generation</li>
        </ul>
        <hr>
        <p style="font-size: 1.2rem; color: #9E9E9E;"><strong>Baseline ROAS: 2.1x</strong></p>
        <p style="color: #666;">Good, but generic. No industry knowledge.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="value-card" style="border-color: #2196F3;">
        <h3 style="color: #2196F3;">🏢 Industry LoRA</h3>
        <p><strong>Retail Media Expertise</strong></p>
        <ul>
            <li>RMIS schema understanding</li>
            <li>Campaign best practices</li>
            <li>Retail media terminology</li>
            <li>Attribution models</li>
        </ul>
        <hr>
        <p style="font-size: 1.2rem; color: #2196F3;"><strong>Enhanced ROAS: 2.8x (+33%)</strong></p>
        <p style="color: #666;">Solid industry knowledge, but still generic.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="value-card" style="border-color: #4CAF50; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);">
        <h3 style="color: #2E7D32;">🏭 YOUR Manufacturer LoRA</h3>
        <p><strong>🏆 Your Competitive Advantage</strong></p>
        <ul>
            <li><strong>Product affinity models</strong></li>
            <li><strong>Historical performance by SKU</strong></li>
            <li><strong>Margin optimization</strong></li>
            <li><strong>Your brand voice</strong></li>
        </ul>
        <hr>
        <p style="font-size: 1.2rem; color: #2E7D32;"><strong>Optimized ROAS: 3.5x (+25% more)</strong></p>
        <p style="color: #2E7D32; font-weight: 600;">Unbeatable. Trained on YOUR proprietary data.</p>
    </div>
    """, unsafe_allow_html=True)

# Key Benefits
st.markdown("---")
st.markdown("## ✨ Why Manufacturers Choose Federated LoRA")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔒 Your Data Stays Private
    
    - ✅ Train on your proprietary sales data
    - ✅ LoRA adapters are YOUR intellectual property
    - ✅ Never share sensitive information
    - ✅ Full control and ownership
    - ✅ Deploy in your own environment
    
    **Unlike SaaS AI**: Your competitive data never leaves your control.
    """)
    
    st.info("""
    **💡 Competitive Moat**: Your LoRA captures insights competitors can't replicate 
    because they don't have your data.
    """)

with col2:
    st.markdown("""
    ### 🚀 Fast & Cost-Effective
    
    - ⚡ Train in hours, not months
    - 💰 <1% of traditional training cost  
    - 🔄 Update and improve continuously
    - 🔥 Hot-swap without downtime
    - 📊 A/B test model versions in production
    
    **Result**: Iterate faster than competitors while spending less.
    """)
    
    st.success("""
    **📈 Proven Results**: Average 67% ROAS improvement, 89% prediction accuracy, 
    98% SKU coverage with manufacturer LoRA.
    """)

# Comparison Table
st.markdown("---")
st.markdown("## 📊 Compare Your Options")

comparison_df = pd.DataFrame({
    'Capability': [
        'Data Privacy',
        'Competitive Advantage',
        'Customization',
        'Training Cost',
        'Time to Deploy',
        'Continuous Improvement',
        'IP Ownership',
        'Performance (ROAS)'
    ],
    'Generic LLM Only': [
        '⚠️ Public model',
        '❌ Same for everyone',
        '❌ None',
        '$0 (pretrained)',
        'Immediate',
        '❌ Vendor controls',
        '❌ Not yours',
        '2.1x (baseline)'
    ],
    'Traditional SaaS AI': [
        '❌ Data shared',
        '⚠️ Limited',
        '⚠️ Config only',
        '$50K-500K/year',
        '6-12 months',
        '⚠️ Vendor controls',
        '❌ Vendor owns',
        '2.3x (vendor data)'
    ],
    'Federated LoRA (Recommended)': [
        '✅ 100% Private',
        '✅ Unique to you',
        '✅ Fully custom',
        '$8-127/training',
        '2-4 hours',
        '✅ You control',
        '✅ You own',
        '3.5x (your data)'
    ]
})

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        'Capability': st.column_config.TextColumn('Feature', width='medium'),
        'Generic LLM Only': st.column_config.TextColumn('Generic LLM', width='medium'),
        'Traditional SaaS AI': st.column_config.TextColumn('SaaS AI', width='medium'),
        'Federated LoRA (Recommended)': st.column_config.TextColumn('Federated LoRA ⭐', width='medium')
    }
)

# Success Stories
st.markdown("---")
st.markdown("## 📈 Success Stories")
st.markdown("**Real results from manufacturers using federated LoRA:**")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="value-card">
        <h4>🥤 CPG Brand X</h4>
        <p style="font-size: 1.5rem; color: #2E7D32; font-weight: 700;">+67% ROAS</p>
        <p>In first month of deployment</p>
        <hr>
        <p><em>"Trained manufacturer LoRA on 3 years of campaign data. 
        The product affinity insights were game-changing."</em></p>
        <p style="text-align: right; color: #666;">— Marketing Director</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="value-card">
        <h4>📱 Electronics Manufacturer</h4>
        <p style="font-size: 1.5rem; color: #2E7D32; font-weight: 700;">89% Reduction</p>
        <p>In wasted advertising spend</p>
        <hr>
        <p><em>"Proprietary product affinity models identified cross-sell opportunities 
        we never knew existed."</em></p>
        <p style="text-align: right; color: #666;">— VP of Digital Commerce</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="value-card">
        <h4>🍕 Food & Beverage Co</h4>
        <p style="font-size: 1.5rem; color: #2E7D32; font-weight: 700;">2 Hours</p>
        <p>To deploy vs 6 months before</p>
        <hr>
        <p><em>"LoRA federation enabled rapid iteration. We can test new strategies 
        in production same day."</em></p>
        <p style="text-align: right; color: #666;">— Head of Analytics</p>
    </div>
    """, unsafe_allow_html=True)

# Call to Action
st.markdown("---")

st.markdown("""
<div style="text-align: center; padding: 3rem 0;">
    <h2>Ready to Build Your Competitive Advantage?</h2>
    <p style="font-size: 1.2rem; color: #666; margin: 1rem 0 2rem 0;">
        Start with your data. Deploy in hours. Own your AI.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎯 Start Building Your Model Now", type="primary", use_container_width=True, key="cta_bottom"):
        st.switch_page("pages/1_build_your_model.py")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📊 See Live Demo", use_container_width=True, key="demo_bottom"):
            st.switch_page("streamlit_app.py")
    with col_b:
        if st.button("🔒 Learn About Data Privacy", use_container_width=True):
            st.switch_page("pages/2_privacy_story.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.9rem; padding: 2rem 0;">
    <p>🏭 Proprietary LoRA Federation for Retail Media Network Optimization</p>
    <p>Build your competitive advantage with AI that learns from YOUR data.</p>
</div>
""", unsafe_allow_html=True)
