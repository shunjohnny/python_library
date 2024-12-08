// js/guide-loader.js
class GuideLoader {
    constructor() {
        this.colors = {
            primary: '#3b82f6',
            success: '#22c55e',
            warning: '#eab308',
            secondary: '#6366f1',
            danger: '#ef4444'
        };
        this.basePath = this.getBasePath();
    }

    getBasePath() {
        const path = window.location.pathname;
        const match = path.match(/^\/[^/]+\//);
        return match ? match[0] : '/';
    }

    async init() {
        try {
            // インデックスファイルから利用可能なガイドの一覧を取得
            const guides = await this.scanGuides();
            await this.loadGuides(guides);
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

    async scanGuides() {
        try {
            const indexResponse = await fetch(`${this.basePath}guides/index.json`);
            if (!indexResponse.ok) {
                throw new Error('インデックスファイルの読み込みに失敗しました');
            }
            const index = await indexResponse.json();
            return index.files;
        } catch (error) {
            console.error('インデックススキャンエラー:', error);
            throw error;
        }
    }

    async loadGuides(guides) {
        const grid = document.getElementById('guides-grid');
        const loading = document.getElementById('loading');

        if (guides.length === 0) {
            loading.textContent = 'ガイドが見つかりませんでした。';
            return;
        }

        for (const guide of guides) {
            try {
                const guidePath = `${this.basePath}guides/${guide}`;
                console.log('Loading guide from:', guidePath);

                const response = await fetch(guidePath);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const html = await response.text();
                
                const guideInfo = this.extractGuideInfo(html);
                const card = this.createGuideCard(guideInfo, guide);
                grid.appendChild(card);
            } catch (error) {
                console.error(`${guide}の読み込みエラー:`, error);
                const errorCard = this.createErrorCard(guide, error);
                grid.appendChild(errorCard);
            }
        }

        loading.style.display = 'none';
    }

    extractGuideInfo(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // より柔軟な情報抽出
        const title = this.findContent(doc, [
            '.header h1',
            'h1',
            'title',
            '.container h1'
        ]) || 'Untitled Guide';

        const description = this.findContent(doc, [
            '.header p',
            '.description',
            'meta[name="description"]',
            'h2',
            'p'
        ]) || 'No description available';

        // タグの抽出を試みる
        let tags = this.extractTags(doc);
        
        return { title, description, tags };
    }

    findContent(doc, selectors) {
        for (const selector of selectors) {
            const element = doc.querySelector(selector);
            if (element) {
                return element.content || element.textContent;
            }
        }
        return null;
    }

    extractTags(doc) {
        // 様々なタグ形式に対応
        const tagElements = [
            ...doc.querySelectorAll('.tag'),
            ...doc.querySelectorAll('[data-tag]'),
            ...doc.querySelectorAll('.badge'),
            ...doc.querySelectorAll('.label')
        ];

        if (tagElements.length === 0) {
            // タグが見つからない場合は内容から推測
            return this.generateTagsFromContent(doc);
        }

        return tagElements.slice(0, 3).map(tag => ({
            text: tag.textContent.trim(),
            color: this.getTagColor(tag.className)
        }));
    }

    generateTagsFromContent(doc) {
        const tags = [];
        // h1, h2からキーワードを抽出
        const headers = doc.querySelectorAll('h1, h2');
        const commonKeywords = {
            'python': 'primary',
            'guide': 'info',
            'tutorial': 'success',
            'reference': 'warning',
            'example': 'secondary'
        };

        for (const header of headers) {
            const text = header.textContent.toLowerCase();
            for (const [keyword, color] of Object.entries(commonKeywords)) {
                if (text.includes(keyword)) {
                    tags.push({ text: keyword.charAt(0).toUpperCase() + keyword.slice(1), color });
                    break;
                }
            }
            if (tags.length >= 2) break;
        }

        // 最低1つのタグを保証
        if (tags.length === 0) {
            tags.push({ text: 'Guide', color: 'primary' });
        }

        return tags;
    }

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

document.addEventListener('DOMContentLoaded', () => {
    const loader = new GuideLoader();
    loader.init();
});