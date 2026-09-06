import Papa from 'papaparse';

export class AIAnalysisAgent {
  constructor() {
    this.agentName = "CSV Analysis Agent";
    this.version = "1.0.0";
  }

  async analyzeCSV(file, config) {
    try {
      console.log(`🦙 ${this.agentName} starting analysis...`);
      
      // Parse CSV file
      const parsedData = await this.parseCSVFile(file, config.hasHeaders);
      
      // Perform comprehensive analysis
      const analysis = {
        metadata: this.extractMetadata(parsedData, file, config),
        statisticalAnalysis: this.performStatisticalAnalysis(parsedData),
        patternDetection: this.detectPatterns(parsedData),
        insights: this.generateAIInsights(parsedData, config),
        recommendations: this.generateRecommendations(parsedData, config),
        visualizations: this.prepareVisualizations(parsedData),
        anomalies: this.detectAnomalies(parsedData),
        predictiveInsights: this.generatePredictiveInsights(parsedData, config)
      };

      console.log(`✅ ${this.agentName} analysis completed`);
      return analysis;
    } catch (error) {
      console.error(`❌ ${this.agentName} analysis failed:`, error);
      throw error;
    }
  }

  async parseCSVFile(file, hasHeaders = true) {
    return new Promise((resolve, reject) => {
      Papa.parse(file, {
        header: hasHeaders,
        skipEmptyLines: true,
        dynamicTyping: true,
        complete: (results) => {
          if (results.errors.length > 0) {
            reject(new Error(`CSV parsing errors: ${results.errors.map(e => e.message).join(', ')}`));
          } else {
            resolve(results.data);
          }
        },
        error: (error) => reject(error)
      });
    });
  }

  extractMetadata(data, file, config) {
    const columns = data.length > 0 ? Object.keys(data[0]) : [];
    const numericColumns = columns.filter(col => 
      data.some(row => typeof row[col] === 'number' && !isNaN(row[col]))
    );
    const categoricalColumns = columns.filter(col => 
      !numericColumns.includes(col) && data.some(row => row[col] != null)
    );

    return {
      fileName: file.name,
      fileSize: this.formatFileSize(file.size),
      totalRows: data.length,
      totalColumns: columns.length,
      numericColumns: numericColumns.length,
      categoricalColumns: categoricalColumns.length,
      department: config.department,
      dataType: config.dataType,
      analysisTimestamp: new Date().toISOString(),
      columnDetails: columns.map(col => ({
        name: col,
        type: numericColumns.includes(col) ? 'numeric' : 'categorical',
        sampleValues: data.slice(0, 5).map(row => row[col]).filter(val => val != null)
      }))
    };
  }

  performStatisticalAnalysis(data) {
    if (data.length === 0) return {};
    
    const columns = Object.keys(data[0]);
    const numericColumns = columns.filter(col => 
      data.some(row => typeof row[col] === 'number' && !isNaN(row[col]))
    );

    const stats = {};
    
    numericColumns.forEach(column => {
      const values = data.map(row => row[column]).filter(val => typeof val === 'number' && !isNaN(val));
      
      if (values.length > 0) {
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const sorted = [...values].sort((a, b) => a - b);
        const median = sorted[Math.floor(sorted.length / 2)];
        const stdDev = Math.sqrt(values.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / values.length);
        const variance = Math.pow(stdDev, 2);
        
        stats[column] = {
          count: values.length,
          mean: parseFloat(mean.toFixed(2)),
          median: parseFloat(median.toFixed(2)),
          min: Math.min(...values),
          max: Math.max(...values),
          range: Math.max(...values) - Math.min(...values),
          standardDeviation: parseFloat(stdDev.toFixed(2)),
          variance: parseFloat(variance.toFixed(2)),
          sum: values.reduce((a, b) => a + b, 0),
          quartiles: {
            q1: sorted[Math.floor(sorted.length * 0.25)],
            q3: sorted[Math.floor(sorted.length * 0.75)]
          }
        };

        // Detect outliers using IQR method
        const iqr = stats[column].quartiles.q3 - stats[column].quartiles.q1;
        const lowerBound = stats[column].quartiles.q1 - 1.5 * iqr;
        const upperBound = stats[column].quartiles.q3 + 1.5 * iqr;
        
        stats[column].outliers = values.filter(v => v < lowerBound || v > upperBound).length;
        stats[column].outlierPercentage = parseFloat(((stats[column].outliers / values.length) * 100).toFixed(2));
      }
    });

    return stats;
  }

