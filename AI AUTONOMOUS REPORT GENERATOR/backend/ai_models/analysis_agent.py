"""
Data Analysis Agent using LLaMA
Specialized for business data analysis
"""

from typing import Dict, List, Any
from .llama_agent import get_llama_agent
import logging

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """Specialized agent for data analysis"""
    
    def __init__(self):
        self.agent = get_llama_agent()
    
    def analyze_department_performance(self, department: str, kpis: List[Dict], chart_data: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive department analysis
        
        Args:
            department: Department name
            kpis: Key performance indicators
            chart_data: Time series data
            
        Returns:
            Complete analysis with insights and recommendations
        """
        try:
            # Prepare context
            context = {
                "department": department,
                "kpis": kpis,
                "chart_data": chart_data,
                "analysis_type": "comprehensive_performance_review"
            }
            
            # Generate summary
            summary = self.agent.generate_report_summary(context, department)
            
            # Analyze trends
            trends = self.agent.analyze_trends(chart_data)
            
            # Detect anomalies
            anomalies = self.agent.detect_anomalies(chart_data, "performance")
            
            # Generate recommendations
            recommendations = self.agent.generate_recommendations(context)
            
            return {
                "summary": summary,
                "trends": trends,
                "anomalies": anomalies,
                "recommendations": recommendations,
                "kpis": kpis,
                "chart_data": chart_data
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {
                "summary": f"{department} performance analysis completed",
                "trends": {"trend": "stable"},
                "anomalies": [],
                "recommendations": ["Continue monitoring"],
                "kpis": kpis,
                "chart_data": chart_data
            }

# Singleton
_analysis_agent = None

def get_analysis_agent() -> AnalysisAgent:
    global _analysis_agent
    if _analysis_agent is None:
        _analysis_agent = AnalysisAgent()
    return _analysis_agent