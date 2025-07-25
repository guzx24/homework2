# import os
# import requests
# from serpapi import GoogleSearch

# def search(content: str):
#     """
#     使用SerpAPI进行必应搜索
#     :param content: 搜索内容
#     :return: 组合后的提问内容
#     """
#     try:
#         # 使用SerpAPI进行必应搜索
#         params = {
#             "q": content,
#             "engine": "bing",
#             "api_key": os.getenv("SERPAPI_API_KEY")  # 从环境变量获取API密钥
#         }
        
#         search = GoogleSearch(params)
#         results = search.get_dict()
        
#         # 获取第一条结果的摘要
#         if 'organic_results' in results and len(results['organic_results']) > 0:
#             snippet = results['organic_results'][0].get('snippet', '')
#         else:
#             snippet = "未找到相关信息"
        
#         # 组合成有效的提问
#         return f"请根据以下搜索结果回答'{content}':\n\n{snippet}"
        
#     except Exception as e:
#         print(f"搜索出错: {e}")
#         return content  # 出错时返回原始内容


import os
import requests
from serpapi import GoogleSearch

def search(content: str):
    """
    使用SerpAPI进行必应搜索，并处理各种可能的错误。
    :param content: 搜索内容
    :return: 组合后的提问内容，或在出错时返回一个包含错误信息的提示。
    """
    # 1. 检查 API 密钥是否存在
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("错误: SERPAPI_API_KEY 环境变量未设置。")
        # 返回一个对用户友好的错误信息，而不是直接把内容发给模型
        return f"网络搜索功能未配置，无法为您搜索 '{content}'。请检查 API 密钥设置。"

    try:
        print(f"--- [search.py] 正在使用必应搜索: '{content}' ---")
        params = {
            "q": content,
            "engine": "bing",  # 使用必应搜索引擎
            "api_key": api_key
        }
        
        search_client = GoogleSearch(params)
        results = search_client.get_dict()
        
        # 2. 检查并提取第一条自然结果的摘要
        if 'organic_results' in results and len(results['organic_results']) > 0:
            snippet = results['organic_results'][0].get('snippet')
            if snippet:
                print("--- [search.py] 搜索成功，已找到结果摘要。 ---")
                # 3. 采用作业说明中推荐的、对模型更友好的提问格式
                return f"Please answer '{content}' based on the search result:\n\n{snippet}"
            else:
                print("--- [search.py] 搜索成功，但第一条结果没有摘要。 ---")
                return f"网络搜索找到了相关页面，但未能提取摘要。请尝试根据你的知识回答：'{content}'"
        else:
            print("--- [search.py] 搜索成功，但没有找到'organic_results'。 ---")
            return f"未能通过网络搜索找到关于 '{content}' 的直接信息。请尝试根据你的知识回答这个问题。"
            
    except Exception as e:
        print(f"--- [search.py] 搜索过程中发生错误: {e} ---")
        # 4. 在发生网络错误等异常时，返回一个清晰的错误提示
        return f"在为您搜索 '{content}' 的过程中网络连接出现问题。请仅根据您的已有知识进行回答。"
