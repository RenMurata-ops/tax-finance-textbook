#!/usr/bin/env python3
"""Convert the tax/finance textbook markdown to a richly styled HTML page."""

import markdown
import re
import hashlib

def slugify(text):
    """Create a URL-friendly slug from Japanese/English text."""
    return hashlib.md5(text.encode()).hexdigest()[:10]

def build_toc(md_text):
    """Extract headings and build a hierarchical TOC."""
    toc_items = []
    for line in md_text.split('\n'):
        m = re.match(r'^(#{1,2})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            slug = slugify(title)
            toc_items.append((level, title, slug))
    return toc_items

def inject_heading_ids(html_content, md_text):
    """Add id attributes to h1 and h2 tags for anchor navigation."""
    toc = build_toc(md_text)
    for level, title, slug in toc:
        tag = f'h{level}'
        # Escape special regex chars in title
        escaped = re.escape(title)
        # Replace ** bold markers that markdown converts
        pattern = f'<{tag}>(.+?)</{tag}>'
        # We need a smarter approach - find headings and add IDs

    # Simple approach: add IDs to all h1 and h2 tags sequentially
    toc_idx = 0
    def add_id(match):
        nonlocal toc_idx
        tag = match.group(1)
        if tag in ('h1', 'h2'):
            if toc_idx < len(toc):
                slug = toc[toc_idx][2]
                toc_idx += 1
                return f'<{tag} id="{slug}">'
        return match.group(0)

    html_content = re.sub(r'<(h[12])>', add_id, html_content)
    return html_content

def generate_toc_html(toc_items):
    """Generate sidebar TOC HTML."""
    parts = []
    current_part = None

    for level, title, slug in toc_items:
        if level == 1:
            # Part heading
            short = title
            # Shorten for sidebar
            if '：' in short:
                short = short.split('：')[0] + '<br><small>' + short.split('：')[1] + '</small>'
            parts.append(f'<li class="toc-part"><a href="#{slug}">{short}</a><ul>')
            current_part = True
        elif level == 2:
            # Chapter heading
            short = title
            if len(short) > 25:
                short = short[:25] + '…'
            if current_part:
                parts.append(f'<li class="toc-chapter"><a href="#{slug}">{short}</a></li>')

    # Close any open ul/li
    result = '\n'.join(parts)
    # Close all open <ul> tags
    open_uls = result.count('<ul>') - result.count('</ul>')
    result += '</ul></li>' * open_uls

    return f'<ul class="toc-list">{result}</ul>'

def build_html():
    base = '/Users/renmurata/Documents/tax_finance_textbook'

    # Read new chapters
    intro_text = ''
    strategy_text = ''
    try:
        with open(f'{base}/chapter00_intro.md', 'r') as f:
            intro_text = f.read()
    except FileNotFoundError:
        pass
    try:
        with open(f'{base}/chapter01_strategy.md', 'r') as f:
            strategy_text = f.read()
    except FileNotFoundError:
        pass

    with open(f'{base}/complete_textbook.md', 'r') as f:
        original_text = f.read()

    # Combine: 序章 + 戦略会計 + 既存content (reordered)
    # The existing Part 1 "地図（全体像）" content is mostly covered by 序章 now,
    # so we keep it but the new chapters come first
    md_text = intro_text + '\n\n---\n\n' + strategy_text + '\n\n---\n\n' + original_text

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite', 'toc'])
    html_content = md.convert(md_text)

    # Build TOC
    toc_items = build_toc(md_text)
    toc_html = generate_toc_html(toc_items)

    # Inject heading IDs
    html_content = inject_heading_ids(html_content, md_text)

    # Build the full HTML page
    page = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>税金・会計・財務の教科書</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
/* ===== Reset & Base ===== */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
  --primary: #1a365d;
  --primary-light: #2b6cb0;
  --accent: #92400e;
  --accent-light: #b45309;
  --bg: #f7fafc;
  --bg-card: #ffffff;
  --text: #2d3748;
  --text-light: #718096;
  --border: #e2e8f0;
  --sidebar-w: 300px;
  --part1: #2b6cb0;
  --part2: #2f855a;
  --part3: #9b2c2c;
  --part4: #6b46c1;
  --part5: #c05621;
  --part6: #2c7a7b;
  --part7: #744210;
  --part8: #4a5568;
}}

html {{ scroll-behavior: smooth; }}

