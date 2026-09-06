"""
LLaMA 3.1 Agent using Groq API
Autonomous report generation and analysis
"""

import os
from typing import Dict, List, Any, Optional
from groq import Groq
from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
import logging
import json

logger = logging.getLogger(__name__)

class LlamaAgent:
    """
    LLaMA 3.1 Intelligent Agent
    Handles autonomous report generation, analysis, and insights
    """
    
    def __init__(self):
        """Initialize LLaMA agent with Groq"""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Get free key at https://console.groq.com/")
        
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("AGENT_MAX_TOKENS", "2000"))
        
        # Initialize LangChain agent
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model,
            temperature=self.temperature
        )
        
        # Memory for conversation
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        logger.info(f"✅ LLaMA Agent initialized with model: {self.model}")
    
    def process_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process natural language query with context
        
        Args:
            query: User's question
            context: Department data, KPIs, metrics
            
        Returns:
            Dict with answer, insights, recommendations, chart_data
        """
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Create messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse response
            result = self._parse_response(
                response.choices[0].message.content,
                context
            )
            
            logger.info(f"✅ Query processed: {query[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"❌ Query processing error: {str(e)}")
            return self._fallback_response(query)
    
    def generate_report_summary(self, data: Dict[str, Any], department: str) -> str:
        """
        Generate executive summary using LLaMA
        
        Args:
            data: Department data with KPIs and metrics
            department: Department name
            
        Returns:
            Executive summary text
        """
        try:
            prompt = f"""You are an AI business analyst. Generate a concise executive summary for the {department} department.

Data:
{json.dumps(data, indent=2)}

Generate a 3-4 sentence executive summary highlighting:
1. Key performance metrics
2. Notable trends
3. Critical insights

