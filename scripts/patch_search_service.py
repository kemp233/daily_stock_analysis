import os

def patch():
    file_path = "src/search_service.py"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否已经注入过，防止重复注入
    if "AkShare-Priority" in content:
        print("AkShare logic already exists. Skipping.")
        return

    # 定义要注入的代码块
    ak_logic = """
        # === AkShare A-Share Intercept Start (Auto-injected by GitHub Actions) ===
        if not is_foreign and not focus_keywords:
            import akshare as ak
            code = "".join(filter(str.isdigit, stock_code))
            if len(code) == 6:
                logger.info(f"🧬 [AkShare-Priority] 拦截 A 股搜索: {stock_name}({code})")
                try:
                    df = ak.stock_news_em(symbol=code)
                    ak_results = []
                    if not df.empty:
                        for _, r in df.head(max_results + 5).iterrows():
                            # 使用新版定义的 SearchResult 类
                            ak_results.append(SearchResult(
                                title=str(r.iloc[0]),
                                snippet=f"来自东方财富的实时异动：{r.iloc[0]}",
                                url=f"https://mguba.eastmoney.com/mguba/article/0/{code}",
                                source="EastMoney",
                                published_date=str(r.iloc[1])
                            ))
                    if ak_results:
                        resp = SearchResponse(
                            query=query,
                            results=ak_results,
                            provider="AkShare-Internal",
                            success=True
                        )
                        # 利用新版自带的过滤和缓存逻辑
                        filtered_resp = self._filter_news_response(
                            resp, 
                            search_days=search_days, 
                            max_results=max_results,
                            log_scope=f"{stock_code}:AkShare:stock_news"
                        )
                        if filtered_resp.results:
                            self._put_cache(cache_key, filtered_resp)
                            return filtered_resp
                except Exception as e:
                    logger.warning(f"AkShare 尝试失败，回退到通用搜索: {e}")
        # === AkShare A-Share Intercept End ===
"""

    # 寻找注入点：在新版代码的 query 生成之后
    target_pattern = 'query = f"{stock_name} {stock_code} 股票 最新消息"'
    if target_pattern in content:
        new_content = content.replace(target_pattern, target_pattern + ak_logic)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully patched src/search_service.py")
    else:
        print("Error: Target pattern for injection not found in search_service.py")

if __name__ == "__main__":
    patch()
