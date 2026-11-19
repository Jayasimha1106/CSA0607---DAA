"""Render source/output evidence and prepare a complete HTML report for Word."""

from pathlib import Path
from html.parser import HTMLParser
import html
import struct
import textwrap
from zipfile import ZIP_DEFLATED, ZipFile

try:
    import matplotlib.pyplot as plt
except ImportError as error:
    raise RuntimeError("Report screenshots require the already-available matplotlib package.") from error


SOURCE_DIR = Path(__file__).resolve().parent
REPORT_DIR = SOURCE_DIR.parent / "Report"
SCREENSHOT_DIR = REPORT_DIR / "screenshots"
PART_FILES = [
    ("a", "part_a_basic_ops.py"),
    ("b", "part_b_m1_m2.py"),
    ("c", "part_c_s2_recurrence.py"),
    ("d", "part_d_master_theorem.py"),
    ("e", "part_e_cases.py"),
    ("f", "part_f_proof.py"),
    ("g", "part_g_scalability.py"),
]


def wrapped_lines(text, width):
    lines = []
    for line in text.splitlines():
        if not line:
            lines.append("")
            continue
        lines.extend(textwrap.wrap(
            line,
            width=width,
            subsequent_indent="    ",
            replace_whitespace=False,
            drop_whitespace=False,
            break_long_words=True,
            break_on_hyphens=False,
        ))
    return lines


def render_text_images(text, stem, kind, lines_per_image=42):
    """Render long code/output as readable, numbered monospaced PNG pages."""
    background = "#f4f6f8" if kind == "code" else "#111827"
    foreground = "#1f2937" if kind == "code" else "#e5e7eb"
    accent = "#2563eb" if kind == "code" else "#34d399"
    lines = wrapped_lines(text, 116 if kind == "code" else 126)
    if not lines:
        lines = ["(no output)"]
    paths = []
    for page_number, start in enumerate(range(0, len(lines), lines_per_image), start=1):
        page = lines[start:start + lines_per_image]
        height = max(2.2, 0.26 * (len(page) + 2))
        figure, axis = plt.subplots(figsize=(13, height))
        figure.patch.set_facecolor(background)
        axis.set_facecolor(background)
        axis.axis("off")
        for offset, line in enumerate(page):
            axis.text(
                0.025,
                0.97 - offset * (0.90 / max(1, len(page))),
                f"{start + offset + 1:>3}  {line}",
                family="DejaVu Sans Mono",
                fontsize=8.5 if kind == "code" else 9,
                color=accent if kind == "code" and line.lstrip().startswith("#") else foreground,
                va="top",
                transform=axis.transAxes,
            )
        figure.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.02)
        suffix = f"_{page_number:02d}" if len(lines) > lines_per_image else ""
        path = SCREENSHOT_DIR / f"{stem}_{kind}{suffix}.png"
        figure.savefig(path, dpi=140, facecolor=background)
        plt.close(figure)
        paths.append(path)
    return paths


def image_markup(paths, caption):
    elements = [f"<p class='caption'>{html.escape(caption)}</p>"]
    for path in paths:
        relative = path.relative_to(REPORT_DIR).as_posix()
        elements.append(
            f"<p class='evidence'><img src='{relative}' width='600' "
            f"alt='{html.escape(caption)}'></p>"
        )
    return "\n".join(elements)


def build_evidence():
    output_log = (REPORT_DIR / "execution_output.txt").read_text(encoding="utf-8")
    evidence = {}
    for letter, filename in PART_FILES:
        marker = f"=== RUN: {filename} ==="
        start = output_log.index(marker) + len(marker)
        next_marker = output_log.find("\n=== RUN:", start)
        output = output_log[start:next_marker if next_marker != -1 else len(output_log)].strip()
        source = (SOURCE_DIR / filename).read_text(encoding="utf-8")
        code_images = render_text_images(source, f"part_{letter}", "code")
        output_images = render_text_images(output, f"part_{letter}", "output")
        evidence[letter] = (
            image_markup(code_images, f"Part ({letter}) source code: {filename}"),
            image_markup(output_images, f"Part ({letter}) captured terminal output"),
        )
    return evidence


