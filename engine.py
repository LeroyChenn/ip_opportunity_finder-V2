# engine.py
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

class PatentAnalyzer:
    def __init__(self, df_patents, df_market, df_investors):
        self.df_patents = df_patents
        self.df_market = df_market
        self.df_investors = df_investors
        self.tech_areas = df_patents['tech_area'].unique()
        print(f"初始化专利分析器，包含 {len(self.tech_areas)} 个技术领域")
        
        # 准备协同过滤数据
        self._prepare_collaborative_data()
    
    def _prepare_collaborative_data(self):
        """准备协同过滤所需的数据"""
        self.investor_tech_matrix = pd.DataFrame(0, index=self.df_investors['investor_id'], columns=self.tech_areas)
        
        for _, investor in self.df_investors.iterrows():
            for area in investor['focus_areas']:
                if area in self.tech_areas:
                    self.investor_tech_matrix.loc[investor['investor_id'], area] = 1
        
        self.tech_similarity_matrix = self._compute_tech_similarity()
    
    def _compute_tech_similarity(self):
        """计算技术领域之间的相似度"""
        tech_features = []
        for area in self.tech_areas:
            area_data = self.df_patents[self.df_patents['tech_area'] == area]
            features = [
                area_data['quality_score'].mean(),
                area_data['market_potential'].mean(),
                area_data['commercial_viability'].mean(),
                area_data['citations'].mean(),
                area_data['industry_impact'].mean(),
                area_data['investment_attractiveness'].mean(),
                len(area_data)
            ]
            features = [0 if np.isnan(x) else x for x in features]
            tech_features.append(features)
        
        tech_features = np.array(tech_features)
        tech_features = (tech_features - tech_features.mean(axis=0)) / (tech_features.std(axis=0) + 1e-8)
        similarity_matrix = cosine_similarity(tech_features)
        return pd.DataFrame(similarity_matrix, index=self.tech_areas, columns=self.tech_areas)
    
    def calculate_growth_metrics(self):
        """计算增长指标"""
        print("计算增长指标...")
        growth_metrics = {}
        
        for area in self.tech_areas:
            area_data = self.df_patents[self.df_patents['tech_area'] == area]
            market_data = self.df_market[self.df_market['tech_area'] == area]
            
            if len(area_data) == 0:
                continue
            
            yearly_counts = area_data.groupby('year').size()
            if len(yearly_counts) > 1:
                start_count = yearly_counts.iloc[0]
                end_count = yearly_counts.iloc[-1]
                years = len(yearly_counts) - 1
                cagr = (end_count / start_count) ** (1/years) - 1 if start_count > 0 else 0
                
                if len(yearly_counts) > 2:
                    recent_growth = (yearly_counts.iloc[-1] - yearly_counts.iloc[-2]) / yearly_counts.iloc[-2] if yearly_counts.iloc[-2] > 0 else 0
                    previous_growth = (yearly_counts.iloc[-2] - yearly_counts.iloc[-3]) / yearly_counts.iloc[-3] if yearly_counts.iloc[-3] > 0 else 0
                    growth_acceleration = recent_growth - previous_growth
                else:
                    growth_acceleration = 0
            else:
                cagr = 0
                growth_acceleration = 0
            
            if len(market_data) > 0:
                current_market = market_data[market_data['year'] == 2024]
                if len(current_market) > 0:
                    market_growth = current_market['growth_rate'].iloc[0]
                    market_size = current_market['market_size'].iloc[0]
                    competition = current_market['competition_level'].iloc[0]
                    investment_heat = current_market['investment_heat'].iloc[0]
                    government_support = current_market['government_support'].iloc[0]
                else:
                    market_growth = 0.1
                    market_size = 50
                    competition = 50
                    investment_heat = 50
                    government_support = 50
            else:
                market_growth = 0.1
                market_size = 50
                competition = 50
                investment_heat = 50
                government_support = 50
            
            avg_quality = area_data['quality_score'].mean()
            avg_commercial = area_data['commercial_viability'].mean()
            avg_impact = area_data['industry_impact'].mean()
            avg_attractiveness = area_data['investment_attractiveness'].mean()
            
            growth_metrics[area] = {
                'cagr': cagr,
                'growth_acceleration': growth_acceleration,
                'market_growth': market_growth,
                'market_size': market_size,
                'competition_level': competition,
                'investment_heat': investment_heat,
                'government_support': government_support,
                'avg_quality': avg_quality,
                'avg_commercial': avg_commercial,
                'avg_impact': avg_impact,
                'avg_attractiveness': avg_attractiveness,
                'patent_count': len(area_data),
                'company_diversity': area_data['applicant'].nunique()
            }
        
        return growth_metrics
    
    def calculate_opportunity_scores(self):
        """计算机会分数"""
        print("计算机会分数...")
        metrics = self.calculate_growth_metrics()
        
        opportunities = []
        
        for area, metric in metrics.items():
            growth_score = self._normalize_score(metric['cagr'] * 100, 0, 50) * 0.20
            market_score = self._normalize_score(metric['market_growth'] * 100, 0, 30) * 0.15
            size_score = self._normalize_score(metric['market_size'], 0, 300) * 0.15
            quality_score = self._normalize_score(metric['avg_quality'], 0, 100) * 0.15
            commercial_score = self._normalize_score(metric['avg_commercial'], 0, 100) * 0.10
            attractiveness_score = self._normalize_score(metric['avg_attractiveness'], 0, 100) * 0.10
            competition_score = self._normalize_score(100 - metric['competition_level'], 0, 100) * 0.10
            government_score = self._normalize_score(metric['government_support'], 0, 100) * 0.05
            
            opportunity_score = (
                growth_score + market_score + size_score + 
                quality_score + commercial_score + attractiveness_score +
                competition_score + government_score
            )
            
            trend_signal = "📈 Bullish" if metric['growth_acceleration'] > 0 else "📉 Caution" if metric['growth_acceleration'] < 0 else "➡️ Stable"
            
            opportunities.append({
                'tech_area': area,
                'opportunity_score': round(opportunity_score, 1),
                'growth_score': round(growth_score, 1),
                'market_score': round(market_score, 1),
                'quality_score': round(quality_score, 1),
                'commercial_score': round(commercial_score, 1),
                'attractiveness_score': round(attractiveness_score, 1),
                'competition_score': round(competition_score, 1),
                'government_score': round(government_score, 1),
                'cagr': round(metric['cagr'] * 100, 1),
                'market_size': metric['market_size'],
                'investment_heat': metric['investment_heat'],
                'government_support': metric['government_support'],
                'patent_count': metric['patent_count'],
                'company_diversity': metric['company_diversity'],
                'trend_signal': trend_signal,
                'recommendation': self._generate_recommendation(opportunity_score, metric),
                'risk_level': self._assess_risk_level(metric)
            })
        
        return sorted(opportunities, key=lambda x: x['opportunity_score'], reverse=True)
    
    def _normalize_score(self, value, min_val, max_val):
        """标准化分数到0-1范围"""
        if max_val - min_val == 0:
            return 0
        return max(0, min(1, (value - min_val) / (max_val - min_val)))
    
    def _assess_risk_level(self, metric):
        """评估风险等级"""
        risk_factors = []
        
        if metric['competition_level'] > 70:
            risk_factors.append('high_competition')
        if metric['cagr'] < 0.05:
            risk_factors.append('low_growth')
        if metric['market_size'] < 50:
            risk_factors.append('small_market')
        if metric['company_diversity'] < 3:
            risk_factors.append('concentrated_ownership')
        if metric['government_support'] < 40:
            risk_factors.append('low_government_support')
        
        if len(risk_factors) >= 3:
            return 'High'
        elif len(risk_factors) >= 2:
            return 'Medium-High'
        elif len(risk_factors) >= 1:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_recommendation(self, opportunity_score, metric):
        """生成建议"""
        if opportunity_score >= 80:
            return "🚀 卓越机会！强烈推荐投资"
        elif opportunity_score >= 65:
            return "✅ 优质机会！建议积极考虑"
        elif opportunity_score >= 50:
            return "💡 稳健机会！适合长期投资"
        elif opportunity_score >= 35:
            return "⚠️ 谨慎机会！建议深入调研"
        else:
            return "⏸️ 观望机会！建议等待更好时机"
    
    def find_similar_areas(self, target_area, top_k=5):
        """找到相似的技术领域"""
        if target_area not in self.tech_similarity_matrix.index:
            return []
        
        similarities = self.tech_similarity_matrix[target_area].sort_values(ascending=False)
        similarities = similarities[similarities.index != target_area]
        return list(similarities.head(top_k).items())
    
    def collaborative_recommendation(self, investor_id, top_k=10):
        """基于协同过滤的推荐"""
        if investor_id not in self.investor_tech_matrix.index:
            return []
        
        target_vector = self.investor_tech_matrix.loc[investor_id].values.reshape(1, -1)
        investor_similarities = cosine_similarity(target_vector, self.investor_tech_matrix)[0]
        similar_investors = np.argsort(investor_similarities)[::-1][1:4]
        
        recommendations = {}
        for sim_investor_idx in similar_investors:
            sim_investor_id = self.investor_tech_matrix.index[sim_investor_idx]
            sim_investor_vector = self.investor_tech_matrix.loc[sim_investor_id]
            
            for tech_area in self.tech_areas:
                if self.investor_tech_matrix.loc[investor_id, tech_area] == 0 and sim_investor_vector[tech_area] == 1:
                    if tech_area not in recommendations:
                        recommendations[tech_area] = 0
                    recommendations[tech_area] += investor_similarities[sim_investor_idx]
        
        return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    def hybrid_recommendation(self, investor_id, top_k=10):
        """混合推荐"""
        collaborative_recs = self.collaborative_recommendation(investor_id, top_k*2)
        
        if not collaborative_recs:
            investor_focus_areas = self.df_investors[self.df_investors['investor_id'] == investor_id]['focus_areas'].iloc[0]
            if investor_focus_areas:
                return self.find_similar_areas(investor_focus_areas[0], top_k)
            else:
                return []
        
        content_scores = {}
        for area, collab_score in collaborative_recs:
            area_opportunity = next((opp for opp in self.calculate_opportunity_scores() if opp['tech_area'] == area), None)
            if area_opportunity:
                content_score = area_opportunity['opportunity_score'] / 100
            else:
                content_score = 0.5
            
            hybrid_score = collab_score * 0.6 + content_score * 0.4
            content_scores[area] = hybrid_score
        
        return sorted(content_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    def recommend_investors(self, tech_area, max_investors=8):
        """推荐适合的投资者"""
        area_data = self.df_patents[self.df_patents['tech_area'] == tech_area]
        if len(area_data) == 0:
            return []
        
        avg_quality = area_data['quality_score'].mean()
        avg_commercial = area_data['commercial_viability'].mean()
        maturity = area_data['tech_maturity'].mode()[0] if len(area_data['tech_maturity'].mode()) > 0 else 'Growth'
        
        recommendations = []
        
        for _, investor in self.df_investors.iterrows():
            match_score = 0
            total_criteria = 0
            
            if tech_area in investor['focus_areas']:
                match_score += 2
            total_criteria += 2
            
            if avg_quality >= investor['min_quality_score']:
                match_score += 1.5
            total_criteria += 1.5
            
            if maturity.lower() in investor['preferred_stage'].lower():
                match_score += 1
            total_criteria += 1
            
            market_data = self.df_market[self.df_market['tech_area'] == tech_area]
            if len(market_data) > 0:
                current_market = market_data[market_data['year'] == 2024]
                if len(current_market) > 0 and current_market['market_size'].iloc[0] >= investor['min_market_size']:
                    match_score += 1
                total_criteria += 1
            
            match_percentage = (match_score / total_criteria) * 100
            
            if match_percentage >= 40:
                recommendations.append({
                    'investor_name': investor['name'],
                    'investor_type': investor['type'],
                    'match_score': round(match_percentage, 1),
                    'focus_areas': investor['focus_areas'],
                    'risk_tolerance': investor['risk_tolerance'],
                    'investment_size': investor['investment_size'],
                    'reasoning': self._generate_investor_reasoning(match_percentage)
                })
        
        return sorted(recommendations, key=lambda x: x['match_score'], reverse=True)[:max_investors]
    
    def _generate_investor_reasoning(self, match_score):
        """生成投资理由"""
        if match_score >= 80:
            return "高度匹配：投资领域、风险偏好和项目阶段完美契合"
        elif match_score >= 60:
            return "良好匹配：核心投资标准符合，建议重点接触"
        elif match_score >= 40:
            return "一般匹配：部分标准符合，可作为备选投资者"
        else:
            return "低度匹配：建议寻找更合适的投资机构"
    
    def get_market_insights(self, tech_area):
        """获取市场洞察"""
        market_data = self.df_market[self.df_market['tech_area'] == tech_area]
        if len(market_data) == 0:
            return None
        
        latest_year = market_data['year'].max()
        latest_data = market_data[market_data['year'] == latest_year]
        
        if len(latest_data) == 0:
            return None
        
        return {
            'current_growth': latest_data['growth_rate'].iloc[0],
            'market_size': latest_data['market_size'].iloc[0],
            'competition': latest_data['competition_level'].iloc[0],
            'investment_heat': latest_data['investment_heat'].iloc[0],
            'government_support': latest_data['government_support'].iloc[0],
            'risk_level': latest_data['risk_level'].iloc[0]
        }