body {{
  font-family: "Hiragino Kaku Gothic ProN", "Noto Sans JP", "Yu Gothic", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.85;
  font-size: 15.5px;
}}

/* ===== Sidebar ===== */
.sidebar {{
  position: fixed;
  top: 0; left: 0;
  width: var(--sidebar-w);
  height: 100vh;
  background: var(--primary);
  color: #fff;
  overflow-y: auto;
  z-index: 100;
  padding: 0;
  transition: transform 0.3s;
}}

.sidebar-header {{
  padding: 24px 20px 16px;
  background: rgba(0,0,0,0.15);
  border-bottom: 1px solid rgba(255,255,255,0.1);
}}

.sidebar-header h1 {{
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.05em;
  line-height: 1.5;
}}

.sidebar-header p {{
  font-size: 11px;
  opacity: 0.7;
  margin-top: 4px;
}}

.toc-list {{
  list-style: none;
  padding: 12px 0;
}}

.toc-part {{
  margin: 0;
}}

.toc-part > a {{
  display: block;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  text-decoration: none;
  background: rgba(255,255,255,0.05);
  border-left: 4px solid var(--accent);
  transition: background 0.2s;
}}

.toc-part > a:hover {{
  background: rgba(255,255,255,0.12);
}}

.toc-part > a small {{
  font-weight: 400;
  opacity: 0.8;
  font-size: 11px;
}}

.toc-part > ul {{
  list-style: none;
  padding: 0;
}}

.toc-chapter a {{
  display: block;
  padding: 5px 20px 5px 32px;
  font-size: 12px;
  color: rgba(255,255,255,0.75);
  text-decoration: none;
  transition: all 0.2s;
  border-left: 4px solid transparent;
}}

.toc-chapter a:hover {{
  color: #fff;
  background: rgba(255,255,255,0.08);
  border-left-color: var(--accent-light);
}}

/* ===== Main Content ===== */
.main {{
  margin-left: var(--sidebar-w);
  padding: 0;
}}

.content {{
  max-width: 860px;
  margin: 0 auto;
  padding: 40px 48px 80px;
}}

/* ===== Typography ===== */
.content h1 {{
  font-size: 28px;
  font-weight: 800;
  color: var(--primary);
  margin: 80px 0 24px;
  padding: 20px 0 16px;
  border-bottom: 3px solid var(--primary);
  position: relative;
}}

.content h1::before {{
  content: '';
  display: block;
  width: 60px;
  height: 4px;
  background: var(--accent);
  margin-bottom: 12px;
  border-radius: 2px;
}}

.content h1:first-child {{ margin-top: 0; }}

.content h2 {{
  font-size: 22px;
  font-weight: 700;
  color: var(--primary-light);
  margin: 56px 0 18px;
  padding: 12px 0 10px;
  border-bottom: 2px solid var(--border);
}}

.content h3 {{
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin: 36px 0 12px;
  padding-left: 14px;
  border-left: 4px solid var(--accent);
}}

.content h4 {{
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  margin: 24px 0 8px;
}}

.content p {{
  margin: 12px 0;
  text-align: justify;
}}

.content strong {{
  color: var(--primary);
  font-weight: 700;
}}

/* ===== Tables ===== */
.content table {{
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  font-size: 14px;
  background: var(--bg-card);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}

.content thead th {{
  background: var(--primary);
  color: #fff;
  padding: 12px 14px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
}}

.content tbody td {{
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}}

.content tbody tr:nth-child(even) {{
  background: #f8fafc;
}}

.content tbody tr:hover {{
  background: #edf2f7;
}}

/* ===== Code blocks ===== */
.content code {{
  font-family: "SF Mono", "Fira Code", monospace;
  font-size: 13px;
  background: #edf2f7;
  padding: 2px 6px;
  border-radius: 4px;
  color: #c53030;
}}

.content pre {{
  background: #1a202c;
  color: #e2e8f0;
  padding: 20px 24px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
  font-size: 13px;
  line-height: 1.7;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}}

.content pre code {{
  background: none;
  color: inherit;
  padding: 0;
  font-size: 13px;
}}

/* ===== Lists ===== */
.content ul, .content ol {{
  margin: 12px 0;
  padding-left: 28px;
}}

.content li {{
  margin: 6px 0;
}}

/* ===== Horizontal rules (part separators) ===== */
.content hr {{
  border: none;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--border), transparent);
  margin: 48px 0;
}}

