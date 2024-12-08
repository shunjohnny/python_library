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
    }

    async init() {
        try {
            // guides.jsonからガイド一覧を取得
            const response = await fetch('/guides/guides.json');
            const data = await response.json();
            this.guides = data.guides;
            
            // ガイドの情報を取得して表示
            await this.loadGuides();
        } catch (error) {
            console.error('ガイドの読み込みに失敗しました:', error);
            document.getElementById('loading').textContent = 'ガイドの読み込みに失敗しました。';
        }
    }

    async loadGuides() {
        const grid = document.getElementById('guides-grid');
        const loading = document.getElementById('loading');

        for (const guide of this.guides) {
            try {
                // HTMLファイルから必要な情報を抽出
                const response = await fetch(`/guides/${guide.path}`);
                const html = await response.text();
                const guideInfo = this.extractGuideInfo(html);
                
                // カードを作成
                const card = this.createGuideCard(guideInfo, guide.path);
                grid.appendChild(card);
            } catch (error) {
                console.error(`${guide.path}の読み込みに失敗:`, error);
            }
        }

        loading.style.display = 'none';
    }

    extractGuideInfo(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // ヘッダー情報を抽出
        const title = doc.querySelector('.header h1')?.textContent || 'No Title';
        const description = doc.querySelector('.header p')?.textContent || 'No Description';
        
        // タグを抽出
        const tags = Array.from(doc.querySelectorAll('.tag'))
            .map(tag => ({
                text: tag.textContent,
                color: tag.classList[1] || 'primary'
            }))
            .slice(0, 3); // 最大3つまで
        
        return { title, description, tags };
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
            <a href="/guides/${path}" class="button">詳しく見る</a>
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