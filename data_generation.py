# data_generation.py
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from faker import Faker
import requests
import json

# 初始化Faker
fake = Faker()

class DataGenerator:
    def __init__(self):
        self.tech_hierarchy = {
            'FinTech': {
                'subcategories': ['Digital Payments', 'Blockchain', 'WealthTech', 'InsurTech', 'RegTech'],
                'companies': ['HSBC', 'Standard Chartered', 'WeLab', 'TNG', 'ZA Bank', 'Ant Group', 'Tencent', 'Alibaba'],
                'growth_rate': 0.18,
                'market_size': 200,
                'keywords': ['blockchain', 'payment', 'financial', 'banking', 'crypto', 'investment']
            },
            'AI and Machine Learning': {
                'subcategories': ['Computer Vision', 'NLP', 'Predictive Analytics', 'Autonomous Systems', 'Deep Learning'],
                'companies': ['SenseTime', 'HKUST', 'CUHK', 'HKU', 'Microsoft Hong Kong', 'Google AI', 'Baidu Research'],
                'growth_rate': 0.28,
                'market_size': 250,
                'keywords': ['neural network', 'machine learning', 'artificial intelligence', 'deep learning', 'algorithm']
            },
            'Biotechnology': {
                'subcategories': ['Genomics', 'Drug Discovery', 'Medical Devices', 'Biomaterials', 'Bioinformatics'],
                'companies': ['Prenetics', 'HKU Med', 'Chinese Medicine Research Centre', 'GeneHarbor', 'Biotech Labs'],
                'growth_rate': 0.22,
                'market_size': 180,
                'keywords': ['genetic', 'medical', 'drug', 'therapy', 'biomedical', 'healthcare']
            },
            'Smart City': {
                'subcategories': ['Smart Mobility', 'Energy Management', 'Urban Analytics', 'Public Safety', 'IoT Infrastructure'],
                'companies': ['HKT', 'HK Electric', 'MTR Corporation', 'Smart City Consortium', 'UrbanTech Solutions'],
                'growth_rate': 0.16,
                'market_size': 220,
                'keywords': ['iot', 'smart city', 'urban', 'sustainable', 'infrastructure', 'mobility']
            },
            'HealthTech': {
                'subcategories': ['Telemedicine', 'EHR Systems', 'Medical Imaging', 'Wearable Devices', 'Health Analytics'],
                'companies': ['Prenetics', 'DoctorNow', 'Seed', 'Health & Medical', 'MedTech Innovations'],
                'growth_rate': 0.25,
                'market_size': 190,
                'keywords': ['healthcare', 'medical', 'telemedicine', 'diagnosis', 'treatment']
            },
            'Green Technology': {
                'subcategories': ['Renewable Energy', 'Energy Storage', 'Carbon Capture', 'Waste Management', 'Sustainable Materials'],
                'companies': ['CLP Power', 'HK Electric', 'Green Energy Tech', 'EcoTech Solutions', 'Sustainable HK'],
                'growth_rate': 0.21,
                'market_size': 150,
                'keywords': ['renewable', 'sustainable', 'green', 'energy', 'environment', 'carbon']
            },
            'EdTech': {
                'subcategories': ['Online Learning', 'Educational Games', 'Learning Analytics', 'VR Education', 'Adaptive Learning'],
                'companies': ['Hong Kong Education Bureau', 'Online Learning Platform', 'EduTech Startups', 'LearnTech HK'],
                'growth_rate': 0.19,
                'market_size': 120,
                'keywords': ['education', 'learning', 'online', 'teaching', 'educational']
            },
            'Logistics Technology': {
                'subcategories': ['Supply Chain', 'Last-mile Delivery', 'Warehouse Automation', 'Fleet Management', 'Logistics Analytics'],
                'companies': ['Lalamove', 'GoGoVan', 'SF Express', 'DHL Hong Kong', 'LogisticsTech HK'],
                'growth_rate': 0.17,
                'market_size': 160,
                'keywords': ['logistics', 'supply chain', 'delivery', 'shipping', 'transport']
            },
            'Cybersecurity': {
                'subcategories': ['Network Security', 'Data Protection', 'Threat Intelligence', 'Identity Management', 'Cloud Security'],
                'companies': ['CyberSecurity HK', 'SafeNet Solutions', 'HKUST Security Lab', 'Digital Protection Ltd'],
                'growth_rate': 0.24,
                'market_size': 140,
                'keywords': ['security', 'cybersecurity', 'protection', 'encryption', 'firewall']
            },
            'Quantum Computing': {
                'subcategories': ['Quantum Algorithms', 'Quantum Hardware', 'Quantum Cryptography', 'Quantum Simulation'],
                'companies': ['HKU Quantum Lab', 'CUHK Research', 'QuantumTech HK', 'Advanced Computing Ltd'],
                'growth_rate': 0.30,
                'market_size': 90,
                'keywords': ['quantum', 'computing', 'qubit', 'quantum algorithm', 'quantum cryptography']
            }
        }
        
        self.investor_profiles = self._generate_investor_profiles()
    
    def _generate_investor_profiles(self):
        """生成详细的投资者画像"""
        investors = []
        
        investor_templates = [
            {
                'type': 'VC_Firm',
                'risk_tolerance': 'High',
                'investment_size': '10-50M HKD',
                'horizon': '5-10 years',
                'sectors': ['AI and Machine Learning', 'FinTech', 'Biotechnology', 'Quantum Computing'],
                'preference': 'Early Stage',
                'geo_focus': ['Hong Kong', 'Greater Bay Area'],
                'min_quality': 60,
                'min_market_size': 80
            },
            {
                'type': 'Angel_Investor',
                'risk_tolerance': 'Medium-High',
                'investment_size': '1-5M HKD',
                'horizon': '3-7 years',
                'sectors': ['HealthTech', 'EdTech', 'Green Technology'],
                'preference': 'Seed Stage',
                'geo_focus': ['Hong Kong'],
                'min_quality': 50,
                'min_market_size': 50
            },
            {
                'type': 'Corporate_VC',
                'risk_tolerance': 'Medium',
                'investment_size': '20-100M HKD',
                'horizon': 'Strategic',
                'sectors': ['Smart City', 'Logistics Technology', 'Cybersecurity'],
                'preference': 'Growth Stage',
                'geo_focus': ['Asia Pacific'],
                'min_quality': 70,
                'min_market_size': 120
            },
            {
                'type': 'Government_Fund',
                'risk_tolerance': 'Low-Medium',
                'investment_size': '50-200M HKD',
                'horizon': 'Long-term',
                'sectors': ['Green Technology', 'EdTech', 'Smart City', 'HealthTech'],
                'preference': 'All Stages',
                'geo_focus': ['Hong Kong'],
                'min_quality': 65,
                'min_market_size': 100
            },
            {
                'type': 'Private_Equity',
                'risk_tolerance': 'Medium',
                'investment_size': '100-500M HKD',
                'horizon': '3-5 years',
                'sectors': ['FinTech', 'AI and Machine Learning', 'Biotechnology'],
                'preference': 'Mature',
                'geo_focus': ['Global'],
                'min_quality': 75,
                'min_market_size': 150
            }
        ]
        
        for i, template in enumerate(investor_templates):
            for j in range(3):  # 每种类型生成3个投资者
                investor = {
                    'investor_id': f'{template["type"]}_{i+1}_{j+1}',
                    'name': f'{template["type"]} Investor {i+1}-{j+1}',
                    'type': template['type'],
                    'risk_tolerance': template['risk_tolerance'],
                    'investment_size': template['investment_size'],
                    'investment_horizon': template['horizon'],
                    'focus_areas': template['sectors'],
                    'preferred_stage': template['preference'],
                    'geographic_focus': template['geo_focus'],
                    'min_quality_score': template['min_quality'],
                    'min_market_size': template['min_market_size'],
                    'track_record': random.randint(70, 95),
                    'sector_expertise': random.randint(60, 90)
                }
                investors.append(investor)
        
        return pd.DataFrame(investors)
    
    def generate_patent_data(self, num_patents=15000):
        """生成大量专利数据"""
        print(f"正在生成 {num_patents} 条专利数据...")
        
        patents = []
        
        for i in range(num_patents):
            # 选择技术领域
            tech_area = random.choice(list(self.tech_hierarchy.keys()))
            area_info = self.tech_hierarchy[tech_area]
            subcategory = random.choice(area_info['subcategories'])
            company = random.choice(area_info['companies'])
            
            # 生成时间（2010-2024）
            year = random.randint(2010, 2024)
            
            # 基于领域特征生成相关数据
            base_citations = area_info['growth_rate'] * 80
            citations = max(0, int(np.random.poisson(base_citations)))
            
            # 市场潜力与领域相关
            base_potential = area_info['market_size'] / 2
            market_potential = max(10, min(100, int(np.random.normal(base_potential, 15))))
            
            # 专利质量评分（基于多个因素）
            quality_factors = {
                'citations': min(1.0, citations / 100),
                'company_reputation': random.uniform(0.6, 1.0),
                'tech_novelty': random.uniform(0.5, 0.95),
                'commercial_viability': random.uniform(0.4, 0.9)
            }
            quality_score = sum(quality_factors.values()) / len(quality_factors) * 100
            
            # 技术成熟度
            maturity_options = ['Research', 'Prototype', 'Early Adoption', 'Growth', 'Mature']
            maturity_weights = [0.1, 0.2, 0.3, 0.25, 0.15]
            tech_maturity = random.choices(maturity_options, weights=maturity_weights)[0]
            
            patent = {
                'patent_id': f'HK{year}{i:08d}',
                'title': self._generate_intelligent_title(tech_area, subcategory),
                'abstract': self._generate_detailed_abstract(tech_area, subcategory),
                'tech_area': tech_area,
                'subcategory': subcategory,
                'year': year,
                'applicant': company,
                'citations': citations,
                'market_potential': market_potential,
                'quality_score': round(quality_score, 1),
                'commercial_viability': random.randint(40, 95),
                'tech_maturity': tech_maturity,
                'legal_status': random.choice(['Filed', 'Under Examination', 'Granted', 'Active', 'Expired']),
                'geographic_scope': random.choice(['Hong Kong', 'Greater Bay Area', 'Asia Pacific', 'Global']),
                'industry_impact': random.randint(30, 98),
                'investment_attractiveness': random.randint(35, 96),
                'filing_date': self._generate_realistic_date(year),
                'location': 'Hong Kong',
                'research_institution': random.choice([True, False]),
                'collaboration_level': random.choice(['Single Entity', 'University-Industry', 'Cross-border', 'Multi-organization']),
                'technology_readiness': random.randint(2, 9)
            }
            patents.append(patent)
            
            # 进度显示
            if i > 0 and i % 1500 == 0:
                print(f"已生成 {i} 条专利数据...")
        
        df_patents = pd.DataFrame(patents)
        print(f"✓ 成功生成 {len(df_patents)} 条专利数据")
        return df_patents
    
    def _generate_intelligent_title(self, tech_area, subcategory):
        """生成智能化的专利标题"""
        title_templates = {
            'FinTech': [
                'Intelligent {subcategory} Platform for {context}',
                'Blockchain-based {subcategory} Solution for {context}',
                'AI-Powered {subcategory} System for {context}',
                'Secure {subcategory} Framework for {context}'
            ],
            'AI and Machine Learning': [
                'Deep Learning {subcategory} Framework for {context}',
                'Neural Network based {subcategory} Analysis System',
                'Machine Learning {subcategory} Optimization Platform',
                'Intelligent {subcategory} Algorithm for {context}'
            ],
            'Biotechnology': [
                'Advanced {subcategory} Methodology for {context}',
                'Novel {subcategory} Approach in Biomedical Applications',
                'Innovative {subcategory} Technology for {context}',
                'Precision {subcategory} System for Healthcare'
            ],
            'Smart City': [
                'IoT-based {subcategory} Management System',
                'Smart {subcategory} Solution for Urban Environments',
                'Intelligent {subcategory} Platform for Smart Cities',
                'Connected {subcategory} Infrastructure System'
            ],
            'HealthTech': [
                'Digital {subcategory} Platform for Healthcare',
                'Intelligent {subcategory} System for Medical Applications',
                'AI-driven {subcategory} Solution for {context}',
                'Connected {subcategory} Technology in Healthcare'
            ],
            'Green Technology': [
                'Sustainable {subcategory} System for {context}',
                'Eco-friendly {subcategory} Technology',
                'Renewable {subcategory} Solution for Energy',
                'Green {subcategory} Innovation for Environment'
            ],
            'EdTech': [
                'Interactive {subcategory} Platform for Education',
                'Adaptive {subcategory} System for Learning',
                'Digital {subcategory} Solution for {context}',
                'Intelligent {subcategory} Technology in Education'
            ],
            'Logistics Technology': [
                'Automated {subcategory} System for Supply Chain',
                'Intelligent {subcategory} Platform for Logistics',
                'Smart {subcategory} Solution for {context}',
                'Optimized {subcategory} Technology in Transportation'
            ],
            'Cybersecurity': [
                'Advanced {subcategory} Protection System',
                'Secure {subcategory} Framework for {context}',
                'Intelligent {subcategory} Defense Mechanism',
                'Robust {subcategory} Security Solution'
            ],
            'Quantum Computing': [
                'Quantum {subcategory} Algorithm for {context}',
                'Advanced {subcategory} in Quantum Systems',
                'Novel {subcategory} Approach using Quantum Computing',
                'Quantum-enhanced {subcategory} Technology'
            ]
        }
        
        contexts = {
            'FinTech': ['Cross-border Payments', 'Risk Assessment', 'Financial Compliance', 'Digital Banking', 'Wealth Management'],
            'AI and Machine Learning': ['Predictive Analytics', 'Pattern Recognition', 'Automated Decision Making', 'Data Analysis'],
            'Biotechnology': ['Drug Discovery', 'Genetic Analysis', 'Medical Diagnosis', 'Therapeutic Applications'],
            'Smart City': ['Urban Planning', 'Resource Optimization', 'Infrastructure Management', 'Public Services'],
            'HealthTech': ['Patient Care', 'Medical Diagnosis', 'Healthcare Management', 'Treatment Planning'],
            'Green Technology': ['Energy Efficiency', 'Environmental Protection', 'Sustainable Development', 'Carbon Reduction'],
            'EdTech': ['Personalized Learning', 'Educational Assessment', 'Skill Development', 'Knowledge Management'],
            'Logistics Technology': ['Supply Chain Optimization', 'Delivery Efficiency', 'Inventory Management', 'Route Planning'],
            'Cybersecurity': ['Data Protection', 'Network Security', 'Threat Detection', 'Access Control'],
            'Quantum Computing': ['Optimization Problems', 'Cryptography', 'Simulation', 'Machine Learning']
        }
        
        templates = title_templates.get(tech_area, ['Advanced {subcategory} Technology for {context}'])
        template = random.choice(templates)
        context = random.choice(contexts.get(tech_area, ['Innovative Applications']))
        
        return template.format(subcategory=subcategory, context=context)
    
    def _generate_detailed_abstract(self, tech_area, subcategory):
        """生成详细的专利摘要"""
        abstracts = {
            'FinTech': """
            This groundbreaking {subcategory} technology represents a significant advancement in financial services innovation. 
            Developed through extensive research in Hong Kong's dynamic financial ecosystem, the solution leverages 
            cutting-edge cryptographic protocols and distributed ledger technology to enhance security, improve 
            transaction speed, and reduce operational costs. The system addresses key challenges in {context} while 
            maintaining the highest standards of data privacy and regulatory compliance. With applications spanning 
            cross-border payments, digital asset management, and financial inclusion, this technology demonstrates 
            strong commercial viability and positions Hong Kong at the forefront of financial innovation.
            """,
            'AI and Machine Learning': """
            This sophisticated {subcategory} system utilizes state-of-the-art machine learning algorithms to deliver 
            unprecedented accuracy in complex data analysis and pattern recognition tasks. The technology incorporates 
            advanced neural network architectures and innovative feature extraction methods, making it particularly 
            effective for real-time decision-making scenarios. Developed through collaborative research between 
            Hong Kong's leading academic institutions and industry partners, this innovation has demonstrated 
            remarkable performance across multiple domains including {context}. The system's modular design and 
            scalability make it suitable for both enterprise-level deployments and specialized applications.
            """,
            'Biotechnology': """
            This innovative {subcategory} methodology represents a major breakthrough in biomedical research and 
            healthcare technology. The approach combines novel biological insights with advanced computational 
            methods to address critical challenges in {context}. Through rigorous testing and validation in 
            Hong Kong's world-class research facilities, the technology has shown exceptional promise in improving 
            diagnostic accuracy, treatment efficacy, and patient outcomes. The invention demonstrates strong 
            potential for commercialization and significant impact on global healthcare challenges, positioning 
            Hong Kong as a leader in biotechnological innovation.
            """,
            'Smart City': """
            This comprehensive {subcategory} solution addresses the unique challenges of urban environments through 
            intelligent technology integration. Designed specifically for Hong Kong's dense urban landscape, the 
            system leverages IoT sensors, data analytics, and automated control mechanisms to optimize resource 
            usage and improve quality of life. The technology demonstrates significant improvements in {context} 
            while maintaining cost-effectiveness and sustainability. With applications in urban planning, 
            infrastructure management, and public services, this innovation represents a significant step forward 
            in smart city development and positions Hong Kong as a model for urban innovation.
            """
        }
        
        default_abstract = """
        This innovative {subcategory} technology represents a significant contribution to the field of {tech_area}. 
        Developed through extensive research and rigorous testing in Hong Kong's innovation ecosystem, the invention 
        demonstrates novel approaches to addressing current market challenges in {context}. The technology showcases 
        strong commercial potential, technical sophistication, and practical applicability across multiple domains. 
        With its robust architecture and scalable design, this innovation positions Hong Kong as a leader in 
        technological advancement and creates new opportunities for economic growth and industry transformation.
        """
        
        contexts = {
            'FinTech': ['financial services', 'digital transactions', 'regulatory technology'],
            'AI and Machine Learning': ['artificial intelligence applications', 'data analysis', 'automated systems'],
            'Biotechnology': ['healthcare solutions', 'medical research', 'therapeutic development'],
            'Smart City': ['urban management', 'infrastructure optimization', 'public services'],
            'HealthTech': ['healthcare delivery', 'medical technology', 'patient care'],
            'Green Technology': ['sustainable development', 'environmental protection', 'energy efficiency'],
            'EdTech': ['educational technology', 'learning systems', 'knowledge management'],
            'Logistics Technology': ['supply chain management', 'logistics optimization', 'transportation systems'],
            'Cybersecurity': ['digital protection', 'security systems', 'threat prevention'],
            'Quantum Computing': ['computational challenges', 'scientific research', 'technical applications']
        }
        
        abstract_template = abstracts.get(tech_area, default_abstract)
        context = random.choice(contexts.get(tech_area, ['technological innovation']))
        
        return abstract_template.format(subcategory=subcategory, tech_area=tech_area, context=context)
    
    def _generate_realistic_date(self, year):
        """生成真实的申请日期"""
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        return random_date.strftime('%Y-%m-%d')
    
    def generate_market_data(self):
        """生成全面的市场数据"""
        print("正在生成市场趋势数据...")
        
        market_data = []
        
        for area, info in self.tech_hierarchy.items():
            base_growth = info['growth_rate']
            base_market_size = info['market_size']
            base_competition = random.randint(25, 75)
            
            for year in range(2010, 2025):
                # 随时间变化的趋势
                year_factor = (year - 2010) / 14  # 0到1的标准化
                
                # 增长趋势（考虑技术成熟度曲线）
                if year_factor < 0.3:
                    # 早期：波动较大
                    growth_variation = random.uniform(-0.05, 0.08)
                elif year_factor < 0.7:
                    # 成长期：稳定增长
                    growth_variation = random.uniform(-0.02, 0.05)
                else:
                    # 成熟期：增长放缓
                    growth_variation = random.uniform(-0.03, 0.03)
                
                growth_rate = max(0.03, base_growth + growth_variation)
                
                # 市场规模增长（复合增长）
                market_growth = (1 + growth_rate) ** year_factor
                market_size = int(base_market_size * market_growth)
                
                # 竞争程度变化
                if year_factor < 0.4:
                    competition_change = random.uniform(0.05, 0.15)  # 早期竞争增加
                else:
                    competition_change = random.uniform(-0.1, 0.1)  # 后期波动
                
                competition_level = max(15, min(85, base_competition + competition_change * 100))
                
                # 投资热度（与增长率和市场规模相关）
                investment_heat = min(95, max(25, int(
                    50 + (growth_rate * 200) + (market_size / 10) - (competition_level / 2)
                )))
                
                # 政府支持度
                government_support = random.randint(45, 95)
                
                # 风险等级
                risk_factors = competition_level / 100 + max(0, 0.5 - growth_rate)
                if risk_factors < 0.3:
                    risk_level = 'Low'
                elif risk_factors < 0.6:
                    risk_level = 'Medium'
                else:
                    risk_level = 'High'
                
                market_data.append({
                    'tech_area': area,
                    'year': year,
                    'growth_rate': round(growth_rate, 4),
                    'market_size': market_size,
                    'competition_level': int(competition_level),
                    'investment_heat': investment_heat,
                    'government_support': government_support,
                    'risk_level': risk_level,
                    'region': 'Hong Kong'
                })
        
        df_market = pd.DataFrame(market_data)
        print(f"✓ 成功生成 {len(df_market)} 条市场数据")
        return df_market
    
    def generate_all_data(self, num_patents=15000):
        """生成所有数据"""
        print("=" * 60)
        print("IP机会发现平台 - 全面数据生成系统")
        print("=" * 60)
        
        df_patents = self.generate_patent_data(num_patents)
        df_market = self.generate_market_data()
        df_investors = self.investor_profiles
        
        print(f"\n✓ 数据生成完成:")
        print(f"  - 专利数据: {len(df_patents)} 条记录")
        print(f"  - 市场数据: {len(df_market)} 条记录") 
        print(f"  - 投资者数据: {len(df_investors)} 条记录")
        
        # 数据质量检查
        print(f"\n📊 数据质量报告:")
        print(f"  - 技术领域分布: {df_patents['tech_area'].nunique()} 个领域")
        print(f"  - 平均专利质量: {df_patents['quality_score'].mean():.1f}")
        print(f"  - 数据时间范围: {df_patents['year'].min()}-{df_patents['year'].max()}")
        
        return df_patents, df_market, df_investors

# 全局函数
def generate_patent_data(num_patents=15000):
    """生成专利数据的便捷函数"""
    generator = DataGenerator()
    return generator.generate_all_data(num_patents)

# 测试代码
if __name__ == "__main__":
    generator = DataGenerator()
    df_patents, df_market, df_investors = generator.generate_all_data(2000)
    
    print("\n专利数据样例:")
    print(df_patents[['patent_id', 'title', 'tech_area', 'quality_score', 'market_potential']].head(3))
    
    print(f"\n技术领域分布:")
    print(df_patents['tech_area'].value_counts())
    
    print(f"\n市场数据样例:")
    print(df_market.head(3))
    
    print(f"\n投资者数据样例:")
    print(df_investors[['name', 'type', 'focus_areas']].head(3))