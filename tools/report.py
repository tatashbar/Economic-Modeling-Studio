#!/usr/bin/env python3
"""Write a Word report (.docx) from a Markdown results report. Standard library only.

Usage:  python tools/report.py docx <report.md> --out <report.docx> [--root <dir>]

Supported Markdown: headings (# to ####), paragraphs, **bold**, *italic*, `code`, [links](url),
bullet and numbered lists (two levels), pipe tables, code blocks, block quotes and images
(![caption](chart.png)). A paragraph that names a chart file in backticks (`.../chart.png`) also
gets the chart embedded below it, so a results pack that only points to its charts still shows them.
Images are PNG, JPEG or GIF, scaled to the page width and numbered as figures; tables are numbered
too. Image paths are resolved against the report's folder, then --root (default: the current folder).
The first level-1 heading is the document title. A missing image is reported and listed in the
document as missing; it never stops the report.
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("docx", help="Markdown report to Word")
    d.add_argument("md")
    d.add_argument("--out", required=True)
    d.add_argument("--root", default=None, help="folder that chart paths are relative to (default: current folder)")
    a = ap.parse_args(argv)
    if not os.path.isfile(a.md):
        print("report: file not found: %s" % a.md, file=sys.stderr)
        return 2
    res = to_docx(a.md, a.out, a.root)
    print("Wrote %s: %d figures, %d tables." % (res["out"], res["figures"], res["tables"]))
    for m in res["missing"]:
        print("  missing chart: %s" % m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