def report_html(evidence):
    sections = [
        """
        <h1>Scalability Audit of ShopSphere</h1>
        <p><b>Course Code &amp; Name:</b> CSA06 – Design and Analysis of Algorithms</p>
        <p><b>Assessment:</b> CO1 – Assessment Tool 1</p>
        <p><b>Student Name:</b> __________________________________________</p>
        <p><b>Registration Number:</b> ___________________________________</p>
        <p class="cover-note">Prepared 19 November 2026</p>
        <p class="cover-note">A data-structures and recurrence-based analysis of ShopSphere's e-commerce workloads.</p>
        <div class="page-break"></div>
        <h2>Executive summary</h2>
        <p>The audit identifies M1's all-pairs product comparison and the current M4 recurrence as quadratic bottlenecks. M2 is linear despite a contrary Θ(n log n) claim, while S2 is logarithmic. At one million records and 100 million operations per second, M1 and current M4 exceed the ten-minute budget; the other measured workloads pass under the stated operation models.</p>
        <p>All counts and growth ratios below are generated by the included Python scripts. The printed M4 redesign and M5 estimates use their leading Θ models for the million-record budget; the recurrence script separately computes exact recurrence values for powers of two.</p>
        <h2>Model and assumptions</h2>
        <ul>
          <li>One dominant comparison, Audit step, or recurrence level-work unit counts as one operation.</li>
          <li>Binary search operates on a sorted index. Its comparisons are key-to-middle equality/order probes.</li>
          <li>Scalability uses 100,000,000 operations/second and a 600-second window, giving 60,000,000,000 operations.</li>
          <li>Asymptotic runtime estimates ignore machine-specific overhead, memory latency, I/O, concurrency, and implementation constants not stated in the assignment.</li>
        </ul>

        <h2>(a) Input size and dominant basic operations</h2>
        <p>The input size <em>n</em> is the number of products or records processed. The dominant operation is the repeated unit whose count determines the module's asymptotic growth.</p>
        <table><tr><th>Module</th><th>Input</th><th>Dominant basic operation and location</th><th>Growth / reason</th></tr>
          <tr><td>M1</td><td>n products</td><td>Compare the (title, seller) keys of a pair in the nested all-pairs loops.</td><td>Θ(n²); Θ(n) pairs for each of Θ(n) outer-loop positions.</td></tr>
          <tr><td>M2</td><td>n audit records</td><td>Perform one Audit operation during each inner-loop iteration at level i.</td><td>Θ(n); the inner-loop sizes form a geometric series.</td></tr>
          <tr><td>M3 / S1</td><td>n products</td><td>Compare the requested product key with each candidate in a sequential scan.</td><td>Θ(n) worst case; up to n candidates are examined.</td></tr>
          <tr><td>M3 / S2</td><td>n sorted products</td><td>Compare the key with the middle entry in the current search interval.</td><td>Θ(log n); each comparison halves the remaining interval.</td></tr>
          <tr><td>M4 current</td><td>n records</td><td>At each recursive call, process n records and make four calls on half-size inputs.</td><td>Θ(n²); a=4, b=2 and n^(log₂4)=n² dominates f(n)=n.</td></tr>
          <tr><td>M4 redesign</td><td>n records</td><td>Process n records and make two half-size recursive calls.</td><td>Θ(n log n); each of log n levels performs Θ(n) total work.</td></tr>
          <tr><td>M5</td><td>n records</td><td>Perform n log₂n work in the recurrence's non-recursive work at each level.</td><td>Θ(n log²n); Θ(log n) levels, each costing Θ(n) in aggregate.</td></tr>
        </table>
        <p>Space: M1's pairwise scan is O(1) auxiliary space. Recursive S2 uses O(log n) stack space; its iterative version uses O(1). A hash-based M1 redesign trades O(n) extra space for expected linear time.</p>
        """,
        """
        <h2>(b) Exact operation counts: M1 and M2</h2>
        <h3>M1: pairwise comparison</h3>
        <p>For outer-loop index i, compare the current product with each of its n−i−1 later products. Therefore:</p>
        <p class="equation">C₁(n) = Σ<sub>i=0</sub><sup>n−1</sup>(n−i−1) = (n−1)+(n−2)+…+1+0 = n(n−1)/2.</p>
        <p>The leading term is n²/2, so the exact count is Θ(n²) comparisons. The loops retain only counters and indexes, giving O(1) auxiliary space. The executable counter matches the formula for n = 1, 2, 5, 16, 31, and 64.</p>
        <h3>M2: geometric Audit loop</h3>
        <p>Let k = ⌈log₂n⌉. There are k outer iterations. At outer index i, the inner loop performs 2<sup>i</sup> Audit operations—not n operations on every iteration.</p>
        <p class="equation">A₂(n) = 1+2+4+…+2<sup>k−1</sup> = (2<sup>k</sup>−1)/(2−1) = 2<sup>⌈log₂n⌉</sup>−1.</p>
        <p>Because n ≤ 2<sup>k</sup> &lt; 2n, this total is Θ(n). For n = 1,024, k=10 and A₂=1+2+…+512=1,023. The Θ(n log n) claim is incorrect: it treats the inner loop as n steps on every outer iteration instead of summing its geometric sizes.</p>
        <p>The script prints A₂/n and A₂/(n log₂n). The first stays bounded (near 1 to 2); the second decreases as n grows, consistent with Θ(n), not Θ(n log n).</p>
        """,
        """
        <h2>(c) S2 recurrence and space</h2>
        <p>Binary search examines a middle entry, then continues on at most half the remaining sorted range. With one comparison unit per level, the worst-case recurrence and base are:</p>
        <p class="equation">T(n)=T(n/2)+1, for n&gt;1; &nbsp; T(1)=1.</p>
        <p>Backward substitution, for n=2<sup>k</sup>:</p>
        <ol>
          <li>T(n)=T(n/2)+1.</li><li>=T(n/2²)+2.</li><li>=T(n/2³)+3.</li>
          <li>After j substitutions: T(n)=T(n/2<sup>j</sup>)+j.</li>
          <li>Set j=k=log₂n, so n/2<sup>k</sup>=1.</li>
          <li>T(n)=T(1)+k=1+log₂n, hence Θ(log n).</li>
        </ol>
        <p>The program searches for the deepest (last) key for n=2<sup>k</sup>, confirming k+1 comparisons for both iterative and recursive implementations over k=0…10. Iteration uses O(1) auxiliary space. Recursion has O(log n) stack frames, as the printed depth demonstrates.</p>
        """,
        """
        <h2>(d) Master Theorem and recurrence checks</h2>
        <h3>M4 current</h3>
        <p>a=4, b=2, f(n)=n, and n<sup>log₂4</sup>=n². Since n=O(n<sup>2−ε</sup>) for ε=1, this is Case 1 and T(n)=Θ(n²). With T(1)=1 and n a power of two, substitution gives T(n)=4(2(n/2)²−n/2)+n=2n²−n; thus T(n)/n² approaches 2. Doubling n multiplies the leading cost by about 4.</p>
        <h3>M4 redesign</h3>
        <p>a=2, b=2, f(n)=n, and n<sup>log₂2</sup>=n. This is Case 2 with f(n)=Θ(n), so T(n)=Θ(n log n). For T(1)=1, T(n)=2T(n/2)+n resolves to n log₂n+n. The T(n)/(n log₂n) ratio approaches 1; the doubling ratio is slightly above 2 and approaches 2.</p>
        <h3>M5: extended Master Theorem and recursion tree</h3>
        <p>a=2, b=2, n<sup>log₂2</sup>=n and f(n)=n log n. The ratio f(n)/n=log n is not O(n<sup>−ε</sup>) and is not Θ(1); f(n) is also not polynomially larger than n because log n is not Ω(n<sup>ε</sup>). Therefore none of the three basic cases applies. The extended Case 2 (f(n)=Θ(n<sup>log_ba</sup>log<sup>k</sup>n), k=1) gives Θ(n log²n).</p>
        <p>Recursion-tree confirmation: at level i, there are 2<sup>i</sup> subproblems of size n/2<sup>i</sup>. Their combined level cost is 2<sup>i</sup>(n/2<sup>i</sup>)log₂(n/2<sup>i</sup>)=n(log₂n−i). For n=2<sup>k</sup>, summing levels i=0…k−1 gives n(k+(k−1)+…+1)=n·k(k+1)/2=Θ(n log²n); the leaves add Θ(n). The computed T(n)/(n log²n) ratios approach a positive constant.</p>
        <p>All three recurrences are numerically evaluated with T(1)=1 for powers of two. The printed T(2n)/T(n) values trend toward 4 for current M4 and toward 2 for the redesign and M5 (with logarithmic factors making the latter two slightly above 2 at finite sizes).</p>
        """,
        """
        <h2>(e) Best, average, and worst search cases</h2>
        <h3>S1: sequential scan</h3>
        <p>Best case: 1 comparison (the first product matches). Worst case: n comparisons (the match is last or the key is absent). If a successful key is uniformly distributed, the position counts are 1,2,…,n and:</p>
        <p class="equation">A<sub>success</sub>(n)=(1+2+…+n)/n=n(n+1)/(2n)=(n+1)/2.</p>
        <p>If success occurs with probability p and a miss requires n comparisons, the expected count is A(n)=p(n+1)/2+(1−p)n. For n=1,000,000 and p=0.5, this is 0.5(500,000.5)+0.5(1,000,000)=750,000.25 comparisons. The n=16 simulation verifies the successful-average formula: 8.5 comparisons.</p>
        <h3>S2: binary search</h3>
        <p>Best case: 1 comparison when the key is at the midpoint. Worst case: ⌊log₂n⌋+1 comparisons (20 at n=1,000,000). For uniformly successful keys, the average is approximately log₂n−1 (and is Θ(log n)); the simulation measures 3.375 comparisons at n=16, compared with the approximation 3. The exact average depends on the shape of the search tree.</p>
        <p>Use S2 when the product index remains sorted and available; otherwise a hash lookup is another expected O(1) lookup option after indexing.</p>
        """,
        """
        <h2>(f) Prove f(n)=Θ(n²), but f(n) is not O(n)</h2>
        <p>Let f(n)=3n²+10n log₂n+50 for integer n≥1.</p>
        <p><b>Lower bound:</b> all terms are nonnegative, so f(n)≥3n². Choose c₁=3.</p>
        <p><b>Upper bound:</b> for n≥1, log₂n≤n, so 10n log₂n≤10n². Also 50≤50n². Hence f(n)≤3n²+10n²+50n²=63n². Choose c₂=63 and n₀=1.</p>
        <p>Thus 3n²≤f(n)≤63n² for every n≥1, proving f(n)=Θ(n²). The script numerically checks the bounds at n=1, 2, 10, 100, 1,000, 1,000,000 and 100,000,000.</p>
        <p><b>Not O(n):</b> if f(n)≤cn for all sufficiently large n, then 3n²≤cn, implying n≤c/3. This fails for every n&gt;c/3, a contradiction. Equivalently, f(n)/n≥3n grows without bound; the script displays increasing ratios.</p>
        """,
        """
        <h2>(g) Scalability and redesign decisions</h2>
        <p>At n=1,000,000, 100,000,000 operations/second, the window is 600 seconds or 60,000,000,000 operations. The scalable counts in the code use M1's exact count, M2's exact geometric sum, S2's worst-case comparison formula, and the leading Θ-models n², n log₂n and n log₂²n for M4 current, M4 redesign and M5, respectively.</p>
        <table><tr><th>Module</th><th>Operations at n=1,000,000</th><th>Estimated time</th><th>Window</th></tr>
          <tr><td>M1</td><td>499,999,500,000</td><td>4,999.995000 s (about 83.3 min)</td><td><b>FAIL</b></td></tr>
          <tr><td>M2</td><td>1,048,575</td><td>0.010485750 s</td><td><b>PASS</b></td></tr>
          <tr><td>S1 (worst case)</td><td>1,000,000</td><td>0.010000000 s</td><td><b>PASS</b></td></tr>
          <tr><td>S2</td><td>20 comparisons</td><td>0.000000200 s (model)</td><td><b>PASS</b></td></tr>
          <tr><td>M4 current</td><td>1,000,000,000,000</td><td>10,000 s (about 2.78 h)</td><td><b>FAIL</b></td></tr>
          <tr><td>M4 redesign</td><td>19,931,568.57</td><td>0.199315686 s</td><td><b>PASS</b></td></tr>
          <tr><td>M5</td><td>397,267,425.63</td><td>3.972674256 s</td><td><b>PASS</b></td></tr>
        </table>
        <p>The M4 and M5 counts above are leading-term operation models, not exact integer instruction counts. Exact powers-of-two recurrence evaluations (including M4 redesign's additional n term) are shown in part (d). All figures are theoretical estimates at the stipulated throughput, not wall-clock benchmarks.</p>
        <h3>Growth when input increases from 100,000 to 1,000,000</h3>
        <table><tr><th>Module</th><th>T(100,000)</th><th>T(1,000,000)</th><th>Growth ratio</th></tr>
          <tr><td>M1</td><td>4,999,950,000</td><td>499,999,500,000</td><td>100.000900</td></tr>
          <tr><td>M2</td><td>131,071</td><td>1,048,575</td><td>8.000053</td></tr>
          <tr><td>S1 (worst case)</td><td>100,000</td><td>1,000,000</td><td>10.000000</td></tr>
          <tr><td>S2</td><td>17</td><td>20</td><td>1.176471</td></tr>
          <tr><td>M4 current</td><td>10,000,000,000</td><td>1,000,000,000,000</td><td>100.000000</td></tr>
          <tr><td>M4 redesign</td><td>1,660,964.05</td><td>19,931,568.57</td><td>12.000000</td></tr>
          <tr><td>M5</td><td>27,588,015.67</td><td>397,267,425.63</td><td>14.400000</td></tr>
        </table>
        <h3>Recommendations</h3>
        <ol>
          <li><b>Redesign M1:</b> index products by the composite (title, seller) key in a hash map/set for expected O(n) total time and O(n) extra space; alternatively sort by (title, seller) and scan adjacent entries in O(n log n) time.</li>
          <li><b>Redesign M4:</b> remove redundant replicated recursion and use the non-replicated two-half design 2T(n/2)+n, reducing Θ(n²) to Θ(n log n).</li>
          <li><b>Keep M2, S2 and M5:</b> their modeled work fits the window; keep S2 backed by a sorted index.</li>
          <li><b>Replace S1 on large catalog searches:</b> use S2 when sorted-index ordering is maintained, or use a hash lookup when the workload favors key lookup.</li>
        </ol>
        """,
        """
        <h2>Conclusion</h2>
        <p>The core scalability risks are the all-pairs M1 scan and M4's four-way recursive duplication. Their quadratic growth makes each tenfold input increase roughly a hundredfold operation increase. M2's geometric inner loop is linear, not n log n, and S2's logarithmic search is practical at million-record scale. The recommended composite-key index and two-child M4 redesign address the bottlenecks while preserving the audit and search functionality.</p>
        <h2>Summary of results</h2>
        <table><tr><th>Component</th><th>Time</th><th>Auxiliary space</th><th>Audit outcome</th></tr>
          <tr><td>M1 current pairwise scan</td><td>Θ(n²)</td><td>O(1)</td><td>Fail; redesign with hash or sort-and-scan.</td></tr>
          <tr><td>M2 Audit loop</td><td>Θ(n)</td><td>O(1)</td><td>Pass; Θ(n log n) claim rejected.</td></tr>
          <tr><td>S1 linear search</td><td>Best Θ(1), average/worst Θ(n)</td><td>O(1)</td><td>Replace for large catalog lookups.</td></tr>
          <tr><td>S2 binary search</td><td>Θ(log n)</td><td>O(1) iterative; O(log n) recursive</td><td>Pass; use sorted index.</td></tr>
          <tr><td>M4 current</td><td>Θ(n²)</td><td>O(log n) recursion depth</td><td>Fail; four-way design is too costly.</td></tr>
          <tr><td>M4 redesign</td><td>Θ(n log n)</td><td>O(log n) recursion depth</td><td>Pass; recommended replacement.</td></tr>
          <tr><td>M5</td><td>Θ(n log²n)</td><td>Recurrence-dependent</td><td>Pass under supplied model.</td></tr>
          <tr><td>f(n)=3n²+10n log₂n+50</td><td>Θ(n²), not O(n)</td><td>—</td><td>Bounds verified with c₁=3, c₂=63, n₀=1.</td></tr>
        </table>
        <h2>Code of Conduct declaration</h2>
        <p>I declare that this submission is my own work, that sources or assistance used have been acknowledged where required, and that I have followed the institution's academic integrity and Code of Conduct requirements.</p>
        <p><b>Name:</b> ____________________________________ &nbsp;&nbsp; <b>Signature:</b> ______________________________</p>
        <p><b>Date:</b> ____________________________________</p>
        <h2>Appendix: generated plots</h2>
        <p>The growth charts below are generated by <code>plots.py</code> and are also provided as PNG files in the report's <code>graphs</code> folder.</p>
        <p class="evidence"><img src="graphs/growth_curves.png" alt="ShopSphere module growth curves"></p>
        <p class="caption">Figure 1. Representative asymptotic growth curves for the audited modules (log-log axes).</p>
        <p class="evidence"><img src="graphs/m2_vs_growth_candidates.png" alt="M2 compared with n and n log n"></p>
        <p class="caption">Figure 2. M2 exact Audit count compared with n and n log₂n; M2 tracks linear growth.</p>
        """,
    ]

    evidence_html = []
    for letter, filename in PART_FILES:
        code_html, output_html = evidence[letter]
        evidence_html.append(
            f"<h3>Part ({letter}) evidence</h3><p>Implemented in <code>{html.escape(filename)}</code>.</p>"
            f"{code_html}{output_html}"
        )
    full_sections = sections[:]
    for index, evidence_section in enumerate(evidence_html, start=1):
        full_sections[index] += evidence_section
    body = "\n".join(full_sections)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Scalability Audit of ShopSphere</title>
