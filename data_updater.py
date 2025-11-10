import schedule
import time
import threading
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd

class RealTimeUpdater:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.last_update = None
        self.is_updating = False
        self.update_count = 0
        
    def start_background_update(self):
        """启动后台更新线程"""
        def update_loop():
            while True:
                try:
                    self.update_opportunity_scores()
                    # 每2小时更新一次（演示用可以设置更短时间）
                    time.sleep(7200)  
                except Exception as e:
                    print(f"更新失败: {e}")
                    time.sleep(300)  # 5分钟后重试
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    def update_opportunity_scores(self):
        """更新机会分数"""
        if self.is_updating:
            return
            
        self.is_updating = True
        try:
            print("开始更新机会分数...")
            
            # 使用无需密钥的数据获取器
            from data_fetcher import NoKeyDataFetcher
            fetcher = NoKeyDataFetcher()
            
            # 获取所有技术领域的最新数据
            updated_patents = []
            updated_market = []
            
            for area in fetcher.tech_areas:
                # 获取专利数据
                new_patents = fetcher.fetch_patent_data(area)
                updated_patents.append(new_patents)
                
                # 获取市场数据
                market_data = fetcher.fetch_market_data(area)
                market_data['tech_area'] = area
                market_data['year'] = datetime.now().year
                updated_market.append(market_data)
            
            # 合并数据
            if updated_patents:
                all_patents = pd.concat(updated_patents, ignore_index=True)
                self.analyzer.df_patents = all_patents
                
                # 更新市场数据
                market_df = pd.DataFrame(updated_market)
                self.analyzer.df_market = market_df
                
                # 重新计算机会分数
                new_opportunities = self.analyzer.calculate_opportunity_scores()
                
                # 更新缓存
                try:
                    st.cache_data.clear()
                except:
                    pass
                
                self.update_count += 1
                self.last_update = datetime.now()
                print(f"机会分数更新完成 ({self.update_count}): {self.last_update}")
                
        except Exception as e:
            print(f"更新失败: {e}")
        finally:
            self.is_updating = False
    
    def get_update_status(self):
        """获取更新状态"""
        return {
            'last_update': self.last_update,
            'is_updating': self.is_updating,
            'update_count': self.update_count,
            'next_update': self.last_update + timedelta(hours=2) if self.last_update else None
        }
    
    def manual_update(self):
        """手动触发更新"""
        if not self.is_updating:
            self.update_opportunity_scores()
            return True
        return False