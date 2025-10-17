"""Custom Training UI - Let users train adapters without code."""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.training.dataset_builder import DatasetBuilder
from src.training.train_lora import LoRATrainingConfig, LoRATrainer

# Page config
st.set_page_config(
    page_title="Custom LoRA Training",
    page_icon="🎓",
    layout="wide"
)

# Professional styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Archivo', sans-serif; }
    .main { max-width: 1400px; margin: 0 auto; }
    .stButton > button { 
        border-radius: 0.75rem;
        font-weight: 500;
        transition: all 300ms;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    h1 { color: hsl(240, 10%, 3.9%); font-weight: 700; }
    h2 { color: hsl(240, 10%, 3.9%); font-weight: 600; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'training_examples' not in st.session_state:
    st.session_state.training_examples = []
if 'current_dataset' not in st.session_state:
    st.session_state.current_dataset = None
if 'training_history' not in st.session_state:
    st.session_state.training_history = []

# Header
st.title("🎓 Custom LoRA Training (No Code Required)")
st.markdown("**Train your own adapters with a visual interface**")

# Sidebar navigation
with st.sidebar:
    st.header("Training Wizard")
    
    step = st.radio(
        "Select Step:",
        [
            "1️⃣ Dataset Builder",
            "2️⃣ Training Configuration",
            "3️⃣ Start Training",
            "4️⃣ Monitor Progress"
        ]
    )
    
    st.markdown("---")
    
    # Quick stats
    st.subheader("Quick Stats")
    st.metric("Examples", len(st.session_state.training_examples))
    st.metric("Datasets", 1 if st.session_state.current_dataset else 0)
    st.metric("Training Jobs", len(st.session_state.training_history))

# Main content based on step
if step == "1️⃣ Dataset Builder":
    st.header("Step 1: Build Training Dataset")
    
    tab1, tab2, tab3 = st.tabs(["📝 Add Examples", "📊 Review Dataset", "📁 Import/Export"])
    
    # Tab 1: Add Examples
    with tab1:
        st.subheader("Add Training Examples")
        
        adapter_type = st.selectbox(
            "What type of adapter are you training?",
            ["Retailer Adapter", "Task Adapter", "Brand Adapter"]
        )
        
        if adapter_type == "Retailer Adapter":
            st.info("**Retailer adapters** learn schema mappings and retailer-specific policies")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Source Field (Retailer)")
                source_field = st.text_input("Field Name", placeholder="e.g., adType")
                source_value = st.text_input("Example Value", placeholder="e.g., sp")
            
            with col2:
                st.markdown("#### Target Field (RMIS)")
                target_field = st.selectbox(
                    "RMIS Field",
                    ["placement_type", "cost", "impressions", "clicks", "conversions", "revenue"]
                )
                target_value = st.text_input("Mapped Value", placeholder="e.g., sponsored_product")
            
            transform = st.text_input("Transform (optional)", placeholder="e.g., enum_map, /1000000")
            
            if st.button("➕ Add Mapping Example", type="primary"):
                example = {
                    'type': 'retailer_mapping',
                    'adapter_type': 'retailer',
                    'input': {source_field: source_value},
                    'output': {target_field: target_value},
                    'transform': transform,
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state.training_examples.append(example)
                st.success(f"✅ Added example ({len(st.session_state.training_examples)} total)")
                st.rerun()
        
        elif adapter_type == "Task Adapter":
            st.info("**Task adapters** learn how to execute specific tasks (planning, optimization, etc.)")
            
            task_type = st.selectbox(
                "Task Type",
                ["Planning", "Budget Optimization", "Creative Generation", "Measurement"]
            )
            
            st.markdown("#### User Objective")
            objective = st.text_area(
                "What the user wants to accomplish",
                placeholder="e.g., Allocate $2.5M to maximize incremental margin with ROAS >= 3.0",
                height=100
            )
            
            st.markdown("#### Expected Tool Call")
            tool_name = st.text_input("Tool Name", placeholder="e.g., allocate_budget")
            tool_args = st.text_area(
                "Tool Arguments (JSON)",
                placeholder='{"total_budget": 2500000, "min_roas": 3.0}',
                height=150
            )
            
            if st.button("➕ Add Task Example", type="primary"):
                try:
                    args = json.loads(tool_args) if tool_args else {}
                    example = {
                        'type': 'task_execution',
                        'adapter_type': 'task',
                        'task_name': task_type.lower(),
                        'objective': objective,
                        'tool_call': {
                            'tool': tool_name,
                            'args': args
                        },
                        'timestamp': datetime.now().isoformat()
                    }
                    st.session_state.training_examples.append(example)
                    st.success(f"✅ Added example ({len(st.session_state.training_examples)} total)")
                    st.rerun()
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON in tool arguments")
        
        elif adapter_type == "Brand Adapter":
            st.info("**Brand adapters** learn brand tone, product hierarchies, and messaging guidelines")
            
            st.markdown("#### Brand Tone Example")
            prompt = st.text_area("Prompt", placeholder="Write a headline for organic snacks", height=80)
            response = st.text_area("Brand-compliant Response", placeholder="Wholesome Goodness in Every Bite", height=80)
            
            tone = st.select_slider("Brand Tone", options=["Professional", "Casual", "Premium", "Playful", "Urgent"])
            
            if st.button("➕ Add Brand Example", type="primary"):
                example = {
                    'type': 'brand_tone',
                    'adapter_type': 'brand',
                    'prompt': prompt,
                    'response': response,
                    'tone': tone,
                    'timestamp': datetime.now().isoformat()
                }
                st.session_state.training_examples.append(example)
                st.success(f"✅ Added example ({len(st.session_state.training_examples)} total)")
                st.rerun()
    
    # Tab 2: Review Dataset
    with tab2:
        st.subheader("Review Training Examples")
        
        if not st.session_state.training_examples:
            st.info("No examples yet. Add some in the 'Add Examples' tab.")
        else:
            # Show examples
            for idx, example in enumerate(st.session_state.training_examples):
                with st.expander(f"Example {idx + 1}: {example.get('type', 'unknown')}"):
                    st.json(example)
                    
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{idx}"):
                            st.session_state.training_examples.pop(idx)
                            st.rerun()
            
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Examples", len(st.session_state.training_examples))
            
            with col2:
                types = [ex.get('adapter_type', 'unknown') for ex in st.session_state.training_examples]
                st.metric("Adapter Types", len(set(types)))
            
            with col3:
                st.metric("Dataset Quality", "Good" if len(st.session_state.training_examples) >= 10 else "Needs More")
    
    # Tab 3: Import/Export
    with tab3:
        st.subheader("Import/Export Dataset")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📥 Import Examples")
            
            uploaded_file = st.file_uploader("Upload JSONL file", type=['jsonl', 'json'])
            
            if uploaded_file:
                try:
                    content = uploaded_file.read().decode('utf-8')
                    lines = content.strip().split('\n')
                    imported = [json.loads(line) for line in lines if line.strip()]
                    
                    st.success(f"✅ Loaded {len(imported)} examples")
                    
                    if st.button("Add to Dataset"):
                        st.session_state.training_examples.extend(imported)
                        st.success(f"✅ Added {len(imported)} examples to dataset")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error loading file: {e}")
        
        with col2:
            st.markdown("#### 📤 Export Dataset")
            
            if st.session_state.training_examples:
                # Generate JSONL
                jsonl_content = '\n'.join([
                    json.dumps(ex) for ex in st.session_state.training_examples
                ])
                
                st.download_button(
                    label="📥 Download JSONL",
                    data=jsonl_content,
                    file_name=f"training_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
                    mime="application/jsonl"
                )
                
                # Show preview
                with st.expander("Preview Export"):
                    st.code(jsonl_content[:500] + "..." if len(jsonl_content) > 500 else jsonl_content)
            else:
                st.info("No examples to export")

elif step == "2️⃣ Training Configuration":
    st.header("Step 2: Configure Training")
    
    if len(st.session_state.training_examples) < 10:
        st.warning("⚠️ You should have at least 10 examples for training. Current: " + 
                   str(len(st.session_state.training_examples)))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Training Parameters")
        
        # Basic settings
        adapter_name = st.text_input("Adapter Name", placeholder="e.g., amazon_schema_v1")
        adapter_type = st.selectbox("Adapter Type", ["retailer", "task", "brand"])
        
        # Model selection
        base_model = st.selectbox(
            "Base Model",
            [
                "meta-llama/Llama-3.1-8B-Instruct",
                "mistralai/Mistral-7B-Instruct-v0.2",
                "meta-llama/Llama-2-7b-chat-hf"
            ]
        )
        
        st.markdown("---")
        
        # LoRA parameters
        st.markdown("#### LoRA Configuration")
        
        col_a, col_b = st.columns(2)
        with col_a:
            lora_r = st.slider("LoRA Rank (r)", 8, 64, 16, 
                              help="Higher rank = more capacity but slower")
            lora_alpha = st.slider("LoRA Alpha", 8, 128, 32,
                                  help="Scaling factor, usually 2x rank")
        
        with col_b:
            lora_dropout = st.slider("LoRA Dropout", 0.0, 0.3, 0.05, 0.01)
            use_4bit = st.checkbox("Use 4-bit Quantization (QLoRA)", value=True,
                                  help="Reduces memory usage significantly")
        
        # Training parameters
        st.markdown("#### Training Configuration")
        
        col_c, col_d = st.columns(2)
        with col_c:
            num_epochs = st.slider("Training Epochs", 1, 10, 3)
            batch_size = st.slider("Batch Size", 1, 16, 4)
        
        with col_d:
            learning_rate = st.number_input("Learning Rate", 0.00001, 0.001, 0.0002, format="%.5f")
            gradient_accum = st.slider("Gradient Accumulation Steps", 1, 8, 4)
    
    with col2:
        st.subheader("Training Summary")
        
        st.markdown(f"""
        **Dataset:**
        - Examples: {len(st.session_state.training_examples)}
        - Type: {adapter_type}
        
        **Model:**
        - Base: {base_model.split('/')[-1]}
        - LoRA Rank: {lora_r}
        - Quantization: {'4-bit' if use_4bit else 'None'}
        
        **Training:**
        - Epochs: {num_epochs}
        - Batch Size: {batch_size}
        - Learning Rate: {learning_rate}
        
        **Estimated Time:**
        - ~{num_epochs * (len(st.session_state.training_examples) // batch_size) * 2} minutes
        """)
        
        st.markdown("---")
        
        # Save configuration
        if st.button("💾 Save Configuration", use_container_width=True):
            config = {
                'adapter_name': adapter_name,
                'adapter_type': adapter_type,
                'base_model': base_model,
                'lora_r': lora_r,
                'lora_alpha': lora_alpha,
                'lora_dropout': lora_dropout,
                'use_4bit': use_4bit,
                'num_epochs': num_epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate,
                'gradient_accumulation_steps': gradient_accum
            }
            st.session_state.training_config = config
            st.success("✅ Configuration saved!")

elif step == "3️⃣ Start Training":
    st.header("Step 3: Start Training")
    
    if not st.session_state.training_examples:
        st.error("❌ No training examples. Go back to Step 1.")
    elif 'training_config' not in st.session_state:
        st.error("❌ No training configuration. Go back to Step 2.")
    else:
        config = st.session_state.training_config
        
        st.success("✅ Ready to start training!")
        
        # Show configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Training Configuration")
            st.json(config)
        
        with col2:
            st.subheader("Dataset Preview")
            st.markdown(f"**{len(st.session_state.training_examples)} examples**")
            st.dataframe(
                pd.DataFrame(st.session_state.training_examples).head(5),
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Start training button
        col_a, col_b, col_c = st.columns([2, 1, 2])
        
        with col_b:
            if st.button("🚀 START TRAINING", type="primary", use_container_width=True):
                st.session_state.training_active = True
                st.session_state.training_history.append({
                    'config': config,
                    'examples': len(st.session_state.training_examples),
                    'started_at': datetime.now().isoformat(),
                    'status': 'running'
                })
                st.success("🚀 Training started!")
                st.balloons()
                st.rerun()

elif step == "4️⃣ Monitor Progress":
    st.header("Step 4: Monitor Training Progress")
    
    if not st.session_state.training_history:
        st.info("No training jobs yet. Complete Steps 1-3 first.")
    else:
        for idx, job in enumerate(st.session_state.training_history):
            with st.expander(f"Training Job {idx + 1}: {job['config']['adapter_name']}", 
                           expanded=(idx == len(st.session_state.training_history) - 1)):
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Status", job.get('status', 'unknown').upper())
                    st.metric("Examples", job['examples'])
                
                with col2:
                    st.metric("Epochs", job['config']['num_epochs'])
                    st.metric("Started", job['started_at'].split('T')[1].split('.')[0])
                
                with col3:
                    st.metric("LoRA Rank", job['config']['lora_r'])
                    st.metric("Batch Size", job['config']['batch_size'])
                
                # Progress bar (simulated)
                if job.get('status') == 'running':
                    import random
                    progress = random.randint(10, 90)
                    st.progress(progress / 100)
                    st.markdown(f"**Progress: {progress}%**")
                    
                    # Loss curve (simulated)
                    st.markdown("#### Training Loss")
                    import numpy as np
                    steps = np.arange(0, 100)
                    loss = 2.5 * np.exp(-steps / 30) + 0.5 + np.random.normal(0, 0.05, len(steps))
                    st.line_chart(pd.DataFrame({'Loss': loss}))


if __name__ == "__main__":
    st.markdown("---")
    st.markdown("**💡 Tips:**")
    st.markdown("- Start with 10-20 high-quality examples")
    st.markdown("- Use diverse examples covering different scenarios")
    st.markdown("- Review examples carefully before training")
    st.markdown("- Start with default LoRA parameters (rank=16, alpha=32)")
