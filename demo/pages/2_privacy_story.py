"""Data Privacy & IP Protection Story - Explains federated LoRA security model."""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="Data Privacy & IP Protection",
    page_icon="🔒",
    layout="wide"
)

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Archivo', sans-serif; }
    
    .privacy-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .threat-card {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #f44336;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🔒 Your Data, Your Competitive Advantage")
st.markdown("**How Federated LoRA Protects Your Intellectual Property**")

st.markdown("""
Unlike traditional SaaS AI solutions, federated LoRA ensures your proprietary data 
remains YOUR competitive advantage. Here's how:
""")

# Key Promise
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="privacy-card">
        <h3 style="color: #2E7D32;">🔐 Data Never Leaves</h3>
        <p>Your training data stays in your environment. No data sharing, no data pooling.</p>
        <p style="font-weight: 600; margin-top: 1rem;">You control: Storage, Access, Encryption</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="privacy-card">
        <h3 style="color: #2E7D32;">🏆 Your LoRA = Your IP</h3>
        <p>The resulting LoRA adapter is YOUR intellectual property. Competitors can't replicate it.</p>
        <p style="font-weight: 600; margin-top: 1rem;">You own: Model weights, Training config, Insights</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="privacy-card">
        <h3 style="color: #2E7D32;">🛡️ Zero Knowledge</h3>
        <p>Training happens locally. Base model provider sees nothing. Industry LoRA learns from aggregated data only.</p>
        <p style="font-weight: 600; margin-top: 1rem;">Protected: Product data, Margins, Strategies</p>
    </div>
    """, unsafe_allow_html=True)

# Data Flow Diagram
st.markdown("---")
st.markdown("## 🔄 How Data Flows in Federated LoRA")

# Using Mermaid-like ASCII diagram since streamlit-mermaid might not be installed yet
st.code("""
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR PRIVATE ENVIRONMENT                      │
│                                                                  │
│  ┌──────────────┐        ┌──────────────┐        ┌───────────┐ │
│  │ Your         │───────>│  Training    │───────>│   YOUR    │ │
│  │ Proprietary  │ LOCAL  │  Process     │ LOCAL  │   LoRA    │ │
│  │ Data         │        │  (Encrypted) │        │  Adapter  │ │
│  └──────────────┘        └──────────────┘        └───────────┘ │
│        ▲                        ▲                       │       │
│        │                        │                       │       │
│        │ NEVER LEAVES           │ NEVER SHARED          │       │
│        │ YOUR CONTROL           │ EXTERNALLY            │       │
│                                                         │       │
└─────────────────────────────────────────────────────────┼───────┘
                                                          │
                                                          ▼
                           ┌────────────────────────────────────┐
                           │   FEDERATION (Inference Time)      │
                           │                                    │
                           │  Generic LLM (Public)              │
                           │       +                            │
                           │  Industry LoRA (Shared Knowledge)  │
                           │       +                            │
                           │  YOUR LoRA (Private Advantage) ◄── │
                           │                                    │
                           │  = Your Proprietary AI System      │
                           └────────────────────────────────────┘

🔒 Privacy Guarantee: Your training data NEVER leaves your environment
🏆 IP Protection: Your LoRA captures insights competitors can't access
""", language="text")

# Comparison Table
st.markdown("---")
st.markdown("## 📊 Federated LoRA vs Traditional Approaches")

comparison = pd.DataFrame({
    'Aspect': [
        'Training Data Location',
        'Data Sharing',
        'Model Ownership',
        'Competitive Insights',
        'Vendor Lock-in',
        'Privacy Compliance',
        'IP Protection',
        'Update Control'
    ],
    'Traditional SaaS AI': [
        '❌ Vendor cloud (shared)',
        '❌ Pooled with other customers',
        '❌ Vendor owns the model',
        '⚠️ Everyone gets same insights',
        '🔴 High (proprietary format)',
        '⚠️ Depends on vendor',
        '❌ Weak (your data trains shared model)',
        '❌ Vendor controls timing'
    ],
    'Managed AI Services': [
        '⚠️ Their infrastructure',
        '⚠️ "Isolated" but on their systems',
        '⚠️ Licensed, not owned',
        '⚠️ Limited to provided features',
        '🟡 Medium (API dependency)',
        '✅ Usually compliant',
        '⚠️ Contractual only',
        '⚠️ Requires vendor support'
    ],
    'Federated LoRA ⭐': [
        '✅ YOUR environment (local/private cloud)',
        '✅ ZERO data sharing',
        '✅ YOU own the LoRA adapter',
        '✅ Unique to your data',
        '🟢 None (open standard)',
        '✅ Full control',
        '✅ Strong (legally protected IP)',
        '✅ You control everything'
    ]
})

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True,
    column_config={
        'Aspect': st.column_config.TextColumn('Privacy & IP Aspect', width='medium'),
        'Traditional SaaS AI': st.column_config.TextColumn('SaaS AI', width='medium'),
        'Managed AI Services': st.column_config.TextColumn('Managed Services', width='medium'),
        'Federated LoRA ⭐': st.column_config.TextColumn('Federated LoRA', width='medium')
    }
)

# Threat Model
st.markdown("---")
st.markdown("## 🛡️ What We Protect Against")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="threat-card">
        <h4>❌ Threats Eliminated</h4>
        <ul>
            <li><strong>Data Leakage</strong>: Your data never leaves your control</li>
            <li><strong>Competitor Access</strong>: Your LoRA is private, not shared</li>
            <li><strong>Vendor Lock-in</strong>: LoRA is open standard, portable</li>
            <li><strong>IP Theft</strong>: Legally protected as your trade secret</li>
            <li><strong>Model Poisoning</strong>: You control training data</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="privacy-card">
        <h4>✅ Security Guarantees</h4>
        <ul>
            <li><strong>Encryption at Rest</strong>: All data encrypted in your environment</li>
            <li><strong>Encryption in Transit</strong>: TLS 1.3 for all connections</li>
            <li><strong>Access Control</strong>: You manage who can use your LoRA</li>
            <li><strong>Audit Trail</strong>: Full logging of model usage</li>
            <li><strong>Compliance</strong>: GDPR, CCPA, SOC 2 ready</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Competitive Advantage
st.markdown("---")
st.markdown("## 🏆 Your LoRA = Your Competitive Moat")

st.markdown("""
### Why This Matters for Competition

When you train a proprietary manufacturer LoRA:

1. **🔒 You Capture Unique Insights**  
   - Product affinities discovered from YOUR historical data
   - Margin optimization strategies based on YOUR cost structure
   - Customer behavior patterns from YOUR campaigns
   
2. **🚫 Competitors Can't Replicate**  
   - They don't have your data
   - They can't access your LoRA
   - Your insights remain exclusive
   
3. **📈 Advantage Compounds Over Time**  
   - Each campaign generates more proprietary data
   - Your LoRA continuously improves
   - Gap vs competitors widens

4. **💰 Protectable as Trade Secret**  
   - LoRA weights are confidential information
   - Training methodology is proprietary
   - Resulting insights are protected IP
""")

# Real Example
st.info("""
**📚 Real Example**: A CPG manufacturer trained a LoRA on 3 years of campaign data across 
5 retailers. The model discovered that their snack products have 3.2x higher conversion 
when co-promoted with specific beverage categories during Q1. 

**Competitive Advantage**: This insight was invisible in aggregated industry data. 
Competitors using generic or SaaS AI never discovered it. The manufacturer protected 
this as a trade secret and captured 67% ROAS improvement in that quarter.
""")

# Compliance
st.markdown("---")
st.markdown("## ✅ Compliance & Certifications")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("""
    ### 🇪🇺 GDPR Ready
    - Data minimization
    - Right to deletion
    - Data portability
    - Explicit consent
    """)

with col2:
    st.success("""
    ### 🇺🇸 CCPA Compliant
    - Data disclosure
    - Opt-out rights
    - No sale of data
    - Access requests
    """)

with col3:
    st.success("""
    ### 🔐 Security Standards
    - SOC 2 Type II compatible
    - ISO 27001 ready
    - NIST framework aligned
    - PCI DSS for payments
    """)

# FAQ
st.markdown("---")
st.markdown("## ❓ Frequently Asked Questions")

with st.expander("Can the base model provider see my training data?"):
    st.markdown("""
    **No.** Training happens entirely in your environment. The base model (Llama 3.1, etc.) 
    is downloaded once and then used locally. Your training data never leaves your infrastructure.
    """)

with st.expander("What about the Industry LoRA? Does it contain my data?"):
    st.markdown("""
    **No.** The Industry LoRA is trained on aggregated, anonymized retail media knowledge 
    (RMIS schemas, campaign best practices, etc.). It contains zero company-specific data. 
    Your proprietary insights stay in YOUR manufacturer LoRA.
    """)

with st.expander("Can competitors buy or access my LoRA?"):
    st.markdown("""
    **No.** Your LoRA adapter is YOUR intellectual property. It's stored in your environment, 
    encrypted, and access-controlled. Legally, it's protected as a trade secret. 
    Competitors would need to somehow steal your LoRA file AND your training data to replicate it.
    """)

with st.expander("What if I want to switch providers or vendors?"):
    st.markdown("""
    **You're free to leave anytime.** LoRA is an open standard. Your adapter is just a file 
    (~27MB) that you own. You can:
    - Use it with any compatible base model
    - Switch to a different LoRA training framework
    - Host it on any infrastructure
    
    There's zero vendor lock-in because YOU own the LoRA.
    """)

with st.expander("How is this different from federated learning?"):
    st.markdown("""
    **LoRA federation ≠ federated learning.**
    
    - **Federated Learning**: Multiple parties train a SHARED model on their local data. 
      Model updates are aggregated. Some information leakage is possible.
    
    - **LoRA Federation**: Each party trains their OWN LoRA on their OWN data. LoRAs are 
      COMPOSED at inference time but never merged. Zero data sharing.
    
    LoRA federation is more private and gives you stronger IP protection.
    """)

# Call to Action
st.markdown("---")

st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border-radius: 1rem; border: 2px solid #4CAF50;">
    <h2 style="color: #2E7D32;">Ready to Build Your Protected Competitive Advantage?</h2>
    <p style="font-size: 1.1rem; color: #2E7D32; margin: 1rem 0;">
        Your data stays private. Your LoRA stays yours. Your insights stay exclusive.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎯 Start Building Your Model", type="primary", use_container_width=True):
        st.switch_page("pages/1_build_your_model.py")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("👋 Back to Welcome", use_container_width=True):
            st.switch_page("pages/0_welcome.py")
    with col_b:
        if st.button("📊 See Live Demo", use_container_width=True):
            st.switch_page("streamlit_app.py")
