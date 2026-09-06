export class LLaMAService {
  constructor() {
    this.baseURL = process.env.REACT_APP_LLAMA_API_URL || 'http://localhost:8000';
  }

  async generateAIAnalysis(analysisData, config) {
    try {
      const response = await fetch(`${this.baseURL}/api/analytics/llama-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token') || localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          analysis_data: analysisData,
          config: config,
          department: config.department
        })
      });

      if (!response.ok) {
        throw new Error(`LLaMA API error: ${response.statusText}`);
      }

      const result = await response.json();
      return result.analysis;
    } catch (error) {
      console.warn('LLaMA service unavailable, using fallback analysis:', error);
      return this.generateFallbackAnalysis(analysisData, config);
    }
  }

  generateFallbackAnalysis(analysisData, config) {
    // Fallback analysis when LLaMA is not available
    return {
      executive_summary: this.generateFallbackExecutiveSummary(analysisData, config),
      key_findings: analysisData.insights.map(insight => ({
        finding: insight.description,
        impact: insight.impact,
        confidence: insight.confidence
      })),
      narrative_analysis: this.generateNarrativeAnalysis(analysisData, config),
      strategic_recommendations: analysisData.recommendations.map(rec => ({
        recommendation: rec.title,
        rationale: rec.description,
        priority: rec.priority
      }))
    };
  }

  generateFallbackExecutiveSummary(analysis, config) {
    const { metadata, insights, recommendations } = analysis;

    return `
      This comprehensive analysis of ${metadata.fileName} reveals significant opportunities for ${config.department} optimization. 
      The dataset contains ${metadata.totalRows} records with ${metadata.totalColumns} variables, showing ${insights.filter(i => i.impact === 'high').length} high-impact insights.
      
      Key patterns include ${insights.slice(0, 2).map(i => i.description.toLowerCase()).join(' and ')}. 
      The analysis recommends ${recommendations.filter(r => r.priority === 'high').length} high-priority actions 
      that could drive substantial business value through data-informed decision making.
    `.trim();
  }

  generateNarrativeAnalysis(analysis, config) {
    const { patterns, statisticalAnalysis, predictiveInsights } = analysis;

    return `
      The data reveals compelling narratives about ${config.department} operations. 
      ${patterns.trends.length > 0 ? `Notable trends include ${patterns.trends.map(t => `${t.column} showing ${t.trend} movement`).join(', ')}.` : ''}
      ${patterns.correlations.length > 0 ? `Strong correlations were identified between key variables, suggesting potential causal relationships.` : ''}
      
      ${predictiveInsights.length > 0 ? `Looking forward, the analysis suggests ${predictiveInsights.map(p => p.prediction.toLowerCase()).join('; ')}.` : ''}
      
      These insights provide a foundation for strategic planning and operational improvements in the ${config.department} department.
    `.trim();
  }

  async processNaturalLanguageQuery(query, context) {
    try {
      const response = await fetch(`${this.baseURL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token') || localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          query: query,
          department: context.department,
          context: context
        })
      });

      if (!response.ok) {
        throw new Error(`Query API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.warn('LLaMA query service unavailable:', error);
      return {
        answer: "I'm unable to process your query right now. Please try again later or check the analysis report for insights.",
        insights: [],
        recommendations: []
      };
    }
  }
}

export const llamaService = new LLaMAService();