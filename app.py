import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# ========================
# PROMPT LIBRARY
# ========================
PROMPT_LIBRARY = {
    "blog": {
        "name": "Blog Post Generator",
        "description": "Generate SEO-optimized blog posts on any topic",
        "templates": [
            {
                "title": "How-To Guide",
                "prompt": "Write a comprehensive how-to guide about {topic}. Include: 1) Introduction explaining why this matters, 2) Step-by-step instructions with clear headings, 3) Pro tips and best practices, 4) Common mistakes to avoid, 5) Conclusion with next steps. Tone: {tone}. Target audience: {audience}. Word count: ~{word_count} words.",
                "defaults": {"tone": "professional and friendly", "audience": "beginners", "word_count": "800"}
            },
            {
                "title": "Listicle",
                "prompt": "Create an engaging listicle titled '{topic}: Top [Number] Tips/Strategies'. Include: catchy introduction, numbered items with detailed explanations, real-world examples for each point, and a compelling conclusion. Tone: {tone}. Target: {audience}. Length: ~{word_count} words.",
                "defaults": {"tone": "conversational and energetic", "audience": "general readers", "word_count": "1000"}
            },
            {
                "title": "Industry Analysis",
                "prompt": "Write an in-depth industry analysis about {topic}. Structure: Executive summary, current market landscape, key trends and statistics, major players, future outlook, and actionable insights. Tone: {tone}. Audience: {audience}. Length: ~{word_count} words.",
                "defaults": {"tone": "analytical and authoritative", "audience": "industry professionals", "word_count": "1200"}
            }
        ]
    },
    "email": {
        "name": "Email Composer",
        "description": "Craft professional and persuasive emails",
        "templates": [
            {
                "title": "Cold Outreach",
                "prompt": "Write a compelling cold outreach email for: {topic}. Include: attention-grabbing subject line, personalized opening, clear value proposition, social proof or credibility marker, soft call-to-action, and professional signature. Tone: {tone}. Recipient: {audience}.",
                "defaults": {"tone": "confident but respectful", "audience": "potential client/partner"}
            },
            {
                "title": "Follow-Up",
                "prompt": "Draft a follow-up email regarding: {topic}. Include: reference to previous interaction, gentle reminder of value, address potential objections, clear next steps, and polite closing. Tone: {tone}. Context: {audience}.",
                "defaults": {"tone": "warm and persistent", "audience": "after no response"}
            },
            {
                "title": "Newsletter",
                "prompt": "Create a newsletter about {topic}. Structure: engaging subject line, brief personal greeting, 3-5 key sections with headers, one main CTA, P.S. line for engagement. Tone: {tone}. Audience: {audience}. Length: ~{word_count} words.",
                "defaults": {"tone": "friendly and informative", "audience": "subscribers", "word_count": "500"}
            }
        ]
    },
    "social": {
        "name": "Social Media Content",
        "description": "Generate posts for various social platforms",
        "templates": [
            {
                "title": "LinkedIn Post",
                "prompt": "Write a LinkedIn post about {topic}. Include: hook in first 2 lines, personal story or insight, actionable takeaway, 3-5 relevant hashtags, and engagement question. Tone: {tone}. Audience: {audience}.",
                "defaults": {"tone": "professional and insightful", "audience": "industry professionals"}
            },
            {
                "title": "Twitter/X Thread",
                "prompt": "Create a Twitter/X thread about {topic}. Structure: 5-8 tweets, first tweet is a hook, each tweet is under 280 characters, include 1-2 key hashtags, end with engagement question or CTA. Tone: {tone}. Audience: {audience}.",
                "defaults": {"tone": "concise and punchy", "audience": "tech/business audience"}
            },
            {
                "title": "Instagram Caption",
                "prompt": "Write an Instagram caption for content about {topic}. Include: engaging hook, storytelling element, emoji usage (moderate), 10-15 relevant hashtags, and CTA. Tone: {tone}. Audience: {audience}.",
                "defaults": {"tone": "casual and authentic", "audience": "lifestyle/followers"}
            }
        ]
    },
    "code": {
        "name": "Code Generator",
        "description": "Generate code snippets and documentation",
        "templates": [
            {
                "title": "Function/Method",
                "prompt": "Write a {language} function that {topic}. Requirements: clean code with docstring, input validation, error handling, example usage, and comments explaining logic. Follow {language} best practices.",
                "defaults": {"language": "Python"}
            },
            {
                "title": "API Endpoint",
                "prompt": "Create a {language} API endpoint for: {topic}. Include: route definition, request/response models, validation, error responses, authentication consideration, and example requests.",
                "defaults": {"language": "Python (FastAPI/Flask)"}
            },
            {
                "title": "SQL Query",
                "prompt": "Write a SQL query for: {topic}. Include: optimized query, explanation of joins/indexes used, handling of edge cases, and sample output. Database: {language}.",
                "defaults": {"language": "PostgreSQL"}
            }
        ]
    },
    "marketing": {
        "name": "Marketing Copy",
        "description": "Create compelling marketing materials",
        "templates": [
            {
                "title": "Product Description",
                "prompt": "Write a product description for: {topic}. Include: headline with benefit, problem statement, solution overview, 3-5 key features with benefits, social proof placeholder, and strong CTA. Tone: {tone}. Audience: {audience}.",
                "defaults": {"tone": "persuasive and benefit-driven", "audience": "potential buyers"}
            },
            {
                "title": "Landing Page Copy",
                "prompt": "Create landing page copy for: {topic}. Sections needed: Hero headline + subheadline, problem agitation, solution presentation, 3 benefit blocks, testimonial placeholder, FAQ (3 questions), and CTA section. Tone: {tone}. Audience: {audience}.",
                "defaults": {"tone": "bold and conversion-focused", "audience": "target customers"}
            },
            {
                "title": "Ad Copy",
                "prompt": "Write ad copy for: {topic}. Create 3 variations: 1) Short (under 50 words), 2) Medium (under 100 words), 3) Long-form (under 150 words). Each should include hook, benefit, urgency element, and CTA. Platform: {audience}. Tone: {tone}.",
                "defaults": {"tone": "urgent and compelling", "audience": "Facebook/Google Ads"}
            }
        ]
    }
}

