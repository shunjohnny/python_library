import os
from bs4 import BeautifulSoup
import glob
from datetime import datetime
import shutil

def generate_sidebar_html(files_info, current_path=None):
    """
    トグル可能なサイドバーとボタンのHTMLを生成する
    """
    # 現在のファイルがindex.htmlかどうかを判定
    is_index = current_path is None or 'index.html' in current_path

    # サイドバーの項目を生成
    sidebar_items = []
    for info in files_info:
        if is_index:
            # index.htmlからの場合は、contentディレクトリを含むパスを使用
            file_path = f"content/{info['path']}"
        else:
            # content内のhtmlからの場合は、同じディレクトリからの相対パス
            file_path = info['path']
        
        relative_path = file_path.replace('\\', '/')  # Windows対応
        sidebar_items.append(
            f'<a href="{relative_path}" class="sidebar-item">{info["title"]}</a>'
        )

    return f'''
    <button id="sidebarToggle" class="sidebar-toggle">
        <span>📑</span>
    </button>
    <div id="sidebar" class="sidebar">
        <nav class="sidebar-content">
            {os.linesep.join(sidebar_items)}
        </nav>
    </div>
    <script>
        document.getElementById("sidebarToggle").addEventListener("click", function() {{
            const sidebar = document.getElementById("sidebar");
            sidebar.classList.toggle("open");
            this.classList.toggle("active");
        }});
    </script>
    '''

def modify_html_content(html_content, sidebar_content, current_path=None):
    """
    HTMLコンテンツにトグル可能なサイドバーと戻るボタンを追加する
    """
    # 現在のファイルの深さに基づいて相対パスを計算
    depth = len(current_path.split(os.sep)) if current_path else 0
    base_path = '../' * depth  # インデックスは1つ上の階層にある
    index_path = os.path.join(base_path, 'index.html').replace('\\', '/')

    styles = '''
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
        position: relative;
    }
    .sidebar-toggle {
        position: absolute;
        top: 1rem;
        right: 1rem;
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 0.5rem;
        background: white;
        border: 1px solid #e2e8f0;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        z-index: 1001;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .sidebar-toggle:hover {
        background: #f1f5f9;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar-toggle.active {
        background: #f1f5f9;
        transform: translateX(-250px);
    }
    .sidebar {
        position: absolute;
        top: 0;
        right: 0;
        width: 250px;
        height: 100%;
        background: #f1f5f9;
        border-left: 1px solid #e2e8f0;
        padding: 1rem;
        padding-top: 4rem;
        box-sizing: border-box;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        z-index: 1000;
        box-shadow: -2px 0 4px rgba(0, 0, 0, 0.1);
    }
    .sidebar.open {
        transform: translateX(0);
    }
    .sidebar-content {
        height: 100%;
        overflow-y: auto;
    }
    .sidebar-item {
        display: block;
        padding: 0.75rem 1rem;
        color: #475569;
        text-decoration: none;
        transition: all 0.2s ease;
        border-radius: 0.375rem;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
    }
    .sidebar-item:hover {
        background: white;
        color: #1d4ed8;
        transform: translateX(4px);
    }
    .back-button {
        position: absolute;
        top: 1rem;
        left: 1rem;
        height: 2.5rem;
        padding: 0 1rem;
        border-radius: 0.5rem;
        background: white;
        border: 1px solid #e2e8f0;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.95rem;
        z-index: 1001;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        color: #475569;
        text-decoration: none;
    }
    .back-button:hover {
        background: #f1f5f9;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
        color: #1d4ed8;
    }
    .back-button span {
        margin-right: 0.5rem;
    }
    </style>
    '''
    
    back_button = f'''
    <a href="{index_path}" class="back-button">
        <span>←</span> インデックス
    </a>
    '''
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # スタイルを追加
    if soup.head is None:
        soup.html.insert(0, BeautifulSoup('<head></head>', 'html.parser'))
    if soup.head.find('style'):
        soup.head.style.append(styles)
    else:
        soup.head.append(BeautifulSoup(f'<style>{styles}</style>', 'html.parser'))
    
    # サイドバーとボタンを追加
    container_div = soup.find('div', class_='container')
    if container_div:
        # 戻るボタンを追加
        container_div.append(BeautifulSoup(back_button, 'html.parser'))
        # サイドバーを追加
        container_div.append(BeautifulSoup(sidebar_content, 'html.parser'))
    
    return str(soup)

