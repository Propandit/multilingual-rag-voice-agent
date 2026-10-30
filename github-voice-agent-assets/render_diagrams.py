"""Render public architecture diagrams; no private project inputs are read."""
from pathlib import Path
from html import escape
import argparse
import asyncio
import json

ROOT = Path(__file__).resolve().parent
C = {
    'ink': '#12253F', 'muted': '#51627A', 'line': '#8291A6',
    'local': '#0F766E', 'local_bg': '#EAF7F4',
    'cloud': '#6D45B7', 'cloud_bg': '#F2EDFB',
    'device': '#2F5D9A', 'device_bg': '#EDF3FC',
    'amber': '#A15C0B', 'amber_bg': '#FFF5E6',
}


class Diagram:
    def __init__(self, width, height, title, description):
        self.width, self.height = width, height
        self.parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs>
<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z" fill="{C['line']}"/></marker>
<marker id="data" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z" fill="{C['local']}"/></marker>
</defs>
<rect width="100%" height="100%" fill="#FFFFFF"/>
<g font-family="Segoe UI, Arial, sans-serif">''']

    def text(self, x, y, value, size=21, color='ink', weight=400):
        self.parts.append(f'<text x="{x}" y="{y}" fill="{C.get(color, color)}" font-size="{size}" font-weight="{weight}">{escape(value)}</text>')

    def rect(self, x, y, w, h, fill, stroke='none', radius=20):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')

    def card(self, x, y, w, h, title, lines, kind='local', label=None):
        self.rect(x, y, w, h, C[kind + '_bg'], C[kind])
        base = y + 38
        if label:
            self.text(x + 22, y + 27, label.upper(), 14, kind, 700)
            base = y + 61
        self.text(x + 22, base, title, 25, 'ink', 650)
        for n, line in enumerate(lines):
            self.text(x + 22, base + 33 + n * 27, line, 20, 'muted')

    def arrow(self, points, data=False, end=True):
        path = 'M ' + ' L '.join(f'{x} {y}' for x, y in points)
        color = C['local'] if data else C['line']
        dash = ' stroke-dasharray="8 7"' if data else ''
        marker = f' marker-end="url(#{"data" if data else "arrow"})"' if end else ''
        self.parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round"{dash}{marker}/>')

    def save(self, filename):
        (ROOT / filename).write_text('\n'.join(self.parts + ['</g></svg>']), encoding='utf-8')


def pipeline():
    d = Diagram(1600, 1260, 'RAG voice agent pipeline',
                'Approved sources are extracted and validated into text and structured stores. Visitor speech reaches a cloud conversational model that calls local retrieval tools, receives evidence, generates an answer, and streams speech to the handset.')
    d.text(60, 76, 'From approved knowledge to a spoken answer', 44, weight=700)
    d.text(60, 119, 'Multilingual voice agent  /  Native handset  /  Retrieval at answer time', 23, 'muted')
    d.rect(40, 164, 1520, 266, '#F8FAFC', '#DFE6EE', 24)
    d.text(65, 204, '01  PREPARE THE KNOWLEDGE', 20, weight=700)
    d.card(65, 234, 300, 158, 'Approved sources', ['Website text and FAQs', 'Documents, CSV, reports'])
    d.card(440, 234, 300, 158, 'Extract & normalize', ['Parse text and tables', 'Preserve fields and units'])
    d.card(815, 234, 300, 158, 'Validate & organize', ['Review quality and dates', 'Keep source references'])
    d.card(1190, 234, 340, 158, 'Knowledge store', ['Text: SQLite FTS5', 'Tables: dated snapshots'])
    for a, b in [(365, 440), (740, 815), (1115, 1190)]:
        d.arrow([(a, 313), (b-8, 313)])

    d.rect(40, 458, 1520, 648, '#F8FAFC', '#DFE6EE', 24)
    d.text(65, 500, '02  RETRIEVE EVIDENCE AND ANSWER', 20, weight=700)
    # Data dependencies travel outside the conversation arrows.
    d.arrow([(1530, 313), (1578, 313), (1578, 580), (1538, 580)], data=True)
    d.arrow([(1578, 580), (1578, 750), (1538, 750)], data=True)
    d.card(65, 577, 300, 151, 'Visitor speaks', ['Handset microphone', 'Native audio streaming'], 'device')
    d.card(440, 577, 300, 151, 'Speech to text', ['ElevenLabs Agents', 'Recognize visitor speech'], 'cloud')
    d.card(815, 577, 300, 151, 'LLM selects tools', ['Understand the question', 'Request relevant evidence'], 'cloud')
    d.card(1190, 531, 340, 123, 'Search text', ['FTS5 + relevance ranking', 'Explanations and procedures'])
    d.card(1190, 701, 340, 123, 'Query structured data', ['Exact fields and units', 'Figures and comparisons'])
    d.arrow([(365, 652), (432, 652)])
    d.arrow([(740, 652), (807, 652)])
    d.arrow([(1115, 610), (1152, 610), (1152, 592), (1182, 592)])
    d.arrow([(1115, 685), (1152, 685), (1152, 762), (1182, 762)])
    d.arrow([(1530, 620), (1546, 620), (1546, 861), (1360, 861)], end=False)
    d.arrow([(1360, 824), (1360, 912)])
    d.text(1190, 893, 'Tool results', 18, 'muted')
    d.card(1190, 920, 340, 145, 'Retrieved evidence', ['Relevant passages or rows', 'Source and freshness metadata'])
    d.card(815, 920, 300, 145, 'Generate answer', ['LLM uses returned evidence', 'Follow the visitor\'s language'], 'cloud')
    d.card(440, 920, 300, 145, 'Text to speech', ['Multilingual voice', 'Natural pace and phrasing'], 'cloud')
    d.card(65, 920, 300, 145, 'Visitor hears reply', ['Audio streams to speaker', 'Conversation continues'], 'device')
    for a, b in [(1190, 1115), (815, 740), (440, 365)]:
        d.arrow([(a, 992), (b+8, 992)])

    d.rect(65, 1140, 18, 18, C['local_bg'], C['local'], 4)
    d.text(96, 1156, 'Local knowledge & tools', 19, 'muted')
    d.rect(395, 1140, 18, 18, C['cloud_bg'], C['cloud'], 4)
    d.text(426, 1156, 'Cloud conversation', 19, 'muted')
    d.rect(686, 1140, 18, 18, C['device_bg'], C['device'], 4)
    d.text(717, 1156, 'Physical handset', 19, 'muted')
    d.arrow([(962, 1149), (1011, 1149)], data=True)
    d.text(1028, 1156, 'Reads stored data', 19, 'muted')
    d.text(65, 1203, 'English opening, then English / Hindi / Hinglish. Browser optional; cloud voice needs internet.', 21, 'muted')
    d.save('rag-voice-pipeline.svg')


def refresh():
    d = Diagram(1600, 760, 'Validated data refresh pipeline',
                'A scheduled worker fetches a report and validates it. Valid reports become snapshots used by answer tools. Invalid reports leave the last valid snapshot available and record the failure.')
    d.text(60, 76, 'Keep answers connected to validated data', 44, weight=700)
    d.text(60, 119, 'Scheduled refresh  /  Versioned snapshots  /  Last valid data retained on failure', 23, 'muted')
    d.rect(40, 167, 1520, 498, '#F8FAFC', '#DFE6EE', 24)
    d.card(65, 242, 250, 151, 'Scheduled worker', ['Run when due', 'Catch up on startup'])
    d.card(370, 242, 250, 151, 'Fetch source', ['Collect the report', 'Record retrieval time'])
    d.card(675, 242, 250, 151, 'Validate report', ['Check expected fields', 'Check units and values'])
    d.card(980, 242, 250, 151, 'Publish snapshot', ['Save validated data', 'Keep earlier versions'])
    d.card(1285, 242, 250, 151, 'Answer tools', ['Use latest validated', 'available snapshot'])
    for a, b in [(315, 370), (620, 675), (925, 980), (1230, 1285)]:
        d.arrow([(a, 317), (b-8, 317)])
    d.text(937, 299, 'PASS', 13, 'local', 700)
    d.arrow([(800, 393), (800, 482)])
    d.text(815, 446, 'FAIL OR UNAVAILABLE', 16, 'amber', 700)
    d.card(675, 490, 555, 132, 'Keep the last valid snapshot', ['Record the failed attempt and retry later.', 'Expose freshness limits when answering.'], 'amber')
    d.arrow([(1230, 556), (1410, 556), (1410, 401)])
    d.text(1260, 533, 'Fallback data', 18, 'muted')
    d.text(65, 704, 'A daily fetch does not guarantee daily source changes. Documents need a separate update workflow.', 22, 'muted')
    d.save('data-refresh-pipeline.svg')


async def render(browser_path):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        opts = {'headless': True}
        if browser_path:
            opts['executable_path'] = browser_path
        browser = await p.chromium.launch(**opts)
        for filename, height in [('rag-voice-pipeline', 1260), ('data-refresh-pipeline', 760)]:
            page = await browser.new_page(viewport={'width': 1600, 'height': height}, device_scale_factor=2)
            svg = (ROOT / f'{filename}.svg').read_text(encoding='utf-8')
            await page.set_content('<style>body{margin:0;background:white}svg{display:block}</style>' + svg)
            await page.evaluate('document.fonts.ready')
            # Detect overflowing text before the asset is published.
            overflow = await page.locator('svg text').evaluate_all('els => els.filter(e => {const b=e.getBBox();return b.x<0 || b.y<0 || b.x+b.width>1600 || b.y+b.height>'+str(height)+'}).map(e=>e.textContent)')
            if overflow:
                raise RuntimeError('Text extends beyond canvas: ' + json.dumps(overflow))
            await page.screenshot(path=str(ROOT / f'{filename}.png'))
            await page.close()
        await browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', help='Optional path to an existing Chromium executable')
    args = parser.parse_args()
    pipeline()
    refresh()
    asyncio.run(render(args.browser))