<style>
body {{ font-family: Calibri, Arial, sans-serif; color: #172033; font-size: 11pt; line-height: 1.35; }}
h1 {{ color: #163a63; font-size: 28pt; margin-top: 40pt; }}
h2 {{ color: #163a63; font-size: 19pt; border-bottom: 1px solid #9db4cc; padding-bottom: 4pt; page-break-after: avoid; }}
h3 {{ color: #24527a; font-size: 14pt; page-break-after: avoid; }}
p {{ margin: 6pt 0; }}
li {{ margin: 4pt 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 10pt 0; font-size: 9.5pt; }}
th {{ background: #dce8f3; color: #163a63; }}
td, th {{ border: 1px solid #8da3b8; padding: 5pt; vertical-align: top; }}
.equation {{ text-align: center; font-weight: bold; color: #163a63; margin: 12pt; }}
.caption {{ color: #4b5563; font-style: italic; font-size: 9pt; margin-top: 10pt; }}
.evidence {{ text-align: center; }}
.evidence img {{ width: 6.25in; height: auto; }}
.cover-note {{ color: #53677d; margin-top: 22pt; }}
.page-break {{ page-break-after: always; }}
code {{ font-family: Consolas, monospace; color: #204c75; }}
</style></head><body>{body}</body></html>"""


class ReportHtmlParser(HTMLParser):
    """Read the report's simple HTML blocks for a dependency-free DOCX writer."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self.paragraph_tag = None
        self.paragraph_class = ""
        self.paragraph_text = []
        self.paragraph_images = []
        self.table_rows = []
        self.table_row = None
        self.table_cell = None
        self.table_cell_header = False
        self.in_table = False
        self.in_head = False
        self.suppress_tag = None

    def flush_paragraph(self):
        if self.paragraph_tag is None:
            return
        text = "".join(self.paragraph_text).strip()
        if text:
            kind = "equation" if self.paragraph_class == "equation" else self.paragraph_tag
            if self.paragraph_tag == "li":
                text = "• " + text
            self.blocks.append(("paragraph", kind, text))
        for image in self.paragraph_images:
            self.blocks.append(("image", image))
        self.paragraph_tag = None
        self.paragraph_text = []
        self.paragraph_images = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "head":
            self.in_head = True
        if tag in ("style", "script", "title"):
            self.suppress_tag = tag
        if self.suppress_tag:
            return
        if tag == "div" and "page-break" in attributes.get("class", ""):
            self.flush_paragraph()
            self.blocks.append(("page_break",))
        elif tag == "table":
            self.flush_paragraph()
            self.in_table = True
            self.table_rows = []
        elif self.in_table and tag == "tr":
            self.table_row = []
        elif self.in_table and tag in ("td", "th"):
            self.table_cell = []
            self.table_cell_header = tag == "th"
        elif self.in_table and tag == "br" and self.table_cell is not None:
            self.table_cell.append(" ")
        elif not self.in_table and tag in ("h1", "h2", "h3", "p", "li"):
            self.flush_paragraph()
            self.paragraph_tag = tag
            self.paragraph_class = attributes.get("class", "")
        elif not self.in_table and tag == "img" and self.paragraph_tag is not None:
            self.paragraph_images.append(attributes["src"])
        elif not self.in_table and tag == "br" and self.paragraph_tag is not None:
            self.paragraph_text.append(" ")

    def handle_endtag(self, tag):
        if self.suppress_tag == tag:
            self.suppress_tag = None
            return
        if tag == "head":
            self.in_head = False
        if self.in_head:
            return
        if self.in_table and tag in ("td", "th") and self.table_cell is not None:
            self.table_row.append(("".join(self.table_cell).strip(), self.table_cell_header))
            self.table_cell = None
        elif self.in_table and tag == "tr" and self.table_row is not None:
            self.table_rows.append(self.table_row)
            self.table_row = None
        elif self.in_table and tag == "table":
            self.blocks.append(("table", self.table_rows))
            self.table_rows = []
            self.in_table = False
        elif not self.in_table and tag in ("h1", "h2", "h3", "p", "li"):
            self.flush_paragraph()

    def handle_data(self, data):
        if self.suppress_tag or self.in_head:
            return
        if self.table_cell is not None:
            self.table_cell.append(data)
        elif self.paragraph_tag is not None:
            self.paragraph_text.append(data)


def xml_text(value):
    return html.escape(value, quote=False)


def make_run(text, size=22, bold=False, color=None, italic=False):
    properties = [f'<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>', f'<w:sz w:val="{size}"/>']
    if bold:
        properties.append("<w:b/>")
    if italic:
        properties.append("<w:i/>")
    if color:
        properties.append(f'<w:color w:val="{color}"/>')
    return (
        f"<w:r><w:rPr>{''.join(properties)}</w:rPr>"
        f'<w:t xml:space="preserve">{xml_text(text)}</w:t></w:r>'
    )


def make_paragraph(kind, text):
    settings = {
        "h1": (56, True, "163A63", "center", 300, 180),
        "h2": (38, True, "163A63", "left", 260, 100),
        "h3": (30, True, "24527A", "left", 180, 60),
        "equation": (24, True, "163A63", "center", 120, 120),
        "li": (22, False, None, "left", 50, 20),
        "p": (22, False, None, "left", 60, 40),
    }
    size, bold, color, alignment, before, after = settings.get(kind, settings["p"])
    ppr = (
        f'<w:pPr><w:jc w:val="{alignment}"/>'
        f'<w:spacing w:before="{before}" w:after="{after}"/>'
        "</w:pPr>"
    )
    return f"<w:p>{ppr}{make_run(text, size, bold, color, kind == 'equation')}</w:p>"


def make_table(rows):
    if not rows:
        return ""
    column_count = max(len(row) for row in rows)
    total_width = 9360
    column_width = total_width // column_count
    borders = (
        "<w:tblBorders>"
        '<w:top w:val="single" w:sz="4" w:color="8DA3B8"/>'
        '<w:left w:val="single" w:sz="4" w:color="8DA3B8"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="8DA3B8"/>'
        '<w:right w:val="single" w:sz="4" w:color="8DA3B8"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="8DA3B8"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="8DA3B8"/>'
        "</w:tblBorders>"
    )
    table = (
        f'<w:tbl><w:tblPr><w:tblW w:w="{total_width}" w:type="dxa"/>'
        f"{borders}</w:tblPr><w:tblGrid>"
        + "".join(f'<w:gridCol w:w="{column_width}"/>' for _ in range(column_count))
        + "</w:tblGrid>"
    )
    for row_index, row in enumerate(rows):
        table += "<w:tr>"
        for cell_text, is_header in row:
            header = is_header or row_index == 0
            shading = '<w:shd w:fill="DCE8F3"/>' if header else ""
            cell_run = make_run(cell_text, 19, header, "163A63" if header else None)
            table += (
                f'<w:tc><w:tcPr><w:tcW w:w="{column_width}" w:type="dxa"/>'
                f"{shading}</w:tcPr><w:p><w:pPr><w:spacing w:after=\"35\"/></w:pPr>"
                f"{cell_run}</w:p></w:tc>"
            )
        table += "</w:tr>"
    return table + "</w:tbl>"


def image_paragraph(image_source, report_dir, image_relations):
    image_path = (report_dir / image_source).resolve()
    image_data = image_path.read_bytes()
    width_px, height_px = struct.unpack(">II", image_data[16:24])
    max_width = 5_700_000
    cx = min(max_width, width_px * 9525)
    cy = int(cx * height_px / width_px)
    relationship_id = f"rId{len(image_relations) + 1}"
    media_name = f"image{len(image_relations) + 1}.png"
    image_relations.append((relationship_id, media_name, image_data))
    drawing = f"""
    <w:p><w:pPr><w:jc w:val="center"/><w:spacing w:before="50" w:after="50"/></w:pPr>
      <w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="{cx}" cy="{cy}"/>
        <wp:docPr id="{len(image_relations)}" name="{media_name}"/>
        <wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>
        <a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
          <pic:pic><pic:nvPicPr><pic:cNvPr id="{len(image_relations)}" name="{media_name}"/><pic:cNvPicPr/></pic:nvPicPr>
          <pic:blipFill><a:blip r:embed="{relationship_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
          <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>
        </a:graphicData></a:graphic>
      </wp:inline></w:drawing></w:r>
    </w:p>"""
    return drawing


def write_docx(report_markup, report_dir, output_path):
    parser = ReportHtmlParser()
    parser.feed(report_markup)
    image_relations = []
    body = []
    for block in parser.blocks:
        if block[0] == "paragraph":
            body.append(make_paragraph(block[1], block[2]))
        elif block[0] == "table":
            body.append(make_table(block[1]))
        elif block[0] == "image":
            body.append(image_paragraph(block[1], report_dir, image_relations))
        elif block[0] == "page_break":
            body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
<w:body>{''.join(body)}
<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="900" w:right="900" w:bottom="900" w:left="900" w:header="450" w:footer="450" w:gutter="0"/></w:sectPr>
</w:body></w:document>"""
    relationships = [
        '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    ]
    for relationship_id, media_name, _ in image_relations:
        relationships.append(
            f'<Relationship Id="{relationship_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{media_name}"/>'
        )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(relationships)
        + "</Relationships>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        "</Types>"
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>'
        '<w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="80"/></w:pPr>'
        '</w:pPrDefault></w:docDefaults></w:styles>'
    )
    with ZipFile(output_path, "w", ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", content_types)
        package.writestr("_rels/.rels", root_rels)
        package.writestr("word/document.xml", document)
        package.writestr("word/_rels/document.xml.rels", rels_xml)
        package.writestr("word/styles.xml", styles)
        for _, media_name, image_data in image_relations:
            package.writestr(f"word/media/{media_name}", image_data)


def main():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for graph in ("growth_curves.png", "m2_vs_growth_candidates.png"):
        if not (REPORT_DIR / "graphs" / graph).exists():
            raise FileNotFoundError(f"Required graph not found: {graph}; run run_all.py first.")
    evidence = build_evidence()
    output_path = REPORT_DIR / "report_temp.html"
    markup = report_html(evidence)
    output_path.write_text(markup, encoding="utf-8")
    docx_path = REPORT_DIR / "Scalability_Audit_of_ShopSphere.docx"
    write_docx(markup, REPORT_DIR, docx_path)
    screenshot_count = len(list(SCREENSHOT_DIR.glob("*.png")))
    print(f"Rendered {screenshot_count} source/output evidence images.")
    print(f"Created the DOCX report at {docx_path}")
    print(f"Prepared temporary Word-importable markup at {output_path}")


if __name__ == "__main__":
    main()
