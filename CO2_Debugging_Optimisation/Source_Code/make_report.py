"""Builds docs/CSA06_CO2_SentinelOps_Report.docx from the repo's real results."""
import csv
import os
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RES = os.path.join(ROOT, "Supporting_Files")
sys.path.insert(0, os.path.join(ROOT, "Source_Code"))
sys.path.insert(0, os.path.join(ROOT, "Source_Code"))
from pseudocode_text import CORRECTED, OPTIMISED  # noqa: E402
import original as ORIG  # noqa: E402
import corrected as COR  # noqa: E402
import optimised as OPT  # noqa: E402

NAVY = RGBColor(0x1F, 0x38, 0x64)
doc = Document()

# ------------------------------------------------------------------ page + styles
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2)
sec.top_margin = sec.bottom_margin = Cm(2)
TEXT_W = 17.0  # cm

st = doc.styles
st["Normal"].font.name = "Calibri"
st["Normal"].font.size = Pt(10.5)
st["Normal"].element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st["Normal"].paragraph_format.space_after = Pt(5)
for name, size, before in (("Heading 1", 16, 16), ("Heading 2", 13, 12), ("Heading 3", 11, 8)):
    h = st[name]
    h.font.name = "Calibri"
    h.font.size = Pt(size)
    h.font.bold = True
    h.font.color.rgb = NAVY
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    h.element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    h.element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    h.paragraph_format.space_before = Pt(before)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def cell_margins(table, top=40, bottom=40, left=70, right=70):
    tblPr = table._tbl.tblPr
    m = OxmlElement("w:tblCellMar")
    for k, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        e = OxmlElement(f"w:{k}")
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        m.append(e)
    tblPr.append(m)


def set_repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:tblHeader")
    e.set(qn("w:val"), "true")
    trPr.append(e)


