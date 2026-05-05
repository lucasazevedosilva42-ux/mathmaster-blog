import os, json, re, datetime, requests, subprocess, time
from pathlib import Path

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
BASE_URL  = "https://lucasazevedosilva42-ux.github.io/mathmaster-blog"
ANALYTICS = "G-YXVE6HWKNM"
ADSENSE   = "ca-pub-4133658586839866"

TEMAS = [
    {"slug": "linear-equations-algebra",        "title": "Linear Equations: Complete Guide to Solving Algebra Problems",           "category": "Algebra",           "emoji": "📐"},
    {"slug": "quadratic-functions-parabola",     "title": "Quadratic Functions and Parabolas: Everything You Need to Know",         "category": "Functions",         "emoji": "📈"},
    {"slug": "trigonometry-sin-cos-tan",         "title": "Trigonometry Made Simple: Sine, Cosine, and Tangent Explained",         "category": "Trigonometry",      "emoji": "📐"},
    {"slug": "logarithms-exponentials",          "title": "Logarithms and Exponential Functions: A Step-by-Step Guide",            "category": "Functions",         "emoji": "🔢"},
    {"slug": "statistics-mean-median-mode",      "title": "Statistics Basics: Mean, Median, Mode and Standard Deviation",          "category": "Statistics",        "emoji": "📊"},
    {"slug": "probability-fundamentals",         "title": "Probability Fundamentals: From Basic Concepts to Real Problems",         "category": "Probability",       "emoji": "🎲"},
    {"slug": "geometry-circles-area",            "title": "Circle Geometry: Area, Circumference and Arc Length Mastered",          "category": "Geometry",          "emoji": "⭕"},
    {"slug": "pythagorean-theorem",              "title": "Pythagorean Theorem: Applications and Problem Solving",                  "category": "Geometry",          "emoji": "📐"},
    {"slug": "polynomials-factoring",            "title": "Polynomials and Factoring: Complete Algebra Tutorial",                   "category": "Algebra",           "emoji": "🔢"},
    {"slug": "sequences-arithmetic-geometric",   "title": "Arithmetic and Geometric Sequences: Patterns in Mathematics",           "category": "Sequences",         "emoji": "🔢"},
    {"slug": "inequalities-solving",             "title": "Solving Inequalities: Linear, Quadratic and Systems",                   "category": "Algebra",           "emoji": "📐"},
    {"slug": "matrices-determinants",            "title": "Matrices and Determinants: Linear Algebra Fundamentals",                "category": "Linear Algebra",    "emoji": "🔢"},
    {"slug": "vectors-operations",               "title": "Vectors in Mathematics: Operations, Magnitude and Direction",           "category": "Vectors",           "emoji": "➡️"},
    {"slug": "complex-numbers",                  "title": "Complex Numbers: Imaginary Numbers and Real Applications",              "category": "Algebra",           "emoji": "🔢"},
    {"slug": "limits-introduction-calculus",     "title": "Introduction to Limits: The Gateway to Calculus",                      "category": "Calculus",          "emoji": "📈"},
    {"slug": "derivatives-differentiation",      "title": "Derivatives Explained: Differentiation Rules and Applications",         "category": "Calculus",          "emoji": "📈"},
    {"slug": "integrals-antiderivatives",        "title": "Integrals and Antiderivatives: The Fundamental Theorem of Calculus",    "category": "Calculus",          "emoji": "📈"},
    {"slug": "plane-geometry-triangles",         "title": "Triangle Geometry: Types, Properties and Theorems Explained",           "category": "Geometry",          "emoji": "📐"},
    {"slug": "analytic-geometry-lines",          "title": "Analytic Geometry: Lines, Slopes and Equations Explained",              "category": "Analytic Geometry", "emoji": "📐"},
    {"slug": "combinatorics-permutations",       "title": "Combinatorics: Permutations and Combinations Explained",               "category": "Combinatorics",     "emoji": "🔢"},
    {"slug": "set-theory-fundamentals",          "title": "Set Theory: Union, Intersection and Complement Explained",              "category": "Foundations",       "emoji": "🔵"},
    {"slug": "number-systems-natural-integers",  "title": "Number Systems: Natural, Integer, Rational and Real Numbers",           "category": "Foundations",       "emoji": "🔢"},
    {"slug": "financial-math-interest",          "title": "Financial Mathematics: Simple and Compound Interest Explained",         "category": "Applied Math",      "emoji": "💰"},
    {"slug": "percentage-ratio-proportion",      "title": "Percentage, Ratio and Proportion: Real-World Applications",            "category": "Applied Math",      "emoji": "💹"},
    {"slug": "functions-domain-range",           "title": "Functions: Domain, Range, and Graph Interpretation",                    "category": "Functions",         "emoji": "📈"},
    {"slug": "3d-geometry-solids",               "title": "3D Geometry: Volume and Surface Area of Solids",                        "category": "Geometry",          "emoji": "🔷"},
    {"slug": "absolute-value-modulus",           "title": "Absolute Value and Modulus: Equations and Inequalities",                "category": "Algebra",           "emoji": "📐"},
    {"slug": "binomial-theorem",                 "title": "Binomial Theorem: Pascal's Triangle and Expansion Explained",           "category": "Algebra",           "emoji": "🔢"},
    {"slug": "conic-sections-ellipse-hyperbola", "title": "Conic Sections: Ellipse, Hyperbola and Parabola Guide",                "category": "Analytic Geometry", "emoji": "📐"},
    {"slug": "graph-theory-introduction",        "title": "Introduction to Graph Theory: Nodes, Edges and Applications",          "category": "Discrete Math",     "emoji": "🔗"},
]