/* ===== Charts section ===== */
.chart-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin: 32px 0;
}}

.chart-card {{
  background: var(--bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid var(--border);
}}

.chart-card h3 {{
  font-size: 14px;
  color: var(--primary);
  margin: 0 0 16px;
  padding: 0;
  border: none;
}}

.chart-card canvas {{
  max-height: 260px;
}}

/* ===== Info boxes ===== */
.info-box {{
  background: #ebf8ff;
  border-left: 4px solid var(--primary-light);
  padding: 16px 20px;
  border-radius: 0 8px 8px 0;
  margin: 20px 0;
  font-size: 14px;
}}

/* ===== Diagram containers ===== */
.diagram {{
  background: var(--bg-card);
  border-radius: 12px;
  padding: 32px;
  margin: 24px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid var(--border);
  text-align: center;
}}

.diagram svg {{
  max-width: 100%;
}}

/* ===== Hero / Cover ===== */
.hero {{
  background: linear-gradient(135deg, var(--primary) 0%, #2b4c7e 50%, var(--primary-light) 100%);
  color: #fff;
  padding: 80px 48px 60px;
  margin: -40px -48px 40px;
  border-radius: 0 0 24px 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
}}

.hero::before {{
  content: '';
  position: absolute;
  top: -50%; right: -20%;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
  border-radius: 50%;
}}

.hero h1 {{
  font-size: 36px;
  font-weight: 800;
  border: none;
  color: #fff;
  margin: 0;
  padding: 0;
  letter-spacing: 0.04em;
}}

.hero h1::before {{ display: none; }}

.hero .subtitle {{
  font-size: 16px;
  opacity: 0.85;
  margin-top: 12px;
  font-weight: 400;
}}

.hero .meta {{
  margin-top: 24px;
  display: flex;
  gap: 24px;
  justify-content: center;
  font-size: 13px;
  opacity: 0.7;
}}

/* ===== Part colors ===== */
.part-indicator {{
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}}

/* ===== Scroll to top ===== */
.scroll-top {{
  position: fixed;
  bottom: 32px; right: 32px;
  width: 44px; height: 44px;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 50;
}}

.scroll-top.visible {{ opacity: 1; }}

/* ===== Mobile toggle ===== */
.menu-toggle {{
  display: none;
  position: fixed;
  top: 12px; left: 12px;
  z-index: 200;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 18px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}}

/* ===== Print ===== */
@media print {{
  .sidebar, .menu-toggle, .scroll-top {{ display: none !important; }}
  .main {{ margin-left: 0; }}
  .content {{ padding: 20px; }}
}}

/* ===== Mobile ===== */
@media (max-width: 900px) {{
  .sidebar {{
    transform: translateX(-100%);
  }}
  .sidebar.open {{
    transform: translateX(0);
    box-shadow: 4px 0 24px rgba(0,0,0,0.3);
  }}
  .main {{
    margin-left: 0;
  }}
  .menu-toggle {{
    display: block;
  }}
  .content {{
    padding: 60px 20px 80px;
  }}
  .hero {{
    margin: -60px -20px 32px;
    padding: 60px 20px 40px;
  }}
  .hero h1 {{ font-size: 24px; }}
  .chart-grid {{
    grid-template-columns: 1fr;
  }}
}}
</style>
</head>
<body>

<!-- Mobile menu toggle -->
<button class="menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')" aria-label="メニュー">&#9776;</button>

<!-- Sidebar -->
<nav class="sidebar">
  <div class="sidebar-header">
    <h1>税金・会計・財務の教科書</h1>
    <p>戦略会計 × 実務税財</p>
    <a href="index.html" style="display:inline-block;margin-top:12px;font-size:12px;color:#71717a;text-decoration:none;border:1px solid #3f3f46;padding:4px 12px;border-radius:6px;">← トップに戻る</a>
  </div>
  {toc_html}
</nav>

<!-- Main content -->
<div class="main">
  <div class="content">

    <!-- Hero cover -->
    <div class="hero">
      <h1>税金・会計・財務の教科書</h1>
      <div class="subtitle">経営方針 → 戦略会計 → 税・財理解 → 実務──意思決定の流れで体系的に学ぶ</div>
      <div class="meta">
        <span>序章 + 全9部構成 + 補章</span>
        <span>約15万文字</span>
        <span>2025〜2026年度対応</span>
      </div>
    </div>

    <!-- Charts: Visual overview -->
    <h2 id="visual-overview" style="margin-top:24px;">図解で見る日本の税と財務</h2>

    <div class="chart-grid">
      <div class="chart-card">
        <h3>所得税の累進税率</h3>
        <canvas id="chart-income-tax"></canvas>
      </div>
      <div class="chart-card">
        <h3>国家予算の歳入構成</h3>
        <canvas id="chart-revenue"></canvas>
      </div>
      <div class="chart-card">
        <h3>国家予算の歳出構成</h3>
        <canvas id="chart-expense"></canvas>
      </div>
      <div class="chart-card">
        <h3>法人実効税率の国際比較</h3>
        <canvas id="chart-corp-intl"></canvas>
      </div>
    </div>

    <!-- Diagram: 三つの領域 -->
    <div class="diagram">
      <h3 style="border:none;padding:0;margin:0 0 20px;font-size:16px;color:var(--primary);">会計・税務・財務の関係</h3>
      <svg viewBox="0 0 700 320" xmlns="http://www.w3.org/2000/svg" style="max-width:600px;">
        <!-- Circles -->
        <circle cx="250" cy="160" r="130" fill="#2b6cb0" opacity="0.15" stroke="#2b6cb0" stroke-width="2"/>
        <circle cx="450" cy="160" r="130" fill="#c05621" opacity="0.15" stroke="#c05621" stroke-width="2"/>
        <circle cx="350" cy="60" r="100" fill="#2f855a" opacity="0.12" stroke="#2f855a" stroke-width="2"/>
        <!-- Labels -->
        <text x="180" y="165" font-size="18" font-weight="700" fill="#2b6cb0" text-anchor="middle">会計</text>
        <text x="180" y="188" font-size="11" fill="#4a5568" text-anchor="middle">利益を測る</text>
        <text x="180" y="203" font-size="11" fill="#4a5568" text-anchor="middle">PL / BS / CF</text>
        <text x="520" y="165" font-size="18" font-weight="700" fill="#c05621" text-anchor="middle">財務</text>
        <text x="520" y="188" font-size="11" fill="#4a5568" text-anchor="middle">お金を回す</text>
        <text x="520" y="203" font-size="11" fill="#4a5568" text-anchor="middle">資金調達 / 投資</text>
        <text x="350" y="35" font-size="18" font-weight="700" fill="#2f855a" text-anchor="middle">税務</text>
        <text x="350" y="55" font-size="11" fill="#4a5568" text-anchor="middle">税金を計算する</text>
        <!-- Overlap labels -->
        <text x="310" y="110" font-size="10" fill="#555" text-anchor="middle">税効果会計</text>
        <text x="400" y="110" font-size="10" fill="#555" text-anchor="middle">節税戦略</text>
        <text x="350" y="185" font-size="10" fill="#555" text-anchor="middle">CF管理</text>
        <!-- Center -->
        <text x="350" y="145" font-size="12" font-weight="700" fill="#1a365d" text-anchor="middle">CFO</text>
      </svg>
    </div>

    <!-- Diagram: 事業規模の進化 -->
    <div class="diagram">
      <h3 style="border:none;padding:0;margin:0 0 20px;font-size:16px;color:var(--primary);">事業規模の進化と必要な知識</h3>
      <svg viewBox="0 0 750 140" xmlns="http://www.w3.org/2000/svg" style="max-width:700px;">
        <!-- Arrow base -->
        <rect x="30" y="55" width="690" height="30" rx="15" fill="#e2e8f0"/>
        <polygon points="720,70 700,50 700,90" fill="#e2e8f0"/>
        <!-- Stages -->
        <circle cx="100" cy="70" r="30" fill="#2b6cb0"/>
        <text x="100" y="75" font-size="10" fill="#fff" text-anchor="middle" font-weight="700">個人</text>
        <text x="100" y="110" font-size="10" fill="#4a5568" text-anchor="middle">確定申告</text>
        <text x="100" y="124" font-size="10" fill="#4a5568" text-anchor="middle">青色申告</text>

        <circle cx="270" cy="70" r="35" fill="#6b46c1"/>
        <text x="270" y="68" font-size="10" fill="#fff" text-anchor="middle" font-weight="700">中小</text>
        <text x="270" y="82" font-size="10" fill="#fff" text-anchor="middle" font-weight="700">法人</text>
        <text x="270" y="116" font-size="10" fill="#4a5568" text-anchor="middle">法人税・社保</text>
        <text x="270" y="130" font-size="10" fill="#4a5568" text-anchor="middle">役員報酬設計</text>

        <circle cx="460" cy="70" r="40" fill="#c05621"/>
        <text x="460" y="68" font-size="10" fill="#fff" text-anchor="middle" font-weight="700">中堅</text>
        <text x="460" y="82" font-size="10" fill="#fff" text-anchor="middle" font-weight="700">企業</text>
        <text x="460" y="122" font-size="10" fill="#4a5568" text-anchor="middle">連結・移転価格</text>
        <text x="460" y="136" font-size="10" fill="#4a5568" text-anchor="middle">管理会計</text>

        <circle cx="640" cy="70" r="44" fill="#2f855a"/>
        <text x="640" y="68" font-size="10" fill="#fff" text-anchor="middle" font-weight="700">上場</text>
        <text x="640" y="82" font-size="10" fill="#fff" text-anchor="middle" font-weight="700">企業</text>
        <text x="640" y="126" font-size="10" fill="#4a5568" text-anchor="middle">開示・IR・J-SOX</text>
        <text x="640" y="140" font-size="10" fill="#4a5568" text-anchor="middle">IFRS・ESG</text>
      </svg>
    </div>

    <!-- Diagram: 財務三表の連動 -->
    <div class="diagram">
      <h3 style="border:none;padding:0;margin:0 0 20px;font-size:16px;color:var(--primary);">財務三表の連動メカニズム</h3>
      <svg viewBox="0 0 700 280" xmlns="http://www.w3.org/2000/svg" style="max-width:600px;">
        <!-- PL Box -->
        <rect x="20" y="20" width="200" height="240" rx="12" fill="#fff" stroke="#c53030" stroke-width="2"/>
        <rect x="20" y="20" width="200" height="40" rx="12" fill="#c53030"/>
        <rect x="20" y="48" width="200" height="12" fill="#c53030"/>
        <text x="120" y="46" font-size="14" fill="#fff" text-anchor="middle" font-weight="700">損益計算書 (PL)</text>
        <text x="40" y="85" font-size="12" fill="#4a5568">売上高</text>
        <text x="40" y="110" font-size="12" fill="#4a5568">− 売上原価</text>
        <text x="40" y="135" font-size="12" fill="#4a5568">− 販管費</text>
        <text x="40" y="165" font-size="12" fill="#4a5568">= 営業利益</text>
        <text x="40" y="195" font-size="12" fill="#4a5568">± 営業外損益</text>
        <text x="40" y="230" font-size="14" fill="#c53030" font-weight="700">= 当期純利益</text>
        <!-- BS Box -->
        <rect x="260" y="20" width="200" height="240" rx="12" fill="#fff" stroke="#2b6cb0" stroke-width="2"/>
        <rect x="260" y="20" width="200" height="40" rx="12" fill="#2b6cb0"/>
        <rect x="260" y="48" width="200" height="12" fill="#2b6cb0"/>
        <text x="360" y="46" font-size="14" fill="#fff" text-anchor="middle" font-weight="700">貸借対照表 (BS)</text>
        <line x1="360" y1="65" x2="360" y2="252" stroke="#e2e8f0" stroke-width="1"/>
        <text x="290" y="90" font-size="11" fill="#4a5568">流動資産</text>
        <text x="290" y="130" font-size="11" fill="#4a5568">固定資産</text>
        <text x="380" y="90" font-size="11" fill="#4a5568">流動負債</text>
        <text x="380" y="130" font-size="11" fill="#4a5568">固定負債</text>
        <text x="380" y="180" font-size="11" fill="#2b6cb0" font-weight="700">純資産</text>
        <text x="380" y="200" font-size="10" fill="#2b6cb0">(利益剰余金)</text>
        <!-- CF Box -->
        <rect x="500" y="20" width="180" height="240" rx="12" fill="#fff" stroke="#2f855a" stroke-width="2"/>
        <rect x="500" y="20" width="180" height="40" rx="12" fill="#2f855a"/>
        <rect x="500" y="48" width="180" height="12" fill="#2f855a"/>
        <text x="590" y="46" font-size="13" fill="#fff" text-anchor="middle" font-weight="700">CF計算書</text>
        <text x="520" y="90" font-size="11" fill="#4a5568">営業CF</text>
        <text x="520" y="140" font-size="11" fill="#4a5568">投資CF</text>
        <text x="520" y="190" font-size="11" fill="#4a5568">財務CF</text>
        <text x="520" y="235" font-size="12" fill="#2f855a" font-weight="700">= 現金増減</text>
        <!-- Arrows -->
        <path d="M 120 245 Q 120 270 260 235" stroke="#c53030" stroke-width="2" fill="none" marker-end="url(#arrowR)"/>
        <path d="M 340 255 Q 400 280 520 240" stroke="#2b6cb0" stroke-width="2" fill="none" marker-end="url(#arrowB)"/>
        <text x="170" y="270" font-size="10" fill="#c53030">純利益→利益剰余金</text>
        <text x="430" y="275" font-size="10" fill="#2b6cb0">現金→BS資産</text>
        <defs>
          <marker id="arrowR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#c53030"/>
          </marker>
          <marker id="arrowB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#2b6cb0"/>
          </marker>
        </defs>
      </svg>
    </div>

    <!-- Additional charts -->
    <div class="chart-grid">
      <div class="chart-card">
        <h3>社会保険料率の内訳</h3>
        <canvas id="chart-social-ins"></canvas>
      </div>
      <div class="chart-card">
        <h3>個人 vs 法人の税負担比較</h3>
        <canvas id="chart-individual-vs-corp"></canvas>
      </div>
    </div>

    <!-- Main textbook content -->
    {html_content}

  </div>
</div>

<!-- Scroll to top -->
<button class="scroll-top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" aria-label="トップへ戻る">&#8593;</button>

<script>
// Scroll to top button visibility
window.addEventListener('scroll', () => {{
  const btn = document.querySelector('.scroll-top');
  btn.classList.toggle('visible', window.scrollY > 500);
}});

// Close mobile sidebar when clicking a link
document.querySelectorAll('.sidebar a').forEach(a => {{
  a.addEventListener('click', () => {{
    document.querySelector('.sidebar').classList.remove('open');
  }});
}});

// Active TOC highlighting
const observer = new IntersectionObserver(entries => {{
  entries.forEach(entry => {{
    if (entry.isIntersecting) {{
      document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));
      const id = entry.target.id;
      const link = document.querySelector(`.sidebar a[href="#${{id}}"]`);
      if (link) {{
        link.style.color = '#fff';
        link.style.borderLeftColor = '#b45309';
      }}
    }}
  }});
}}, {{ threshold: 0.3 }});

