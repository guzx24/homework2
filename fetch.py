import requests
from bs4 import BeautifulSoup

def fetch(url: str):
    """
    拉取网页内容，提取所有 p 标签文本，拼接为 processed results，
    再生成 question 并返回。
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        # 提取所有 p 标签文本
        p_texts = [p.get_text(strip=True) for p in soup.find_all('p')]
        processed_results = '\n'.join(p_texts)
        # 生成 question
        question = f"Act as a summarizer. Please summarize {url}. The following is the content:\n\n{processed_results}"
        return question
    except Exception as e:
        return f"[网页抓取或处理失败: {e}]"


if __name__ == "__main__":
    print(fetch("https://dev.qweather.com/en/help"))