# ─── helpers ────────────────────────────────────────────────────────────────

def get_topic():
    pf  = Path("publicados_en.json")
    pub = set(json.loads(pf.read_text()) if pf.exists() else [])
    for t in TEMAS:
        if t["slug"] not in pub:
            return t
    return TEMAS[0]   # cycle back after all published

def mark_published(slug):
    pf  = Path("publicados_en.json")
    pub = json.loads(pf.read_text()) if pf.exists() else []
    if slug not in pub:
        pub.append(slug)
    pf.write_text(json.dumps(pub, ensure_ascii=False, indent=2))

# ─── content generation ──────────────────────────────────────────────────────

def generate_content(topic):
    print(f"📝 Generating: {topic['title']}")
    url     = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}

    prompt = f"""You are an expert math educator writing a comprehensive blog post in English.

Topic: "{topic['title']}"
Category: {topic['category']}

Write a complete, educational blog post. Return ONLY valid JSON (no markdown, no backticks):
{{
  "meta_description": "SEO description under 155 chars",
  "intro": "Engaging introduction ~150 words. Hook the reader, explain why this topic matters.",
  "section1_title": "First main concept title",
  "section1": "Detailed explanation ~200 words with step-by-step examples.",
  "section2_title": "Second concept or worked example title",
  "section2": "~200 words — deeper dive with worked examples.",
  "section3_title": "Practice and Real-World Applications",
  "section3": "~150 words — real-world uses and practice tips.",
  "exercise1": "A clear math exercise problem (one sentence).",
  "exercise1_answer": "Complete step-by-step solution (3-5 steps).",
  "exercise2": "Another practice exercise.",
  "exercise2_answer": "Complete step-by-step solution.",
  "calculator_label": "Descriptive calculator name, e.g. 'Quadratic Formula Calculator'",
  "calculator_input1_label": "Label for first numeric input",
  "calculator_input2_label": "Label for second input, or empty string if only one input",
  "calculator_formula": "Valid JavaScript expression using variables input1 and input2 (use Math.* for math). Must return a number or string.",
  "calculator_result_label": "What the result represents",
  "tip": "One study tip for this topic, under 70 chars.",
  "conclusion": "Motivating conclusion ~100 words."
}}"""

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.75,
        "max_tokens": 4000,
    }

    for attempt in range(4):
        try:
            r = requests.post(url, json=body, headers=headers, timeout=120)
            r.raise_for_status()
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if "```" in txt:
                for part in txt.split("```"):
                    if "{" in part:
                        txt = part.replace("json", "", 1).strip()
                        break
            return json.loads(txt)
        except Exception as e:
            wait = 30 * (attempt + 1)
            print(f"⚠️ Attempt {attempt+1}: {e} — waiting {wait}s")
            time.sleep(wait)
    raise Exception("Failed to generate content after 4 attempts")

