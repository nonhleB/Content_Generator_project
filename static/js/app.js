// ========================
// CONTENTGEN AI — APP LOGIC
// ========================

const App = {
    // State
    currentType: 'blog',
    currentTemplate: '',
    currentContent: '',
    currentPrompt: '',
    promptLibrary: {},

    // DOM Elements
    elements: {},

    init() {
        this.cacheElements();
        this.bindEvents();
        this.loadPrompts();
        this.renderPromptLibrary();
    },

    cacheElements() {
        this.elements = {
            typeGrid: document.getElementById('typeGrid'),
            templateSelect: document.getElementById('templateSelect'),
            templateInfo: document.getElementById('templateInfo'),
            topicInput: document.getElementById('topicInput'),
            paramsGroup: document.getElementById('paramsGroup'),
            paramsGrid: document.getElementById('paramsGrid'),
            generateBtn: document.getElementById('generateBtn'),
            btnLoader: document.getElementById('btnLoader'),
            outputContent: document.getElementById('outputContent'),
            outputFooter: document.getElementById('outputFooter'),
            wordCount: document.getElementById('wordCount'),
            charCount: document.getElementById('charCount'),
            genTime: document.getElementById('genTime'),
            copyBtn: document.getElementById('copyBtn'),
            downloadBtn: document.getElementById('downloadBtn'),
            promptsGrid: document.getElementById('promptsGrid'),
            toast: document.getElementById('toast'),
            tabBtns: document.querySelectorAll('.tab-btn'),
        };
    },

    bindEvents() {
        // Type selection
        this.elements.typeGrid.addEventListener('click', (e) => {
            const btn = e.target.closest('.type-btn');
            if (btn) {
                this.selectType(btn.dataset.type);
            }
        });

        // Template selection
        this.elements.templateSelect.addEventListener('change', (e) => {
            this.selectTemplate(e.target.value);
        });

        // Generate
        this.elements.generateBtn.addEventListener('click', () => {
            this.generateContent();
        });

        // Copy
        this.elements.copyBtn.addEventListener('click', () => {
            this.copyToClipboard();
        });

        // Download
        this.elements.downloadBtn.addEventListener('click', () => {
            this.downloadContent();
        });

        // Tabs
        this.elements.tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTab(btn.dataset.tab);
            });
        });

        // Nav scroll spy
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                }
            });
        });
    },

    async loadPrompts() {
        try {
            const response = await fetch('/api/prompts');
            this.promptLibrary = await response.json();
            this.populateTemplates();
        } catch (error) {
            console.error('Failed to load prompts:', error);
        }
    },

    selectType(type) {
        this.currentType = type;

        // Update UI
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === type);
        });

        // Populate templates
        this.populateTemplates();

        // Reset template
        this.elements.templateSelect.value = '';
        this.elements.templateInfo.classList.remove('show');
        this.elements.paramsGroup.classList.remove('show');
    },

    populateTemplates() {
        const typeData = this.promptLibrary[this.currentType];
        if (!typeData) return;

        const select = this.elements.templateSelect;
        select.innerHTML = '<option value="">Select a template...</option>';

        typeData.templates.forEach((template, index) => {
            const option = document.createElement('option');
            option.value = this.getTemplateKey(this.currentType, index);
            option.textContent = template.title;
            select.appendChild(option);
        });
    },

    getTemplateKey(type, index) {
        const keys = {
            blog: ['howto', 'listicle', 'analysis'],
            email: ['cold', 'followup', 'newsletter'],
            social: ['linkedin', 'twitter', 'instagram'],
            code: ['function', 'api', 'sql'],
            marketing: ['product', 'landing', 'ad']
        };
        return keys[type]?.[index] || '';
    },

    getTemplateIndex(type, key) {
        const keys = {
            blog: ['howto', 'listicle', 'analysis'],
            email: ['cold', 'followup', 'newsletter'],
            social: ['linkedin', 'twitter', 'instagram'],
            code: ['function', 'api', 'sql'],
            marketing: ['product', 'landing', 'ad']
        };
        return keys[type]?.indexOf(key) ?? 0;
    },

    selectTemplate(templateKey) {
        this.currentTemplate = templateKey;

        const typeData = this.promptLibrary[this.currentType];
        if (!typeData || !templateKey) {
            this.elements.templateInfo.classList.remove('show');
            this.elements.paramsGroup.classList.remove('show');
            return;
        }

        const index = this.getTemplateIndex(this.currentType, templateKey);
        const template = typeData.templates[index];

        if (template) {
            // Show template info
            this.elements.templateInfo.innerHTML = `
                <strong>${template.title}</strong><br>
                ${typeData.description}
            `;
            this.elements.templateInfo.classList.add('show');

            // Show and populate params
            this.renderParams(template.defaults || {});
            this.elements.paramsGroup.classList.add('show');
        }
    },

    renderParams(defaults) {
        const grid = this.elements.paramsGrid;
        grid.innerHTML = '';

        const paramConfigs = {
            tone: { label: 'Tone', type: 'select', options: ['professional', 'casual', 'friendly', 'formal', 'persuasive', 'analytical'] },
            audience: { label: 'Audience', type: 'text', placeholder: 'e.g., beginners, executives' },
            word_count: { label: 'Word Count', type: 'select', options: ['500', '800', '1000', '1200', '1500'] },
            language: { label: 'Language', type: 'select', options: ['Python', 'JavaScript', 'Java', 'Go', 'Rust', 'PostgreSQL', 'MySQL'] }
        };

        Object.entries(defaults).forEach(([key, defaultValue]) => {
            const config = paramConfigs[key] || { label: key, type: 'text' };

            const field = document.createElement('div');
            field.className = 'param-field';

            if (config.type === 'select') {
                field.innerHTML = `
                    <label>${config.label}</label>
                    <select id="param-${key}">
                        ${config.options.map(opt => 
                            `<option value="${opt}" ${opt === defaultValue ? 'selected' : ''}>${opt}</option>`
                        ).join('')}
                    </select>
                `;
            } else {
                field.innerHTML = `
                    <label>${config.label}</label>
                    <input type="text" id="param-${key}" value="${defaultValue}" placeholder="${config.placeholder || ''}">
                `;
            }

            grid.appendChild(field);
        });
    },

    async generateContent() {
        const topic = this.elements.topicInput.value.trim();

        if (!topic) {
            this.showToast('Please enter a topic', 'error');
            this.elements.topicInput.focus();
            return;
        }

        if (!this.currentTemplate) {
            this.showToast('Please select a template', 'error');
            return;
        }

        // Show loading
        this.elements.generateBtn.classList.add('loading');
        this.elements.generateBtn.disabled = true;

        // Collect params
        const params = {};
        this.elements.paramsGrid.querySelectorAll('input, select').forEach(el => {
            const key = el.id.replace('param-', '');
            params[key] = el.value;
        });

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: this.currentType,
                    topic: topic,
                    template: this.currentTemplate,
                    params: params
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentContent = data.content;
                this.currentPrompt = this.buildPromptDisplay(topic, params);
                this.displayContent(data);
                this.showToast('Content generated successfully!');
            } else {
                this.showToast(data.error || 'Generation failed', 'error');
            }
        } catch (error) {
            console.error('Generation error:', error);
            this.showToast('Network error. Please try again.', 'error');
        } finally {
            this.elements.generateBtn.classList.remove('loading');
            this.elements.generateBtn.disabled = false;
        }
    },

    buildPromptDisplay(topic, params) {
        const typeData = this.promptLibrary[this.currentType];
        const index = this.getTemplateIndex(this.currentType, this.currentTemplate);
        const template = typeData?.templates[index];

        if (!template) return '';

        let prompt = template.prompt;
        prompt = prompt.replace('{topic}', topic);
        Object.entries(params).forEach(([key, value]) => {
            prompt = prompt.replace(`{${key}}`, value);
        });

        return prompt;
    },

    displayContent(data) {
        // Update metadata
        this.elements.wordCount.textContent = `${data.metadata.word_count} words`;
        this.elements.charCount.textContent = `${data.metadata.char_count} chars`;
        this.elements.genTime.textContent = `Generated ${new Date(data.timestamp).toLocaleTimeString()}`;
        this.elements.outputFooter.style.display = 'block';

        // Default to preview tab
        this.switchTab('preview');
        this.renderPreview();
    },

    switchTab(tab) {
        // Update tab buttons
        this.elements.tabBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });

        // Render content based on tab
        const container = this.elements.outputContent;

        switch(tab) {
            case 'preview':
                this.renderPreview();
                break;
            case 'markdown':
                this.renderMarkdown();
                break;
            case 'prompt':
                this.renderPrompt();
                break;
        }
    },

    renderPreview() {
        if (!this.currentContent) return;

        const container = this.elements.outputContent;
        container.innerHTML = `<div class="content-preview">${marked.parse(this.currentContent)}</div>`;

        // Highlight code blocks
        container.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    },

    renderMarkdown() {
        if (!this.currentContent) return;

        const container = this.elements.outputContent;
        container.innerHTML = `<pre class="markdown-raw">${this.escapeHtml(this.currentContent)}</pre>`;
    },

    renderPrompt() {
        if (!this.currentPrompt) return;

        const container = this.elements.outputContent;
        container.innerHTML = `
            <div class="prompt-view">
                <span class="prompt-label">Engineered Prompt</span>
                ${this.escapeHtml(this.currentPrompt)}
            </div>
        `;
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    copyToClipboard() {
        if (!this.currentContent) return;

        navigator.clipboard.writeText(this.currentContent).then(() => {
            this.showToast('Copied to clipboard!');
        }).catch(() => {
            this.showToast('Failed to copy', 'error');
        });
    },

    downloadContent() {
        if (!this.currentContent) return;

        const blob = new Blob([this.currentContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `content-${this.currentType}-${Date.now()}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('Downloaded!');
    },

    showToast(message, type = 'success') {
        const toast = this.elements.toast;
        toast.querySelector('.toast-message').textContent = message;
        toast.querySelector('.toast-icon').textContent = type === 'error' ? '❌' : '✅';
        toast.style.borderColor = type === 'error' ? 'var(--danger)' : 'var(--success)';

        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    },

    renderPromptLibrary() {
        const grid = this.elements.promptsGrid;
        if (!grid) return;

        // Wait for prompts to load
        const render = () => {
            if (Object.keys(this.promptLibrary).length === 0) {
                setTimeout(render, 100);
                return;
            }

            grid.innerHTML = '';

            const icons = {
                blog: '📝',
                email: '📧',
                social: '📱',
                code: '💻',
                marketing: '📢'
            };

            Object.entries(this.promptLibrary).forEach(([key, data]) => {
                const card = document.createElement('div');
                card.className = 'prompt-card';

                const templatesHtml = data.templates.map(t => `
                    <div class="prompt-template-item">
                        <div class="prompt-template-name">${t.title}</div>
                        <div class="prompt-template-text">${t.prompt.substring(0, 120)}...</div>
                    </div>
                `).join('');

                card.innerHTML = `
                    <div class="prompt-card-header">
                        <span class="prompt-card-icon">${icons[key] || '📄'}</span>
                        <h3 class="prompt-card-title">${data.name}</h3>
                    </div>
                    <p class="prompt-card-desc">${data.description}</p>
                    <div class="prompt-card-templates">
                        ${templatesHtml}
                    </div>
                `;

                grid.appendChild(card);
            });
        };

        render();
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
