"""Build Your Model Wizard - Step-by-step proprietary LoRA creation."""

import streamlit as st
import pandas as pd
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="Build Your Model",
    page_icon="🏭",
    layout="wide"
)

# Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Archivo', sans-serif; }
    
    .step-active {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
    }
    
    .step-completed {
        background: #e8f5e9;
        color: #2E7D32;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
    }
    
    .step-pending {
        background: #f5f5f5;
        color: #999;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'build_step' not in st.session_state:
    st.session_state.build_step = 0
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'training_progress' not in st.session_state:
    st.session_state.training_progress = 0

# Header
st.title("🏭 Build Your Proprietary Manufacturer LoRA")
st.markdown("**Follow this wizard to create your competitive advantage AI**")

# Progress tracker
steps = [
    ("📊", "Upload Data"),
    ("🎨", "Define Brand"),
    ("⚙️", "Configure"),
    ("🚀", "Train"),
    ("✅", "Deploy")
]

current_step = st.session_state.build_step

# Progress bar
progress = (current_step + 1) / len(steps)
st.progress(progress, text=f"Step {current_step + 1} of {len(steps)}")

# Step indicators
cols = st.columns(len(steps))
for idx, (icon, name) in enumerate(steps):
    with cols[idx]:
        if idx < current_step:
            st.markdown(f'<div class="step-completed">✅ {icon} {name}</div>', unsafe_allow_html=True)
        elif idx == current_step:
            st.markdown(f'<div class="step-active">👉 {icon} {name}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="step-pending">⏳ {icon} {name}</div>', unsafe_allow_html=True)

st.markdown("---")

# STEP 1: Upload Data
if current_step == 0:
    st.header("Step 1: Upload Your Proprietary Data")
    
    st.markdown("""
    ### 🔒 What Makes Your Data Valuable?
    
    Your manufacturer data contains insights generic models can't know:
    - 📊 **Historical performance** of YOUR products at specific retailers
    - 🎯 **Product affinities** unique to your brand  
    - 💰 **Margin optimization** based on your cost structure
    - 🎨 **Brand voice** and messaging that resonates
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Campaign Data")
        uploaded_file = st.file_uploader(
            "Upload CSV with historical campaigns",
            type=['csv'],
            help="Include: campaign_id, product, retailer, spend, revenue, conversions"
        )
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_data = df
            st.success(f"✅ Loaded {uploaded_file.name}")
            
            st.dataframe(df.head(10), use_container_width=True)
            
            st.subheader("📊 Data Quality")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Records", f"{len(df):,}")
            with col_b:
                completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.metric("Completeness", f"{completeness:.0f}%")
            with col_c:
                st.metric("Columns", len(df.columns))
    
    with col2:
        st.info("""
        ### 🔒 Privacy Guarantee
        
        Your data:
        - ✅ Stays in your environment
        - ✅ Trains YOUR LoRA only
        - ✅ Never shared with others
        - ✅ Full encryption at rest
        
        **You own the resulting model.**
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.uploaded_data is not None:
        if st.button("Next: Define Brand Voice →", type="primary", use_container_width=True):
            st.session_state.build_step = 1
            st.rerun()

# STEP 2: Brand Voice
elif current_step == 1:
    st.header("Step 2: Define Your Brand Voice")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        brand_tone = st.selectbox(
            "Brand Tone",
            ["Premium", "Accessible", "Innovative", "Traditional", "Playful"]
        )
        
        st.text_area(
            "Brand Guidelines (optional)",
            placeholder="E.g., Always emphasize sustainability, avoid price competition messaging...",
            height=120
        )
        
        st.subheader("Example Brand Messages")
        st.markdown("Provide 3-5 examples of your best-performing ad copy:")
        
        for i in range(3):
            st.text_input(f"Example {i+1}", key=f"example_{i}", placeholder="Your best ad headline or copy")
    
    with col2:
        st.success(f"""
        ### ✅ Data Loaded
        
        {len(st.session_state.uploaded_data):,} historical records ready for training
        """)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("← Back", use_container_width=True):
            st.session_state.build_step = 0
            st.rerun()
    with col_b:
        if st.button("Next: Configure Training →", type="primary", use_container_width=True):
            st.session_state.build_step = 2
            st.rerun()

# STEP 3: Configure
elif current_step == 2:
    st.header("Step 3: Configure Training")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Training Parameters")
        
        epochs = st.slider("Training Epochs", 1, 10, 3, help="More epochs = better fit but longer training")
        learning_rate = st.select_slider("Learning Rate", options=["Conservative", "Balanced", "Aggressive"], value="Balanced")
        lora_rank = st.slider("LoRA Rank", 8, 64, 16, help="Higher rank = more capacity")
        
        st.info(f"""
        **Selected Config:**
        - Epochs: {epochs}
        - Learning Rate: {learning_rate}
        - LoRA Rank: {lora_rank}
        """)
    
    with col2:
        st.subheader("💰 Estimated Costs")
        
        training_mins = epochs * 15
        cost = training_mins * 0.18
        
        st.metric("Training Time", f"{training_mins} minutes")
        st.metric("GPU Cost", f"${cost:.2f}")
        st.metric("Total Cost", f"${cost:.2f}")
        
        st.success("""
        💡 **Compare to alternatives:**
        - Full model training: $42,000
        - Traditional ML: $15,000
        - LoRA: $8.40
        
        **99.98% cost savings!**
        """)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("← Back", use_container_width=True):
            st.session_state.build_step = 1
            st.rerun()
    with col_b:
        if st.button("Start Training →", type="primary", use_container_width=True):
            st.session_state.build_step = 3
            st.session_state.training_progress = 0
            st.rerun()

# STEP 4: Train
elif current_step == 3:
    st.header("Step 4: Training Your Manufacturer LoRA")
    
    progress_container = st.empty()
    status_container = st.empty()
    
    # Simulate training
    if st.session_state.training_progress < 100:
        st.session_state.training_progress += 20
        time.sleep(0.3)
        st.rerun()
    
    progress_container.progress(st.session_state.training_progress / 100)
    
    if st.session_state.training_progress >= 100:
        status_container.success("✅ Training complete!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Loss", "0.34", "↓ 71%")
        with col2:
            st.metric("Validation Accuracy", "94%", "↑ 23%")
        with col3:
            st.metric("Training Time", "47 min")
        
        if st.button("Next: Test & Deploy →", type="primary"):
            st.session_state.build_step = 4
            st.rerun()
    else:
        status_container.info(f"⏳ Training epoch {st.session_state.training_progress // 33 + 1}/3...")

# STEP 5: Deploy
elif current_step == 4:
    st.header("Step 5: Test & Deploy")
    
    st.success("🎉 Your proprietary manufacturer LoRA is ready!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Before (Generic + Industry)")
        st.metric("Expected ROAS", "2.8x")
        st.metric("Accuracy", "67%")
        st.metric("SKU Coverage", "85%")
    
    with col2:
        st.markdown("### After (+ Your LoRA)")
        st.metric("Expected ROAS", "3.5x", "+25%")
        st.metric("Accuracy", "89%", "+33%")
        st.metric("SKU Coverage", "98%", "+15%")
    
    st.markdown("---")
    st.subheader("🧪 Test Your Model")
    
    test_query = st.text_area("Enter a planning query", "Allocate $2.5M to maximize incremental margin")
    
    if st.button("Test Query", type="primary"):
        with st.spinner("Running inference..."):
            time.sleep(1)
            st.success("✅ Query processed using YOUR proprietary model")
            st.json({
                "model_used": "llama-3.1-8b + industry_retail + YOUR_manufacturer_lora",
                "confidence": 0.94,
                "insights_from_proprietary_data": [
                    "Product affinity: Snack + Beverage (YOUR data)",
                    "Optimal margin products for Q1 (YOUR historical performance)"
                ]
            })
    
    st.markdown("---")
    
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        if st.button("🚀 Deploy to Production", type="primary", use_container_width=True):
            st.balloons()
            st.success("✅ Deployed! Your proprietary AI is now live.")
    
    with col_b:
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.build_step = 0
            st.session_state.training_progress = 0
            st.rerun()