# ─── HTML builder ────────────────────────────────────────────────────────────

def build_html(topic, data, date_str):
    title    = topic["title"]
    slug     = topic["slug"]
    category = topic["category"]
    emoji    = topic.get("emoji", "📐")
    meta     = data.get("meta_description", "")

    has_input2   = bool(data.get("calculator_input2_label", "").strip())
    input2_block = ""
    if has_input2:
        label2 = data["calculator_input2_label"].replace('"', "'")
        input2_block = f"""
      <div class="calc-field">
        <label>{label2}</label>
        <input type="number" id="calc-input2" placeholder="0" step="any" />
      </div>"""

    formula     = data.get("calculator_formula", "input1 + input2").replace('"', "'")
    input2_js   = 'const input2 = parseFloat(document.getElementById("calc-input2").value) || 0;' if has_input2 else "const input2 = 0;"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | MathMaster Blog</title>
  <meta name="description" content="{meta}" />
  <meta name="keywords" content="{category.lower()}, mathematics, math tutorial, {slug.replace('-', ', ')}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{meta}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{BASE_URL}/{slug}.html" />
  <link rel="canonical" href="{BASE_URL}/{slug}.html" />

  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Article","headline":"{title}","datePublished":"{date_str}","author":{{"@type":"Organization","name":"MathMaster Blog"}},"publisher":{{"@type":"Organization","name":"MathMaster Blog"}}}}
  </script>

  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ANALYTICS}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{ANALYTICS}');
  </script>

  <!-- AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE}" crossorigin="anonymous"></script>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet" />

  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --blue: #185FA5; --blue-dark: #0f3d6e; --blue-light: #2176c2;
      --gold: #F5A623; --bg: #04080f; --bg2: #070d1a; --bg3: #0d1628;
      --text: #e8edf5; --text-muted: #8a9bb5; --border: rgba(24,95,165,0.25);
    }}
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }}

    nav {{
      position: sticky; top: 0; z-index: 100;
      background: rgba(4,8,15,0.92); backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border); padding: 0 2rem;
    }}
    .nav-inner {{ max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 64px; }}
    .nav-logo {{ font-family: 'Playfair Display', serif; font-size: 1.3rem; font-weight: 700; color: #fff; text-decoration: none; }}
    .nav-logo span {{ color: var(--blue); }}
    .nav-back {{ color: var(--text-muted); text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }}
    .nav-back:hover {{ color: #fff; }}

    .post-hero {{
      background: linear-gradient(135deg, var(--bg2), var(--bg3));
      border-bottom: 1px solid var(--border); padding: 3.5rem 2rem 3rem; text-align: center;
    }}
    .post-category {{
      display: inline-block; background: rgba(24,95,165,0.15); border: 1px solid rgba(24,95,165,0.4);
      color: #7ab3e0; font-size: 0.75rem; font-weight: 700; padding: 0.3rem 0.9rem;
      border-radius: 100px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 1rem;
    }}
    .post-hero h1 {{
      font-family: 'Playfair Display', serif; font-size: clamp(1.8rem, 4vw, 2.8rem);
      font-weight: 900; line-height: 1.25; max-width: 800px; margin: 0 auto 1rem;
    }}
    .post-meta {{ font-size: 0.85rem; color: var(--text-muted); display: flex; align-items: center; justify-content: center; gap: 1.5rem; flex-wrap: wrap; }}

    .post-container {{ max-width: 780px; margin: 0 auto; padding: 3rem 2rem; }}
    .ad-slot {{ margin: 2rem 0; text-align: center; }}
    .post-intro {{ font-size: 1.1rem; line-height: 1.8; color: #c8d8ea; margin-bottom: 2.5rem; padding-bottom: 2rem; border-bottom: 1px solid var(--border); }}

    h2 {{ font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700; margin: 2.5rem 0 1rem; }}
    p {{ margin-bottom: 1.2rem; color: #c0cfe0; }}

    .highlight-box {{
      background: rgba(24,95,165,0.1); border-left: 3px solid var(--blue);
      border-radius: 0 8px 8px 0; padding: 1.2rem 1.5rem; margin: 1.5rem 0;
    }}
    .highlight-box strong {{ color: var(--blue); }}

    .calculator {{
      background: var(--bg2); border: 1px solid var(--border); border-radius: 14px;
      padding: 1.75rem; margin: 2.5rem 0;
    }}
    .calc-title {{ font-family: 'Playfair Display', serif; font-size: 1.1rem; font-weight: 700; margin-bottom: 1.25rem; }}
    .calc-title span {{ color: var(--blue); }}
    .calc-fields {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin-bottom: 1.25rem; }}
    .calc-field label {{ display: block; font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.4rem; font-weight: 500; }}
    .calc-field input {{
      width: 100%; background: var(--bg3); border: 1px solid var(--border); border-radius: 8px;
      padding: 0.65rem 1rem; color: var(--text); font-size: 1rem; font-family: 'DM Sans', sans-serif; transition: border-color 0.2s;
    }}
    .calc-field input:focus {{ outline: none; border-color: var(--blue); }}
    .calc-btn {{
      background: var(--blue); color: #fff; border: none; border-radius: 8px;
      padding: 0.7rem 1.8rem; font-size: 0.95rem; font-weight: 600; cursor: pointer; transition: background 0.2s;
    }}
    .calc-btn:hover {{ background: var(--blue-light); }}
    .calc-result {{
      margin-top: 1rem; background: var(--bg3); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.25rem;
    }}
    .calc-result-label {{ font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.25rem; }}
    .calc-result-value {{ font-size: 1.5rem; font-weight: 700; color: var(--blue); }}

    .exercises {{ margin: 2.5rem 0; }}
    .exercise {{
      background: var(--bg2); border: 1px solid var(--border); border-radius: 12px;
      padding: 1.5rem; margin-bottom: 1.25rem;
    }}
    .exercise-num {{ font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--blue); margin-bottom: 0.5rem; }}
    .exercise-q {{ font-weight: 600; margin-bottom: 0.75rem; color: var(--text); }}
    .exercise-toggle {{
      background: transparent; border: 1px solid var(--border); border-radius: 6px;
      color: var(--text-muted); font-size: 0.85rem; padding: 0.4rem 0.9rem; cursor: pointer;
      transition: border-color 0.2s, color 0.2s; font-family: 'DM Sans', sans-serif;
    }}
    .exercise-toggle:hover {{ border-color: var(--blue); color: var(--text); }}
    .exercise-answer {{ display: none; margin-top: 1rem; background: rgba(24,95,165,0.08); border-radius: 8px; padding: 1rem; font-size: 0.9rem; color: var(--text-muted); line-height: 1.7; }}
    .exercise-answer.show {{ display: block; }}

    .tip-box {{
      background: rgba(245,166,35,0.08); border: 1px solid rgba(245,166,35,0.3);
      border-radius: 10px; padding: 1rem 1.25rem; margin: 2rem 0;
      display: flex; align-items: flex-start; gap: 0.75rem;
    }}
    .tip-icon {{ font-size: 1.2rem; flex-shrink: 0; }}
    .tip-text {{ font-size: 0.9rem; color: #d4b86a; }}

    .post-nav {{
      border-top: 1px solid var(--border); padding-top: 2rem; margin-top: 3rem;
      display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;
    }}
    .back-link {{ color: var(--blue); text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
    .back-link:hover {{ text-decoration: underline; }}
    .shop-link {{
      background: var(--blue); color: #fff; padding: 0.6rem 1.4rem; border-radius: 8px;
      text-decoration: none; font-weight: 600; font-size: 0.9rem; transition: background 0.2s;
    }}
    .shop-link:hover {{ background: var(--blue-light); }}

    @media (max-width: 600px) {{ .post-container {{ padding: 2rem 1rem; }} }}
  </style>
</head>
<body>

<nav>
  <div class="nav-inner">
    <a href="index.html" class="nav-logo">Math<span>Master</span></a>
    <a href="index.html" class="nav-back">← All Articles</a>
  </div>
</nav>

<div class="post-hero">
  <span class="post-category">{emoji} {category}</span>
  <h1>{title}</h1>
  <div class="post-meta">
    <span>📅 {date_str}</span>
    <span>⏱️ 8 min read</span>
    <span>📐 MathMaster Blog</span>
  </div>
</div>

<div class="post-container">

  <div class="ad-slot">
    <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE}"
         data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </div>

  <p class="post-intro">{data.get("intro", "")}</p>

  <h2>{data.get("section1_title", "Core Concepts")}</h2>
  <p>{data.get("section1", "")}</p>

  <div class="highlight-box">
    <strong>Key Point:</strong> {data.get("tip", "Practice consistently to master this topic.")}
  </div>

  <h2>{data.get("section2_title", "Worked Examples")}</h2>
  <p>{data.get("section2", "")}</p>

  <div class="calculator">
    <div class="calc-title"><span>🧮</span> {data.get("calculator_label", "Interactive Calculator")}</div>
    <div class="calc-fields">
      <div class="calc-field">
        <label>{data.get("calculator_input1_label", "Value A")}</label>
        <input type="number" id="calc-input1" placeholder="0" step="any" />
      </div>{input2_block}
    </div>
    <button class="calc-btn" onclick="calculate()">Calculate →</button>
    <div class="calc-result">
      <div class="calc-result-label">{data.get("calculator_result_label", "Result")}</div>
      <div class="calc-result-value" id="calc-result">—</div>
    </div>
  </div>

  <h2>{data.get("section3_title", "Practice and Applications")}</h2>
  <p>{data.get("section3", "")}</p>

  <div class="ad-slot">
    <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE}"
         data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </div>

  <h2>Practice Exercises</h2>
  <div class="exercises">
    <div class="exercise">
      <div class="exercise-num">Exercise 1</div>
      <div class="exercise-q">{data.get("exercise1", "")}</div>
      <button class="exercise-toggle" onclick="toggleAnswer(this)">Show Solution</button>
      <div class="exercise-answer">{data.get("exercise1_answer", "")}</div>
    </div>
    <div class="exercise">
      <div class="exercise-num">Exercise 2</div>
      <div class="exercise-q">{data.get("exercise2", "")}</div>
      <button class="exercise-toggle" onclick="toggleAnswer(this)">Show Solution</button>
      <div class="exercise-answer">{data.get("exercise2_answer", "")}</div>
    </div>
  </div>

  <div class="tip-box">
    <span class="tip-icon">💡</span>
    <span class="tip-text"><strong>Study Tip:</strong> {data.get("tip", "Practice regularly for best results.")}</span>
  </div>

  <h2>Conclusion</h2>
  <p>{data.get("conclusion", "")}</p>

  <div class="post-nav">
    <a href="index.html" class="back-link">← Back to All Articles</a>
    <a href="https://pay.kiwify.com.br/PAXxuLd" target="_blank" class="shop-link">📚 Get Study Materials</a>
  </div>

</div>

<script>
  function calculate() {{
    const input1 = parseFloat(document.getElementById('calc-input1').value) || 0;
    {input2_js}
    try {{
      const result = {formula};
      document.getElementById('calc-result').textContent = (typeof result === 'number') ? result.toFixed(4).replace(/\\.?0+$/, '') : result;
    }} catch(e) {{
      document.getElementById('calc-result').textContent = 'Error';
    }}
  }}

  function toggleAnswer(btn) {{
    const answer = btn.nextElementSibling;
    const open   = answer.classList.toggle('show');
    btn.textContent = open ? 'Hide Solution' : 'Show Solution';
  }}
</script>

</body>
</html>"""

# ─── index updater ───────────────────────────────────────────────────────────

def update_index(topic, date_str):
    idx = Path("index.html")
    if not idx.exists():
        print("⚠️ index.html not found"); return

    content = idx.read_text(encoding="utf-8")

    card = f"""
    <a href="{topic['slug']}.html" class="post-card">
      <div class="post-card-img">{topic.get('emoji', '📐')}</div>
      <div class="post-card-body">
        <div class="post-card-tag">{topic['category']}</div>
        <div class="post-card-title">{topic['title']}</div>
        <div class="post-card-meta">
          <span>📅 {date_str}</span>
          <span>⏱️ 8 min read</span>
        </div>
      </div>
    </a>"""

    marker = "<!-- POSTS_LIST -->"
    if marker in content:
        # Only insert if this slug isn't already in the index
        if f'href="{topic["slug"]}.html"' not in content:
            content = content.replace(marker, card + "\n    " + marker)
        else:
            print(f"⚠️ Card for {topic['slug']} already in index — skipping")

    # Remove empty state once posts exist
    content = re.sub(r'\s*<!-- EMPTY_STATE_START -->.*?<!-- EMPTY_STATE_END -->', "", content, flags=re.DOTALL)

    idx.write_text(content, encoding="utf-8")
    print("✅ index.html updated")

# ─── sitemap updater ─────────────────────────────────────────────────────────

def update_sitemap(topic, date_str):
    sm = Path("sitemap.xml")
    xml = sm.read_text(encoding="utf-8") if sm.exists() else ""

    entry = f"""  <url>
    <loc>{BASE_URL}/{topic['slug']}.html</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>"""

    if "<urlset" in xml:
        url_loc = f"{BASE_URL}/{topic['slug']}.html"
        if url_loc in xml:
            print(f"⚠️ {topic['slug']} already in sitemap — skipping")
            return
        xml = xml.replace("</urlset>", entry + "\n</urlset>")
    else:
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
{entry}
</urlset>"""

    sm.write_text(xml, encoding="utf-8")
    print("✅ sitemap.xml updated")

# ─── git push ────────────────────────────────────────────────────────────────

def git_push(topic, date_str):
    slug  = topic["slug"]
    files = [f"{slug}.html", "publicados_en.json", "index.html", "sitemap.xml"]

    subprocess.run(["git", "config", "user.email", "bot@mathmaster.blog"],  check=False)
    subprocess.run(["git", "config", "user.name",  "MathMaster Bot"],        check=False)
    subprocess.run(["git", "add"] + files,                                   check=False)

    diff = subprocess.run(["git", "diff", "--staged", "--quiet"])
    if diff.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"✅ Post: {topic['title'][:60]} — {date_str}"], check=True)
        # Pull rebase in case another concurrent run pushed first
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=False)
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Published: {slug}.html")
    else:
        print("⚠️ No changes to commit")

# ─── main ────────────────────────────────────────────────────────────────────

def main():
    print(f"🚀 MathMaster Blog — {datetime.date.today()}")
    if not GROQ_KEY:
        raise Exception("GROQ_API_KEY not set")

    topic    = get_topic()
    date_str = datetime.date.today().isoformat()

    print(f"📐 Topic: {topic['title']} [{topic['category']}]")
    data = generate_content(topic)

    html_content = build_html(topic, data, date_str)
    Path(f"{topic['slug']}.html").write_text(html_content, encoding="utf-8")
    print(f"✅ Saved: {topic['slug']}.html")

    mark_published(topic["slug"])
    update_index(topic, date_str)
    update_sitemap(topic, date_str)
    git_push(topic, date_str)

if __name__ == "__main__":
    main()
