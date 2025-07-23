from serpapi import GoogleSearch
import logging
import requests

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search(content: str):
    """
    使用SerpAPI进行必应搜索并返回格式化结果
    """
    # 您的SerpAPI密钥
    API_KEY = "a94695382f364300dd39e0d91aba0d5f39d4358b628309d4cf91ad0ca183ec63"
    
    try:
        logger.info(f"正在搜索: {content}")
        
        # 设置搜索参数
        params = {
            "engine": "bing",
            "q": content,
            "api_key": API_KEY
        }
        
        # 执行搜索
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # 提取搜索结果
        if "organic_results" in results and results["organic_results"]:
            first_result = results["organic_results"][0]
            snippet = first_result.get("snippet", "无可用摘要")
            title = first_result.get("title", "无标题")
            link = first_result.get("link", "#")
            
            # 格式化问题
            formatted_content = (
                f"请基于以下必应搜索结果回答: {content}\n\n"
                f"**{title}**\n"
                f"{snippet}\n"
                f"来源: {link}"
            )
            logger.info(f"搜索成功: {content}")
            return formatted_content
        else:
            error_msg = f"⚠️ 未找到 '{content}' 的搜索结果"
            logger.warning(error_msg)
            return error_msg
    
    except Exception as e:
        error_msg = f"⚠️ 搜索错误: {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    print(search("Sun Wukong"))