def extract_html_info(file_path):
    """
    HTMLファイルから詳細な情報を抽出する
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        
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
        
        # Modern Guideの文言を削除
        title = title.replace(' Modern Guide', '').strip()
        header_title = header_title.replace(' Modern Guide', '').strip()
        
        return {
            'title': header_title,
            'header_title': header_title,
            'header_description': header_description,
            'topics': topics,
            'tags': tags,
            'path': file_path,
            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M')
        }

def generate_index_html(html_files_info):
    """
    インデックスページのHTMLを生成する
    """
    html_content = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ドキュメントライブラリ</title>
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
        position: relative;
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
        transition: all 0.2s ease;
    }
    .tag:hover {
        background: #1d4ed8;
    }
    .success { background: #22c55e; }
    .warning { background: #eab308; }
    .info { background: #0ea5e9; }
    .danger { background: #ef4444; }
    .primary { background: #6366f1; }
    .sidebar-toggle {
        position: absolute;
        top: 1rem;
        right: 1rem;
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 0.5rem;
        background: white;
        border: 1px solid #e2e8f0;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        z-index: 1001;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .sidebar-toggle:hover {
        background: #f1f5f9;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar-toggle.active {
        background: #f1f5f9;
        transform: translateX(-250px);
    }
    .sidebar {
        position: absolute;
        top: 0;
        right: 0;
        width: 250px;
        height: 100%;
        background: #f1f5f9;
        border-left: 1px solid #e2e8f0;
        padding: 1rem;
        padding-top: 4rem;
        box-sizing: border-box;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        z-index: 1000;
        box-shadow: -2px 0 4px rgba(0, 0, 0, 0.1);
    }
    .sidebar.open {
        transform: translateX(0);
    }
    .sidebar-content {
        height: 100%;
        overflow-y: auto;
    }
    .sidebar-item {
        display: block;
        padding: 0.75rem 1rem;
        color: #475569;
        text-decoration: none;
        transition: all 0.2s ease;
        border-radius: 0.375rem;
        margin-bottom: 0.25rem;
        font-size: 0.95rem;
    }
    .sidebar-item:hover {
        background: white;
        color: #1d4ed8;
        transform: translateX(4px);
    }
</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 ドキュメントライブラリ</h1>
            <p>技術ドキュメント & ガイド</p>
        </div>
        <div class="content">'''

    for info in html_files_info:
        # index.htmlからのリンクなので、contentディレクトリを含める
        link_path = f"content/{info['path']}"
        html_content += f'''
            <div class="card">
                <h2><a href="{link_path}" style="text-decoration: none; color: inherit;">{info['header_title']}</a></h2>
                <div class="card-meta">最終更新: {info['modified']}</div>
                <p class="description">{info['header_description']}</p>
                <div class="tag-group">
                    {''.join(f'<span class="tag">{tag}</span>' for tag in info['tags'][:5])}
                </div>
            </div>'''

    html_content += '''
        </div>'''
    
    # サイドバーを追加（index.htmlからのパスを使用）
    html_content += generate_sidebar_html(html_files_info, 'index.html')
    
    html_content += '''
    </div>
</body>
</html>'''

    return html_content

def main():
    content_dir = 'content'
    build_dir = 'build'
    
    # buildディレクトリをクリーンアップ
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # contentディレクトリを作成（存在しない場合）
    if not os.path.exists(content_dir):
        os.makedirs(content_dir)
    
    # contentディレクトリの内容をコピー
    if os.path.exists(content_dir):
        shutil.copytree(content_dir, os.path.join(build_dir, 'content'), dirs_exist_ok=True)
    
    # HTMLファイルを処理
    html_files = glob.glob(os.path.join(content_dir, '**/*.html'), recursive=True)
    files_info = []
    
    # ファイル情報を収集
    for file_path in html_files:
        if os.path.basename(file_path) != 'index.html':
            try:
                info = extract_html_info(file_path)
                rel_path = os.path.relpath(file_path, content_dir)
                # contentディレクトリプレフィックスを除いたパスを保存
                info['path'] = rel_path
                files_info.append(info)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
    
    # 各HTMLファイルを処理
    for src_path in html_files:
        if os.path.basename(src_path) != 'index.html':
            rel_path = os.path.relpath(src_path, content_dir)
            dest_path = os.path.join(build_dir, 'content', rel_path)
            
            try:
                with open(src_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # サイドバーを追加
                modified_content = modify_html_content(content, generate_sidebar_html(files_info, rel_path), rel_path)
                
                # 処理済みファイルを保存
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, 'w', encoding='utf-8') as file:
                    file.write(modified_content)
                    
            except Exception as e:
                print(f"Error modifying {rel_path}: {str(e)}")
    
    # index.htmlを生成
    index_content = generate_index_html(files_info)
    with open(os.path.join(build_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"\nProcessing complete. Output files are in the '{build_dir}' directory.")

if __name__ == "__main__":
    main()