# ========================
# AI CONTENT GENERATION ENGINE
# ========================
class ContentEngine:
    """Simulates AI content generation with structured, high-quality outputs"""

    BLOG_INTROS = [
        "In today's rapidly evolving landscape, understanding {topic} has become more crucial than ever. Whether you're just starting out or looking to refine your approach, this comprehensive guide will walk you through everything you need to know.",
        "Have you ever wondered what separates the pros from the amateurs when it comes to {topic}? The answer might surprise you. In this deep dive, we'll explore the strategies, tools, and insights that can transform your approach.",
        "The world of {topic} is changing faster than most people realize. New trends emerge daily, and what worked yesterday might not work tomorrow. Here's your roadmap to staying ahead of the curve."
    ]

    BLOG_BODY = [
        "## Understanding the Fundamentals\n\nBefore diving into advanced strategies, it's essential to grasp the core concepts. {topic} isn't just about surface-level knowledge—it's about building a foundation that supports long-term success. Start by identifying your primary objectives and mapping out a clear path to achieve them.\n\n### Key Principles to Remember\n\n1. **Consistency is King**: Regular engagement with {topic} yields compound results over time.\n2. **Data-Driven Decisions**: Let metrics guide your strategy, not assumptions.\n3. **Adaptability**: The ability to pivot based on feedback separates leaders from followers.\n\n## Step-by-Step Implementation\n\n### Step 1: Research and Planning\nBegin by conducting thorough research on {topic}. Use tools like Google Trends, industry reports, and competitor analysis to identify gaps and opportunities. Create a content calendar or project roadmap that aligns with your goals.\n\n### Step 2: Execution with Precision\nThis is where theory meets practice. Apply your research systematically, documenting each step. Don't rush the process—quality always trumps speed. Test different approaches and measure results meticulously.\n\n### Step 3: Optimization and Iteration\nReview your outcomes against your initial KPIs. What worked? What didn't? Use these insights to refine your approach. Remember, iteration is not failure—it's the engine of improvement.",
        "## The Current State of {topic}\n\nRecent developments have fundamentally shifted how we approach {topic}. Industry data shows a 40% increase in adoption over the past year, with early adopters reporting significant ROI improvements.\n\n### Market Trends\n\n- **Automation Integration**: 73% of successful implementations now leverage automated workflows\n- **Personalization at Scale**: Customized approaches are no longer optional—they're expected\n- **Cross-Platform Synergy**: The most effective strategies span multiple channels seamlessly\n\n## Practical Strategies\n\n### Strategy 1: The Foundation Method\nStart with the basics. Build a solid infrastructure before adding complexity. This means investing in the right tools, training your team, and establishing clear SOPs.\n\n### Strategy 2: The Agile Approach\nImplement in sprints. Test small, learn fast, and scale what works. This minimizes risk while maximizing learning velocity.\n\n### Strategy 3: The Ecosystem Play\nDon't operate in isolation. Connect {topic} with complementary areas to create a multiplier effect. Integration is where the magic happens."
    ]

    BLOG_CONCLUSIONS = [
        "## Wrapping Up\n\nMastering {topic} is a journey, not a destination. The strategies outlined in this guide provide a solid starting point, but the real growth happens through consistent application and continuous learning.\n\n**Your Next Steps:**\n1. Choose ONE strategy from this guide to implement this week\n2. Set measurable goals for the next 30 days\n3. Join communities focused on {topic} for ongoing support\n\nRemember: The best time to start was yesterday. The second best time is now. What will your first step be?",
        "## Final Thoughts\n\nAs we've explored, {topic} offers tremendous opportunities for those willing to invest the time and effort. The landscape will continue evolving, but the fundamentals remain constant: provide value, stay authentic, and never stop learning.\n\n**Quick Action Plan:**\n- Bookmark this guide for reference\n- Share it with someone who needs to see it\n- Drop a comment below with your biggest takeaway\n\nHere's to your success with {topic}! 🚀"
    ]

    EMAIL_TEMPLATES = {
        "cold": """**Subject Line:** Quick question about {topic}

Hi [Name],

I hope this message finds you well. I came across your work in {topic} and was genuinely impressed by [specific detail].

I'm reaching out because I believe there's a significant opportunity for us to collaborate on {topic}-related initiatives. Specifically, I've helped similar organizations achieve [specific result] through [approach].

Would you be open to a brief 15-minute call next week to explore how this might work for [their company]?

Best regards,  
[Your Name]

P.S. I recently published a case study on {topic} that might interest you—happy to share if helpful.""",

        "followup": """**Subject Line:** Following up: {topic}

Hi [Name],

I wanted to circle back on my previous message regarding {topic}. I understand you're likely juggling multiple priorities, so I'll keep this brief.

The reason I'm particularly keen to connect is [specific value proposition]. In the past month alone, we've seen [relevant metric] for clients in similar situations.

If timing isn't right now, no worries at all—just let me know if I should check back in a few weeks.

Best,  
[Your Name]""",

        "newsletter": """**Subject Line:** This week in {topic}: What you need to know

Hey [First Name],

Welcome to this week's edition! Let's dive into what's happening in {topic}.

**🔥 Top Story**  
[Headline about {topic} development]  
[2-3 sentence summary with key insight]

**📊 By the Numbers**  
- Stat 1: [Relevant metric]  
- Stat 2: [Relevant metric]  
- Stat 3: [Relevant metric]

**💡 Pro Tip**  
[Actionable advice related to {topic}]

**🔗 Worth Your Time**  
[Link to valuable resource]

That's all for this week! Hit reply and let me know what you think—I'd love to hear from you.

Cheers,  
[Your Name]

P.S. [Engagement hook or bonus tip]"""
    }

    SOCIAL_TEMPLATES = {
        "linkedin": """🚀 {topic} is changing the game, and here's what most people miss:

[Personal insight or story about {topic}]

The difference between those who succeed and those who don't? It's not talent—it's consistency and willingness to adapt.

3 things I've learned:
1. [Key lesson]
2. [Key lesson]  
3. [Key lesson]

What's your experience with {topic}? Drop a comment below 👇

#{hashtag} #ProfessionalGrowth #Leadership""",

        "twitter": """🧵 Thread: {topic}

Most people get {topic} wrong. Here's the real framework:

1/ [Hook tweet]

2/ [Core insight]

3/ [Supporting point]

4/ [Practical application]

5/ [Common mistake to avoid]

6/ [Key takeaway]

7/ [Call to action/engagement question]

Follow for more threads like this. RT if you found value! 🔄""",

        "instagram": """✨ {topic} unlocked 🔓

Swipe to see the transformation →

[Story element about {topic}]

Drop a 💯 if you agree!

.
.
.
#{hashtag} #growthmindset #success #motivation #entrepreneur #hustle #goals #inspiration"""
    }

    CODE_TEMPLATES = {
        "function": """def {func_name}(data):
    \"\"\"
    Process and analyze data for {topic}.

    Args:
        data: Input data to process (dict or list)

    Returns:
        dict: Processed result with metadata

    Raises:
        ValueError: If input validation fails
        TypeError: If data type is unsupported

    Example:
        >>> sample = {{"id": 1, "value": "test"}}
        >>> result = {func_name}(sample)
        >>> print(result["status"])
        'success'
    \"\"\"
    # Input validation
    if not data:
        raise ValueError("Input data cannot be empty")

    if not isinstance(data, (dict, list)):
        raise TypeError(f"Expected dict or list, got {{type(data).__name__}}")

    try:
        # Core processing logic for {topic}
        processed = {{
            "input_size": len(data),
            "processed_at": datetime.now().isoformat(),
            "topic": "{topic}",
            "result": process_core(data)
        }}

        # Post-processing and enrichment
        return enrich_output(processed)

    except Exception as e:
        logger.error(f"Error in {func_name}: {{str(e)}}")
        raise RuntimeError(f"Processing failed: {{str(e)}}") from e


def process_core(data):
    \"\"\"Core business logic for {topic}.\"\"\"
    # TODO: Implement specific logic
    return {{"status": "processed", "data": data}}


def enrich_output(result):
    \"\"\"Add metadata and format output.\"\"\"
    result["version"] = "1.0.0"
    result["metadata"] = {{
        "engine": "content-processor",
        "optimized": True
    }}
    return result


# Example usage and testing
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Test case 1: Valid input
    sample_input = {{"key": "value", "topic": "{topic}"}}
    try:
        output = {func_name}(sample_input)
        print(f"✅ Success: {{output}}")
    except Exception as e:
        print(f"❌ Error: {{e}}")

    # Test case 2: Empty input (should raise ValueError)
    try:
        {func_name}({{}})
    except ValueError as e:
        print(f"✅ Caught expected error: {{e}}")""",

        "api": """from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

app = FastAPI(
    title="{topic} API",
    description="RESTful API for managing {topic} resources",
    version="1.0.0"
)

# ====================
# DATA MODELS
# ====================

class {model_name}Base(BaseModel):
    \"\"\"Base schema for {topic}.\"\"\"
    name: str = Field(..., min_length=1, max_length=100, description="Resource name")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description")
    status: str = Field(default="active", pattern="^(active|inactive|pending)$")
    priority: int = Field(default=1, ge=1, le=5, description="Priority level 1-5")

class {model_name}Create({model_name}Base):
    \"\"\"Schema for creating a new {topic}.\"\"\"
    pass

class {model_name}({model_name}Base):
    \"\"\"Full schema with system-generated fields.\"\"\"
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ====================
# MOCK DATABASE
# ====================

_db = {{}}
_counter = 1

# ====================
# API ENDPOINTS
# ====================

@app.post("/api/v1/{endpoint}", response_model={model_name}, status_code=201)
async def create_{endpoint}(item: {model_name}Create):
    \"\"\"
    Create a new {topic} resource.

    Args:
        item: {model_name} object with required fields

    Returns:
        Created {model_name} object with generated ID and timestamps

    Raises:
        HTTPException: If validation fails or resource already exists
    \"\"\"
    global _counter

    # Check for duplicates
    for existing in _db.values():
        if existing["name"] == item.name:
            raise HTTPException(
                status_code=409, 
                detail=f"Resource with name '{{item.name}}' already exists"
            )

    # Create resource
    new_item = {{
        "id": _counter,
        **item.model_dump(),
        "created_at": datetime.now(),
        "updated_at": None
    }}
    _db[_counter] = new_item
    _counter += 1

    return {model_name}(**new_item)


@app.get("/api/v1/{endpoint}/{{item_id}}", response_model={model_name})
async def get_{endpoint}(item_id: int):
    \"\"\"
    Retrieve a {topic} resource by ID.

    Args:
        item_id: Unique identifier of the resource

    Returns:
        {model_name} object if found

    Raises:
        HTTPException: 404 if resource not found
    \"\"\"
    if item_id not in _db:
        raise HTTPException(
            status_code=404, 
            detail=f"{topic} with id {{item_id}} not found"
        )
    return {model_name}(**_db[item_id])


@app.get("/api/v1/{endpoint}", response_model=List[{model_name}])
async def list_{endpoint}(
    status: Optional[str] = None,
    priority: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    \"\"\"
    List all {topic} resources with optional filtering.

    Query Parameters:
        status: Filter by status (active/inactive/pending)
        priority: Filter by priority level (1-5)
        skip: Number of items to skip (pagination)
        limit: Maximum items to return (max 100)
    \"\"\"
    results = list(_db.values())

    if status:
        results = [r for r in results if r["status"] == status]
    if priority:
        results = [r for r in results if r["priority"] == priority]

    return [{model_name}(**r) for r in results[skip:skip + limit]]


@app.put("/api/v1/{endpoint}/{{item_id}}", response_model={model_name})
async def update_{endpoint}(item_id: int, item: {model_name}Create):
    \"\"\"Update an existing {topic} resource.\"\"\"
    if item_id not in _db:
        raise HTTPException(status_code=404, detail="Not found")

    _db[item_id].update({{**item.model_dump(), "updated_at": datetime.now()}})
    return {model_name}(**_db[item_id])


@app.delete("/api/v1/{endpoint}/{{item_id}}")
async def delete_{endpoint}(item_id: int):
    \"\"\"Delete a {topic} resource.\"\"\"
    if item_id not in _db:
        raise HTTPException(status_code=404, detail="Not found")

    del _db[item_id]
    return {{"message": f"{topic} {{item_id}} deleted successfully"}}


# Health check
@app.get("/health")
async def health_check():
    return {{"status": "healthy", "service": "{topic}-api", "timestamp": datetime.now()}}""",

        "sql": """-- =====================================================
-- Optimized Query for: {topic}
-- Expected execution time: < 100ms with proper indexing
-- Author: Content Generator
-- =====================================================

WITH ranked_{table_name} AS (
    SELECT 
        t.id,
        t.name,
        t.category,
        t.status,
        t.created_at,
        t.priority,
        COUNT(DISTINCT r.id) AS related_count,
        ARRAY_AGG(DISTINCT r.tag) FILTER (WHERE r.tag IS NOT NULL) AS tags,
        ROW_NUMBER() OVER (
            PARTITION BY t.category 
            ORDER BY t.priority DESC, t.created_at DESC
        ) AS category_rank
    FROM {table_name} t
    LEFT JOIN related_entities r 
        ON t.id = r.parent_id 
        AND r.is_active = TRUE
    WHERE t.status = 'active'
        AND t.created_at >= CURRENT_DATE - INTERVAL '30 days'
        AND (t.priority >= 3 OR t.featured = TRUE)
    GROUP BY 
        t.id, t.name, t.category, t.status, 
        t.created_at, t.priority
    HAVING COUNT(DISTINCT r.id) >= 1
),
aggregated_stats AS (
    SELECT 
        category,
        COUNT(*) AS total_items,
        AVG(related_count) AS avg_related,
        MAX(created_at) AS latest_update
    FROM ranked_{table_name}
    GROUP BY category
)
SELECT 
    r.id,
    r.name,
    r.category,
    r.priority,
    r.related_count,
    r.tags,
    r.created_at,
    s.total_items AS category_total,
    s.avg_related AS category_avg
FROM ranked_{table_name} r
JOIN aggregated_stats s ON r.category = s.category
WHERE r.category_rank <= 10
ORDER BY 
    r.priority DESC,
    r.related_count DESC,
    r.created_at DESC;

-- =====================================================
-- RECOMMENDED INDEXES
-- =====================================================

-- Composite index for the main filter conditions
CREATE INDEX CONCURRENTLY idx_{table_name}_status_created 
    ON {table_name}(status, created_at) 
    WHERE status = 'active';

-- Partial index for featured/priority items
CREATE INDEX CONCURRENTLY idx_{table_name}_featured_priority 
    ON {table_name}(category, priority DESC, created_at DESC) 
    WHERE featured = TRUE OR priority >= 3;

-- Foreign key index for joins
CREATE INDEX CONCURRENTLY idx_related_parent_active 
    ON related_entities(parent_id, is_active) 
    WHERE is_active = TRUE;

-- GIN index for array/tag searches (if using PostgreSQL)
CREATE INDEX CONCURRENTLY idx_related_tags_gin 
    ON related_entities USING GIN(tags);

-- =====================================================
-- EXPLAIN ANALYZE TIPS
-- =====================================================
-- Run: EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) <query>
-- Look for: Seq Scan -> Index Scan transformations
-- Target: Index Only Scans where possible"""
    }

    MARKETING_TEMPLATES = {
        "product": """# {topic}

## The Problem
[Describe the pain point that {topic} solves. Be specific about the daily frustrations your target audience faces.]

## The Solution
Introducing [Product Name]—the smarter way to handle {topic}. Built for [target audience] who demand results without the complexity.

### Key Features

✅ **Feature One** — [Benefit-focused description. Not what it does, but what it enables.]  
✅ **Feature Two** — [Benefit-focused description]  
✅ **Feature Three** — [Benefit-focused description]  
✅ **Feature Four** — [Benefit-focused description]  
✅ **Feature Five** — [Benefit-focused description]

### What Our Users Say
> "[Testimonial placeholder—real social proof drives conversions. Include specific metrics if possible.]"
> — [Name], [Title], [Company]

### Ready to Transform Your {topic}?
[Strong CTA button text: e.g., "Start Your Free Trial"]

✓ No credit card required  
✓ 14-day free trial  
✓ Cancel anytime

[CTA Button]""",

        "landing": """# Hero Section
## [Headline: Main benefit of {topic} in 8 words or less]
### [Subheadline: How you deliver it + social proof element]

[CTA Button: Primary action - e.g., "Get Started Free"]

---

# Problem Section
## Still struggling with {topic}?
[Agitate the problem with 3 specific pain points that resonate emotionally]

---

# Solution Section
## There's a better way
[Introduce your solution to {topic} with a clear value proposition]

### Benefit Block 1
**[Benefit Title]**  
[Description with specific outcome and metric]

### Benefit Block 2
**[Benefit Title]**  
[Description with specific outcome and metric]

### Benefit Block 3
**[Benefit Title]**  
[Description with specific outcome and metric]

---

# Social Proof
## Trusted by [number]+ professionals worldwide
[Testimonial carousel placeholder - include photos, names, and specific results]

---

# FAQ
**Q: How quickly can I see results with {topic}?**  
A: Most users see measurable improvements within [timeframe]. Our onboarding process is designed for immediate impact.

**Q: Is this suitable for beginners?**  
A: Absolutely. Our intuitive interface and guided setup make it accessible regardless of your experience level with {topic}.

**Q: What if I'm not satisfied?**  
A: We offer a [guarantee terms - e.g., 30-day money-back guarantee]. No questions asked. Your success is our priority.

---

# CTA Section
## Ready to get started?
[Compelling reason to act now - scarcity, urgency, or exclusive offer]

[Primary CTA Button]  
[Secondary text link: "See pricing" or "Talk to sales"]""",

        "ad": """## Ad Variation 1 (Short - Under 50 words)

Stop wasting time on {topic}.

[Product Name] helps you [key benefit] in just [timeframe].

Join [number] professionals already saving [metric].

👉 [CTA: Start free trial]

---

## Ad Variation 2 (Medium - Under 100 words)

What if {topic} didn't have to be so complicated?

Most people overthink it. The truth? You just need the right system.

[Product Name] is that system. We've helped [number] [audience] achieve [specific result] without [common pain point].

✓ [Benefit 1]  
✓ [Benefit 2]  
✓ [Benefit 3]

Limited time: [Offer details]

👉 [CTA: Claim your spot]

---

## Ad Variation 3 (Long-form - Under 150 words)

I used to dread dealing with {topic}.

Every day felt like a battle against [pain point]. I tried [common solution 1], [common solution 2], even [common solution 3]. Nothing stuck.

Then I discovered [Product Name].

Within [timeframe], everything changed. {topic} went from my biggest stress to my biggest strength. I finally had [desired outcome].

Here's what makes it different:

1. **[Differentiator 1]** — [Explanation with specific advantage]
2. **[Differentiator 2]** — [Explanation with specific advantage]  
3. **[Differentiator 3]** — [Explanation with specific advantage]

The best part? You can try it completely free for [trial period]. No credit card. No commitment. Just results.

[number] people made the switch this month. Will you be next?

👉 [CTA: Start your free trial now]"""
    }

    @staticmethod
    def generate_blog(topic, tone="professional", audience="general", word_count="800"):
        intro = random.choice(ContentEngine.BLOG_INTROS).format(topic=topic)
        body = random.choice(ContentEngine.BLOG_BODY).format(topic=topic)
        conclusion = random.choice(ContentEngine.BLOG_CONCLUSIONS).format(topic=topic)

        content = f"# {topic}: A Complete Guide\n\n*{tone.capitalize()} tone | For {audience} | ~{word_count} words*\n\n---\n\n{intro}\n\n{body}\n\n{conclusion}"
        return content

    @staticmethod
    def generate_email(topic, template_type="cold", tone="professional", audience="general"):
        template = ContentEngine.EMAIL_TEMPLATES.get(template_type, ContentEngine.EMAIL_TEMPLATES["cold"])
        return template.format(topic=topic, tone=tone, audience=audience)

    @staticmethod
    def generate_social(topic, platform="linkedin", tone="professional", audience="general"):
        template = ContentEngine.SOCIAL_TEMPLATES.get(platform, ContentEngine.SOCIAL_TEMPLATES["linkedin"])
        hashtag = topic.lower().replace(" ", "")
        return template.format(topic=topic, tone=tone, audience=audience, hashtag=hashtag)

    @staticmethod
    def generate_code(topic, language="Python", template_type="function"):
        func_name = topic.lower().replace(" ", "_").replace("-", "_")[:30]
        model_name = "".join(word.capitalize() for word in topic.split()[:2]) + "Item"
        endpoint = topic.lower().replace(" ", "-").replace("_", "-")[:20]
        table_name = topic.lower().replace(" ", "_").replace("-", "_")[:20]

        if template_type == "function":
            return ContentEngine.CODE_TEMPLATES["function"].format(
                topic=topic, func_name=func_name
            )
        elif template_type == "api":
            return ContentEngine.CODE_TEMPLATES["api"].format(
                topic=topic, model_name=model_name, endpoint=endpoint
            )
        else:  # sql
            return ContentEngine.CODE_TEMPLATES["sql"].format(
                topic=topic, table_name=table_name
            )

    @staticmethod
    def generate_marketing(topic, template_type="product", tone="professional", audience="general"):
        template = ContentEngine.MARKETING_TEMPLATES.get(template_type, ContentEngine.MARKETING_TEMPLATES["product"])
        return template.format(topic=topic, tone=tone, audience=audience)


