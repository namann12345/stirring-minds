"""
Test LLaMA Agent
"""

import os
from dotenv import load_dotenv
from ai_models.llama_agent import get_llama_agent

load_dotenv()

def test_query():
    """Test basic query"""
    print("🧪 Testing LLaMA Agent...")
    
    agent = get_llama_agent()
    
    # Test query
    context = {
        "department": "sales",
        "kpis": [
            {"label": "Total Deals", "value": "156", "change": "+22%"},
            {"label": "Revenue", "value": "$2.4M", "change": "+12%"}
        ]
    }
    
    result = agent.process_query(
        "What was the Q2 sales performance?",
        context
    )
    
    print("\n✅ Query Result:")
    print(f"Answer: {result['answer']}")
    print(f"\nInsights: {result['insights']}")
    print(f"\nRecommendations: {result['recommendations']}")

if __name__ == "__main__":
    test_query()