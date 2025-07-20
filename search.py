import requests

# 替换为你的SerpApi密钥
SERPAPI_API_KEY = "your_serpapi_api_key_here"

def search(content: str):
    """
    使用SerpApi进行必应搜索并返回处理后的内容
    """
    try:
        # 使用SerpApi进行搜索
        params = {
            "engine": "bing",
            "q": content,
            "api_key": SERPAPI_API_KEY
        }
        
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = response.json()
        
        # 提取第一条搜索结果
        if "organic_results" in results and len(results["organic_results"]) > 0:
            first_result = results["organic_results"][0]
            snippet = first_result.get("snippet", "")
            
            # 组合搜索内容和结果（按照作业要求格式）
            return f"请根据以下搜索结果回答 '{content}':\n\n{snippet}"
        
        # 没有搜索结果时返回原始内容
        return content
    
    except Exception as e:
        print(f"搜索出错: {str(e)}")
        # 出错时返回原始内容
        return f"搜索失败，请重试。原始问题: {content}"