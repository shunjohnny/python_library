import os
from bs4 import BeautifulSoup
import glob

def extract_html_info(file_path):
    """
    HTMLファイルからtitleとdescriptionを抽出する
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        
        title = soup.title.string if soup.title else os.path.basename(file_path)
        description = ''
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
            
        return {
            'title': title,
            'description': description,
            'path': file_path
        }

def generate_index_html(html_files_info):
    """
    抽出した情報からindex.htmlを生成する
    """
    html_content = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>コンテンツ一覧</title>
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
    transition: transform 0.2s ease-in-out;
  }
  .card:hover {
    transform: translateY(-2px);
  }
  .card h2 {
    margin-top: 0;
    color: #1e293b;
  }
  .description {
    color: #475569;
    margin: 0.5rem 0;
    line-height: 1.6;
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
    background: #3b82f6;
    color: white;
    font-size: 0.875rem;
    margin: 0.3rem;
  }
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📚 コンテンツライブラリ</h1>
      <p>ドキュメントとガイド集</p>
    </div>
    
    <div class="content">
'''
    
    # 記事の内容を追加
    for info in html_files_info:
        html_content += f'''      <div class="card">
        <h2><a href="{info['path']}">{info['title']}</a></h2>
        <p class="description">{info['description']}</p>
        <div class="tag-group">
          <span class="tag">Document</span>
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