def no_split(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:cantSplit")
    e.set(qn("w:val"), "true")
    trPr.append(e)


def H1(t): return doc.add_heading(t, 1)
def H2(t): return doc.add_heading(t, 2)
def H3(t): return doc.add_heading(t, 3)


def P(text="", bold_lead=None, italic=False, size=None, align=None, after=None, keep=False):
    p = doc.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
        if size:
            r.font.size = Pt(size)
    r = p.add_run(text)
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    if align:
        p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if keep:
        p.paragraph_format.keep_with_next = True
    return p


def B(text, bold_lead=None, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    if level:
        p.paragraph_format.left_indent = Cm(1.2)
    if bold_lead:
        p.add_run(bold_lead).bold = True
    p.add_run(text)
    return p


def mono_run(p, text, size=8):
    r = p.add_run(text)
    r.font.name = "Courier New"
    r.element.rPr.rFonts.set(qn("w:eastAsia"), "Courier New")
    r.element.rPr.rFonts.set(qn("w:hAnsi"), "Courier New")
    r.element.rPr.rFonts.set(qn("w:cs"), "Courier New")
    r.font.size = Pt(size)
    return r


def CODE(text, size=7.5, caption=None):
    """Shaded one-cell table holding monospaced text (copyable)."""
    if caption:
        c = P(caption, italic=True, size=9, after=2, keep=True)
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    cell_margins(t, 60, 60, 100, 100)
    c = t.rows[0].cells[0]
    c.width = Cm(TEXT_W)
    shade(c, "F4F4F4")
    lines = text.rstrip("\n").split("\n")
    first = True
    for ln in lines:
        p = c.paragraphs[0] if first else c.add_paragraph()
        first = False
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        mono_run(p, ln if ln else " ", size)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def TABLE(headers, rows, widths, size=9, mono_cols=(), header_fill="D9E2F3", bold_first=False, align_right=()):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    cell_margins(t)
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.width = Cm(widths[i])
        shade(c, header_fill)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(size)
    set_repeat_header(t.rows[0])
    for row in rows:
        cells = t.add_row().cells
        no_split(t.rows[-1])
        for i, v in enumerate(row):
            cells[i].width = Cm(widths[i])
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if i in align_right:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            if i in mono_cols:
                mono_run(p, str(v), size - 1)
            else:
                r = p.add_run(str(v))
                r.font.size = Pt(size)
                if bold_first and i == 0:
                    r.bold = True
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def IMG(path, width_cm, caption=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = bool(caption)
    p.add_run().add_picture(path, width=Cm(width_cm))
    if caption:
        c = P(caption, italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER, after=8)


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def footer_page_numbers():
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("CSA06 CO2 – SentinelOps Debugging and Optimisation   |   Page ")
    r.font.size = Pt(8)
    for kind, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        r2 = p.add_run()
        r2.font.size = Pt(8)
        if kind:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            r2._r.append(fc)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = txt
            r2._r.append(it)


def read_csv(name):
    with open(os.path.join(RES, name)) as f:
        return list(csv.DictReader(f))


def fmt(n):
    return f"{int(n):,}"


footer_page_numbers()

# =================================================================== TITLE
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Department of Computer Science and Engineering")
r.bold = True
r.font.size = Pt(12)
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("CSA06 – Design and Analysis of Algorithms")
r.bold = True
r.font.size = Pt(18)
r.font.color.rgb = NAVY
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("CO2 – Debugging and Optimisation Task")
r.font.size = Pt(14)
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("SentinelOps SOC Alert-Triage Module")
r.italic = True
r.font.size = Pt(13)

TABLE(["Field", "Entry"], [
    ["Student Name", ""],
    ["Student Reg. No.", ""],
    ["GitHub repository link", ""],
    ["Course Outcome assessed", "Apply Brute Force technique to solve sorting, searching, Closest-Pair and Convex-Hull problems"],
    ["Maximum Marks", "50"],
], [5, 12], size=10, bold_first=True)

H2("Contents")
for line in ("Summary of results",
             "Part (a) – Reproduce and identify the defects  (10 marks)",
             "Part (b) – Root causes and systematic debugging  (12 marks)",
             "Part (c) – Optimise the corrected module  (10 marks)",
             "Part (d) – Analysis before and after  (10 marks)",
             "Part (e) – Production-quality code, test harness and GitHub submission  (8 marks)",
             "Appendix A – Original code;  Appendix B – Corrected code"):
    B(line)

# =================================================================== SUMMARY
H1("Summary of results")
P("The module contained nine defects: two in sort_alerts, two in is_blocked, two in find_signature and three in "
  "closest_logins. Each was located by running the code on the test data, explained, fixed one at a time without "
  "rewriting the functions, and re-tested after each change. The corrected module was then optimised for the "
  "production workload (50,000 alerts, 8,000 login events per day) and every optimised function was checked against the "
  "corrected one.")
cp_rows = read_csv("closest_pair_measurements.csv")
u8 = [r for r in cp_rows if r["dataset"] == "uniform" and r["n"] == "8000"][0]
sx8 = [r for r in cp_rows if r["dataset"] == "same_x" and r["n"] == "8000"][0]
so_rows = read_csv("sort_comparisons.csv")
ns50 = [r for r in so_rows if r["input"] == "nearly_sorted" and r["n"] == "50000"][0]
rd10 = [r for r in so_rows if r["input"] == "random" and r["n"] == "10000"][0]
bl = read_csv("blocklist_measurements.csv")[0]
TABLE(["Function", "Defects", "Before (corrected brute force)", "After (optimised)"], [
    ["sort_alerts", "D1, D2",
     f"Insertion sort: {fmt(rd10['insertion_comparisons'])} comparisons for 10,000 random alerts; Θ(n²)",
     f"Timsort: {fmt(rd10['timsort_comparisons'])} comparisons for the same input; O(n log n), O(n) if nearly sorted"],
    ["is_blocked", "D3, D4",
     f"≈ {float(bl['avg_comparisons_per_lookup_sequential(measured on 5000)']):.0f} comparisons per lookup (b = 1,000); "
     f"{float(bl['sequential_seconds_for_all_queries']):.2f} s for 50,000 lookups",
     f"O(1) hash look-up; {float(bl['set_lookup_seconds_for_all_queries']):.4f} s for 50,000 lookups"],
    ["find_signature", "D5, D6",
     "Missed the last alignment, reported false hits; O(nm)",
     "Correct, exact minimum number of comparisons, still O(nm) worst case"],
    ["closest_logins", "D7, D8, D9",
     f"{fmt(u8['corrected_brute_dist_comps'])} distance computations at n = 8,000",
     f"{fmt(u8['optimised_dist_comps'])} (uniform data); no gain in the worst case ({fmt(sx8['optimised_dist_comps'])})"],
], [3, 2, 6, 6], size=9)
P("Test status: 82 checks in the test harness pass (all boundary cases plus 2,000 randomised comparisons between the "
  "optimised and the corrected module).", after=4)

# =================================================================== PART A
page_break()
H1("Part (a) – Reproduce and Identify the Defects (10 marks)")
H2("A.1  How the module was run")
P("The code in the question paper was saved as src/original.py. Its indentation was lost when the question was converted to "
  "PDF, so it was restored using the standard structure; the else in is_blocked is paired with the if inside the loop "
  "(read as the else of the if inside the loop; if it was meant as a for-else, the output on the test data is the same, because a match still returns False). The test data from the question was then run with:")
CODE("$ python src/demo.py original")
P("Test data:", keep=True)
CODE('''alerts    = [("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)]
blocklist = ["10.0.0.5", "10.0.0.9", "172.16.4.2"]
queries   = ["10.0.0.9", "10.0.0.5", "8.8.8.8"]
log, pattern = "FAILFAIXFAIL", "FAIL"
events    = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]      # (x, y) in km''')
IMG(os.path.join(RES, "shot_run_original.png"), 12.5, "Figure 1 – Execution output of the original module on the test data (expected lines in blue, actual in orange).")

H2("A.2  Expected output versus actual output")
TABLE(["Function", "Expected output", "Actual output (original)"], [
    ["sort_alerts", "[(A2,9), (A4,9), (A3,5), (A1,3), (A5,1)]\nhighest first; A2 before A4 (arrival order)",
     "[(A4,9), (A3,5), (A3,5), (A5,1), (A5,1)]\nA1 and A2 lost, A3 and A5 duplicated"],
    ["is_blocked", "[True, True, False]\n(10.0.0.9 and 10.0.0.5 are listed; 8.8.8.8 is not)", "[False, False, False]\nblocked addresses get through"],
    ["find_signature", "[0, 8]\n(FAIL at index 0 and at the very end)", "[0, 4]\nindex 8 missed, index 4 (FAIX) is a false signature"],
    ["closest_logins", "((0, 5), 1.4142…)\n(2,3) and (3,4) are √2 ≈ 1.41 km apart", "((0, 2), 60.44…)\n(2,3) and (40,50): the FARTHEST pair"],
], [3, 7, 7], size=9, bold_first=True)

H2("A.3  Defect register")
P("Nine defects were found. None was marked in the code; each is located by function, faulty line and nature of the error.", keep=True)
TABLE(["ID", "Function", "Faulty line", "Nature of the error"], [
    ["D1", "sort_alerts", "while j > 0 and alerts[j][1] < key[1]:", "Off-by-one boundary. Index 0 is never compared or shifted, so nothing can be inserted before the first element."],
    ["D2", "sort_alerts", "alerts[j] = key", "Wrong insertion slot. After the loop the free slot is j + 1, not j; writing at j overwrites an element (alert lost, another duplicated)."],
    ["D3", "is_blocked", "if blocklist[i] == ip:\n    return False", "Wrong return value. A successful match returns False."],
    ["D4", "is_blocked", "else:\n    return False  (inside the loop)", "Premature exit. The loop returns after examining only the first entry; no final return after the loop, so an empty blocklist returns None."],
    ["D5", "find_signature", "for i in range(n - m):", "Off-by-one loop bound. The last alignment i = n − m is never tried, so a signature at the end of the log is missed."],
    ["D6", "find_signature", "if j == m - 1:", "Wrong match test. j is also m − 1 when the mismatch occurs at the LAST character, so partial matches such as FAIX are reported as hits."],
    ["D7", "closest_logins", "min_dist = 0", "Wrong initial value for a minimum search; it must be +∞, otherwise no distance can ever be smaller."],
    ["D8", "closest_logins", "if d > min_dist:", "Wrong comparison direction. It keeps the largest distance, i.e. finds the farthest pair."],
    ["D9", "closest_logins", "for j in range(len(events)):", "Wrong inner range. Pairs (i, i) with d = 0 and both (i, j) and (j, i) are examined; the inner loop must start at i + 1."],
], [1.1, 2.6, 5.6, 7.7], size=8.5, mono_cols=(2,), bold_first=True)
P("The defects interact. Fixing only D7 leaves (None, inf), because D8 still compares in the wrong direction; fixing D7 and D8 but not D9 "
  "gives ((0, 0), 0.0), because the self-pair has distance 0. This is shown in Part (b).", italic=True, size=9.5)

# =================================================================== PART B
page_break()
H1("Part (b) – Root Causes and Systematic Debugging (12 marks)")
H2("B.1  Pseudocode of the corrected algorithms")
P("Prepared before implementing the fixes.", keep=True)
for k, v in CORRECTED.items():
    CODE(v, size=7.5, caption=k)

H2("B.2  Root cause of each defect and how it was fixed")
P("Each fix was applied to the original source one at a time (experiments/debug_steps.py applies them cumulatively and re-runs the "
  "tests after every step; the full log is in results/debug_steps_log.txt).", keep=True)


def defect(did, title, wrong, why, fix, verify):
    H3(f"{did} – {title}")
    P(wrong, bold_lead="What was wrong: ", after=2)
    P(why, bold_lead="Why / effect: ", after=2)
    P(fix, bold_lead="Fix: ", after=2)
    P(verify, bold_lead="Verified by: ", after=6)


defect("D1", "sort_alerts: loop condition j > 0",
       "The while loop stops when j reaches 0, so alerts[0] is never compared with the key.",
       "A key that is stronger than every element to its left should end up at index 0, but the loop leaves j = 0 without shifting alerts[0]. "
       "With the second defect this destroys data: for key A2 (9) at i = 1, j = 0, the loop does not run and the key is written over alerts[0].",
       "while j >= 0 and alerts[j][1] < key[1]:",
       "Re-running after D1 alone gave [A1, A1, A1, A1, A4] (still wrong, because D2 remains), proving the boundary was only half of the fault; after D2 the output is correct.")
defect("D2", "sort_alerts: alerts[j] = key",
       "After the while loop, j points to the element that is NOT smaller than the key (or to −1). The free slot is j + 1.",
       "Writing at j overwrites a valid alert. In the trace below, at i = 1 the key A2 replaces A1 (A1 is lost) and A2 now exists twice. "
       "Because every insertion destroys one element and copies another, alerts disappeared and others were duplicated, exactly as reported.",
       "alerts[j + 1] = key",
       "Trace of the corrected insertion (Table B2) and the output [A2, A4, A3, A1, A5] on the test data; the 'no alert lost or duplicated' test compares the multiset of input and output.")
defect("D3", "is_blocked: return False on a match",
       "When blocklist[i] == ip the function returns False.",
       "A listed address is reported as not blocked, so blocked IP addresses get through.",
       "return True",
       "After D3 the query list gives [False, True, False]: 10.0.0.5 (listed first) is now found, but 10.0.0.9 (listed second) is still False because D4 stops the search after the first entry.")
defect("D4", "is_blocked: else-branch returns inside the loop",
       "The else attached to the if returns False for the first entry that does not match, ending the search after one comparison. No statement follows the loop.",
       "Only blocklist[0] is ever tested. 10.0.0.9 (second entry) is never reached, and an empty blocklist falls off the end and returns None instead of False.",
       "Remove the else and put return False after the loop, so False is returned only when all entries were checked.",
       "After D4: [True, True, False]; empty blocklist gives False (was None).")
defect("D5", "find_signature: range(n - m)",
       "range(n − m) generates i = 0 … n − m − 1, but there are n − m + 1 possible alignments (0 … n − m).",
       "For n = 12 and m = 4 the last alignment i = 8, where FAIL ends the log, is never tested, so 'signatures at the end of a log were missed'.",
       "for i in range(n - m + 1):",
       "After D5 the result is [0, 4, 8]: index 8 appears, the false hit at 4 remains until D6. See the alignment table (Table B3).")
defect("D6", "find_signature: if j == m - 1",
       "The test is made after the inner loop and cannot distinguish 'all m characters matched' from 'mismatch at the last character'.",
       "At i = 4 the text is FAIX: F, A, I match and X ≠ L breaks out with j = 3 = m − 1, so the condition is true and 4 is appended. The first match (i = 0) also gives j = 3, so the same test accepts both cases.",
       "Use the for-else construct: else runs only when the loop finished without break, i.e. all m characters matched.",
       "After D6: [0, 8]. Boundary test: find_signature('FAIX', 'FAIL') returns [] and overlapping matches ('aa' in 'aaaa') return [0, 1, 2].")
defect("D7", "closest_logins: min_dist = 0",
       "A minimum search must start from a value larger than any possible distance.",
       "With 0 as the start, once the comparison direction is corrected no distance can ever be smaller than min_dist, so pair would stay None.",
       "min_dist = float('inf')",
       "After D7 alone the function returns (None, inf): the initial value is right but D8 keeps the comparison wrong.")
defect("D8", "closest_logins: if d > min_dist",
       "The comparison keeps the larger distance. The loop therefore computes the maximum, not the minimum.",
       "This is why the report flagged logins hundreds of kilometres apart: the original returned the farthest pair (2,3)–(40,50), 60.44 km, for the test data.",
       "if d < min_dist:",
       "After D8 (D9 still open) the result is ((0, 0), 0.0): the code now finds a minimum, but the self-pair is the minimum.")
defect("D9", "closest_logins: inner loop range(len(events))",
       "The inner loop starts at 0, so it pairs an event with itself (d = 0) and visits each pair twice, (i, j) and (j, i).",
       "A self-pair always has distance 0, which beats every real pair; it also doubles the work.",
       "for j in range(i + 1, len(events)):",
       "After D9: ((0, 5), 1.4142135623730951), equal to the expected answer; the number of distance computations falls from n² to n(n − 1)/2.")

H2("B.3  Step-by-step traces")
H3("Table B1 – Insertion trace of the ORIGINAL sort_alerts (D1 and D2 active)")
TABLE(["Pass", "key", "j at loop end", "List after the pass", "Problem"], [
    ["start", "–", "–", "A1:3  A2:9  A3:5  A4:9  A5:1", ""],
    ["i = 1", "A2:9", "0", "A2:9  A2:9  A3:5  A4:9  A5:1", "A1 overwritten (lost), A2 duplicated"],
    ["i = 2", "A3:5", "1", "A2:9  A3:5  A3:5  A4:9  A5:1", "A2 copy overwritten, A3 duplicated"],
    ["i = 3", "A4:9", "0", "A4:9  A3:5  A3:5  A3:5  A5:1", "A2 lost, A3 now three times"],
    ["i = 4", "A5:1", "3", "A4:9  A3:5  A3:5  A5:1  A5:1", "Final (wrong) output"],
], [1.6, 1.6, 2.2, 6.0, 5.6], size=8.5, bold_first=True)
H3("Table B2 – Insertion trace of the CORRECTED sort_alerts")
TABLE(["Pass", "key", "Shifts", "Inserted at", "List after the pass"], [
    ["start", "–", "–", "–", "A1:3  A2:9  A3:5  A4:9  A5:1"],
    ["i = 1", "A2:9", "1 (A1)", "0", "A2:9  A1:3  A3:5  A4:9  A5:1"],
    ["i = 2", "A3:5", "1 (A1)", "1", "A2:9  A3:5  A1:3  A4:9  A5:1"],
    ["i = 3", "A4:9", "2 (A1, A3)", "1", "A2:9  A4:9  A3:5  A1:3  A5:1"],
    ["i = 4", "A5:1", "0", "4", "A2:9  A4:9  A3:5  A1:3  A5:1"],
], [1.6, 1.6, 2.8, 2.4, 8.6], size=8.5, bold_first=True)
P("At i = 3 the key A4:9 stops in front of A2:9 because the test 9 < 9 is false; equal severities therefore keep their arrival order "
  "(stability), which is why the strict '<' must be kept.", size=9.5)

H3("Table B3 – Alignment table for log = FAILFAIXFAIL, pattern = FAIL  (n = 12, m = 4)")
log, pat = "FAILFAIXFAIL", "FAIL"
n, m = len(log), len(pat)
rows = []
for i in range(n - m + 1):
    cmp_ = []
    j = 0
    while j < m:
        ok = log[i + j] == pat[j]
        cmp_.append(f"{log[i+j]}{'=' if ok else '≠'}{pat[j]}")
        if not ok:
            break
        j += 1
    true_hit = j == m
    if i < n - m:
        orig = "reported" if j >= m - 1 else "no"
    else:
        orig = "never tried"
    rows.append([i, log[i:i + m], "  ".join(cmp_), "YES" if true_hit else "no", orig,
                 "YES" if true_hit else "no"])
TABLE(["i", "Text window", "Comparisons (stop at first ≠)", "Real match", "Original reports", "Corrected reports"],
      rows, [0.9, 2.2, 5.4, 2.2, 3.3, 3.0], size=8.5, mono_cols=(1, 2))
P("Row i = 4 is the false signature (FAIX): the original accepts it through D6. Row i = 8 is the real signature at the end of the log, "
  "which the original never reaches because of D5.", size=9.5)

H2("B.4  Re-test after every correction")
P("Outputs after each cumulative fix (from results/debug_steps_log.txt). The function changed in each step is shown; the others kept their previous result.", keep=True)
TABLE(["Step", "Function", "Output on the test data", "Status"], [
    ["original", "all", "sort [A4,A3,A3,A5,A5]; blocked [F,F,F]; sig [0,4]; closest ((0,2), 60.44)", "all wrong"],
    ["after D1", "sort_alerts", "[A1, A1, A1, A1, A4]", "still wrong (D2)"],
    ["after D2", "sort_alerts", "[A2, A4, A3, A1, A5]", "correct"],
    ["after D3", "is_blocked", "[False, True, False]", "still wrong (D4)"],
    ["after D4", "is_blocked", "[True, True, False]; empty list → False", "correct"],
    ["after D5", "find_signature", "[0, 4, 8]", "still wrong (D6)"],
    ["after D6", "find_signature", "[0, 8]", "correct"],
    ["after D7", "closest_logins", "(None, inf)", "still wrong (D8)"],
    ["after D8", "closest_logins", "((0, 0), 0.0)", "still wrong (D9)"],
    ["after D9", "closest_logins", "((0, 5), 1.4142135623730951)", "correct"],
], [2.0, 2.8, 9.2, 3.0], size=8.5, bold_first=True)
IMG(os.path.join(RES, "shot_run_corrected.png"), 12.5, "Figure 2 – Execution output of the corrected module: actual equals expected for all four functions.")

H2("B.5  Boundary tests")


def run(f, *a):
    try:
        return f(*a)
    except Exception as e:  # pragma: no cover
        return type(e).__name__


bt = [
    ("sort_alerts", "empty list", "[]", lambda m: m.sort_alerts([])),
    ("sort_alerts", "single alert", "[(X,4)]", lambda m: m.sort_alerts([("X", 4)])),
    ("sort_alerts", "equal severities a, b, c (all 5)", "[a, b, c]", lambda m: [x[0] for x in m.sort_alerts([("a", 5), ("b", 5), ("c", 5)])]),
    ("is_blocked", "empty blocklist", "False", lambda m: m.is_blocked([], "10.0.0.5")),
    ("is_blocked", "IP is the last entry", "True", lambda m: m.is_blocked(["a", "b", "c"], "c")),
    ("find_signature", "pattern at the very end (xxxxFAIL)", "[4]", lambda m: m.find_signature("xxxxFAIL", "FAIL")),
    ("find_signature", "pattern longer than log (FAI / FAIL)", "[]", lambda m: m.find_signature("FAI", "FAIL")),
    ("find_signature", "pattern equals log", "[0]", lambda m: m.find_signature("FAIL", "FAIL")),
    ("find_signature", "overlapping (aa in aaaa)", "[0, 1, 2]", lambda m: m.find_signature("aaaa", "aa")),
    ("closest_logins", "empty list", "(None, None)", lambda m: m.closest_logins([])),
    ("closest_logins", "one event", "(None, None)", lambda m: m.closest_logins([(1, 1)])),
    ("closest_logins", "two events (0,0), (3,4)", "((0, 1), 5.0)", lambda m: m.closest_logins([(0, 0), (3, 4)])),
]
rows = []
for fn, desc, exp, t_ in bt:
    o, c, p_ = run(t_, ORIG), run(t_, COR), run(t_, OPT)
    rows.append([fn, desc, exp, str(o), str(c), str(p_)])
TABLE(["Function", "Test", "Expected", "Original", "Corrected", "Optimised"], rows,
      [2.5, 4.4, 2.5, 2.7, 2.5, 2.4], size=8, mono_cols=(2, 3, 4, 5))
P("Two original results look right only by accident: with one pair the 'farthest pair' is the only pair, and with n = m the buggy loop range is "
  "empty. Defining the empty-pattern and fewer-than-two-events behaviour is a design decision (documented in the docstrings): "
  "find_signature returns [] and closest_logins returns (None, None). The original returned (None, 0) for these inputs, which looks like a real result.", size=9.5)

# =================================================================== PART C
page_break()
H1("Part (c) – Optimise the Corrected Module (10 marks)")
P("All optimisations keep the corrected outputs. The final module is src/optimised.py (listed in Part (e)).")
H2("C.1  Pseudocode of the optimised algorithms")
for k, v in OPTIMISED.items():
    CODE(v, size=7.5, caption=k)

H2("C.2  sort_alerts – is insertion sort still suitable?")
n50 = fmt(ns50["insertion_comparisons"])
P(f"Insertion sort costs Θ(n + I) where I is the number of inversions (pairs in the wrong order). For a queue that is nearly sorted it is "
  f"excellent: in the measurements an already sorted queue of 50,000 alerts plus 20 late arrivals needed {n50} comparisons, about "
  f"{int(ns50['insertion_comparisons'])/50000:.1f} per alert. It is also stable, in place and simple.")
P("It is not suitable as the general method, because the cost depends entirely on the input order and has no safety margin. "
  "For random order I ≈ 0.225·n² with 10 severity levels, i.e. about 560 million comparisons for 50,000 alerts "
  "(measured 22.7 million already for 10,000), and in the worst case (alerts arriving lowest severity first) n(n − 1)/2 = 1,249,975,000.")
P("Decision: replace it by the built-in stable merge-based sort (Timsort). It is also adaptive (about n comparisons on nearly sorted data) "
  "but guarantees O(n log n) on any input. list.sort(reverse=True) keeps equal severities in arrival order, so the output is identical. "
  "The corrected insertion sort is kept as sort_alerts_insertion for comparison.")

H2("C.3  is_blocked – repeated blocklist look-ups")
P("Every alert triggers a look-up, so 50,000 queries against b blocked addresses cost q·b comparisons with sequential search. "
  "The blocklist is converted once into a hash set (build_blocklist, O(b)); each look-up is then O(1) on average, giving O(b + q) in total. "
  "is_blocked accepts either form, so a plain list still works through sequential search. A sorted list with binary search (O(log b) per look-up) "
  "would also work, but the hash set is simpler and faster here.")

H2("C.4  find_signature – no redundant comparisons")
B("only the n − m + 1 feasible alignments are tried; m = 0 and m > n return [] immediately;")
B("each alignment is abandoned at its first mismatch, and a match is declared only when j reaches m, so the wrong post-loop test (D6) and its extra comparisons disappear;")
B("every character comparison therefore either extends the current match or ends the alignment. The experiment confirms that the measured "
  "count equals the minimum possible count computed independently for all four test cases.")

H2("C.5  closest_logins – three techniques")
B("each unordered pair is examined once (n(n − 1)/2 instead of n²: no self-pairs, no repeated pairs);", "Pairs: ")
B("squared distances are compared; one math.sqrt is taken at the end instead of one per pair, removing the most expensive of the 7 operations per pair;", "No square root: ")
B("events are visited in order of x. If the x-gap alone is larger than the best distance so far, no later point can be closer, so the inner loop stops. "
  "The test is strict (dx² > best), so pairs that tie with the best are still examined and the same pair as brute force is returned.", "Pruning: ")
P("Pruning does not change the worst-case complexity: if all logins have the same x (all on one meridian) nothing can be pruned and the "
  "algorithm degrades to n(n − 1)/2 pair checks. The next step beyond brute force would be the O(n log n) divide-and-conquer closest-pair algorithm; "
  "it is outside the scope of this brute-force task.", size=10)

# =================================================================== PART D
page_break()
H1("Part (d) – Analysis Before and After (10 marks)")
H2("D.1  Operation counts and time complexity")
P("Basic operation = one comparison (sort, search, string matching) or one distance computation (closest pair). "
  "For the closest pair one full distance costs 2 subtractions, 2 multiplications, 1 addition, 1 square root and 1 comparison = 7 operations.", keep=True)
TABLE(["Function", "Before (after correction)", "After optimisation"], [
    ["sort_alerts",
     "Comparisons: best n − 1 (sorted), worst n(n − 1)/2 (reverse), average ≈ n²/4 for distinct keys. Moves ≈ comparisons. "
     "T(n) = Θ(n²) worst/average, Θ(n) best. Space O(1). n = 50,000: 49,999 / 1,249,975,000 / ≈ 625,000,000.",
     "Timsort: best n − 1, worst ≈ n·log₂n comparisons (≈ 0.78 million for n = 50,000). T(n) = O(n log n), Θ(n) when nearly sorted. Space O(n)."],
    ["is_blocked",
     "One lookup: best 1, worst b comparisons, average b/2 for a hit. q lookups: q·b worst case. T = O(q·b). "
     "Example q = 50,000, b = 1,000: ≈ 50 million comparisons worst case.",
     "Build O(b) once, then O(1) average per lookup. T = O(b + q) = 51,000 operations for the example."],
    ["find_signature",
     "(n − m + 1) alignments, each 1 … m comparisons: best n − m + 1 (first character always wrong), worst m(n − m + 1) (e.g. aaa…a with aaab). T = O(nm). "
     "The original did (n − m) alignments, so it missed one and mis-tested the rest.",
     "Same bounds, T = O(nm), but exactly the minimum comparisons for every input; no extra test per alignment. Space O(1) besides the output."],
    ["closest_logins",
     "Original: n² distances × 7 = 7n² operations (n = 8,000: 64 million distances). Corrected: n(n − 1)/2 distances (31,996,000 for n = 8,000) × 7. T = Θ(n²).",
     "Sort by x: O(n log n) comparisons. Then P pairs examined, P ≤ n(n − 1)/2, each costing 7 cheap operations (2 subtractions, 2 multiplications, 1 addition, prune test and best test) and no square root. T = O(n log n + P): worst case Θ(n²), "
     "much smaller P when points are spread out."],
], [2.6, 7.2, 7.2], size=8.5, bold_first=True)

H2("D.2  Measurement 1 – distance computations in closest_logins")
P("Batch sizes 1,000, 2,000, 4,000 and 8,000 events. Brute-force distance computations were counted by counting the calls to math.sqrt made by the "
  "unmodified corrected function (one per pair); the original's n² was measured for n = 1,000 and 2,000 (1,000,000 and 4,000,000, exactly n²) and follows the same loop structure for larger n. "
  "The optimised count is the stats counter inside optimised.closest_logins. Three data sets (fixed seeds): uniform = random points in a 1000 × 1000 km square; "
  "clustered = 20 city clusters of about 15 km spread; same_x = every login on the same meridian (worst case for the x-pruning). "
  "For every run the optimised result was asserted to be identical to the corrected brute-force result.", keep=True)
rows = []
for r in cp_rows:
    rows.append([r["dataset"], fmt(r["n"]), fmt(r["original_dist_comps(n^2)"]), fmt(r["corrected_brute_dist_comps"]),
                 fmt(r["optimised_dist_comps"]), f"{float(r['reduction_factor']):,.0f}×" if float(r['reduction_factor']) > 1.5 else "1.0×",
                 f"{float(r['brute_seconds']):.3f}", f"{float(r['optimised_seconds']):.4f}"])
TABLE(["Data set", "n", "Original n²", "Brute force n(n−1)/2", "Optimised", "Reduction", "Brute s", "Optimised s"], rows,
      [2.1, 1.3, 2.4, 2.7, 2.0, 2.0, 1.7, 2.0], size=8.5, align_right=(1, 2, 3, 4, 5, 6, 7))
IMG(os.path.join(RES, "graph_closest_pair.png"), 12.8, "Figure 3 – Distance computations versus n (log scale). Brute force follows n(n−1)/2; pruning removes almost all work except on the same_x worst case.")
IMG(os.path.join(RES, "shot_experiments.png"), 12.5, "Figure 4 – Execution output of run_experiments.py (closest_logins part).")

H2("D.3  Measurement 2 – insertion-sort comparisons, nearly sorted versus random")
P("Comparisons were counted by giving each severity an int subclass that counts every '<' (the sorting code itself is unmodified). Severities are 1–10 (many ties). "
  "Random: random order. Nearly sorted: a queue already sorted by severity plus 20 late-arriving alerts. "
  "Prediction for random input: E[comparisons] ≈ 0.225·n(n − 1) + n − 1, because two random severities are strictly ordered the wrong way with probability 0.45 "
  "and each pair is in that state with probability 1/2.", keep=True)
rows = []
for r in so_rows:
    nn = int(r["n"])
    pred = f"{0.225 * nn * (nn - 1) + nn - 1:,.0f}" if r["input"] == "random" else f"≈ {10 * nn:,}"
    rows.append([r["input"].replace("_", " "), fmt(nn), fmt(r["insertion_comparisons"]), pred, fmt(r["timsort_comparisons"]),
                 f"{float(r['insertion_seconds']):.4f}", f"{float(r['timsort_seconds']):.4f}"])
TABLE(["Input", "n", "Insertion (measured)", "Insertion (predicted)", "Timsort", "Insertion s", "Timsort s"], rows,
      [2.4, 1.4, 3.0, 3.2, 2.0, 2.4, 2.6], size=8.5, align_right=(1, 2, 3, 4, 5, 6))
P("The nearly-sorted prediction is n + 0.45·k·n with k = 20 late alerts ≈ 10n; the measured 8.6n–10.4n differs because only 20 random late alerts are inserted "
  "(each one moves past a random fraction of the queue). The random 50,000 case was not run (≈ 560 million comparisons in pure Python); the formula gives it.", size=9.5)
IMG(os.path.join(RES, "graph_sorting.png"), 12.8, "Figure 5 – Comparisons versus n (log–log). Random insertion sort has slope 2; nearly sorted insertion sort and both Timsort curves have slope ≈ 1.")

H2("D.4  Measurement 3 – blocklist look-ups and signature scan")
bl_t = read_csv("blocklist_measurements.csv")[0]
TABLE(["Measure (b = 1,000 addresses, 50,000 look-ups, half hits)", "Sequential list", "Hash set"], [
    ["Average comparisons per look-up", f"{float(bl_t['avg_comparisons_per_lookup_sequential(measured on 5000)']):.1f}  (predicted 0.5·b/2 + 0.5·b = 750)", "≈ 1 hash probe"],
    ["Time for all 50,000 look-ups", f"{float(bl_t['sequential_seconds_for_all_queries']):.3f} s", f"{float(bl_t['set_lookup_seconds_for_all_queries']):.4f} s  (+ {float(bl_t['set_build_seconds'])*1000:.2f} ms to build once)"],
], [8.0, 5.0, 4.0], size=8.5)
sg = read_csv("signature_measurements.csv")
rows = [[r["case"], fmt(r["n"]), r["m"], fmt(r["original_char_comparisons(buggy loop)"]), fmt(r["optimised_char_comparisons"]), r["hits"]] for r in sg]
TABLE(["find_signature case", "n", "m", "Original comparisons", "Corrected/optimised comparisons", "Hits"], rows,
      [5.5, 1.7, 0.9, 3.0, 4.2, 1.6], size=8.5, align_right=(1, 2, 3, 4, 5))
P("On the test log the optimised scan makes 18 comparisons against 14 for the original; the extra 4 are the comparisons of the alignment i = 8, which the original skipped (D5) "
  "– so the higher count is the price of the correct answer. The worst case a¹⁰⁰⁰⁰⁰ / aaaaaaab gives 799,944 = m(n − m + 1) = 8 × 99,993 and the best case 99,997 = n − m + 1, matching the formulas in D.1.", size=9.5)

H2("D.5  Do the measurements agree with the analysis?")
B("Random insertion sort grows by a factor of ≈ 4 when n doubles (231,425 → 900,962 → … → 22.7 million for n = 1,000 … 10,000), matching Θ(n²), and the "
  "values are within 3 % of the 0.225·n(n − 1) prediction. Nearly sorted input grows linearly (≈ 8–10 comparisons per alert), matching Θ(n + I). "
  "Timsort is far below both in every case, as O(n log n) and O(n) predict.", "Sorting – yes. ")
B("The measured 753.7 comparisons per look-up agrees with the predicted 750; the hash set removes the dependence on b, and 50,000 look-ups drop from about {:.1f} s to {:.3f} s.".format(float(bl_t["sequential_seconds_for_all_queries"]), float(bl_t["set_lookup_seconds_for_all_queries"])), "Blocklist – yes. ")
B("Counts equal the independently computed minimum, and the best/worst cases equal n − m + 1 and m(n − m + 1) exactly.", "Signature scan – yes. ")
sx_b, sx_o = float(sx8["brute_seconds"]), float(sx8["optimised_seconds"])
B(f"Brute force matches n(n − 1)/2 exactly (499,500 … 31,996,000) and the original matches n² (1,000,000 and 4,000,000 measured). The optimised counts are far lower on spread-out data "
  f"(for example 14,445 versus 31,996,000 at n = 8,000, a factor of about 2,200) and they are NOT monotone in n (2,004 at n = 1,000 but 1,497 at n = 2,000): the count depends "
  f"on how soon a small best distance is found, i.e. on the data, not just on n. This agrees with the analysis, which only bounds the cost by O(n log n + P) with "
  f"P ≤ n(n − 1)/2. The same_x run confirms the worst case: no reduction at all (31,996,000), only a small time gain ({sx_b:.1f} s against {sx_o:.1f} s) because the square root is gone. "
  f"So pruning is a heuristic improvement for typical location data, not a better worst-case bound.", "Closest pair – yes, with one caution. ")

# =================================================================== PART E
page_break()
H1("Part (e) – Production-Quality Code, Test Harness and Submission (8 marks)")
H2("E.1  Final optimised module (src/optimised.py)")
CODE(open(os.path.join(ROOT, "Source_Code", "optimised.py")).read(), size=7)
H2("E.2  Test harness (tests/test_harness.py)")
P("The harness checks every function of the corrected and the optimised module, including all boundary cases from Part (b): an empty blocklist, a pattern at the very end, "
  "a pattern longer than the log, equal severities and fewer than two login events. It also compares the optimised functions with the corrected ones and with simple reference "
  "implementations on 500 random cases (ties included). It exits with status 1 if any check fails.")
CODE(open(os.path.join(ROOT, "Source_Code", "test_harness.py")).read(), size=7)
IMG(os.path.join(RES, "shot_harness.png"), 14.5, "Figure 6 – Test-harness output (82 passed, 0 failed). The complete log is results/test_harness_log.txt.")

H2("E.3  GitHub repository")
P("Repository layout (as required by the submission instructions):", keep=True)
CODE('''CO2_Debugging_Optimisation/
├── Pseudocode/         Pseudocode.md
├── Source_Code/        original.py  corrected.py  optimised.py  demo.py
│                       test_harness.py  debug_steps.py  run_experiments.py
├── Report/             CSA06_CO2_SentinelOps_Report.docx
├── Supporting_Files/   test datasets, logs, *.csv results, graph_*.png, shot_*.png
└── README.md''', size=8)
CODE('''git init
git add .
git commit -m "CSA06 CO2: SentinelOps module - debugged and optimised"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main''', size=8, caption="Commands to publish (then paste the repository link into Google Classroom and into the cover table above):")

# =================================================================== APPENDICES
page_break()
H1("Appendix A – Original code (as given, indentation restored)")
CODE(open(os.path.join(ROOT, "Source_Code", "original.py")).read(), size=7.5)
H1("Appendix B – Corrected code (nine fixes, structure unchanged)")
CODE(open(os.path.join(ROOT, "Source_Code", "corrected.py")).read(), size=7.5)

out = os.path.join(ROOT, "Report", "CSA06_CO2_SentinelOps_Report.docx")
doc.save(out)
print("saved", out)