document.querySelectorAll('h1[id], h2[id]').forEach(h => observer.observe(h));

// ===== Charts =====
const chartColors = {{
  blue: '#2b6cb0',
  red: '#c53030',
  green: '#2f855a',
  orange: '#c05621',
  purple: '#6b46c1',
  teal: '#2c7a7b',
  gray: '#718096',
  yellow: '#d69e2e',
}};

// Income tax progressive rates
new Chart(document.getElementById('chart-income-tax'), {{
  type: 'bar',
  data: {{
    labels: ['195万以下', '〜330万', '〜695万', '〜900万', '〜1800万', '〜4000万', '4000万超'],
    datasets: [{{
      label: '所得税率',
      data: [5, 10, 20, 23, 33, 40, 45],
      backgroundColor: [
        '#bee3f8', '#90cdf4', '#63b3ed', '#4299e1', '#3182ce', '#2b6cb0', '#1a365d'
      ],
      borderRadius: 4,
    }}, {{
      label: '住民税(一律)',
      data: [10, 10, 10, 10, 10, 10, 10],
      backgroundColor: 'rgba(237,137,54,0.5)',
      borderRadius: 4,
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ font: {{ size: 11 }} }} }},
      tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': ' + ctx.raw + '%' }} }}
    }},
    scales: {{
      x: {{ stacked: true, ticks: {{ font: {{ size: 10 }} }} }},
      y: {{ stacked: true, max: 60, ticks: {{ callback: v => v + '%', font: {{ size: 11 }} }} }}
    }}
  }}
}});

