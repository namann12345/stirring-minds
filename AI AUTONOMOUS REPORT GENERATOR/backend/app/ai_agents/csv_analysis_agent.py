import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from scipy import stats
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go
import plotly.express as px

logger = logging.getLogger(__name__)

class CSVAnalysisAgent:
    def __init__(self):
        self.agent_name = "Backend CSV Analysis Agent"
        self.version = "2.0.0"
        self.supported_file_types = ['.csv', '.xlsx', '.xls']
    
    async def analyze_csv_file(self, file_content: bytes, filename: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method that processes CSV files and generates comprehensive reports
        """
        try:
            logger.info(f"🦙 Starting AI analysis for {filename}")
            
            # Parse the file based on type
            df = await self._parse_file(file_content, filename, config.get('has_headers', True))
            
            if df.empty:
                raise ValueError("No data found in the uploaded file")
            
            # Perform comprehensive analysis
            analysis_result = {
                'metadata': self._extract_metadata(df, filename, config),
                'statistical_analysis': await self._perform_statistical_analysis(df),
                'pattern_detection': await self._detect_patterns(df),
                'insights': await self._generate_ai_insights(df, config),
                'recommendations': await self._generate_recommendations(df, config),
                'anomalies': await self._detect_anomalies(df),
                'predictive_insights': await self._generate_predictive_insights(df, config),
                'visualizations': await self._prepare_visualizations(df),
                'executive_summary': await self._generate_executive_summary(df, config),
                'agent_info': {
                    'name': self.agent_name,
                    'version': self.version,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"✅ AI analysis completed for {filename}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {str(e)}")
            raise e
    
    async def _parse_file(self, file_content: bytes, filename: str, has_headers: bool = True) -> pd.DataFrame:
        """Parse CSV or Excel files"""
        try:
            if filename.endswith('.csv'):
                # For CSV files
                import io
                text_content = file_content.decode('utf-8')
                df = pd.read_csv(io.StringIO(text_content), header=0 if has_headers else None)
            else:
                # For Excel files
                import io
                df = pd.read_excel(io.BytesIO(file_content), header=0 if has_headers else None)
            
            # Basic data cleaning
            df = df.dropna(how='all')  # Remove completely empty rows
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
            
            return df
            
        except Exception as e:
            logger.error(f"File parsing error: {str(e)}")
            raise ValueError(f"Could not parse file {filename}: {str(e)}")
    
    def _extract_metadata(self, df: pd.DataFrame, filename: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic metadata about the dataset"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        return {
            'filename': filename,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns_count': len(numeric_columns),
            'categorical_columns_count': len(categorical_columns),
            'columns_list': df.columns.tolist(),
            'department': config.get('department', 'general'),
            'data_type': config.get('data_type', 'general'),
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 ** 2
        }
    
    async def _perform_statistical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis"""
        stats_result = {}
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            data = df[column].dropna()
            if len(data) > 0:
                stats_result[column] = {
                    'count': int(len(data)),
                    'mean': float(data.mean()),
                    'median': float(data.median()),
                    'std': float(data.std()),
                    'min': float(data.min()),
                    'max': float(data.max()),
                    'range': float(data.max() - data.min()),
                    'variance': float(data.var()),
                    'skewness': float(data.skew()),
                    'kurtosis': float(data.kurtosis()),
                    'q1': float(data.quantile(0.25)),
                    'q3': float(data.quantile(0.75)),
                    'iqr': float(data.quantile(0.75) - data.quantile(0.25))
                }
                
                # Detect outliers using IQR method
                q1 = stats_result[column]['q1']
                q3 = stats_result[column]['q3']
                iqr = stats_result[column]['iqr']
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = data[(data < lower_bound) | (data > upper_bound)]
                
                stats_result[column]['outliers_count'] = int(len(outliers))
                stats_result[column]['outliers_percentage'] = float((len(outliers) / len(data)) * 100)
        
        return stats_result
    
    async def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns, trends, and correlations in the data"""
        patterns = {
            'trends': [],
            'correlations': [],
            'seasonality': [],
            'data_quality_issues': []
        }
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        # Trend detection
        for column in numeric_columns:
            if len(df) > 10:  # Only detect trends if we have enough data
                data = df[column].dropna().values
                if len(data) > 10:
                    # Simple linear trend detection
                    x = np.arange(len(data))
                    slope, _, r_value, _, _ = stats.linregress(x, data)
                    
                    if abs(r_value) > 0.5:  # Significant correlation
                        trend = 'increasing' if slope > 0 else 'decreasing'
                        patterns['trends'].append({
                            'column': column,
                            'trend': trend,
                            'strength': abs(r_value),
                            'slope': float(slope),
                            'confidence': min(100, abs(r_value) * 100)
                        })
        
        # Correlation detection
        if len(numeric_columns) >= 2:
            correlation_matrix = df[numeric_columns].corr()
            for i, col1 in enumerate(numeric_columns):
                for j, col2 in enumerate(numeric_columns):
                    if i < j:  # Avoid duplicates and self-correlation
                        corr = correlation_matrix.iloc[i, j]
                        if abs(corr) > 0.7:  # Strong correlation
                            patterns['correlations'].append({
                                'column1': col1,
                                'column2': col2,
                                'correlation': float(corr),
                                'strength': 'strong' if abs(corr) > 0.8 else 'moderate',
                                'direction': 'positive' if corr > 0 else 'negative'
                            })
        
        # Data quality issues
        for column in df.columns:
            missing_count = df[column].isna().sum()
            if missing_count > 0:
                patterns['data_quality_issues'].append({
                    'column': column,
                    'issue': 'missing_values',
                    'count': int(missing_count),
                    'percentage': float((missing_count / len(df)) * 100),
                    'severity': 'high' if (missing_count / len(df)) > 0.1 else 'medium'
                })
        
        return patterns
    
    async def _generate_ai_insights(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered insights from the data"""
        insights = []
        stats = await self._perform_statistical_analysis(df)
        patterns = await self._detect_patterns(df)
        metadata = self._extract_metadata(df, '', config)
        
        # Data quality insights
        total_cells = metadata['total_rows'] * metadata['total_columns']
        numeric_cells = sum([col_stats['count'] for col_stats in stats.values()])
        data_completeness = (numeric_cells / total_cells) * 100 if total_cells > 0 else 0
        
        if data_completeness < 80:
            insights.append({
                'type': 'warning',
                'category': 'Data Quality',
                'title': 'Low Data Completeness',
                'description': f'Only {data_completeness:.1f}% of cells contain analyzable data',
                'impact': 'high',
                'confidence': 85
            })
        
        # Statistical insights
        for column, col_stats in stats.items():
            if col_stats['outliers_percentage'] > 10:
                insights.append({
                    'type': 'warning',
                    'category': 'Data Distribution',
                    'title': 'High Outlier Presence',
                    'description': f'{column} has {col_stats["outliers_percentage"]:.1f}% outliers',
                    'impact': 'medium',
                    'confidence': 90
                })
            
            if col_stats['std'] > 0 and abs(col_stats['skewness']) > 1:
                skew_type = 'right' if col_stats['skewness'] > 0 else 'left'
                insights.append({
                    'type': 'info',
                    'category': 'Data Distribution',
                    'title': 'Skewed Distribution',
                    'description': f'{column} shows {skew_type} skewness ({col_stats["skewness"]:.2f})',
                    'impact': 'medium',
                    'confidence': 80
                })
        
        # Pattern-based insights
        for trend in patterns['trends']:
            if trend['confidence'] > 70:
                insights.append({
                    'type': 'success' if trend['trend'] == 'increasing' else 'warning',
                    'category': 'Trend Analysis',
                    'title': f'{trend["trend"].title()} Trend Detected',
                    'description': f'{trend["column"]} shows {trend["trend"]} trend (confidence: {trend["confidence"]:.1f}%)',
                    'impact': 'high',
                    'confidence': trend['confidence']
                })
        
        # Department-specific insights
        insights.extend(await self._generate_department_insights(df, config, stats, patterns))
        
        return sorted(insights, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['impact']], reverse=True)
    
    async def _generate_department_insights(self, df: pd.DataFrame, config: Dict[str, Any], 
                                          stats: Dict, patterns: Dict) -> List[Dict[str, Any]]:
        """Generate department-specific insights"""
        insights = []
        department = config.get('department', '').lower()
        
        if department == 'finance':
            # Look for financial metrics
            revenue_cols = [col for col in df.columns if any(word in col.lower() for word in ['revenue', 'sales', 'income'])]
            expense_cols = [col for col in df.columns if any(word in col.lower() for word in ['expense', 'cost', 'spend'])]
            
            if revenue_cols and expense_cols:
                revenue_col = revenue_cols[0]
                expense_col = expense_cols[0]
                
                if revenue_col in stats and expense_col in stats:
                    revenue_avg = stats[revenue_col]['mean']
                    expense_avg = stats[expense_col]['mean']
                    
                    if revenue_avg > 0:
                        profit_margin = ((revenue_avg - expense_avg) / revenue_avg) * 100
                        insights.append({
                            'type': 'success' if profit_margin > 20 else 'warning' if profit_margin > 10 else 'error',
                            'category': 'Financial Health',
                            'title': 'Profitability Analysis',
                            'description': f'Estimated profit margin: {profit_margin:.1f}%',
                            'impact': 'high',
                            'confidence': 85
                        })
        
        elif department == 'sales':
            amount_cols = [col for col in df.columns if any(word in col.lower() for word in ['amount', 'value', 'deal', 'sale'])]
            if amount_cols:
                amount_col = amount_cols[0]
                if amount_col in stats:
                    avg_deal_size = stats[amount_col]['mean']
                    total_sales = stats[amount_col]['sum']
                    
                    insights.append({
                        'type': 'success' if avg_deal_size > stats[amount_col]['median'] else 'info',
                        'category': 'Sales Performance',
                        'title': 'Deal Size Analysis',
                        'description': f'Average deal size: ${avg_deal_size:,.2f} | Total: ${total_sales:,.2f}',
                        'impact': 'high',
                        'confidence': 90
                    })
        
        return insights
    
    async def _generate_recommendations(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        insights = await self._generate_ai_insights(df, config)
        patterns = await self._detect_patterns(df)
        
        # Data quality recommendations
        data_quality_issues = [i for i in insights if i['category'] == 'Data Quality']
        if data_quality_issues:
            recommendations.append({
                'priority': 'high',
                'category': 'Data Management',
                'title': 'Improve Data Quality',
                'description': 'Address data completeness and consistency issues',
                'action_steps': [
                    'Implement data validation rules',
                    'Set up automated data cleaning processes',
                    'Establish data quality monitoring'
                ],
                'expected_impact': 'High improvement in analysis reliability',
                'implementation_effort': 'Medium'
            })
        
        # Department-specific recommendations
        department = config.get('department', '').lower()
        if department == 'finance':
            recommendations.append({
                'priority': 'high',
                'category': 'Financial Optimization',
                'title': 'Implement Advanced Financial Modeling',
                'description': 'Use predictive analytics for better financial planning',
                'action_steps': [
                    'Develop time-series forecasting models',
                    'Implement cost-benefit analysis framework',
                    'Set up automated financial reporting'
                ],
                'expected_impact': '20-30% improvement in financial planning accuracy',
                'implementation_effort': 'High'
            })
        
        elif department == 'sales':
            recommendations.append({
                'priority': 'high',
                'category': 'Sales Optimization',
                'title': 'Optimize Sales Pipeline Management',
                'description': 'Leverage data insights to improve sales efficiency',
                'action_steps': [
                    'Implement lead scoring system',
                    'Develop sales performance dashboards',
                    'Create targeted sales training programs'
                ],
                'expected_impact': '15-25% increase in conversion rates',
                'implementation_effort': 'Medium'
            })
        
        # General analytics recommendations
        if patterns['correlations']:
            recommendations.append({
                'priority': 'medium',
                'category': 'Analytics Enhancement',
                'title': 'Leverage Correlation Insights',
                'description': 'Use identified correlations for predictive modeling',
                'action_steps': [
                    'Develop regression models for key relationships',
                    'Create business rules based on correlation patterns',
                    'Implement automated alerting for correlation changes'
                ],
                'expected_impact': 'Improved decision-making accuracy',
                'implementation_effort': 'Medium'
            })
        
        return sorted(recommendations, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
    
    async def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies and outliers in the data"""
        anomalies = []
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            data = df[column].dropna().values.reshape(-1, 1)
            if len(data) > 10:
                # Use Isolation Forest for anomaly detection
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                predictions = iso_forest.fit_predict(data)
                outlier_indices = np.where(predictions == -1)[0]
                
                if len(outlier_indices) > 0:
                    anomalies.append({
                        'column': column,
                        'anomaly_count': int(len(outlier_indices)),
                        'anomaly_percentage': float((len(outlier_indices) / len(data)) * 100),
                        'severity': 'high' if (len(outlier_indices) / len(data)) > 0.1 else 'medium',
                        'description': f'Detected {len(outlier_indices)} potential anomalies using machine learning',
                        'suggestion': 'Review these data points for potential errors or special cases'
                    })
        
        return anomalies
    
    async def _generate_predictive_insights(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate predictive insights and forecasts"""
        predictive_insights = []
        patterns = await self._detect_patterns(df)
        stats = await self._perform_statistical_analysis(df)
        
        # Trend-based predictions
        for trend in patterns['trends']:
            if trend['confidence'] > 70:
                predictive_insights.append({
                    'type': 'trend_projection',
                    'metric': trend['column'],
                    'prediction': f'Expected to continue {trend["trend"]} trend in next period',
                    'confidence': trend['confidence'],
                    'basis': 'Historical trend analysis with linear regression',
                    'timeframe': 'Short-term (next reporting period)'
                })
        
        # Statistical predictions
        for column, col_stats in stats.items():
            if col_stats['count'] > 30:  # Only predict if we have enough data
                predictive_insights.append({
                    'type': 'range_prediction',
                    'metric': column,
                    'prediction': f'Expected range: {col_stats["mean"] - col_stats["std"]:.2f} to {col_stats["mean"] + col_stats["std"]:.2f}',
                    'confidence': 75,
                    'basis': 'Statistical distribution analysis',
                    'timeframe': 'Immediate future based on current distribution'
                })
        
        return predictive_insights
    
    async def _prepare_visualizations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prepare data for visualizations"""
        visualizations = []
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        # Distribution charts for numeric columns
        for column in numeric_columns:
            data = df[column].dropna()
            if len(data) > 0:
                # Create histogram data
                hist, bins = np.histogram(data, bins=min(10, len(data)))
                bin_centers = (bins[:-1] + bins[1:]) / 2
                
                histogram_data = []
                for i, count in enumerate(hist):
                    histogram_data.append({
                        'bin_start': float(bins[i]),
                        'bin_end': float(bins[i+1]),
                        'count': int(count),
                        'frequency': float((count / len(data)) * 100)
                    })
                
                visualizations.append({
                    'type': 'histogram',
                    'title': f'Distribution of {column}',
                    'data': histogram_data,
                    'config': {
                        'x_key': 'bin_start',
                        'y_key': 'count'
                    }
                })
        
        return visualizations
    
    async def _generate_executive_summary(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of the analysis"""
        metadata = self._extract_metadata(df, '', config)
        insights = await self._generate_ai_insights(df, config)
        recommendations = await self._generate_recommendations(df, config)
        
        high_impact_insights = [i for i in insights if i['impact'] == 'high']
        high_priority_recommendations = [r for r in recommendations if r['priority'] == 'high']
        
        return {
            'overview': f"This analysis of {metadata['filename']} reveals {len(insights)} key insights across {metadata['total_rows']} records. "
                       f"The data shows significant opportunities for {config.get('department', 'business')} optimization.",
            'key_takeaways': [insight['description'] for insight in high_impact_insights[:3]],
            'business_impact': f"Implementing the {len(high_priority_recommendations)} high-priority recommendations could drive substantial value "
                             f"through data-informed decision making in the {config.get('department', 'business')} department.",
            'next_steps': [rec['title'] for rec in high_priority_recommendations[:2]]
        }

# Global agent instance
csv_analysis_agent = CSVAnalysisAgent()