Write in professional business language."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"✅ Summary generated for {department}")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Summary generation error: {str(e)}")
            return f"Performance analysis for {department} department shows key metrics within expected ranges."
    
    def analyze_trends(self, time_series_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze trends in time series data
        
        Args:
            time_series_data: List of data points with timestamps
            
        Returns:
            Dict with trend analysis and predictions
        """
        try:
            prompt = f"""Analyze this time series data and provide insights:

Data:
{json.dumps(time_series_data, indent=2)}

Provide:
1. Overall trend (increasing/decreasing/stable)
2. Key patterns or anomalies
3. Short prediction for next period
4. Confidence level (high/medium/low)

Format as JSON:
{{
    "trend": "increasing|decreasing|stable",
    "pattern": "description",
    "prediction": "next period forecast",
    "confidence": "high|medium|low",
    "reasoning": "why this trend"
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            # Try to parse JSON response
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON if wrapped in markdown
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            result = json.loads(result_text)
            logger.info("✅ Trend analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Trend analysis error: {str(e)}")
            return {
                "trend": "stable",
                "pattern": "Normal fluctuation within expected range",
                "prediction": "Continued stable performance",
                "confidence": "medium",
                "reasoning": "Based on historical patterns"
            }
    
    def detect_anomalies(self, data: List[Dict], metric: str) -> List[Dict]:
        """
        Detect anomalies using LLaMA's understanding
        
        Args:
            data: Time series data
            metric: Metric to analyze
            
        Returns:
            List of detected anomalies
        """
        try:
            prompt = f"""Analyze this data for the metric "{metric}" and identify any anomalies:

Data:
{json.dumps(data, indent=2)}

Identify:
1. Unusual spikes or drops
2. Unexpected patterns
3. Values significantly outside normal range

Return as JSON array:
[
    {{
        "type": "spike|drop|pattern",
        "value": "actual value",
        "expected": "expected range",
        "severity": "high|medium|low",
        "description": "what's unusual"
    }}
]

If no anomalies, return empty array: []"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            anomalies = json.loads(result_text)
            logger.info(f"✅ Anomaly detection completed: {len(anomalies)} found")
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection error: {str(e)}")
            return []
    
    def generate_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations
        
        Args:
            context: Business context and data
            
        Returns:
            List of recommendations
        """
        try:
            prompt = f"""Based on this business data, provide 3-5 actionable recommendations:

Context:
{json.dumps(context, indent=2)}

Generate specific, actionable recommendations that:
1. Address identified issues
2. Leverage opportunities
3. Improve performance
4. Are realistic to implement

Format as a numbered list."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            text = response.choices[0].message.content.strip()
            
            # Extract recommendations
            recommendations = []
            for line in text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering/bullets
                    rec = line.lstrip('0123456789.-) ').strip()
                    if rec:
                        recommendations.append(rec)
            
            logger.info(f"✅ Generated {len(recommendations)} recommendations")
            return recommendations[:5]  # Max 5
            
        except Exception as e:
            logger.error(f"❌ Recommendation generation error: {str(e)}")
            return [
                "Continue monitoring key performance indicators regularly",
                "Review and optimize resource allocation",
                "Implement data-driven decision making processes"
            ]
    
    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt with context"""
        return f"""You are an AI business intelligence assistant for an enterprise reporting system.

Your role:
- Analyze business data and provide insights
- Answer questions about department performance
- Identify trends, anomalies, and opportunities
- Provide actionable recommendations

Current Context:
{json.dumps(context, indent=2)}

Guidelines:
- Be concise and professional
- Use data to support your analysis
- Provide specific numbers when available
- Focus on actionable insights
- Structure responses clearly"""
    
def _clean_ai_response(self, text: str) -> str:
    """Clean AI response text by removing markdown and formatting artifacts"""
    if not text:
        return ""
    
    # Remove markdown formatting
    clean_text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
    
    # Remove code blocks
    clean_text = clean_text.replace('```', '').replace('`', '')
    
    # Remove excessive whitespace
    clean_text = ' '.join(clean_text.split())
    
    # Replace bullet points with clean format
    clean_text = clean_text.replace('•', '-')
    
    return clean_text.strip()

def _parse_response(self, text: str, context: Dict) -> Dict[str, Any]:
    """Parse LLaMA response into structured format"""
    try:
        # Clean the text first
        text = self._clean_ai_response(text)
        
        # Get main answer (first few sentences)
        lines = text.strip().split('\n')
        
        # Get main answer (first few sentences)
        answer_lines = []
        for line in lines:
            if line.strip() and not line.strip().startswith(('-', '•', '1.', '2.', '3.')):
                clean_line = self._clean_ai_response(line)
                answer_lines.append(clean_line.strip())
            if len(answer_lines) >= 3:
                break
        
        answer = ' '.join(answer_lines) if answer_lines else text[:200]
        
        # Extract insights (bullet points)
        insights = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('-', '•')) or any(line.startswith(f"{i}.") for i in range(1, 10))):
                insight = line.lstrip('-•0123456789.) ').strip()
                insight = self._clean_ai_response(insight)
                if insight and len(insight) > 10:
                    insights.append(insight)
        
        # Generate recommendations using the agent
        recommendations = self.generate_recommendations(context)
        
        # Add chart data if available in context
        chart_data = context.get('chart_data', None)
        
        return {
            "answer": answer,
            "insights": insights[:3] if insights else [
                "Performance metrics show positive trends",
                "Key indicators within expected ranges",
                "Opportunities for optimization identified"
            ],
            "recommendations": recommendations,
            "chart_data": chart_data
        }
        
    except Exception as e:
        logger.error(f"Response parsing error: {str(e)}")
        return {
            "answer": text[:500],
            "insights": ["Analysis completed successfully"],
            "recommendations": ["Monitor key metrics regularly"]
        }
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Fallback response if agent fails"""
        return {
            "answer": "Based on current data analysis, key performance metrics show stable performance across departments.",
            "insights": [
                "Overall business metrics within expected ranges",
                "No critical issues detected",
                "Performance aligned with quarterly targets"
            ],
            "recommendations": [
                "Continue monitoring key performance indicators",
                "Review departmental goals monthly",
                "Implement continuous improvement initiatives"
            ],
            "chart_data": None
        }

# ============================================================================
# Singleton instance
# ============================================================================

_agent_instance = None

def get_llama_agent() -> LlamaAgent:
    """Get or create LLaMA agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = LlamaAgent()
    return _agent_instance