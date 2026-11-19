"""Renders each results/qN_output.txt as a terminal-style PNG into screenshots/ (for the report)."""
import glob, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
for f in sorted(glob.glob("../results/q*_output.txt")):
    lines = open(f).read().rstrip().split("\n")
    h = max(2.0, 0.19 * len(lines) + 0.6); w = max(8, 0.085 * max(len(l) for l in lines) + 0.6)
    fig = plt.figure(figsize=(w, h), facecolor="#1e1e1e")
    fig.text(0.01, 0.99, "\n".join(lines), family="monospace", fontsize=8, color="#d4d4d4", va="top", ha="left")
    name = os.path.basename(f).replace("_output.txt", "_output.png")
    fig.savefig("../screenshots/" + name, dpi=130, facecolor="#1e1e1e"); plt.close(fig)
    print("saved", name)
