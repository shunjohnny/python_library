// js/guide-loader.js
class GuideLoader {
    constructor() {
        this.guides = [];
        this.colors = {
            primary: '#3b82f6',
            success: '#22c55e',
            warning: '#eab308',
            secondary: '#6366f1',
            danger: '#ef4444'
        };
        // GitHub Pagesのベースパスを取得
        this.basePath = this.getBasePath();
    }

    // GitHub PagesのベースパスをURLから取得
    getBasePath() {
        const path = window.location.pathname;
        // リポジトリ名をパスから抽出（例：/repo-name/ or /）
        const match = path.match(/^\/[^/]+\//);
        return match ? match[0] : '/';
    }

    async init() {
        try {
            await this.loadGuides();
        } catch (error) {
            console.error('初期化エラー:', error);
            document.getElementById('loading').innerHTML = `
                <div style="color: #ef4444;">
                    <p>ガイドの読み込みに失敗しました。</p>
                    <p style="font-size: 0.8em; color: #666;">エラー詳細: ${error.message}</p>
                </div>
            `;
        }
    }

    async loadGuides() {
        const grid = document.getElementById('guides-grid');
        const loading = document.getElementById('loading');

        for (const guide of this.guides) {
            try {
                // HTMLファイルのパスを構築
                const guidePath = `${this.basePath}guides/${guide.path}`;
                console.log('Loading guide from:', guidePath);

                // HTMLファイルを取得
                const response = await fetch(guidePath);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const html = await response.text();
                
                // ガイド情報を抽出してカードを作成
                const guideInfo = this.extractGuideInfo(html);
                const card = this.createGuideCard(guideInfo, guide.path);
                grid.appendChild(card);
            } catch (error) {
                console.error(`${guide.path}の読み込みエラー:`, error);
                // エラーカードを表示
                const errorCard = this.createErrorCard(guide.path, error);
                grid.appendChild(errorCard);
            }
        }

        loading.style.display = 'none';
    }

    // エラーカードの作成
    createErrorCard(path, error) {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <h2 style="color: #ef4444;">読み込みエラー</h2>
            <p>ガイド "${path}" の読み込みに失敗しました。</p>
            <p style="font-size: 0.8em; color: #666;">エラー詳細: ${error.message}</p>
        `;
        return card;
    }

    extractGuideInfo(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // ヘッダー情報を抽出（より柔軟な抽出方法）
        const title = 
            doc.querySelector('.header h1')?.textContent || 
            doc.querySelector('h1')?.textContent || 
            'No Title';
        
        const description = 
            doc.querySelector('.header p')?.textContent || 
            doc.querySelector('h2')?.textContent || 
            'No Description';
        
        // タグを抽出（存在しない場合はデフォルトタグを使用）
        let tags = Array.from(doc.querySelectorAll('.tag'))
            .map(tag => ({
                text: tag.textContent,
                color: this.getTagColor(tag.className)
            }))
            .slice(0, 3);

        // タグが見つからない場合はデフォルトタグを設定
        if (tags.length === 0) {
            tags = [{
                text: 'ガイド',
                color: 'primary'
            }];
        }
        
        return { title, description, tags };
    }

    getTagColor(className) {
        const colorClasses = ['primary', 'success', 'warning', 'secondary', 'danger'];
        for (const color of colorClasses) {
            if (className.includes(color)) return color;
        }
        return 'primary';
    }

    createGuideCard(info, path) {
        const card = document.createElement('div');
        card.className = 'card';
        
        const content = `
            <h2>${info.title}</h2>
            <p>${info.description}</p>
            ${info.tags.map(tag => `
                <span class="tag" style="background: ${this.colors[tag.color] || this.colors.primary}">
                    ${tag.text}
                </span>
            `).join('')}
            <a href="${this.basePath}guides/${path}" class="button">詳しく見る</a>
        `;
        
        card.innerHTML = content;
        return card;
    }
}

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    const loader = new GuideLoader();
    loader.init();
});