  detectPatterns(data) {
    const patterns = {
      trends: [],
      correlations: [],
      seasonality: [],
      clusters: []
    };

    if (data.length < 5) return patterns;

    const columns = Object.keys(data[0]);
    const numericColumns = columns.filter(col => 
      data.some(row => typeof row[col] === 'number' && !isNaN(row[col]))
    );

    // Trend detection
    numericColumns.forEach(column => {
      const values = data.map(row => row[column]).filter(val => typeof val === 'number' && !isNaN(val));
      
      if (values.length > 10) {
        const firstThird = values.slice(0, Math.floor(values.length / 3));
        const lastThird = values.slice(-Math.floor(values.length / 3));
        
        const firstAvg = firstThird.reduce((a, b) => a + b, 0) / firstThird.length;
        const lastAvg = lastThird.reduce((a, b) => a + b, 0) / lastThird.length;
        
        const trend = lastAvg > firstAvg ? 'increasing' : lastAvg < firstAvg ? 'decreasing' : 'stable';
        const changePercent = ((lastAvg - firstAvg) / firstAvg) * 100;
        
        if (Math.abs(changePercent) > 5) {
          patterns.trends.push({
            column,
            trend,
            changePercentage: parseFloat(changePercent.toFixed(2)),
            confidence: Math.min(100, Math.abs(changePercent) * 2)
          });
        }
      }
    });

    // Correlation detection
    if (numericColumns.length >= 2) {
      for (let i = 0; i < numericColumns.length; i++) {
        for (let j = i + 1; j < numericColumns.length; j++) {
          const col1 = numericColumns[i];
          const col2 = numericColumns[j];
          
          const values1 = data.map(row => row[col1]).filter(val => typeof val === 'number' && !isNaN(val));
          const values2 = data.map(row => row[col2]).filter(val => typeof val === 'number' && !isNaN(val));
          
          if (values1.length === values2.length && values1.length > 5) {
            const correlation = this.calculateCorrelation(values1, values2);
            
            if (Math.abs(correlation) > 0.7) {
              patterns.correlations.push({
                column1: col1,
                column2: col2,
                correlation: parseFloat(correlation.toFixed(3)),
                strength: Math.abs(correlation) > 0.9 ? 'strong' : Math.abs(correlation) > 0.7 ? 'moderate' : 'weak',
                direction: correlation > 0 ? 'positive' : 'negative'
              });
            }
          }
        }
      }
    }

    return patterns;
  }

