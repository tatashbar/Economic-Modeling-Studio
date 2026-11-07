#!/usr/bin/env python3
"""Write a Word report (.docx) or a PowerPoint deck (.pptx) from a Markdown results report. Standard library only.

Usage:  python tools/report.py docx <report.md> --out <report.docx> [--root <dir>]
        python tools/report.py pptx <report.md> --out <deck.pptx> [--root <dir>]
        python tools/report.py bundle <report.md> --out <folder> [--root <dir>] [--no-zip]

Supported Markdown: headings (# to ####), paragraphs, **bold**, *italic*, `code`, [links](url),
bullet and numbered lists (two levels), pipe tables, code blocks, block quotes and images
(![caption](chart.png)). A paragraph that names a chart file in backticks (`.../chart.png`) also
gets the chart embedded below it, so a results pack that only points to its charts still shows them.
Images are PNG, JPEG or GIF, scaled to the page width and numbered as figures; tables are numbered
too. Image paths are resolved against the report's folder, then --root (default: the current folder).
The first level-1 heading is the document title. A missing image is reported and listed in the
document as missing; it never stops the report.

The deck (16:9) has a title slide, a questions-and-answers slide from the Summary section, and for
each question or objective (each level-2 section) a slide with the answer next to its first chart,
the method as a footnote and the caveats; further charts and tables get slides of their own, and long
tables are split. "Not assessed" and "Annex" sections become table slides.

The bundle collects the report, the Word file and the deck, every chart, code file and run folder the
report names into one folder with an index (README.md), and zips it. Raw, restricted and confidential
data are never copied.
"""
import argparse
import datetime
import os
import re
import struct
import sys
import zipfile
from xml.sax.saxutils import escape

PAGE_W_TWIPS, MARGIN_TWIPS = 12240, 1440
TEXT_W_EMU = int((PAGE_W_TWIPS - 2 * MARGIN_TWIPS) / 1440 * 914400)
MAX_IMG_H_EMU = int(7.5 * 914400)
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif")
NUM_RE = re.compile(r"^[\s(+\-−–]*[$€£]?\d[\d,.]*\s*%?\)?$|^[+\-−–]?\d*\.?\d+(e[+\-]?\d+)?$|^—$|^-$")

W = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
     'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
     'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
     'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
     'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')


