import os
from bs4 import BeautifulSoup
import glob
from datetime import datetime
import re

def extract_html_info(file_path):
    """
    HTMLファイルから詳細な情報を抽出する
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        
        # 基本情報の抽出
        title = soup.title.string if soup.title else os.path.basename(file_path)
        
        # ヘッダー情報の抽出
        header = soup.find('div', class_='header')
        header_title = header.find('h1').text if header and header.find('h1') else title
        header_description = header.find('p').text if header and header.find('p') else ''
        
        # カード情報の抽出
        cards = soup.find_all('div', class_='card')
        topics = [card.find('h2').text for card in cards if card.find('h2')]
        
        # タグの抽出
        tags = []
        tag_elements = soup.find_all('span', class_='tag')
        for tag in tag_elements:
            tag_text = tag.text.strip()
            if tag_text and tag_text not in tags:
                tags.append(tag_text)
        
        # ファイル情報
        file_size = os.path.getsize(file_path) / 1024  # KB
        mod_time = os.path.getmtime(file_path)
        
        return {
            'title': title,
            'header_title': header_title,
            'header_description': header_description,
            'topics': topics[:3],  # 最初の3つのトピックのみ
            'tags': tags[:5],      # 最初の5つのタグのみ
            'path': file_path,
            'size': f"{file_size:.1f}KB",
            'modified': datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M'),
            'emoji': extract_emoji(header_title) or '📄'
        }

def extract_emoji(text):
    """
    文字列から最初の絵文字を抽出
    """
    if not text:
        return None
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    emojis = emoji_pattern.findall(text)
    return emojis[0] if emojis else None

def generate_index_html(html_files_info):
    """
    抽出した情報からリッチなindex.htmlを生成する
    """
    html_content = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Document Library</title>
<style>
  body {
    font-family: system-ui, -apple-system, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    background: #f8fafc;
    padding: 2rem;
  }
  .container {
    background: white;
    border-radius: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }
  .header {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    color: white;
    padding: 2rem;
  }
  .content {
    padding: 2rem;
  }
  .card {
    background: #f1f5f9;
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
    border: 1px solid #e2e8f0;
  }
  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  .card-header {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
  }
  .card-emoji {
    font-size: 2rem;
    margin-right: 1rem;
    background: white;
    width: 3rem;
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.75rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
  .card-title {
    flex-grow: 1;
  }
  .card h2 {
    margin: 0;
    color: #1e293b;
    font-size: 1.25rem;
  }
  .card-meta {
    font-size: 0.875rem;
    color: #64748b;
    margin-top: 0.25rem;
  }
  .description {
    color: #475569;
    margin: 0.5rem 0;
    line-height: 1.6;
  }
  .topics {
    margin: 1rem 0;
    color: #475569;
    font-size: 0.875rem;
  }
  .topic {
    display: inline-block;
    margin-right: 1rem;
  }
  .topic::before {
    content: "•";
    margin-right: 0.5rem;
    color: #3b82f6;
  }
  a {
    text-decoration: none;
    color: #1d4ed8;
  }
  a:hover {
    text-decoration: underline;
  }
  .tag-group {
    margin-top: 1rem;
  }
  .tag {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    background: #e0e7ff;
    color: #1d4ed8;
    font-size: 0.75rem;
    margin: 0.3rem;
    transition: all 0.2s ease;
  }
  .tag:hover {
    background: #1d4ed8;
    color: white;
  }
  .stats {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e2e8f0;
    font-size: 0.875rem;
    color: #64748b;
  }
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📚 Document Library</h1>
      <p>Technical Documentation & Guides</p>
    </div>
    
    <div class="content">
'''
    
    # 記事の内容を追加
    for info in html_files_info:
        topics_html = '\n'.join([f'<span class="topic">{topic}</span>' for topic in info['topics']]) if info['topics'] else ''
        tags_html = '\n'.join([f'<span class="tag">{tag}</span>' for tag in info['tags']]) if info['tags'] else ''
        
        html_content += f'''      <div class="card">
        <div class="card-header">
          <div class="card-emoji">{info['emoji']}</div>
          <div class="card-title">
            <h2><a href="{info['path']}">{info['header_title']}</a></h2>
            <div class="card-meta">{info['path']} • {info['modified']}</div>
          </div>
        </div>
        <p class="description">{info['header_description']}</p>
        <div class="topics">{topics_html}</div>
        <div class="tag-group">{tags_html}</div>
        <div class="stats">
          <span>📏 {info['size']}</span>
          <span>📝 {len(info['topics'])} sections</span>
          <span>🏷 {len(info['tags'])} tags</span>
        </div>
      </div>
'''
    
    # HTMLを閉じる
    html_content += '''    </div>
  </div>
</body>
</html>'''
    
    return html_content

def main():
    # カレントディレクトリ内のすべてのHTMLファイルを取得
    html_files = glob.glob('**/*.html', recursive=True)
    
    # index.htmlは除外
    html_files = [f for f in html_files if not f.endswith('index.html')]
    
    # 各HTMLファイルの情報を抽出
    files_info = []
    for file_path in html_files:
        try:
            info = extract_html_info(file_path)
            files_info.append(info)
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # index.htmlを生成
    index_content = generate_index_html(files_info)
    
    # index.htmlをルートディレクトリに保存
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)

if __name__ == "__main__":
    main()