// Revenue composition
new Chart(document.getElementById('chart-revenue'), {{
  type: 'doughnut',
  data: {{
    labels: ['所得税 (21兆)', '法人税 (15兆)', '消費税 (23兆)', 'その他税収', 'その他収入', '公債金 (33兆)'],
    datasets: [{{
      data: [21, 15, 23, 12, 7, 33],
      backgroundColor: [
        chartColors.blue, chartColors.purple, chartColors.orange,
        chartColors.teal, chartColors.gray, chartColors.red
      ],
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }}, padding: 8 }} }}
    }}
  }}
}});

// Expense composition
new Chart(document.getElementById('chart-expense'), {{
  type: 'doughnut',
  data: {{
    labels: ['社会保障 (38兆)', '国債費 (26兆)', '地方交付税 (17兆)', '防衛 (8兆)', '公共事業 (6兆)', '文教科学 (5兆)', 'その他 (15兆)'],
    datasets: [{{
      data: [38, 26, 17, 8, 6, 5, 15],
      backgroundColor: [
        chartColors.red, chartColors.gray, chartColors.teal,
        chartColors.blue, chartColors.green, chartColors.purple, chartColors.yellow
      ],
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }}, padding: 8 }} }}
    }}
  }}
}});

// International corporate tax comparison
new Chart(document.getElementById('chart-corp-intl'), {{
  type: 'bar',
  data: {{
    labels: ['日本', '米国', '英国', 'ドイツ', 'フランス', '韓国', 'シンガポール', '香港'],
    datasets: [{{
      label: '法人実効税率',
      data: [30.6, 25.8, 25.0, 29.9, 25.8, 24.2, 17.0, 16.5],
      backgroundColor: [
        chartColors.red, chartColors.blue, chartColors.teal, chartColors.orange,
        chartColors.purple, chartColors.green, chartColors.gray, chartColors.yellow
      ],
      borderRadius: 4,
    }}]
  }},
  options: {{
    responsive: true,
    indexAxis: 'y',
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: ctx => ctx.raw + '%' }} }}
    }},
    scales: {{
      x: {{ max: 35, ticks: {{ callback: v => v + '%', font: {{ size: 11 }} }} }}
    }}
  }}
}});

