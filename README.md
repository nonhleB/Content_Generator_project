# ⚡ ContentGen AI

**AI-Powered Content Generator** — A production-ready Flask application for generating multi-format content using prompt engineering techniques. Built as Week 2 project for AI Content Creation & Automation.

## 🎯 Features

- **5 Content Types**: Blog Posts, Emails, Social Media, Code, Marketing Copy
- **15+ Prompt Templates**: Professionally engineered prompts with parameterization
- **Real-time Preview**: Markdown rendering with syntax highlighting
- **Export Options**: Copy to clipboard or download as `.md`
- **Prompt Library**: Browse all templates with their engineering structure
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🏗️ Architecture

```
content-generator/
├── app.py                 # Flask backend + Content Engine
├── templates/
│   └── index.html         # Single-page application UI
├── static/
│   ├── css/
│   │   └── style.css      # Dark theme styling
│   └── js/
│       └── app.js         # Frontend logic
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
└── .gitignore
```

## 🚀 Deploy to Render

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/content-generator.git
git push -u origin main
```

### Step 2: Create Web Service on Render
1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `contentgen-ai`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### Step 3: Deploy
Render will automatically deploy on every git push. Your app will be live at `https://contentgen-ai.onrender.com`.

## 🖥️ Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/content-generator.git
cd content-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open http://localhost:5000
```

## 📚 Prompt Engineering Case Study

### Prompt Structure
Each template follows a structured approach:

1. **Role Definition**: Implicit through tone and audience parameters
2. **Task Specification**: Clear action verbs (Write, Create, Draft)
3. **Format Requirements**: Explicit structure (headings, sections, length)
4. **Constraints**: Word counts, character limits, platform specifics
5. **Examples**: Placeholder patterns for user input

### Iteration Strategy
- **Template 1**: Basic structure with minimal constraints
- **Template 2**: Added specificity with audience targeting
- **Template 3**: Advanced formatting with platform optimization

## 🎓 Learning Outcomes

- ✅ Prompt optimization and refinement
- ✅ AI content generation workflows
- ✅ Content structuring using AI patterns
- ✅ Automation concepts and deployment
- ✅ Individual project ownership

## 📜 License

MIT License — Built for educational purposes.

---

**Week 2 — AI for Content Creation & Automation**  
*Core Competencies: Prompt Optimization, AI Content Generation, Productivity Workflows*
