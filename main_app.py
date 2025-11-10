# main_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# 侧边栏导航
st.sidebar.title("导航")
page = st.sidebar.radio("选择功能", [
    "机会发现", 
    "技术分析", 
    "趋势追踪",
    "个性化推荐",
    "投资者匹配"
])

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
    st.header("智能机会推荐系统")
    
    st.subheader("构建您的投资画像")
    
    col1, col2 = st.columns(2)
    
    with col1:
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
        
        min_quality = st.slider("最低质量要求", 0, 100, 50)
    
    with col2:
        preferred_areas = st.multiselect(
            "重点关注领域 (可选)",
            options=df_patents['tech_area'].unique(),
            help="选择您特别感兴趣的领域"
        )
        
        min_market_size = st.slider("最小市场规模", 10, 300, 60)
        max_competition = st.slider("最大可接受竞争程度", 0, 100, 70)
    
    investment_size = st.selectbox(
        "投资规模偏好",
        ['天使轮 (50-500万港币)', 'A轮 (500-2000万港币)', 'B轮及以上 (2000万港币以上)'],
        index=1
    )
    
    if st.button("生成智能推荐", type="primary"):
        with st.spinner('正在分析最佳投资机会...'):
            opportunities = analyzer.calculate_opportunity_scores()
            
            filtered_opps = []
            for opp in opportunities:
                score = 0
                total_weight = 0
                
                risk_mapping = {'非常保守': 0.2, '保守': 0.4, '适中': 0.6, '积极': 0.8, '非常积极': 1.0}
                risk_factor = risk_mapping[risk_tolerance]
                if opp['risk_level'] in ['Low', 'Medium'] and risk_factor >= 0.6:
                    score += 1
                elif opp['risk_level'] in ['Medium-High', 'High'] and risk_factor >= 0.8:
                    score += 1
                total_weight += 1
                
                if opp['quality_score'] >= min_quality:
                    score += 1
                total_weight += 1
                
                if opp['market_size'] >= min_market_size:
                    score += 1
                total_weight += 1
                
                competition_score = 100 - opp['competition_score']
                if competition_score <= max_competition:
                    score += 1
                total_weight += 1
                
                if not preferred_areas or opp['tech_area'] in preferred_areas:
                    score += 2
                total_weight += 2
                
                match_percentage = (score / total_weight) * 100
                
                if match_percentage >= 30 or opp['opportunity_score'] >= 50:
                    opp['match_percentage'] = match_percentage
                    filtered_opps.append(opp)
            
            if filtered_opps:
                filtered_opps = sorted(
                    filtered_opps, 
                    key=lambda x: (x['match_percentage'] * 0.4 + x['opportunity_score'] * 0.6), 
                    reverse=True
                )
                
                st.success(f"找到 {len(filtered_opps)} 个匹配的投资机会")
                
                for i, opp in enumerate(filtered_opps[:10]):
                    with st.container():
                        st.markdown(f"### {i+1}. {opp['tech_area']}")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("综合分数", f"{opp['opportunity_score']}")
                            st.metric("匹配度", f"{opp['match_percentage']:.1f}%")
                        with col2:
                            st.metric("增长潜力", f"{opp['cagr']}%")
                            st.metric("市场规模", f"{opp['market_size']}亿")
                        with col3:
                            st.metric("质量评分", f"{opp['quality_score']}")
                            st.metric("竞争程度", f"{opp['competition_score']}")
                        with col4:
                            st.metric("风险等级", opp['risk_level'])
                            st.metric("趋势信号", opp['trend_signal'])
                        
                        investment_recommendation = get_investment_recommendation(opp['opportunity_score'], opp['risk_level'])
                        
                        with st.expander("详细分析"):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.write("投资建议:", investment_recommendation)
                                st.write("推荐理由:", opp['recommendation'])
                                
                                investors = analyzer.recommend_investors(opp['tech_area'], 3)
                                if investors:
                                    st.write("推荐投资者:")
                                    for inv in investors:
                                        st.write(f"- {inv['investor_name']} ({inv['match_score']}% 匹配) - {inv['reasoning']}")
                            
                            with col_b:
                                insights = analyzer.get_market_insights(opp['tech_area'])
                                if insights:
                                    st.write("市场洞察:")
                                    st.write(f"- 当前增长率: {insights['current_growth']*100:.1f}%")
                                    st.write(f"- 投资热度: {insights['investment_heat']}/100")
                                    st.write(f"- 政府支持度: {insights['government_support']}/100")
                                    st.write(f"- 风险等级: {insights['risk_level']}")
                        
                        st.divider()
            else:
                st.warning("没有找到完全匹配的机会，以下是一些高潜力领域供参考:")
                for opp in opportunities[:8]:
                    with st.container():
                        st.markdown(f"### {opp['tech_area']}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("机会分数", f"{opp['opportunity_score']}")
                        with col2:
                            st.metric("增长潜力", f"{opp['cagr']}%")
                        with col3:
                            st.metric("风险等级", opp['risk_level'])
                        
                        st.info(f"建议: {opp['recommendation']}")
                        st.divider()

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