// Social insurance
new Chart(document.getElementById('chart-social-ins'), {{
  type: 'bar',
  data: {{
    labels: ['厚生年金', '健康保険', '介護保険', '雇用保険', '労災保険', '子育て拠出金'],
    datasets: [{{
      label: '本人負担',
      data: [9.15, 5.0, 0.8, 0.55, 0, 0],
      backgroundColor: chartColors.blue,
      borderRadius: 4,
    }}, {{
      label: '事業主負担',
      data: [9.15, 5.0, 0.8, 0.90, 0.3, 0.36],
      backgroundColor: chartColors.orange,
      borderRadius: 4,
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ font: {{ size: 11 }} }} }},
      tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': ' + ctx.raw + '%' }} }}
    }},
    scales: {{
      x: {{ stacked: true, ticks: {{ font: {{ size: 10 }} }} }},
      y: {{ stacked: true, ticks: {{ callback: v => v + '%', font: {{ size: 11 }} }} }}
    }}
  }}
}});

// Individual vs Corporate tax burden
new Chart(document.getElementById('chart-individual-vs-corp'), {{
  type: 'line',
  data: {{
    labels: ['300万', '500万', '700万', '900万', '1200万', '1800万', '3000万', '5000万'],
    datasets: [{{
      label: '個人 (所得税+住民税+社保)',
      data: [18, 24, 29, 33, 38, 44, 50, 53],
      borderColor: chartColors.red,
      backgroundColor: 'rgba(197,48,48,0.1)',
      fill: true,
      tension: 0.3,
    }}, {{
      label: '法人 (法人税+社保+役員報酬)',
      data: [22, 25, 27, 29, 31, 33, 35, 36],
      borderColor: chartColors.blue,
      backgroundColor: 'rgba(43,108,176,0.1)',
      fill: true,
      tension: 0.3,
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }} }} }},
      tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ': 約' + ctx.raw + '%' }} }}
    }},
    scales: {{
      y: {{ ticks: {{ callback: v => v + '%', font: {{ size: 11 }} }}, max: 60 }}
    }}
  }}
}});
</script>
</body>
</html>'''

    with open('/Users/renmurata/Documents/tax_finance_textbook/textbook.html', 'w') as f:
        f.write(page)

    print(f"HTML file generated successfully!")
    import os
    size = os.path.getsize('/Users/renmurata/Documents/tax_finance_textbook/textbook.html')
    print(f"File size: {size:,} bytes ({size/1024/1024:.1f} MB)")

if __name__ == '__main__':
    build_html()