  calculateCorrelation(x, y) {
    const n = x.length;
    const sum_x = x.reduce((a, b) => a + b, 0);
    const sum_y = y.reduce((a, b) => a + b, 0);
    const sum_xy = x.reduce((sum, val, i) => sum + val * y[i], 0);
    const sum_x2 = x.reduce((sum, val) => sum + val * val, 0);
    const sum_y2 = y.reduce((sum, val) => sum + val * val, 0);
    
    const numerator = n * sum_xy - sum_x * sum_y;
    const denominator = Math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y));
    
    return denominator === 0 ? 0 : numerator / denominator;
  }

  generateAIInsights(data, config) {
    const insights = [];
    const stats = this.performStatisticalAnalysis(data);
    const patterns = this.detectPatterns(data);
    const metadata = this.extractMetadata(data, { name: '', size: 0 }, config);

    // Data Quality Insights
    const totalCells = metadata.totalRows * metadata.totalColumns;
    const numericCells = Object.values(stats).reduce((sum, col) => sum + col.count, 0);
    const dataCompleteness = (numericCells / totalCells) * 100;

    if (dataCompleteness < 80) {
      insights.push({
        type: 'warning',
        category: 'Data Quality',
        title: 'Low Data Completeness',
        description: `Only ${dataCompleteness.toFixed(1)}% of cells contain numeric data. Consider data cleaning.`,
        impact: 'high',
        confidence: 85
      });
    }

    // Statistical Insights
    Object.entries(stats).forEach(([column, stat]) => {
      if (stat.outlierPercentage > 10) {
        insights.push({
          type: 'warning',
          category: 'Data Distribution',
          title: 'High Outlier Presence',
          description: `${column} has ${stat.outlierPercentage}% outliers, which may skew analysis.`,
          impact: 'medium',
          confidence: 90
        });
      }

      if (stat.standardDeviation / stat.mean > 0.5) {
        insights.push({
          type: 'info',
          category: 'Data Variability',
          title: 'High Data Variability',
          description: `${column} shows significant variability (CV: ${((stat.standardDeviation / stat.mean) * 100).toFixed(1)}%).`,
          impact: 'medium',
          confidence: 80
        });
      }
    });

    // Pattern-based Insights
    patterns.trends.forEach(trend => {
      insights.push({
        type: trend.trend === 'increasing' ? 'success' : 'warning',
        category: 'Trend Analysis',
        title: `${trend.trend.charAt(0).toUpperCase() + trend.trend.slice(1)} Trend Detected`,
        description: `${trend.column} shows ${trend.trend} trend (${trend.changePercentage > 0 ? '+' : ''}${trend.changePercentage}% change)`,
        impact: 'high',
        confidence: trend.confidence
      });
    });

    patterns.correlations.forEach(corr => {
      insights.push({
        type: 'info',
        category: 'Relationship Analysis',
        title: `${corr.strength.charAt(0).toUpperCase() + corr.strength.slice(1)} Correlation Found`,
        description: `${corr.column1} and ${corr.column2} show ${corr.direction} correlation (r=${corr.correlation})`,
        impact: 'medium',
        confidence: Math.abs(corr.correlation) * 100
      });
    });

    // Department-specific insights
    insights.push(...this.generateDepartmentSpecificInsights(data, config, stats, patterns));

    return insights.sort((a, b) => {
      const impactOrder = { high: 3, medium: 2, low: 1 };
      return impactOrder[b.impact] - impactOrder[a.impact];
    });
  }

  generateDepartmentSpecificInsights(data, config, stats, patterns) {
    const insights = [];
    const department = config.department.toLowerCase();

    switch (department) {
      case 'finance':
        // Look for financial metrics
        const revenueCol = Object.keys(stats).find(col => 
          col.toLowerCase().includes('revenue') || col.toLowerCase().includes('sales')
        );
        const expenseCol = Object.keys(stats).find(col => 
          col.toLowerCase().includes('expense') || col.toLowerCase().includes('cost')
        );

        if (revenueCol && expenseCol) {
          const profitMargin = ((stats[revenueCol].mean - stats[expenseCol].mean) / stats[revenueCol].mean) * 100;
          
          insights.push({
            type: profitMargin > 20 ? 'success' : profitMargin > 10 ? 'info' : 'warning',
            category: 'Financial Health',
            title: 'Profitability Analysis',
            description: `Estimated profit margin: ${profitMargin.toFixed(1)}%`,
            impact: 'high',
            confidence: 85
          });
        }
        break;

      case 'sales':
        const amountCol = Object.keys(stats).find(col => 
          col.toLowerCase().includes('amount') || col.toLowerCase().includes('value')
        );
        if (amountCol) {
          const avgDealSize = stats[amountCol].mean;
          const salesEfficiency = stats[amountCol].sum / data.length;
          
          insights.push({
            type: avgDealSize > stats[amountCol].median ? 'success' : 'info',
            category: 'Sales Performance',
            title: 'Deal Size Analysis',
            description: `Average deal size: $${avgDealSize.toFixed(2)} | Efficiency: $${salesEfficiency.toFixed(2)} per record`,
            impact: 'high',
            confidence: 90
          });
        }
        break;

      case 'hr':
        const salaryCol = Object.keys(stats).find(col => 
          col.toLowerCase().includes('salary') || col.toLowerCase().includes('compensation')
        );
        if (salaryCol) {
          const salaryRange = stats[salaryCol].max - stats[salaryCol].min;
          const compaRatio = stats[salaryCol].mean / stats[salaryCol].median;
          
          insights.push({
            type: compaRatio > 0.9 && compaRatio < 1.1 ? 'success' : 'warning',
            category: 'Compensation Analysis',
            title: 'Salary Distribution',
            description: `Salary range: $${salaryRange.toFixed(2)} | Compa-ratio: ${compaRatio.toFixed(2)}`,
            impact: 'medium',
            confidence: 80
          });
        }
        break;
    }

    return insights;
  }

  generateRecommendations(data, config) {
    const recommendations = [];
    const insights = this.generateAIInsights(data, config);
    const stats = this.performStatisticalAnalysis(data);
    const patterns = this.detectPatterns(data);

    // Data quality recommendations
    const dataQualityIssues = insights.filter(i => i.category === 'Data Quality');
    if (dataQualityIssues.length > 0) {
      recommendations.push({
        priority: 'high',
        category: 'Data Management',
        title: 'Enhance Data Quality',
        description: 'Implement data validation and cleaning procedures to improve analysis accuracy.',
        actionSteps: [
          'Set up automated data validation rules',
          'Implement missing data imputation strategies',
          'Establish data quality monitoring dashboard'
        ],
        expectedImpact: 'High improvement in analysis reliability',
        implementationEffort: 'Medium'
      });
    }

    // Department-specific recommendations
    switch (config.department.toLowerCase()) {
      case 'finance':
        recommendations.push({
          priority: 'high',
          category: 'Financial Optimization',
          title: 'Implement Advanced Financial Modeling',
          description: 'Use predictive analytics for revenue forecasting and expense optimization.',
          actionSteps: [
            'Develop time-series forecasting models',
            'Implement cost-benefit analysis framework',
            'Set up automated financial reporting'
          ],
          expectedImpact: '20-30% improvement in financial planning accuracy',
          implementationEffort: 'High'
        });
        break;

      case 'sales':
        recommendations.push({
          priority: 'high',
          category: 'Sales Optimization',
          title: 'Optimize Sales Pipeline Management',
          description: 'Leverage data insights to improve conversion rates and deal velocity.',
          actionSteps: [
            'Implement lead scoring system',
            'Develop sales performance dashboards',
            'Create targeted sales training programs'
          ],
          expectedImpact: '15-25% increase in conversion rates',
          implementationEffort: 'Medium'
        });
        break;

      case 'hr':
        recommendations.push({
          priority: 'medium',
          category: 'Workforce Analytics',
          title: 'Enhance Talent Management Strategy',
          description: 'Use data-driven insights for better talent acquisition and retention.',
          actionSteps: [
            'Implement employee performance analytics',
            'Develop retention risk assessment models',
            'Create skills gap analysis framework'
          ],
          expectedImpact: '10-20% reduction in attrition rates',
          implementationEffort: 'Medium'
        });
        break;
    }

    // General analytics recommendations
    if (patterns.correlations.length > 0) {
      recommendations.push({
        priority: 'medium',
        category: 'Analytics Enhancement',
        title: 'Leverage Correlation Insights',
        description: 'Use identified correlations to build predictive models and business rules.',
        actionSteps: [
          'Develop regression models for key relationships',
          'Create business rules based on correlation patterns',
          'Implement automated alerting for correlation changes'
        ],
        expectedImpact: 'Improved decision-making accuracy',
        implementationEffort: 'Medium'
      });
    }

    return recommendations.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  }

  detectAnomalies(data) {
    const anomalies = [];
    const stats = this.performStatisticalAnalysis(data);
    
    Object.entries(stats).forEach(([column, stat]) => {
      if (stat.outliers > 0) {
        anomalies.push({
          column,
          type: 'statistical_outlier',
          severity: stat.outlierPercentage > 20 ? 'high' : stat.outlierPercentage > 10 ? 'medium' : 'low',
          description: `${stat.outliers} outliers detected (${stat.outlierPercentage}% of data)`,
          impact: 'May affect statistical analysis and model performance',
          suggestion: 'Review outlier data points for data entry errors or special cases'
        });
      }
    });

    return anomalies;
  }

  generatePredictiveInsights(data, config) {
    const predictiveInsights = [];
    const patterns = this.detectPatterns(data);
    const stats = this.performStatisticalAnalysis(data);

    // Trend-based predictions
    patterns.trends.forEach(trend => {
      if (trend.confidence > 70) {
        predictiveInsights.push({
          type: 'trend_projection',
          metric: trend.column,
          prediction: `Expected to continue ${trend.trend} by approximately ${Math.abs(trend.changePercentage).toFixed(1)}% in next period`,
          confidence: trend.confidence,
          basis: 'Historical trend analysis',
          timeframe: 'Short-term (next reporting period)'
        });
      }
    });

    // Statistical predictions
    Object.entries(stats).forEach(([column, stat]) => {
      if (stat.count > 30) { // Only predict if we have enough data
        predictiveInsights.push({
          type: 'range_prediction',
          metric: column,
          prediction: `Expected range: ${(stat.mean - stat.standardDeviation).toFixed(2)} to ${(stat.mean + stat.standardDeviation).toFixed(2)}`,
          confidence: 75,
          basis: 'Statistical distribution analysis',
          timeframe: 'Immediate future'
        });
      }
    });

    return predictiveInsights;
  }

  prepareVisualizations(data) {
    const visualizations = [];
    const columns = Object.keys(data[0]);
    const numericColumns = columns.filter(col => 
      data.some(row => typeof row[col] === 'number' && !isNaN(row[col]))
    );

    // Distribution charts for numeric columns
    numericColumns.forEach(column => {
      const values = data.map(row => row[column]).filter(val => typeof val === 'number' && !isNaN(val));
      
      if (values.length > 0) {
        // Create histogram data
        const min = Math.min(...values);
        const max = Math.max(...values);
        const range = max - min;
        const binCount = Math.min(10, Math.floor(Math.sqrt(values.length)));
        const binSize = range / binCount;
        
        const histogramData = [];
        for (let i = 0; i < binCount; i++) {
          const binStart = min + i * binSize;
          const binEnd = binStart + binSize;
          const count = values.filter(v => v >= binStart && v < binEnd).length;
          histogramData.push({
            range: `${binStart.toFixed(2)}-${binEnd.toFixed(2)}`,
            count,
            frequency: parseFloat((count / values.length * 100).toFixed(2))
          });
        }

        visualizations.push({
          type: 'histogram',
          title: `Distribution of ${column}`,
          data: histogramData,
          config: {
            xKey: 'range',
            yKey: 'count',
            fillColor: '#3b82f6'
          }
        });
      }
    });

    // Time series if date column exists
    const dateColumn = columns.find(col => 
      col.toLowerCase().includes('date') || col.toLowerCase().includes('month') || col.toLowerCase().includes('year')
    );

    if (dateColumn && numericColumns.length > 0) {
      const numericColumn = numericColumns[0];
      const timeSeriesData = data
        .filter(row => row[dateColumn] != null && typeof row[numericColumn] === 'number')
        .slice(0, 50) // Limit for performance
        .map(row => ({
          period: row[dateColumn],
          value: row[numericColumn]
        }));

      if (timeSeriesData.length > 5) {
        visualizations.push({
          type: 'line',
          title: `${numericColumn} Over Time`,
          data: timeSeriesData,
          config: {
            xKey: 'period',
            yKey: 'value',
            strokeColor: '#10b981'
          }
        });
      }
    }

    return visualizations;
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  async generateExecutiveSummary(analysis, config) {
    // This would integrate with LLaMA in a real implementation
    return {
      overview: `Analysis of ${analysis.metadata.fileName} containing ${analysis.metadata.totalRows} records across ${analysis.metadata.totalColumns} variables. The data reveals ${analysis.insights.length} key insights with ${analysis.recommendations.length} actionable recommendations.`,
      keyTakeaways: analysis.insights.slice(0, 3).map(insight => insight.description),
      businessImpact: `This analysis provides ${config.department} with data-driven insights for strategic decision-making and operational optimization.`,
      nextSteps: analysis.recommendations.slice(0, 2).map(rec => rec.title)
    };
  }
}

// Singleton instance
export const aiAnalysisAgent = new AIAnalysisAgent();