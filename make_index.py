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
            'path': os.path.relpath(file_path, 'content')
        }

def generate_index_html(html_files_info):
    """
    抽出した情報からindex.htmlを生成する
    """
    html_content = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>サイトインデックス</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .article {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #eee;
            border-radius: 5px;
        }
        .article h2 {
            margin-top: 0;
        }
        .article p {
            color: #666;
        }
        .article a {
            text-decoration: none;
            color: #0366d6;
        }
        .article a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>コンテンツ一覧</h1>
'''
    
    # 記事の内容を追加
    for info in html_files_info:
        html_content += f'''    <div class="article">
        <h2><a href="{info['path']}">{info['title']}</a></h2>
        <p>{info['description']}</p>
    </div>
'''
    
    # HTMLを閉じる
    html_content += '''</body>
</html>'''
    
    return html_content

def main():
    # contentディレクトリが存在しない場合は作成
    if not os.path.exists('content'):
        os.makedirs('content')
    
    # contentディレクトリ内のすべてのHTMLファイルを取得
    html_files = glob.glob('content/**/*.html', recursive=True)
    
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
    
    # index.htmlを保存
    with open('content/index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)

if __name__ == "__main__":
    main()