# ---------------------------------------------------------------- images
def image_size(path):
    """(width_px, height_px, dpi_x, dpi_y) for PNG, JPEG or GIF; dpi defaults to 96."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        dx = dy = 96.0
        i = 8
        while i + 8 <= len(data):
            n, typ = struct.unpack(">I4s", data[i:i + 8])
            if typ == b"pHYs" and n == 9:
                px, py, unit = struct.unpack(">IIB", data[i + 8:i + 17])
                if unit == 1 and px and py:
                    dx, dy = px * 0.0254, py * 0.0254
                break
            if typ == b"IDAT":
                break
            i += 12 + n
        return w, h, dx, dy
    if data[:6] in (b"GIF87a", b"GIF89a"):
        w, h = struct.unpack("<HH", data[6:10])
        return w, h, 96.0, 96.0
    if data[:2] == b"\xff\xd8":
        i, dx, dy = 2, 96.0, 96.0
        while i + 4 <= len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg = struct.unpack(">H", data[i + 2:i + 4])[0]
            if marker == 0xE0 and data[i + 4:i + 9] == b"JFIF\x00":
                unit, x, y = struct.unpack(">BHH", data[i + 11:i + 16])
                if unit == 1 and x and y:
                    dx, dy = float(x), float(y)
                elif unit == 2 and x and y:
                    dx, dy = x * 2.54, y * 2.54
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h, dx, dy
            i += 2 + seg
    raise ValueError("unsupported or damaged image: %s" % path)


# ---------------------------------------------------------------- inline text
INLINE = re.compile(r"(\*\*(?P<b>.+?)\*\*|`(?P<c>[^`]+)`|(?<![\w*])\*(?P<i>[^*\s][^*]*?)\*(?![\w*])"
                    r"|\[(?P<lt>[^\]]+)\]\((?P<lu>[^)\s]+)\))")


def runs(text, bold=False, italic=False, size=None):
    out, pos = [], 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            out.append(run(text[pos:m.start()], bold, italic, size=size))
        if m.group("b") is not None:
            out.extend(runs(m.group("b"), True, italic, size))
        elif m.group("i") is not None:
            out.extend(runs(m.group("i"), bold, True, size))
        elif m.group("c") is not None:
            out.append(run(m.group("c"), bold, italic, code=True, size=size))
        else:
            label, url = m.group("lt"), m.group("lu")
            out.extend(runs(label, bold, italic, size))
            if url != label and not url.startswith("#"):
                out.append(run(" (%s)" % url, bold, italic, size=size, color="595959"))
        pos = m.end()
    if pos < len(text):
        out.append(run(text[pos:], bold, italic, size=size))
    return "".join(out)


def run(text, bold=False, italic=False, code=False, size=None, color=None):
    pr = ""
    if code:
        pr += '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>'
    if bold:
        pr += "<w:b/>"
    if italic:
        pr += "<w:i/>"
    if color:
        pr += '<w:color w:val="%s"/>' % color
    if size or code:
        pr += '<w:sz w:val="%d"/>' % (size or 19)
    pr = "<w:rPr>%s</w:rPr>" % pr if pr else ""
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (pr, escape(text))


def para(content, style=None, extra=""):
    ppr = ""
    if style or extra:
        ppr = "<w:pPr>%s%s</w:pPr>" % ('<w:pStyle w:val="%s"/>' % style if style else "", extra)
    return "<w:p>%s%s</w:p>" % (ppr, content)


# ---------------------------------------------------------------- builder
class Report:
    def __init__(self, md_path, root):
        self.md_path, self.root = md_path, root
        self.base = os.path.dirname(os.path.abspath(md_path))
        self.body, self.media, self.rels = [], [], []
        self.numbered_lists = 0
        self.fig = self.tab = 0
        self.title = None
        self.missing = []
        self.embedded = set()

    def resolve(self, ref):
        ref = ref.strip().strip("<>")
        if os.path.isabs(ref):
            return ref if os.path.isfile(ref) else None
        for b in (self.base, self.root):
            p = os.path.normpath(os.path.join(b, ref))
            if os.path.isfile(p):
                return p
        return None

    def image(self, ref, caption):
        path = self.resolve(ref)
        if path is None:
            self.missing.append(ref)
            self.body.append(para(run("[Chart not found: %s]" % ref, italic=True, color="C00000")))
            return
        key = os.path.normcase(os.path.abspath(path))
        if key in self.embedded:
            return
        try:
            w, h, dx, dy = image_size(path)
        except (ValueError, OSError, struct.error) as e:
            self.missing.append(ref)
            self.body.append(para(run("[Chart could not be read: %s (%s)]" % (ref, e), italic=True, color="C00000")))
            return
        self.embedded.add(key)
        cx, cy = int(w / dx * 914400), int(h / dy * 914400)
        scale = min(1.0, TEXT_W_EMU / cx, MAX_IMG_H_EMU / cy)
        cx, cy = int(cx * scale), int(cy * scale)
        n = len(self.media) + 1
        ext = os.path.splitext(path)[1].lower().replace("jpeg", "jpg")
        name = "image%d%s" % (n, ext)
        self.media.append((name, path))
        rid = "rIdImg%d" % n
        self.rels.append('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                         'relationships/image" Target="media/%s"/>' % (rid, name))
        drawing = (
            '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/><wp:docPr id="%d" name="Figure %d"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic><pic:nvPicPr><pic:cNvPr id="%d" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
            % (cx, cy, n, n, n, escape(name), rid, cx, cy))
        self.body.append(para(drawing, "Figure"))
        self.fig += 1
        cap = caption.strip()
        if not cap:
            cap = os.path.splitext(os.path.basename(path))[0].replace("-", " ").replace("_", " ")
            cap = cap[:1].upper() + cap[1:]
        self.body.append(para(run("Figure %d. " % self.fig, bold=True) + runs(cap), "Caption"))

    def table(self, rows):
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        header, data = cells[0], [r for r in cells[2:]]
        ncol = len(header)
        size = 16 if ncol >= 9 else 18 if ncol >= 6 else None
        caption = getattr(self, "pending_caption", None)
        self.pending_caption = None
        if caption:
            self.tab += 1
            self.body.append(para(run("Table %d. " % self.tab, bold=True) + runs(caption), "Caption"))
        numeric = [all(NUM_RE.match(r[j]) or not r[j] for r in data if j < len(r)) and
                   any(r[j] for r in data if j < len(r)) for j in range(ncol)]
        xml = ['<w:tbl><w:tblPr><w:tblStyle w:val="ReportTable"/><w:tblW w:w="5000" w:type="pct"/>'
               '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" '
               'w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>']
        xml += ['<w:gridCol/>' for _ in range(ncol)]
        xml.append("</w:tblGrid>")
        for ri, r in enumerate([header] + data):
            r = (r + [""] * ncol)[:ncol]
            trpr = '<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' if ri == 0 else '<w:trPr><w:cantSplit/></w:trPr>'
            xml.append("<w:tr>%s" % trpr)
            for j, c in enumerate(r):
                shade = '<w:shd w:val="clear" w:color="auto" w:fill="1F3864"/>' if ri == 0 else \
                    ('<w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>' if ri % 2 == 0 else "")
                jc = '<w:jc w:val="right"/>' if (numeric[j] and j > 0) else ""
                content = runs(c, bold=(ri == 0), size=size)
                if ri == 0:
                    content = content.replace("<w:rPr>", '<w:rPr><w:color w:val="FFFFFF"/>')
                xml.append('<w:tc><w:tcPr>%s</w:tcPr><w:p><w:pPr><w:pStyle w:val="TableText"/>%s</w:pPr>%s</w:p></w:tc>'
                           % (shade, jc, content))
            xml.append("</w:tr>")
        xml.append("</w:tbl>")
        self.body.append("".join(xml))
        self.body.append(para("", "AfterTable"))

    def list_item(self, text, ordered, level):
        if ordered:
            num = self.current_num
        else:
            num = 1
        extra = '<w:numPr><w:ilvl w:val="%d"/><w:numId w:val="%d"/></w:numPr>' % (min(level, 1), num)
        self.body.append(para(runs(text), "ListParagraph", extra))
        self.autoembed(text)

    def autoembed(self, text):
        for ref in re.findall(r"`([^`]+\.(?:png|jpe?g|gif))`", text, flags=re.I):
            if self.resolve(ref):
                self.image(ref, "")

    def build(self, text):
        lines = text.replace("\r\n", "\n").split("\n")
        i, para_buf, in_list = 0, [], None
        self.pending_caption = None

        def flush():
            if para_buf:
                t = " ".join(s.strip() for s in para_buf)
                para_buf.clear()
                m = re.match(r"^\*\*(Table[^*]*|[^*]{3,120})\*\*\s*$", t)
                nxt = i
                while nxt < len(lines) and not lines[nxt].strip():
                    nxt += 1
                if m and nxt < len(lines) and lines[nxt].lstrip().startswith("|"):
                    self.pending_caption = m.group(1)
                    return
                self.body.append(para(runs(t)))
                self.autoembed(t)

        while i < len(lines):
            line = lines[i]
            s = line.strip()
            if s.startswith("```"):
                flush()
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    self.body.append(para(run(lines[i], code=True), "Code"))
                    i += 1
                i += 1
                continue
            if not s:
                flush()
                in_list = None
                i += 1
                continue
            m = re.match(r"^(#{1,4})\s+(.*?)\s*#*$", s)
            if m:
                flush()
                level, t = len(m.group(1)), m.group(2)
                if level == 1 and self.title is None:
                    self.title = re.sub(r"[*`]", "", t)
                    self.body.append(para(runs(t), "Title"))
                    self.body.append(para(run(datetime.date.today().strftime("%d %B %Y").lstrip("0")), "Subtitle"))
                else:
                    self.body.append(para(runs(t), "Heading%d" % min(level if self.title is None else max(level - 1, 1), 3)))
                in_list = None
                i += 1
                continue
            if s.startswith("|"):
                flush()
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    rows.append(lines[i])
                    i += 1
                if len(rows) >= 2 and re.match(r"^\|?\s*:?-{2,}", rows[1].strip()):
                    self.table(rows)
                else:
                    for r in rows:
                        self.body.append(para(runs(r.strip())))
                continue
            m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", s)
            if m:
                flush()
                self.image(m.group(2).split(' "')[0], m.group(1))
                i += 1
                continue
            m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", line)
            if m:
                flush()
                indent = len(m.group(1).replace("\t", "    "))
                ordered = m.group(2)[0].isdigit()
                if ordered and in_list != "ol":
                    self.numbered_lists += 1
                    self.current_num = 1 + self.numbered_lists
                in_list = "ol" if ordered else "ul"
                item = [m.group(3)]
                i += 1
                while i < len(lines) and lines[i].strip() and lines[i].startswith(" " * (indent + 2)) \
                        and not re.match(r"^\s*([-*+]|\d+[.)])\s+", lines[i]):
                    item.append(lines[i].strip())
                    i += 1
                self.list_item(" ".join(item), ordered, 1 if indent >= 2 else 0)
                continue
            if s.startswith(">"):
                flush()
                self.body.append(para(runs(s.lstrip("> ").strip(), italic=True), "Quote"))
                i += 1
                continue
            if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
                flush()
                i += 1
                continue
            para_buf.append(line)
            i += 1
        flush()

    # ------------------------------------------------------------ package
    def write(self, out):
        sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter"/>'
                '<w:pgSz w:w="%d" w:h="15840"/><w:pgMar w:top="1440" w:right="%d" w:bottom="1440" w:left="%d" '
                'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>' % (PAGE_W_TWIPS, MARGIN_TWIPS, MARGIN_TWIPS))
        doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document %s><w:body>%s%s</w:body>'
               '</w:document>' % (W, "".join(self.body), sect))
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.'
                'openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                '<Relationship Id="rIdNumbering" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
                '<Relationship Id="rIdSettings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
                '<Relationship Id="rIdFooter" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
                + "".join(self.rels) + "</Relationships>")
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties '
                'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>%s</dc:title>'
                '<dc:creator>Economic Modeling Studio</dc:creator>'
                '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
                '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified></cp:coreProperties>'
                % (escape(self.title or "Results report"), now, now))
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", CONTENT_TYPES)
            z.writestr("_rels/.rels", ROOT_RELS)
            z.writestr("docProps/core.xml", core)
            z.writestr("word/document.xml", doc)
            z.writestr("word/_rels/document.xml.rels", rels)
            z.writestr("word/styles.xml", STYLES)
            z.writestr("word/numbering.xml", numbering(self.numbered_lists))
            z.writestr("word/settings.xml", SETTINGS)
            z.writestr("word/footer1.xml", FOOTER)
            for name, path in self.media:
                z.write(path, "word/media/" + name)


def numbering(n_ordered):
    def lvls(fmt):
        out = []
        for lv in range(2):
            ind = 360 + 360 * lv
            if fmt == "bullet":
                txt, f = ("•", "bullet") if lv == 0 else ("–", "bullet")
            else:
                txt, f = ("%%%d." % (lv + 1), "decimal") if lv == 0 else ("%%%d)" % (lv + 1), "lowerLetter")
            out.append('<w:lvl w:ilvl="%d"><w:start w:val="1"/><w:numFmt w:val="%s"/><w:lvlText w:val="%s"/>'
                       '<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="%d" w:hanging="360"/></w:pPr></w:lvl>'
                       % (lv, f, txt, ind + 360 * (lv == 0 and 0)))
        return "".join(out)
    nums = ['<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>']
    for k in range(n_ordered):
        nums.append('<w:num w:numId="%d"><w:abstractNumId w:val="1"/><w:lvlOverride w:ilvl="0">'
                    '<w:startOverride w:val="1"/></w:lvlOverride></w:num>' % (k + 2))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:numbering %s>'
            '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/>%s</w:abstractNum>'
            '<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>%s</w:abstractNum>'
            '%s</w:numbering>' % (W, lvls("bullet"), lvls("decimal"), "".join(nums)))


CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Default Extension="png" ContentType="image/png"/><Default Extension="jpg" ContentType="image/jpeg"/>'
    '<Default Extension="gif" ContentType="image/gif"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
    '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
    '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
    '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
    '</Types>')

ROOT_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
    '</Relationships>')

SETTINGS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings %s>'
            '<w:defaultTabStop w:val="720"/><w:characterSpacingControl w:val="doNotCompress"/>'
            '<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" '
            'w:val="15"/></w:compat></w:settings>' % W)

FOOTER = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr %s><w:p><w:pPr><w:jc w:val="center"/>'
          '</w:pPr><w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>'
          '<w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
          '<w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="separate"/></w:r>'
          '<w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:t>1</w:t></w:r>'
          '<w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>' % W)


def _style(sid, name, ppr="", rpr="", based="Normal", kind="paragraph", extra=""):
    return ('<w:style w:type="%s" w:styleId="%s"><w:name w:val="%s"/>%s%s<w:qFormat/>%s%s</w:style>'
            % (kind, sid, name, '<w:basedOn w:val="%s"/>' % based if based else "",
               '<w:next w:val="Normal"/>' if kind == "paragraph" else "", extra,
               ("<w:pPr>%s</w:pPr>" % ppr if ppr else "") + ("<w:rPr>%s</w:rPr>" % rpr if rpr else "")))


STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles %s>'
    '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="Calibri" '
    'w:cs="Calibri"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:lang w:val="en-US"/></w:rPr></w:rPrDefault>'
    '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
    '</w:docDefaults>'
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
    % W
    + _style("Title", "Title", '<w:spacing w:before="0" w:after="60"/>',
             '<w:b/><w:color w:val="1F3864"/><w:sz w:val="40"/>')
    + _style("Subtitle", "Subtitle", '<w:spacing w:after="360"/><w:pBdr><w:bottom w:val="single" w:sz="8" '
             'w:space="6" w:color="1F3864"/></w:pBdr>', '<w:color w:val="595959"/><w:sz w:val="22"/>')
    + _style("Heading1", "heading 1", '<w:keepNext/><w:spacing w:before="360" w:after="120"/><w:outlineLvl w:val="0"/>',
             '<w:b/><w:color w:val="1F3864"/><w:sz w:val="30"/>')
    + _style("Heading2", "heading 2", '<w:keepNext/><w:spacing w:before="240" w:after="80"/><w:outlineLvl w:val="1"/>',
             '<w:b/><w:color w:val="2E5395"/><w:sz w:val="25"/>')
    + _style("Heading3", "heading 3", '<w:keepNext/><w:spacing w:before="200" w:after="60"/><w:outlineLvl w:val="2"/>',
             '<w:b/><w:color w:val="404040"/><w:sz w:val="22"/>')
    + _style("ListParagraph", "List Paragraph", '<w:spacing w:after="60"/><w:ind w:left="720"/>')
    + _style("Caption", "caption", '<w:keepNext/><w:spacing w:before="120" w:after="80"/>',
             '<w:color w:val="404040"/><w:sz w:val="19"/>')
    + _style("Figure", "Figure", '<w:keepNext/><w:jc w:val="center"/><w:spacing w:before="120" w:after="0"/>')
    + _style("TableText", "Table Text", '<w:spacing w:before="20" w:after="20" w:line="240" w:lineRule="auto"/>',
             '<w:sz w:val="19"/>')
    + _style("AfterTable", "After Table", '<w:spacing w:after="60"/>', '<w:sz w:val="8"/>')
    + _style("Code", "Code", '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/><w:shd w:val="clear" '
             'w:color="auto" w:fill="F2F2F2"/>', '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="18"/>')
    + _style("Quote", "Quote", '<w:ind w:left="567"/><w:pBdr><w:left w:val="single" w:sz="12" w:space="8" '
             'w:color="A6A6A6"/></w:pBdr>', '<w:color w:val="404040"/>')
    + '<w:style w:type="table" w:styleId="ReportTable"><w:name w:val="Report Table"/><w:tblPr>'
      '<w:tblBorders><w:top w:val="single" w:sz="8" w:color="1F3864"/><w:bottom w:val="single" w:sz="8" '
      'w:color="1F3864"/><w:insideH w:val="single" w:sz="4" w:color="D9D9D9"/></w:tblBorders>'
      '<w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>'
    + "</w:styles>")


def to_docx(md_path, out, root=None):
    rep = Report(md_path, root or os.getcwd())
    with open(md_path, encoding="utf-8-sig") as f:
        rep.build(f.read())
    rep.write(out)
    return {"figures": rep.fig, "tables": rep.tab, "missing": rep.missing, "out": out}


# ---------------------------------------------------------------- PowerPoint
EMU = 914400
SLIDE_W, SLIDE_H = 12192000, 6858000
DARK, ACCENT, GREY = "1F3864", "2E5395", "595959"
P_NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
METHOD_LABELS = ("method", "data", "source", "approach")
CAVEAT_LABELS = ("caveat", "limitation", "risk")


def parse_blocks(text):
    """Title, intro blocks and [(heading, blocks)] from a Markdown report.
    Blocks: ('p', text), ('li', text, ordered), ('table', caption, rows), ('img', caption, ref)."""
    lines = text.replace("\r\n", "\n").split("\n")
    title, intro, sections = None, [], []
    cur = intro
    buf, i = [], 0

    def flush():
        if buf:
            cur.append(("p", " ".join(s.strip() for s in buf)))
            buf.clear()

    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if s.startswith("```"):
            flush()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
            i += 1
            continue
        if not s or re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            flush()
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*?)\s*#*$", s)
        if m:
            flush()
            if len(m.group(1)) == 1 and title is None:
                title = m.group(2)
            elif len(m.group(1)) <= 2 or not sections:
                sections.append((m.group(2), []))
                cur = sections[-1][1]
            else:
                cur.append(("p", "**%s**" % m.group(2)))
            i += 1
            continue
        if s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            if len(rows) >= 2 and all(re.match(r"^:?-{2,}:?$", c) for c in rows[1] if c):
                caption = ""
                if cur and cur[-1][0] == "p" and re.match(r"^\*\*[^*]+\*\*$", cur[-1][1]):
                    caption = cur.pop()[1].strip("*")
                cur.append(("table", caption, [rows[0]] + rows[2:]))
            else:
                cur.extend(("p", " | ".join(r)) for r in rows)
            continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", s)
        if m:
            flush()
            cur.append(("img", m.group(1), m.group(2).split(' "')[0]))
            i += 1
            continue
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", lines[i])
        if m:
            flush()
            item = [m.group(3)]
            i += 1
            while i < len(lines) and lines[i].strip() and lines[i].startswith("  ") \
                    and not re.match(r"^\s*([-*+]|\d+[.)])\s+", lines[i]):
                item.append(lines[i].strip())
                i += 1
            cur.append(("li", " ".join(item), m.group(2)[0].isdigit()))
            continue
        buf.append(s.lstrip("> ") if s.startswith(">") else s)
        i += 1
    flush()
    # charts named in backticks get their own image block
    for blocks in [intro] + [b for _, b in sections]:
        out = []
        for b in blocks:
            out.append(b)
            if b[0] in ("p", "li"):
                for ref in re.findall(r"`([^`]+\.(?:png|jpe?g|gif))`", b[1], flags=re.I):
                    out.append(("img", "", ref))
        blocks[:] = out
    return title, intro, sections


def plain(text):
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\*\*|`|(?<![\w*])\*(?!\s)|(?<!\s)\*(?![\w*])", "", t)


def a_runs(text, size, color="262626", bold=False):
    out, pos = [], 0

    def r(t, b, it, code=False):
        if not t:
            return ""
        pr = '<a:rPr lang="en-US" sz="%d"%s%s dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s</a:rPr>' % (
            int(size * 100), ' b="1"' if b else "", ' i="1"' if it else "", color,
            '<a:latin typeface="Consolas"/>' if code else "")
        return "<a:r>%s<a:t>%s</a:t></a:r>" % (pr, escape(t))

    for m in INLINE.finditer(text):
        out.append(r(text[pos:m.start()], bold, False))
        if m.group("b") is not None:
            out.append(r(plain(m.group("b")), True, False))
        elif m.group("i") is not None:
            out.append(r(m.group("i"), bold, True))
        elif m.group("c") is not None:
            out.append(r(m.group("c"), bold, False, code=True))
        else:
            out.append(r(m.group("lt"), bold, False))
        pos = m.end()
    out.append(r(text[pos:], bold, False))
    return "".join(out) or '<a:endParaRPr lang="en-US" sz="%d"/>' % int(size * 100)


def fit_size(paras, w, h, sizes=(20, 18, 16, 14, 13, 12, 11, 10, 9)):
    """Largest font size (pt) at which the paragraphs fit a box of w x h EMU, by a character-width estimate."""
    w_pt, h_pt = w / EMU * 72 - 14, h / EMU * 72 - 10
    for s in sizes:
        per_line = max(1, int(w_pt / (0.5 * s)))
        lines = sum(max(1, -(-len(plain(t)) // per_line)) for t in paras)
        if lines * s * 1.25 + len(paras) * s * 0.45 <= h_pt:
            return s
    return sizes[-1]


class Deck:
    def __init__(self, md_path, root):
        self.base = os.path.dirname(os.path.abspath(md_path))
        self.root = root
        self.slides, self.media, self.missing = [], [], []
        self.title = "Results"

    def resolve(self, ref):
        return Report.resolve(self, ref)

    # shapes ------------------------------------------------------------
    def _sp(self, sid, x, y, w, h, body, fill=None, anchor="t"):
        fill_xml = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill if fill else "<a:noFill/>"
        return ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Shape %d"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
                '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
                '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>%s</p:spPr>'
                '<p:txBody><a:bodyPr wrap="square" lIns="91440" tIns="45720" rIns="91440" bIns="45720" anchor="%s">'
                '<a:noAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>'
                % (sid, sid, x, y, w, h, fill_xml, anchor, body or "<a:p/>"))

    @staticmethod
    def _p(content, bullet=None, space=6, align=None):
        ppr = '<a:pPr%s%s><a:spcBef><a:spcPts val="%d"/></a:spcBef>' % (
            ' marL="285750" indent="-285750"' if bullet else "", ' algn="%s"' % align if align else "", space * 100)
        if bullet == "num":
            ppr += '<a:buFont typeface="+mj-lt"/><a:buAutoNum type="arabicPeriod"/>'
        elif bullet:
            ppr += '<a:buFont typeface="Arial"/><a:buChar char="&#8226;"/>'
        else:
            ppr += "<a:buNone/>"
        return "<a:p>%s</a:pPr>%s</a:p>" % (ppr, content)

    def _pic(self, sid, ref, x, y, w, h, rels):
        """Picture scaled into the box, centered across and aligned to the top; returns (xml, height)."""
        path = self.resolve(ref)
        if path is None:
            self.missing.append(ref)
            return self._sp(sid, x, y, w, 457200, self._p(a_runs("[Chart not found: %s]" % ref, 12, "C00000"))), 457200
        try:
            pw, ph, dx, dy = image_size(path)
        except (ValueError, OSError, struct.error):
            self.missing.append(ref)
            return self._sp(sid, x, y, w, 457200, self._p(a_runs("[Chart could not be read: %s]" % ref, 12, "C00000"))), 457200
        ar = (pw / dx) / (ph / dy)
        cw, ch = (w, int(w / ar)) if w / ar <= h else (int(h * ar), h)
        cx, cy = x + (w - cw) // 2, y
        n = len(self.media) + 1
        name = "image%d%s" % (n, os.path.splitext(path)[1].lower().replace("jpeg", "jpg"))
        self.media.append((name, path))
        rid = "rId%d" % (len(rels) + 2)
        rels.append('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                    'relationships/image" Target="../media/%s"/>' % (rid, name))
        return ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="Picture %d" descr="%s"/><p:cNvPicPr>'
                '<a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill>'
                '<a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm>'
                '<a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/>'
                '</a:prstGeom></p:spPr></p:pic>' % (sid, sid, escape(os.path.basename(path)), rid, cx, cy, cw, ch)), ch

    def _table(self, sid, rows, x, y, w, h):
        ncol = max(len(r) for r in rows)
        rows = [(r + [""] * ncol)[:ncol] for r in rows]
        longest = max(len(plain(c)) for r in rows for c in r)
        size = 9 if ncol >= 9 or longest > 120 else 10 if ncol >= 7 or longest > 70 else 12
        weights = [min(max(max(len(plain(r[j])) for r in rows), 4), 60) for j in range(ncol)]
        widths = [int(w * k / sum(weights)) for k in weights]
        numeric = [j > 0 and all(NUM_RE.match(plain(r[j])) or not r[j] for r in rows[1:]) for j in range(ncol)]
        row_h = int(h / max(len(rows), 1))
        xml = ['<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="%d" name="Table %d"/><p:cNvGraphicFramePr>'
               '<a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
               '<p:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></p:xfrm><a:graphic>'
               '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table"><a:tbl>'
               '<a:tblPr firstRow="1" bandRow="1"/><a:tblGrid>' % (sid, sid, x, y, w, h)]
        xml += ['<a:gridCol w="%d"/>' % cw for cw in widths]
        xml.append("</a:tblGrid>")
        for ri, r in enumerate(rows):
            xml.append('<a:tr h="%d">' % min(row_h, 457200))
            for j, c in enumerate(r):
                fill = DARK if ri == 0 else ("F2F2F2" if ri % 2 == 0 else "FFFFFF")
                color = "FFFFFF" if ri == 0 else "262626"
                algn = "r" if numeric[j] else "l"
                xml.append('<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr algn="%s"/>%s</a:p></a:txBody>'
                           '<a:tcPr marL="64008" marR="64008" marT="27432" marB="27432" anchor="ctr">'
                           '<a:lnB w="6350"><a:solidFill><a:srgbClr val="D9D9D9"/></a:solidFill></a:lnB>'
                           '<a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:tcPr></a:tc>'
                           % (algn, a_runs(c, size, color, bold=(ri == 0)), fill))
            xml.append("</a:tr>")
        xml.append("</a:tbl></a:graphicData></a:graphic></p:graphicFrame>")
        return "".join(xml)

    # slides ------------------------------------------------------------
    def slide(self, title, build):
        """build(rels) returns shape XML placed below a title bar."""
        rels = []
        n = len(self.slides) + 1
        tsize = 26 if len(plain(title)) <= 60 else 22 if len(plain(title)) <= 90 else 18
        shapes = [self._sp(2, 0, 0, SLIDE_W, 91440, "", fill=DARK),
                  self._sp(3, 457200, 228600, SLIDE_W - 914400, 822960,
                           self._p(a_runs(plain(title), tsize, DARK, bold=True), space=0), anchor="b"),
                  self._sp(4, 457200, SLIDE_H - 365760, SLIDE_W - 914400, 274320,
                           self._p(a_runs("%s  |  %d" % (plain(self.title), n), 9, "8C8C8C"), space=0, align="r"))]
        shapes.append(build(rels))
        self.slides.append(("".join(shapes), rels))

    def title_slide(self, title, sub):
        body = self._p(a_runs(plain(title), 36, "FFFFFF", bold=True), space=0)
        for s in sub:
            body += self._p(a_runs(plain(s), 14, "D9E2F3"), space=10)
        self.slides.append((self._sp(2, 0, 0, SLIDE_W, SLIDE_H, "", fill=DARK)
                            + self._sp(3, 731520, 1828800, SLIDE_W - 1463040, 3200400, body, anchor="t"), []))

    def text_slide(self, title, paras, bullets=None):
        x, y, w, h = 457200, 1188720, SLIDE_W - 914400, SLIDE_H - 1188720 - 457200
        size = fit_size(paras, w, h)
        body = "".join(self._p(a_runs(t, size), bullet=(bullets[k] if bullets else None), space=8)
                       for k, t in enumerate(paras))
        self.slide(title, lambda rels: self._sp(10, x, y, w, h, body))

    def question_slides(self, heading, blocks):
        main, bullets, method, caveats, images, tables = [], [], [], [], [], []
        for b in blocks:
            if b[0] == "img":
                images.append(b)
            elif b[0] == "table":
                tables.append(b)
            else:
                t = b[1]
                m = re.match(r"^\*\*([^*]+?)[.:]?\*\*[.:]?\s*(.*)$", t)
                label = m.group(1).strip().lower() if m else ""
                if b[0] == "p" and label.startswith(METHOD_LABELS):
                    method.append(m.group(2))
                elif b[0] == "p" and label.startswith(CAVEAT_LABELS):
                    caveats.append(m.group(2))
                elif b[0] == "p" and label == "answer":
                    main.append(m.group(2))
                    bullets.append(None)
                else:
                    main.append(t)
                    bullets.append(("num" if b[2] else "dot") if b[0] == "li" else None)
        seen = set()
        images = [im for im in images if not (im[2] in seen or seen.add(im[2]))]
        has_img = bool(images)
        tx, ty = 457200, 1188720
        tw = 4754880 if has_img else SLIDE_W - 914400
        foot = ("Method and data: " + " ".join(method)) if method else ""
        foot_h = 0
        if foot:
            fs = fit_size([foot], SLIDE_W - 914400, 640080, sizes=(11, 10, 9, 8))
            foot_h = 685800
        th = SLIDE_H - ty - 457200 - foot_h
        paras = main + (["**Caveats.** " + " ".join(caveats)] if caveats else [])
        marks = bullets + ([None] if caveats else [])
        size = fit_size(paras or [""], tw, th)

        def build(rels):
            body = "".join(self._p(a_runs(t, size if k < len(main) else max(size - 2, 9),
                                          "262626" if k < len(main) else GREY), bullet=marks[k], space=8)
                           for k, t in enumerate(paras))
            out = self._sp(10, tx, ty, tw, th, body)
            if has_img:
                px, pw = tx + tw + 182880, SLIDE_W - tx - tw - 182880 - 457200
                pic, ph = self._pic(11, images[0][2], px, ty, pw, th - 457200, rels)
                out += pic
                cap = images[0][1]
                if cap:
                    out += self._sp(12, px, ty + ph + 45720, pw, 411480,
                                    self._p(a_runs(cap, 10, GREY), space=0, align="ctr"))
            if foot:
                out += self._sp(13, 457200, SLIDE_H - 457200 - foot_h, SLIDE_W - 914400, foot_h - 45720,
                                self._p(a_runs(foot, fs, GREY), space=0), fill="F2F2F2")
            return out

        self.slide(heading, build)
        for img in images[1:]:
            self.chart_slide(heading, img)
        for _, cap, rows in tables:
            self.table_slides(heading, cap, rows)

    def chart_slide(self, heading, img):
        _, cap, ref = img

        def build(rels):
            out, ph = self._pic(10, ref, 457200, 1188720, SLIDE_W - 914400, SLIDE_H - 1188720 - 868680, rels)
            if cap:
                out += self._sp(11, 457200, 1188720 + ph + 45720, SLIDE_W - 914400, 365760,
                                self._p(a_runs(cap, 11, GREY), space=0, align="ctr"))
            return out
        self.slide(heading, build)

    def table_slides(self, heading, cap, rows):
        header, data = rows[0], rows[1:]
        longest = max([len(plain(c)) for r in rows for c in r] or [0])
        per = 6 if longest > 120 else 9 if longest > 60 else 13
        chunks = [data[k:k + per] for k in range(0, len(data), per)] or [[]]
        for k, chunk in enumerate(chunks):
            sub = cap + (" (continued)" if k else "")
            y = 1188720

            def build(rels, chunk=chunk, sub=sub):
                out = ""
                yy = y
                if sub:
                    out += self._sp(10, 457200, y, SLIDE_W - 914400, 365760,
                                    self._p(a_runs(sub, 13, ACCENT, bold=True), space=0))
                    yy += 411480
                h = min(SLIDE_H - yy - 548640, 411480 * (len(chunk) + 1) * (2 if longest > 60 else 1))
                return out + self._table(11, [header] + chunk, 457200, yy, SLIDE_W - 914400, h)
            self.slide(heading, build)

    def build(self, text):
        title, intro, sections = parse_blocks(text)
        self.title = title or "Results"
        sub = [b[1] for b in intro if b[0] == "p"][:2]
        sub.append(datetime.date.today().strftime("%d %B %Y").lstrip("0"))
        self.title_slide(self.title, sub)
        for heading, blocks in sections:
            h = plain(heading).strip().lower()
            if h in ("summary", "key messages", "summary of answers") or h.startswith("summary"):
                items = [b for b in blocks if b[0] in ("li", "p")]
                for k in range(0, len(items), 4):
                    part = items[k:k + 4]
                    self.text_slide("Questions and answers" + (" (continued)" if k else ""), [b[1] for b in part],
                                    [None for b in part])
            elif h.startswith("annex") or h.startswith("appendix") or h.startswith("not assessed"):
                for b in blocks:
                    if b[0] == "table":
                        self.table_slides(heading, b[1], b[2])
                paras = [b[1] for b in blocks if b[0] in ("p", "li")]
                if paras:
                    self.text_slide(heading, paras)
            else:
                self.question_slides(heading, blocks)

    def write(self, out):
        n = len(self.slides)
        ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              '<Default Extension="png" ContentType="image/png"/><Default Extension="jpg" ContentType="image/jpeg"/>'
              '<Default Extension="gif" ContentType="image/gif"/>'
              '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
              '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
              '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
              '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
              '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>'
              '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>'
              '<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>'
              '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>']
        ct += ['<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-'
               'officedocument.presentationml.slide+xml"/>' % (k + 1) for k in range(n)]
        ct.append("</Types>")
        R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
        pres_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.'
                     'openxmlformats.org/package/2006/relationships">'
                     '<Relationship Id="rId1" Type="%sslideMaster" Target="slideMasters/slideMaster1.xml"/>'
                     '<Relationship Id="rId2" Type="%stheme" Target="theme/theme1.xml"/>'
                     '<Relationship Id="rId3" Type="%spresProps" Target="presProps.xml"/>'
                     '<Relationship Id="rId4" Type="%sviewProps" Target="viewProps.xml"/>'
                     '<Relationship Id="rId5" Type="%stableStyles" Target="tableStyles.xml"/>' % ((R,) * 5)]
        pres_rels += ['<Relationship Id="rId%d" Type="%sslide" Target="slides/slide%d.xml"/>' % (k + 10, R, k + 1)
                      for k in range(n)]
        pres_rels.append("</Relationships>")
        pres = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentation %s saveSubsetFonts="1">'
                '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>%s'
                '</p:sldIdLst><p:sldSz cx="%d" cy="%d"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'
                % (P_NS, "".join('<p:sldId id="%d" r:id="rId%d"/>' % (256 + k, k + 10) for k in range(n)),
                   SLIDE_W, SLIDE_H))
        group = ('<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm>'
                 '<a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/>'
                 '</a:xfrm></p:grpSpPr>')
        master = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldMaster %s><p:cSld><p:bg><p:bgRef '
                  'idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg><p:spTree>%s</p:spTree></p:cSld>'
                  '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" '
                  'accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" '
                  'folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/>'
                  '</p:sldLayoutIdLst><p:txStyles><p:titleStyle><a:lvl1pPr><a:defRPr sz="2800"/></a:lvl1pPr>'
                  '</p:titleStyle><p:bodyStyle><a:lvl1pPr><a:defRPr sz="1800"/></a:lvl1pPr></p:bodyStyle>'
                  '<p:otherStyle><a:lvl1pPr><a:defRPr sz="1800"/></a:lvl1pPr></p:otherStyle></p:txStyles>'
                  '</p:sldMaster>' % (P_NS, group))
        master_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.'
                       'openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="%sslideLayout" '
                       'Target="../slideLayouts/slideLayout1.xml"/><Relationship Id="rId2" Type="%stheme" '
                       'Target="../theme/theme1.xml"/></Relationships>' % (R, R))
        layout = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout %s type="blank" preserve="1">'
                  '<p:cSld name="Blank"><p:spTree>%s</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/>'
                  '</p:clrMapOvr></p:sldLayout>' % (P_NS, group))
        layout_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.'
                       'openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="%sslideMaster" '
                       'Target="../slideMasters/slideMaster1.xml"/></Relationships>' % R)
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties '
                'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>%s</dc:title>'
                '<dc:creator>Economic Modeling Studio</dc:creator>'
                '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
                '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified></cp:coreProperties>'
                % (escape(plain(self.title)), now, now))
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", "".join(ct))
            z.writestr("_rels/.rels", ROOT_RELS.replace("word/document.xml", "ppt/presentation.xml"))
            z.writestr("docProps/core.xml", core)
            z.writestr("ppt/presentation.xml", pres)
            z.writestr("ppt/_rels/presentation.xml.rels", "".join(pres_rels))
            z.writestr("ppt/slideMasters/slideMaster1.xml", master)
            z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels)
            z.writestr("ppt/slideLayouts/slideLayout1.xml", layout)
            z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels)
            z.writestr("ppt/theme/theme1.xml", THEME)
            z.writestr("ppt/presProps.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                                            '<p:presentationPr %s/>' % P_NS)
            z.writestr("ppt/viewProps.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                                            '<p:viewPr %s><p:gridSpacing cx="76200" cy="76200"/></p:viewPr>' % P_NS)
            z.writestr("ppt/tableStyles.xml", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       '<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                       'def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>')
            for k, (shapes, rels) in enumerate(self.slides):
                z.writestr("ppt/slides/slide%d.xml" % (k + 1),
                           '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sld %s><p:cSld><p:spTree>%s%s'
                           '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
                           % (P_NS, group, shapes))
                z.writestr("ppt/slides/_rels/slide%d.xml.rels" % (k + 1),
                           '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://'
                           'schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" '
                           'Type="%sslideLayout" Target="../slideLayouts/slideLayout1.xml"/>%s</Relationships>'
                           % (R, "".join(rels)))
            for name, path in self.media:
                z.write(path, "ppt/media/" + name)


def _theme():
    clr = "".join('<a:%s><a:srgbClr val="%s"/></a:%s>' % (k, v, k) for k, v in (
        ("dk2", "1F3864"), ("lt2", "E7E6E6"), ("accent1", "2E5395"), ("accent2", "E07A2F"), ("accent3", "5A9E4B"),
        ("accent4", "8C5FA8"), ("accent5", "C9A227"), ("accent6", "2A6F97"), ("hlink", "0563C1"),
        ("folHlink", "954F72")))
    fill = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    line = '<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="http://schemas.openxmlformats.'
            'org/drawingml/2006/main" name="Studio"><a:themeElements><a:clrScheme name="Studio">'
            '<a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>%s</a:clrScheme>'
            '<a:fontScheme name="Studio"><a:majorFont><a:latin typeface="Calibri"/><a:ea typeface=""/>'
            '<a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/>'
            '<a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Studio"><a:fillStyleLst>%s'
            '</a:fillStyleLst><a:lnStyleLst>%s</a:lnStyleLst><a:effectStyleLst>%s</a:effectStyleLst>'
            '<a:bgFillStyleLst>%s</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
            % (clr, fill * 3, line * 3, "<a:effectStyle><a:effectLst/></a:effectStyle>" * 3, fill * 3))


THEME = _theme()


def to_pptx(md_path, out, root=None):
    deck = Deck(md_path, root or os.getcwd())
    with open(md_path, encoding="utf-8-sig") as f:
        deck.build(f.read())
    deck.write(out)
    return {"slides": len(deck.slides), "charts": len(deck.media), "missing": deck.missing, "out": out}


# ---------------------------------------------------------------- bundle
PROTECTED = ("data/raw/", "data/restricted/", "data/confidential/", ".env")
REF_RE = re.compile(r"`([^`]+)`|!\[[^\]]*\]\(([^)\s]+)")


def bundle(md_path, out_dir, root=None, make_zip=True):
    """Collect everything a results report points to into one folder (and a zip next to it).

    Copied: the files next to the report (Word, PowerPoint, the report itself, tables), every chart,
    code file and run folder the report names (paths in backticks, image links, or a run folder such as
    `output/<run-id>/` next to a code path in the same table row or paragraph). Files under --root keep
    their relative path, so `models/<family>/<name>/output/<run-id>/` is found at the same place inside
    the bundle; anything else goes to `charts/` or `files/`. A copy of the report with links rewritten to
    the bundle and an index (README.md) are written at the top. Sources are never changed."""
    import shutil
    root = os.path.abspath(root or os.getcwd())
    md_abs = os.path.abspath(md_path)
    base = os.path.dirname(md_abs)
    out_dir = os.path.abspath(out_dir)
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    with open(md_abs, encoding="utf-8-sig") as f:
        text = f.read()

    copied, missing, skipped, section = {}, [], [], "Report"
    by_section = {}

    def dest_for(path, is_dir):
        rel = os.path.relpath(path, root)
        if not rel.startswith(".."):
            return rel
        sub = "charts" if path.lower().endswith(IMG_EXT) else "files"
        return os.path.join(sub, os.path.basename(path.rstrip("\\/")))

    def take(path):
        path = os.path.normpath(path)
        if path in copied:
            return copied[path]
        if os.path.commonpath([path, out_dir]) == out_dir:
            return None
        rel = os.path.relpath(path, root).replace("\\", "/").lower()
        if rel.startswith(PROTECTED) or rel in ("data/raw", "data/restricted", "data/confidential"):
            skipped.append(rel)
            return None
        d = dest_for(path, os.path.isdir(path))
        target = os.path.join(out_dir, d)
        if os.path.isdir(path):
            shutil.copytree(path, target, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".ipynb_checkpoints"))
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(path, target)
        copied[path] = d.replace("\\", "/") + ("/" if os.path.isdir(path) else "")
        return copied[path]

    def resolve(ref, hints):
        ref = ref.strip().strip("<>")
        if not ref or "://" in ref or ref.startswith("/") and not os.path.exists(ref):
            return None
        cands = [ref] if os.path.isabs(ref) else [os.path.join(b, ref) for b in [base, root] + hints]
        for c in cands:
            if os.path.exists(c):
                return os.path.normpath(c)
        return None

    looks_like_path = re.compile(r"^[\w.\-/\\: ]+(\.[A-Za-z0-9]{1,5}|/)$")
    rewritten = []
    for line in text.replace("\r\n", "\n").split("\n"):
        m = re.match(r"^#{1,4}\s+(.*)$", line.strip())
        if m:
            section = plain(m.group(1)).strip()
        refs = [a or b for a, b in REF_RE.findall(line)]
        refs = [r for r in refs if looks_like_path.match(r.strip()) and ("/" in r or "." in r)]
        hints = []
        for r in refs:
            p = resolve(r, [])
            if p and os.path.isfile(p):
                hints.append(os.path.dirname(p))
        new_line = line
        for r in refs:
            p = resolve(r, hints)
            if p is None:
                if r.strip().startswith(("models/", "output/", "forecasts/")) or r.lower().endswith(IMG_EXT):
                    missing.append(r)
                continue
            d = take(p)
            if d:
                items = by_section.setdefault(section, [])
                run = re.match(r"^(.*/output/[^/]+)/.+$", p.replace(os.sep, "/"))
                if run and os.path.isdir(run.group(1)):
                    rd = take(os.path.normpath(run.group(1)))
                    if rd and rd not in items:
                        items.append(rd)
                if d not in items:
                    items.append(d)
                new_line = new_line.replace("`%s`" % r, "`%s`" % d).replace("](%s" % r, "](%s" % d)
        rewritten.append(new_line)

    deliverables = []
    for name in sorted(os.listdir(base)):
        p = os.path.join(base, name)
        if os.path.isfile(p) and p != md_abs and not name.lower().endswith(".zip"):
            shutil.copy2(p, os.path.join(out_dir, name))
            deliverables.append(name)
    report_name = os.path.basename(md_abs)
    with open(os.path.join(out_dir, report_name), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(rewritten))
    deliverables.append(report_name)

    title = plain(parse_blocks(text)[0] or "Results")
    idx = ["# %s: all results in one place" % title, "",
           "Collected on %s from `%s`. File paths below are relative to this folder." % (
               datetime.date.today().isoformat(), os.path.relpath(md_abs, root).replace("\\", "/")), "",
           "## Read first", ""]
    order = {".docx": 0, ".pptx": 1, ".md": 2}
    for d in sorted(set(deliverables), key=lambda n: (order.get(os.path.splitext(n)[1].lower(), 3), n)):
        idx.append("- `%s`" % d)
    idx += ["", "## By question or section", ""]
    for sec, items in by_section.items():
        idx.append("**%s**" % sec)
        idx.append("")
        idx += ["- `%s`" % d for d in items]
        idx.append("")
    if skipped:
        idx += ["## Not copied (protected data stays where it is)", ""] + ["- `%s`" % s for s in sorted(set(skipped))] + [""]
    if missing:
        idx += ["## Not found", ""] + ["- `%s`" % m for m in sorted(set(missing))] + [""]
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(idx))

    zip_path = None
    if make_zip:
        zip_path = out_dir.rstrip("\\/") + ".zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            top = os.path.basename(out_dir.rstrip("\\/"))
            for dirpath, _, files in os.walk(out_dir):
                for fn in sorted(files):
                    full = os.path.join(dirpath, fn)
                    z.write(full, os.path.join(top, os.path.relpath(full, out_dir)).replace("\\", "/"))
    n_files = sum(len(fs) for _, _, fs in os.walk(out_dir))
    return {"out": out_dir, "zip": zip_path, "files": n_files, "items": len(copied), "missing": sorted(set(missing)),
            "skipped": sorted(set(skipped))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("docx", help="Markdown report to Word")
    d.add_argument("md")
    d.add_argument("--out", required=True)
    d.add_argument("--root", default=None, help="folder that chart paths are relative to (default: current folder)")
    s = sub.add_parser("pptx", help="Markdown report to a PowerPoint deck by question")
    s.add_argument("md")
    s.add_argument("--out", required=True)
    s.add_argument("--root", default=None, help="folder that chart paths are relative to (default: current folder)")
    b = sub.add_parser("bundle", help="collect the report, deliverables, code and run folders in one folder and a zip")
    b.add_argument("md")
    b.add_argument("--out", required=True)
    b.add_argument("--root", default=None, help="studio folder that paths are relative to (default: current folder)")
    b.add_argument("--no-zip", action="store_true")
    a = ap.parse_args(argv)
    if not os.path.isfile(a.md):
        print("report: file not found: %s" % a.md, file=sys.stderr)
        return 2
    if a.cmd == "bundle":
        res = bundle(a.md, a.out, a.root, not a.no_zip)
        print("Wrote %s: %d files from %d items%s." % (res["out"], res["files"], res["items"],
                                                     ", zip %s" % res["zip"] if res["zip"] else ""))
        for s in res["skipped"]:
            print("  not copied (protected): %s" % s)
        for m in res["missing"]:
            print("  not found: %s" % m)
        return 0
    if a.cmd == "pptx":
        res = to_pptx(a.md, a.out, a.root)
        print("Wrote %s: %d slides, %d charts." % (res["out"], res["slides"], res["charts"]))
    else:
        res = to_docx(a.md, a.out, a.root)
        print("Wrote %s: %d figures, %d tables." % (res["out"], res["figures"], res["tables"]))
    for m in res["missing"]:
        print("  missing chart: %s" % m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
