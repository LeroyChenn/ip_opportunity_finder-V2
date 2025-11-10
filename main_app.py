# main_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime

# 导入我们写的模块
from data_generation import generate_patent_data
from engine import PatentAnalyzer

# 设置页面
st.set_page_config(
    page_title="IP机会发现平台",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 标题和介绍
st.title("🔍 IP机会发现平台")
st.markdown("基于专利数据和市场趋势，智能发现高潜力技术投资机会。本平台采用先进的机器学习算法，包括协同过滤和基于内容的推荐，为您提供精准的投资建议。")

# 投资规模建议函数
def get_investment_recommendation(opportunity_score, risk_level):
    if opportunity_score >= 75 and risk_level in ['Low', 'Medium']:
        return "建议大额投资 (1000万港币以上)"
    elif opportunity_score >= 60:
        return "建议中等投资 (500-1000万港币)"
    elif opportunity_score >= 45:
        return "建议小额投资 (100-500万港币)"
    else:
        return "建议谨慎投资或观望 (100万港币以下)"

def generate_investment_recommendation(financial_data):
    """生成投资建议"""
    gross = financial_data['gross_margin']
    net = financial_data['net_margin']
    roi = financial_data['roi']
    payback = financial_data['payback_period']
    
    if gross >= 60 and net >= 25 and roi >= 50 and payback <= 3:
        return "强烈推荐：财务指标优秀，盈利能力强，回收快"
    elif gross >= 45 and net >= 15 and roi >= 25 and payback <= 5:
        return "推荐投资：财务指标良好，投资回报可观"
    elif gross >= 35 and net >= 10 and roi >= 20:
        return "谨慎考虑：财务指标一般，需要关注运营效率"
    else:
        return "暂不推荐：财务指标未达投资标准"

# 侧边栏导航
st.sidebar.title("导航")
page = st.sidebar.radio("选择功能", [
    "机会发现", 
    "技术分析", 
    "趋势追踪",
    "个性化推荐",
    "投资者匹配"
])

def generate_financial_metrics(tech_area):
    """为技术领域生成财务指标（模拟数据）"""
    financial_profiles = {
        'AI': {'gross_margin': (50, 80), 'net_margin': (20, 40), 'roi': (30, 100), 'payback': (2, 5)},
        '区块链': {'gross_margin': (60, 90), 'net_margin': (25, 50), 'roi': (40, 120), 'payback': (1, 4)},
        '生物科技': {'gross_margin': (40, 70), 'net_margin': (15, 35), 'roi': (25, 80), 'payback': (3, 8)},
        '新能源': {'gross_margin': (35, 60), 'net_margin': (10, 25), 'roi': (20, 60), 'payback': (4, 10)},
        '物联网': {'gross_margin': (45, 75), 'net_margin': (18, 38), 'roi': (28, 90), 'payback': (2, 6)},
    }
    
    profile = financial_profiles.get(tech_area, {'gross_margin': (40, 70), 'net_margin': (15, 30), 'roi': (25, 70), 'payback': (3, 7)})
    
    import random
    return {
        'gross_margin': random.randint(profile['gross_margin'][0], profile['gross_margin'][1]),
        'net_margin': random.randint(profile['net_margin'][0], profile['net_margin'][1]),
        'roi': random.randint(profile['roi'][0], profile['roi'][1]),
        'payback_period': random.randint(profile['payback'][0], profile['payback'][1])
    }

# 加载数据和分析器
@st.cache_data
def load_data():
    df_patents, df_market, df_investors = generate_patent_data(8000)
    analyzer = PatentAnalyzer(df_patents, df_market, df_investors)
    return df_patents, df_market, df_investors, analyzer

df_patents, df_market, df_investors, analyzer = load_data()

if page == "机会发现":
    st.header("技术投资机会发现")
    
    with st.spinner('正在分析技术投资机会...'):
        opportunities = analyzer.calculate_opportunity_scores()
    
    st.subheader("机会排行榜")
    
    for i, opp in enumerate(opportunities[:12], 1):
        with st.expander(f"#{i} {opp['tech_area']} - 分数: {opp['opportunity_score']}"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("增长分数", f"{opp['growth_score']}")
                st.metric("CAGR", f"{opp['cagr']}%")
            with col2:
                st.metric("质量分数", f"{opp['quality_score']}")
                st.metric("商业潜力", f"{opp['commercial_score']}")
            with col3:
                st.metric("竞争分数", f"{opp['competition_score']}")
                st.metric("市场规模", f"{opp['market_size']}亿")
            with col4:
                st.metric("风险等级", opp['risk_level'])
                st.metric("趋势信号", opp['trend_signal'])
            
            st.progress(opp['opportunity_score'] / 100)
            st.info(f"建议: {opp['recommendation']}")
            
            similar_areas = analyzer.find_similar_areas(opp['tech_area'])
            if similar_areas:
                st.write("相关领域:", ", ".join([f"{area}({sim:.2f})" for area, sim in similar_areas]))

elif page == "技术分析":
    st.header("技术领域深度分析")
    
    selected_area = st.selectbox("选择技术领域", df_patents['tech_area'].unique())
    
    if selected_area:
        col1, col2 = st.columns(2)
        
        with col1:
            area_data = df_patents[df_patents['tech_area'] == selected_area]
            yearly_counts = area_data.groupby('year').size().reset_index()
            yearly_counts.columns = ['Year', 'Patent Count']
            
            if len(yearly_counts) > 1:
                fig1 = px.line(yearly_counts, x='Year', y='Patent Count', 
                              title=f'{selected_area} - 年度专利趋势',
                              markers=True)
                fig1.update_traces(line=dict(width=3))
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("该领域专利数据不足，无法显示趋势")
        
        with col2:
            market_data = df_market[df_market['tech_area'] == selected_area]
            if len(market_data) > 0:
                market_data = market_data.sort_values('year')
                fig2 = px.line(market_data, x='year', y='growth_rate',
                              title=f'{selected_area} - 市场增长率',
                              labels={'year': '年份', 'growth_rate': '增长率'})
                fig2.update_traces(line=dict(color='green', width=3))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("该领域市场数据不足")
        
        st.subheader("关键指标")
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            total_patents = len(area_data)
            st.metric("总专利数", total_patents)
        
        with col4:
            avg_citations = area_data['citations'].mean()
            st.metric("平均引用数", f"{avg_citations:.1f}")
        
        with col5:
            applicants = area_data['applicant'].nunique()
            st.metric("申请人数量", applicants)
        
        with col6:
            market_potential = area_data['market_potential'].mean()
            st.metric("市场潜力", f"{market_potential:.1f}")

elif page == "趋势追踪":
    st.header("市场趋势追踪")
    
    st.subheader("技术领域增长对比")
    
    growth_data = []
    for area in df_patents['tech_area'].unique():
        area_data = df_patents[df_patents['tech_area'] == area]
        market_data = df_market[df_market['tech_area'] == area]
        
        metrics = analyzer.calculate_growth_metrics()
        if area in metrics:
            patent_growth = metrics[area]['cagr']
            market_growth = metrics[area]['market_growth']
        else:
            patent_growth = 0
            market_growth = 0.1
        
        growth_data.append({
            'Tech Area': area,
            'Patent Growth': patent_growth * 100,
            'Market Growth': market_growth * 100,
            'Total Growth': (patent_growth + market_growth) * 50
        })
    
    growth_df = pd.DataFrame(growth_data)
    
    fig = px.bar(growth_df, x='Tech Area', y=['Patent Growth', 'Market Growth'],
                 title="技术领域增长对比", barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("详细增长数据")
    st.dataframe(growth_df)

elif page == "个性化推荐":
    st.header("🎯 智能投资推荐系统")
    
    st.markdown("""
    ### 基于您的投资偏好和财务指标的综合推荐
    结合您的风险承受能力、投资期限和财务要求，为您匹配最适合的投资机会。
    """)
    
    # 创建两列布局
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 投资偏好设置")
        
        # 基本投资偏好
        risk_tolerance = st.select_slider(
            "风险承受能力",
            options=['非常保守', '保守', '适中', '积极', '非常积极'],
            value='适中'
        )
        
        investment_horizon = st.select_slider(
            "投资期限",
            options=['短期 (1-2年)', '中期 (3-5年)', '长期 (5年以上)'],
            value='中期 (3-5年)'
        )
        
        investment_size = st.selectbox(
            "投资规模偏好",
            ['天使轮 (5-20M)', 'A轮 (20-50M)', 'B轮 (50-100M)', 'C轮及以上 (100M+)'],
            index=1
        )
        
        preferred_areas = st.multiselect(
            "重点关注领域 (可选)",
            options=df_patents['tech_area'].unique(),
            help="选择您特别感兴趣的领域"
        )
    
    with col2:
        st.subheader("💰 财务指标要求")
        
        # 财务指标筛选
        min_roi = st.slider("最低投资回报率 (%)", 10, 200, 25)
        max_payback = st.slider("最长回收周期 (年)", 1, 10, 5)
        min_gross_margin = st.slider("最低毛利润率 (%)", 20, 90, 40)
        min_net_margin = st.slider("最低净利润率 (%)", 5, 60, 15)
        
        # 高级财务选项
        with st.expander("高级财务选项"):
            require_positive_cashflow = st.checkbox("要求正现金流", value=True)
            min_roi_consistency = st.slider("最低ROI稳定性 (%)", 50, 100, 70, 
                                           help="预期ROI实现的概率")
    
    # 风险偏好映射
    risk_mapping = {
        '非常保守': {'max_risk': '低风险', 'min_net_margin': 20, 'min_roi': 20},
        '保守': {'max_risk': '低风险', 'min_net_margin': 15, 'min_roi': 18},
        '适中': {'max_risk': '中风险', 'min_net_margin': 12, 'min_roi': 15},
        '积极': {'max_risk': '中风险', 'min_net_margin': 8, 'min_roi': 12},
        '非常积极': {'max_risk': '高风险', 'min_net_margin': 5, 'min_roi': 10}
    }
    
    # 投资规模映射
    size_mapping = {
        '天使轮 (5-20M)': {'min_market_size': 30, 'max_payback_bonus': 8},
        'A轮 (20-50M)': {'min_market_size': 50, 'max_payback_bonus': 6},
        'B轮 (50-100M)': {'min_market_size': 80, 'max_payback_bonus': 5},
        'C轮及以上 (100M+)': {'min_market_size': 120, 'max_payback_bonus': 4}
    }
    
    if st.button("🎯 生成智能推荐", type="primary", use_container_width=True):
        with st.spinner('正在分析最佳投资机会...'):
            # 获取所有机会
            def calculate_financial_score(financial_data):
                """计算财务健康度分数"""
                score = 0
                # 毛利润率权重25%
                score += min(financial_data['gross_margin'] * 0.25, 25)
                # 净利润率权重30%
                score += min(financial_data['net_margin'] * 0.30, 30)
                # ROI权重25%（除以2避免数值过大）
                score += min(financial_data['roi'] / 2 * 0.25, 25)
                # 回收期权重20%（回收期越短分数越高）
                score += min((10 - financial_data['payback_period']) * 2 * 0.20, 20)
                
                return round(score, 1)

            opportunities = analyzer.calculate_opportunity_scores()
            
            # 为每个机会添加财务指标
            financial_opportunities = []
            for opp in opportunities:
                financial_data = generate_financial_metrics(opp['tech_area'])
                financial_opp = {
                    **opp,
                    **financial_data,
                    'financial_score': calculate_financial_score(financial_data),
                    'investment_recommendation': generate_investment_recommendation(financial_data)
                }
                financial_opportunities.append(financial_opp)
            
            # 筛选和评分
            filtered_opps = []
            risk_profile = risk_mapping[risk_tolerance]
            size_profile = size_mapping[investment_size]
            
            for opp in financial_opportunities:
                match_score = 0
                total_weight = 0
                reasoning = []
                
                # 1. 财务指标匹配 (权重40%)
                financial_match = 0
                if opp['roi'] >= min_roi:
                    financial_match += 25
                    reasoning.append(f"ROI {opp['roi']}% 达标")
                else:
                    reasoning.append(f"ROI {opp['roi']}% 未达{min_roi}%要求")
                
                if opp['payback_period'] <= max_payback:
                    financial_match += 25
                    reasoning.append(f"回收期{opp['payback_period']}年符合要求")
                else:
                    reasoning.append(f"回收期{opp['payback_period']}年超过{max_payback}年限制")
                
                if opp['gross_margin'] >= min_gross_margin:
                    financial_match += 25
                    reasoning.append(f"毛利率{opp['gross_margin']}% 达标")
                else:
                    reasoning.append(f"毛利率{opp['gross_margin']}% 未达{min_gross_margin}%要求")
                
                if opp['net_margin'] >= min_net_margin:
                    financial_match += 25
                    reasoning.append(f"净利率{opp['net_margin']}% 达标")
                else:
                    reasoning.append(f"净利率{opp['net_margin']}% 未达{min_net_margin}%要求")
                
                match_score += financial_match * 0.4
                total_weight += 40
                
                # 2. 风险偏好匹配 (权重20%)
                risk_bonus = 0
                if (opp['risk_level'] in ['低风险'] and risk_profile['max_risk'] == '低风险') or \
                   (opp['risk_level'] in ['低风险', '中风险'] and risk_profile['max_risk'] == '中风险') or \
                   (risk_profile['max_risk'] == '高风险'):
                    risk_bonus = 20
                    reasoning.append("风险等级匹配")
                else:
                    reasoning.append(f"风险等级{opp['risk_level']}不符合要求")
                
                match_score += risk_bonus
                total_weight += 20
                
                # 3. 市场规模匹配 (权重15%)
                if opp['market_size'] >= size_profile['min_market_size']:
                    match_score += 15
                    reasoning.append(f"市场规模{opp['market_size']}亿符合要求")
                else:
                    reasoning.append(f"市场规模{opp['market_size']}亿偏小")
                total_weight += 15
                
                # 4. 领域偏好匹配 (权重15%)
                if not preferred_areas or opp['tech_area'] in preferred_areas:
                    match_score += 15
                    reasoning.append("技术领域匹配")
                else:
                    reasoning.append("技术领域不匹配")
                total_weight += 15
                
                # 5. 投资期限匹配 (权重10%)
                horizon_bonus = 0
                if investment_horizon == '短期 (1-2年)' and opp['payback_period'] <= 2:
                    horizon_bonus = 10
                elif investment_horizon == '中期 (3-5年)' and opp['payback_period'] <= 5:
                    horizon_bonus = 10
                elif investment_horizon == '长期 (5年以上)':
                    horizon_bonus = 10
                
                if horizon_bonus > 0:
                    reasoning.append("投资期限匹配")
                else:
                    reasoning.append("投资期限不匹配")
                
                match_score += horizon_bonus
                total_weight += 10
                
                # 计算最终匹配度
                final_match_percentage = (match_score / total_weight) * 100
                
                # 机会质量加成（基于原始机会分数）
                quality_bonus = opp['opportunity_score'] * 0.1
                final_match_percentage = min(final_match_percentage + quality_bonus, 100)
                
                if final_match_percentage >= 50:  # 匹配度50%以上的机会
                    opp['match_percentage'] = final_match_percentage
                    opp['match_reasoning'] = reasoning
                    filtered_opps.append(opp)
            
            if filtered_opps:
                # 按匹配度和机会分数综合排序
                filtered_opps = sorted(
                    filtered_opps, 
                    key=lambda x: (x['match_percentage'] * 0.6 + x['opportunity_score'] * 0.4), 
                    reverse=True
                )
                
                st.success(f"找到 {len(filtered_opps)} 个匹配的投资机会")
                
                # 显示推荐结果
                for i, opp in enumerate(filtered_opps[:8]):
                    with st.container():
                        # 创建卡片式布局
                        st.markdown(f"### 🎯 {i+1}. {opp['tech_area']}")
                        
                        # 顶部指标行
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("匹配度", f"{opp['match_percentage']:.1f}%")
                            st.metric("综合分数", f"{opp['opportunity_score']}")
                        with col2:
                            st.metric("财务健康度", f"{opp['financial_score']}/100")
                            st.metric("投资回报率", f"{opp['roi']}%")
                        with col3:
                            st.metric("毛利润率", f"{opp['gross_margin']}%")
                            st.metric("净利润率", f"{opp['net_margin']}%")
                        with col4:
                            st.metric("回收周期", f"{opp['payback_period']}年")
                            st.metric("风险等级", opp['risk_level'])
                        
                        # 进度条可视化
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.write("财务匹配度")
                            st.progress(opp['financial_score'] / 100)
                        with col_b:
                            st.write("机会匹配度")
                            st.progress(opp['match_percentage'] / 100)
                        with col_c:
                            st.write("风险适配度")
                            risk_progress = 0.8 if opp['risk_level'] == '低风险' else 0.6 if opp['risk_level'] == '中风险' else 0.4
                            st.progress(risk_progress)
                        
                        # 详细分析
                        with st.expander("📊 详细分析与建议"):
                            tab1, tab2, tab3 = st.tabs(["财务分析", "匹配理由", "投资建议"])
                            
                            with tab1:
                                st.subheader("💰 财务健康度分析")
                                col_x, col_y = st.columns(2)
                                with col_x:
                                    st.write("**核心财务指标**:")
                                    st.write(f"- 毛利润率: {opp['gross_margin']}% | 行业水平: {'优秀' if opp['gross_margin'] >= 60 else '良好' if opp['gross_margin'] >= 45 else '一般'}")
                                    st.write(f"- 净利润率: {opp['net_margin']}% | 行业水平: {'优秀' if opp['net_margin'] >= 25 else '良好' if opp['net_margin'] >= 15 else '一般'}")
                                    st.write(f"- 投资回报率: {opp['roi']}% | 行业水平: {'优秀' if opp['roi'] >= 50 else '良好' if opp['roi'] >= 25 else '一般'}")
                                    st.write(f"- 回收周期: {opp['payback_period']}年 | 行业水平: {'很快' if opp['payback_period'] <= 3 else '合理' if opp['payback_period'] <= 5 else '较长'}")
                                
                                with col_y:
                                    st.write("**财务健康度评估**:")
                                    health_level = "优秀" if opp['financial_score'] >= 80 else "良好" if opp['financial_score'] >= 60 else "一般"
                                    st.write(f"- 综合财务分数: {opp['financial_score']}/100 ({health_level})")
                                    st.write(f"- 盈利能力: {'强' if opp['net_margin'] >= 20 else '中等' if opp['net_margin'] >= 10 else '弱'}")
                                    st.write(f"- 资金效率: {'高' if opp['payback_period'] <= 3 else '中等' if opp['payback_period'] <= 5 else '低'}")
                                    st.write(f"- 增长潜力: {'高' if opp['roi'] >= 40 else '中等' if opp['roi'] >= 20 else '一般'}")
                            
                            with tab2:
                                st.subheader("🎯 匹配理由")
                                st.write("**匹配度分析**:")
                                for reason in opp['match_reasoning'][:6]:  # 显示前6个理由
                                    st.write(f"- {reason}")
                                
                                st.write("**技术优势**:")
                                st.write(f"- 技术质量分数: {opp['quality_score']}/100")
                                st.write(f"- 增长潜力分数: {opp['growth_score']}/100")
                                st.write(f"- 竞争程度: {opp['competition_score']}/100")
                            
                            with tab3:
                                st.subheader("💡 投资建议")
                                st.write(f"**总体建议**: {opp['investment_recommendation']}")
                                
                                # 基于财务指标的具体建议
                                if opp['financial_score'] >= 80:
                                    st.success("💰 **强烈推荐**: 财务指标优秀，盈利能力强，建议大额投资")
                                elif opp['financial_score'] >= 60:
                                    st.info("✅ **推荐投资**: 财务指标良好，投资回报可观，建议中等规模投资")
                                else:
                                    st.warning("⚠️ **谨慎考虑**: 财务指标一般，建议小额投资并密切关注")
                                
                                # 投资策略建议
                                st.write("**投资策略**:")
                                if opp['payback_period'] <= 2 and opp['roi'] >= 50:
                                    st.write("- 快速进入，追求短期高回报")
                                elif opp['payback_period'] <= 5:
                                    st.write("- 稳健投资，平衡风险与回报")
                                else:
                                    st.write("- 长期持有，关注技术壁垒和市场地位")
                                
                                # 显示匹配投资者
                                investors = analyzer.recommend_investors(opp['tech_area'], 3)
                                if investors:
                                    st.write("**🤝 推荐合作投资者**:")
                                    for inv in investors:
                                        st.write(f"- {inv['investor_name']} ({inv['investor_type']}) - 匹配度: {inv['match_score']}%")
                        
                        st.divider()
            else:
                st.warning("没有找到完全匹配的投资机会")
                
                # 显示部分高潜力机会作为参考
                st.info("以下是一些高潜力机会供您参考:")
                high_potential = sorted(financial_opportunities, key=lambda x: x['opportunity_score'], reverse=True)[:3]
                
                for opp in high_potential:
                    with st.container():
                        st.write(f"**{opp['tech_area']}** | 机会分数: {opp['opportunity_score']} | 财务健康度: {opp['financial_score']}/100")
                        st.write(f"投资建议: {opp['investment_recommendation']}")
                        st.progress(opp['opportunity_score'] / 100)
    
    # 财务分析辅助函数（放在页面底部）
    def generate_financial_metrics(tech_area):
        """为技术领域生成财务指标（模拟数据）"""
        financial_profiles = {
            'AI': {'gross_margin': (50, 80), 'net_margin': (20, 40), 'roi': (30, 100), 'payback': (2, 5)},
            '区块链': {'gross_margin': (60, 90), 'net_margin': (25, 50), 'roi': (40, 120), 'payback': (1, 4)},
            '生物科技': {'gross_margin': (40, 70), 'net_margin': (15, 35), 'roi': (25, 80), 'payback': (3, 8)},
            '新能源': {'gross_margin': (35, 60), 'net_margin': (10, 25), 'roi': (20, 60), 'payback': (4, 10)},
            '物联网': {'gross_margin': (45, 75), 'net_margin': (18, 38), 'roi': (28, 90), 'payback': (2, 6)},
        }
        
        profile = financial_profiles.get(tech_area, {'gross_margin': (40, 70), 'net_margin': (15, 30), 'roi': (25, 70), 'payback': (3, 7)})
        
        import random
        return {
            'gross_margin': random.randint(profile['gross_margin'][0], profile['gross_margin'][1]),
            'net_margin': random.randint(profile['net_margin'][0], profile['net_margin'][1]),
            'roi': random.randint(profile['roi'][0], profile['roi'][1]),
            'payback_period': random.randint(profile['payback'][0], profile['payback'][1])
        }

    def calculate_financial_score(financial_data):
        """计算财务健康度分数"""
        score = 0
        # 毛利润率权重25%
        score += min(financial_data['gross_margin'] * 0.25, 25)
        # 净利润率权重30%
        score += min(financial_data['net_margin'] * 0.30, 30)
        # ROI权重25%（除以2避免数值过大）
        score += min(financial_data['roi'] / 2 * 0.25, 25)
        # 回收期权重20%（回收期越短分数越高）
        score += min((10 - financial_data['payback_period']) * 2 * 0.20, 20)
        
        return round(score, 1)

    def generate_investment_recommendation(financial_data):
        """生成投资建议"""
        gross = financial_data['gross_margin']
        net = financial_data['net_margin']
        roi = financial_data['roi']
        payback = financial_data['payback_period']
        
        if gross >= 60 and net >= 25 and roi >= 50 and payback <= 3:
            return "强烈推荐：财务指标优秀，盈利能力强，回收快"
        elif gross >= 45 and net >= 15 and roi >= 25 and payback <= 5:
            return "推荐投资：财务指标良好，投资回报可观"
        elif gross >= 35 and net >= 10 and roi >= 20:
            return "谨慎考虑：财务指标一般，需要关注运营效率"
        else:
            return "暂不推荐：财务指标未达投资标准"

elif page == "投资者匹配":
    st.header("投资者智能匹配")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("投资者列表")
        selected_investor = st.selectbox(
            "选择投资者",
            options=df_investors['name'].tolist(),
            help="选择要分析匹配度的投资者"
        )
    
    with col2:
        st.subheader("投资者详情")
        if selected_investor:
            investor_data = df_investors[df_investors['name'] == selected_investor].iloc[0]
            
            st.write(f"投资者类型: {investor_data['type']}")
            st.write(f"风险偏好: {investor_data['risk_tolerance']}")
            st.write(f"投资规模: {investor_data['investment_size']}")
            st.write(f"投资期限: {investor_data['investment_horizon']}")
            st.write(f"关注领域: {', '.join(investor_data['focus_areas'])}")
            st.write(f"偏好阶段: {investor_data['preferred_stage']}")
            st.write(f"地理偏好: {', '.join(investor_data['geographic_focus'])}")
    
    if st.button("生成匹配推荐", type="primary"):
        with st.spinner('正在分析最佳匹配...'):
            investor_id = df_investors[df_investors['name'] == selected_investor]['investor_id'].iloc[0]
            
            collab_recommendations = analyzer.hybrid_recommendation(investor_id, 8)
            
            if collab_recommendations:
                st.success(f"为 {selected_investor} 找到 {len(collab_recommendations)} 个匹配领域")
                
                opportunities = analyzer.calculate_opportunity_scores()
                opportunity_dict = {opp['tech_area']: opp for opp in opportunities}
                
                for i, (area, score) in enumerate(collab_recommendations, 1):
                    if area in opportunity_dict:
                        opp = opportunity_dict[area]
                        
                        with st.container():
                            st.markdown(f"### {i}. {area}")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("匹配分数", f"{score:.3f}")
                                st.metric("机会分数", f"{opp['opportunity_score']}")
                            with col2:
                                st.metric("增长潜力", f"{opp['cagr']}%")
                                st.metric("市场规模", f"{opp['market_size']}亿")
                            with col3:
                                st.metric("质量评分", f"{opp['quality_score']}")
                                st.metric("竞争程度", f"{opp['competition_score']}")
                            with col4:
                                st.metric("风险等级", opp['risk_level'])
                                st.metric("趋势信号", opp['trend_signal'])
                            
                            st.info(f"推荐理由: 基于协同过滤算法，该领域与投资者的历史偏好高度匹配")
                            st.info(f"投资建议: {opp['recommendation']}")
                            
                            st.divider()
            else:
                st.warning("未找到匹配的推荐领域")

# 页脚
st.markdown("---")
st.markdown("IP机会发现平台 · 基于人工智能的技术投资分析工具 · 包含协同过滤推荐算法")

# 修改导入部分
from data_fetcher import NoKeyDataFetcher  # 替换原来的 DataFetcher
from data_updater import RealTimeUpdater

# 修改数据加载部分
@st.cache_data
def load_data():
    # 使用无需密钥的数据获取器
    fetcher = NoKeyDataFetcher()
    
    # 生成专利数据
    all_patents = []
    for area in fetcher.tech_areas:
        area_patents = fetcher.fetch_patent_data(area)
        all_patents.append(area_patents)
    df_patents = pd.concat(all_patents, ignore_index=True)
    
    # 生成市场数据
    market_data = []
    for area in fetcher.tech_areas:
        data = fetcher.fetch_market_data(area)
        data['tech_area'] = area
        data['year'] = datetime.now().year
        market_data.append(data)
    df_market = pd.DataFrame(market_data)
    
    # 生成投资者数据
    df_investors = fetcher.fetch_investment_data()
    
    analyzer = PatentAnalyzer(df_patents, df_market, df_investors)
    return df_patents, df_market, df_investors, analyzer

# 在侧边栏添加数据源说明
with st.sidebar:
    st.markdown("---")
    st.header("📊 数据来源说明")
    st.info("""
    **当前使用数据**: 
    - 增强模拟专利数据
    - 公开市场统计数据
    - 模拟投资者资料
    
    **更新策略**:
    - 自动更新: 每2小时
    - 手动更新: 随时触发
    - 数据增强: 模拟真实波动
    """)