# ========================
# FLASK ROUTES
# ========================

@app.route('/')
def index():
    return render_template('index.html', prompt_library=PROMPT_LIBRARY)

@app.route('/api/prompts')
def get_prompts():
    return jsonify(PROMPT_LIBRARY)

@app.route('/api/generate', methods=['POST'])
def generate_content():
    data = request.json
    content_type = data.get('type', 'blog')
    topic = data.get('topic', '')
    template = data.get('template', '')
    params = data.get('params', {})

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    engine = ContentEngine()

    try:
        if content_type == 'blog':
            content = engine.generate_blog(
                topic=topic,
                tone=params.get('tone', 'professional'),
                audience=params.get('audience', 'general'),
                word_count=params.get('word_count', '800')
            )
        elif content_type == 'email':
            content = engine.generate_email(
                topic=topic,
                template_type=template or 'cold',
                tone=params.get('tone', 'professional'),
                audience=params.get('audience', 'general')
            )
        elif content_type == 'social':
            content = engine.generate_social(
                topic=topic,
                platform=template or 'linkedin',
                tone=params.get('tone', 'professional'),
                audience=params.get('audience', 'general')
            )
        elif content_type == 'code':
            content = engine.generate_code(
                topic=topic,
                language=params.get('language', 'Python'),
                template_type=template or 'function'
            )
        elif content_type == 'marketing':
            content = engine.generate_marketing(
                topic=topic,
                template_type=template or 'product',
                tone=params.get('tone', 'professional'),
                audience=params.get('audience', 'general')
            )
        else:
            return jsonify({"error": "Invalid content type"}), 400

        return jsonify({
            "success": True,
            "content": content,
            "type": content_type,
            "template": template,
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "word_count": len(content.split()),
                "char_count": len(content)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
