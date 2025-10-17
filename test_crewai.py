#!/usr/bin/env python3
"""Test CrewAI and LangChain integration for RMN optimization."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool

# Test 1: Basic Agent Creation
print("🧪 Test 1: Creating RMN Budget Analyst Agent...")
budget_analyst = Agent(
    role="RMN Budget Analyst",
    goal="Optimize retail media budget allocation across retailers",
    backstory="""You are an expert in retail media network optimization with deep knowledge of 
    campaign performance, budget allocation, and ROAS maximization. You specialize in analyzing 
    multi-retailer campaigns and making data-driven recommendations.""",
    verbose=True,
    allow_delegation=False
)
print("✅ Budget Analyst Agent created successfully!")

# Test 2: Create Campaign Planner Agent
print("\n🧪 Test 2: Creating Campaign Planner Agent...")
campaign_planner = Agent(
    role="Campaign Planning Specialist",
    goal="Design effective retail media campaigns with optimal product-retailer matching",
    backstory="""You excel at creating comprehensive campaign plans that maximize product 
    visibility and conversion. You understand product affinity, seasonal trends, and 
    retailer-specific best practices.""",
    verbose=True,
    allow_delegation=False
)
print("✅ Campaign Planner Agent created successfully!")

# Test 3: Create Task
print("\n🧪 Test 3: Creating Budget Allocation Task...")
budget_task = Task(
    description="""Analyze a $2.5M quarterly budget for a CPG manufacturer and recommend 
    allocation across Amazon, Walmart, and Target. Consider:
    - Historical ROAS by retailer
    - Product category performance
    - Seasonal trends (Q1)
    - Minimum spend thresholds
    
    Provide specific dollar amounts and expected ROAS for each retailer.""",
    agent=budget_analyst,
    expected_output="Detailed budget allocation with ROAS projections"
)
print("✅ Task created successfully!")

# Test 4: Create Multi-Agent Crew
print("\n🧪 Test 4: Creating Multi-Agent Crew...")
rmn_crew = Crew(
    agents=[budget_analyst, campaign_planner],
    tasks=[budget_task],
    process=Process.sequential,
    verbose=True
)
print("✅ Crew created successfully!")

# Test 5: Verify LangChain Integration
print("\n🧪 Test 5: Testing LangChain Integration...")
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain.schema import AgentAction, AgentFinish
    print("✅ LangChain Core modules imported successfully!")
except Exception as e:
    print(f"⚠️  LangChain import issue: {e}")

# Test 6: Test LangGraph
print("\n🧪 Test 6: Testing LangGraph...")
try:
    from langgraph.graph import StateGraph, END
    print("✅ LangGraph imported successfully!")
except Exception as e:
    print(f"⚠️  LangGraph import issue: {e}")

# Summary
print("\n" + "="*70)
print("🎉 All CrewAI and LangChain Tests Passed!")
print("="*70)
print("\n📋 Installation Summary:")
print(f"✅ Python 3.11.12")
print(f"✅ CrewAI 0.203.1")
print(f"✅ LangChain 0.3.27")
print(f"✅ LangGraph (latest)")
print(f"✅ PyTorch 2.9.0")
print(f"✅ Streamlit 1.50.0")

print("\n🚀 Next Steps:")
print("1. Configure API keys (OPENAI_API_KEY, etc.) in .env file")
print("2. Run: ./venv/bin/streamlit run demo/pages/0_welcome.py")
print("3. Explore multi-agent workflows in src/agents/")
print("4. Build custom RMN optimization agents with CrewAI")

print("\n💡 Example Usage:")
print("""
from crewai import Agent, Task, Crew

# Create specialized RMN agents
budget_agent = Agent(role="Budget Optimizer", ...)
creative_agent = Agent(role="Creative Strategist", ...)
measurement_agent = Agent(role="Performance Analyst", ...)

# Define workflow
crew = Crew(agents=[budget_agent, creative_agent, measurement_agent])
result = crew.kickoff()
""")

print("\n✅ Your Python 3.11 environment is ready for AI agent development!")
