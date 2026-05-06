import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np

# ── Brand colours ──────────────────────────────────────────────────────────────
NAVY   = "#1a3a5c"
BLUE   = "#2e86ab"
LBLUE  = "#a8dadc"
ACCENT = "#e84855"
GRAY   = "#f4f4f4"
WHITE  = "#ffffff"

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.facecolor":    WHITE,
    "figure.facecolor":  WHITE,
    "axes.titlesize":    11,
    "axes.labelsize":    9,
    "xtick.labelsize":   8,
    "ytick.labelsize":   8,
})


def _fig_to_svg(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.read().decode("utf-8")


def _fmt_billions(x: float, _pos=None) -> str:
    """Format axis tick as abbreviated number."""
    if abs(x) >= 1_000:
        return f"{x/1_000:.0f}N"
    return f"{x:.0f}"


# ── 1. Revenue & EBITDA bar chart ──────────────────────────────────────────────
def revenue_ebitda_chart(years_data: list[dict]) -> str:
    """Bar chart doanh thu và EBITDA theo năm. Trả về SVG string."""
    if not years_data:
        return ""

    years   = [str(d["year"]) for d in years_data]
    revenue = [d.get("revenue", 0) for d in years_data]
    ebitda  = [d.get("ebitda",  0) for d in years_data]

    x      = np.arange(len(years))
    width  = 0.38
    fig, ax = plt.subplots(figsize=(7, 3.8))

    bars1 = ax.bar(x - width / 2, revenue, width, label="Doanh thu", color=NAVY,   zorder=3)
    bars2 = ax.bar(x + width / 2, ebitda,  width, label="EBITDA",    color=BLUE,   zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_billions))
    ax.set_ylabel("Tỷ đồng")
    ax.set_title("Doanh thu & EBITDA theo năm", fontweight="bold", color=NAVY, pad=10)
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)

    # Value labels
    for bar in list(bars1) + list(bars2):
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h * 1.01,
                f"{h:,.0f}",
                ha="center", va="bottom", fontsize=7, color=NAVY,
            )

    fig.tight_layout()
    return _fig_to_svg(fig)


# ── 2. Revenue breakdown pie ───────────────────────────────────────────────────
def revenue_breakdown_pie(segments: list[dict], title: str) -> str:
    """Pie chart cơ cấu doanh thu. Trả về SVG string."""
    if not segments:
        return ""

    labels = [s.get("name", "N/A") for s in segments]
    sizes  = [max(s.get("percentage", 0), 0) for s in segments]

    if sum(sizes) == 0:
        return ""

    palette = [NAVY, BLUE, LBLUE, ACCENT, "#457b9d", "#e9c46a", "#2a9d8f", "#f4a261"]
    colors  = [palette[i % len(palette)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(5.5, 4))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
        startangle=90,
        colors=colors,
        pctdistance=0.78,
        wedgeprops={"linewidth": 0.8, "edgecolor": WHITE},
    )
    for at in autotexts:
        at.set_fontsize(7.5)
        at.set_color(WHITE)

    ax.legend(
        wedges, labels,
        loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=8, frameon=False,
    )
    ax.set_title(title, fontweight="bold", color=NAVY, pad=10)
    fig.tight_layout()
    return _fig_to_svg(fig)


# ── 3. Sensitivity heatmap ─────────────────────────────────────────────────────
def sensitivity_heatmap(sensitivity: dict) -> str:
    """Heatmap sensitivity analysis (WACC × tăng trưởng). Trả về SVG string."""
    wacc_range   = sensitivity.get("wacc_range",   [])
    growth_range = sensitivity.get("growth_range", [])
    values       = sensitivity.get("values",       [])

    if not (wacc_range and growth_range and values):
        return ""

    matrix = np.array(values, dtype=float)
    nrows, ncols = matrix.shape

    fig, ax = plt.subplots(figsize=(max(5, ncols * 0.9), max(3, nrows * 0.65)))

    vmin, vmax = matrix.min(), matrix.max()
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=vmin, vmax=vmax)

    ax.set_xticks(range(ncols))
    ax.set_xticklabels([f"{g:.1f}%" for g in growth_range], fontsize=8)
    ax.set_yticks(range(nrows))
    ax.set_yticklabels([f"{w:.1f}%" for w in wacc_range],   fontsize=8)
    ax.set_xlabel("Tỷ lệ tăng trưởng dài hạn (%)", labelpad=6)
    ax.set_ylabel("WACC (%)",                        labelpad=6)
    ax.set_title("Phân tích nhạy cảm: Giá trị vốn chủ sở hữu (tỷ đồng)",
                 fontweight="bold", color=NAVY, pad=10)

    # Cell text + highlight center
    mid_r = nrows // 2
    mid_c = ncols // 2
    for r in range(nrows):
        for c in range(ncols):
            val = matrix[r, c]
            txt_color = "white" if (val < vmin + (vmax - vmin) * 0.3
                                    or val > vmin + (vmax - vmin) * 0.7) else "black"
            weight = "bold" if (r == mid_r and c == mid_c) else "normal"
            ax.text(c, r, f"{val:,.0f}", ha="center", va="center",
                    fontsize=7.5, color=txt_color, fontweight=weight)
            if r == mid_r and c == mid_c:
                ax.add_patch(mpatches.FancyBboxPatch(
                    (c - 0.48, r - 0.48), 0.96, 0.96,
                    boxstyle="round,pad=0.02", linewidth=2,
                    edgecolor=NAVY, facecolor="none", zorder=5,
                ))

    cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.ax.tick_params(labelsize=7)
    cbar.set_label("Tỷ đồng", fontsize=8)

    fig.tight_layout()
    return _fig_to_svg(fig)


# ── 4. Valuation waterfall / comparison bar ────────────────────────────────────
def valuation_waterfall(
    dcf_value: float,
    multiples_value: float,
    final_low: float,
    final_high: float,
) -> str:
    """Bar chart so sánh các phương pháp định giá. Trả về SVG string."""
    labels = ["DCF\n(Giá trị vốn chủ)", "EV/EBITDA\n(Multiples)", "Khoảng định giá\n(Low)", "Khoảng định giá\n(High)"]
    values = [dcf_value, multiples_value, final_low, final_high]
    colors = [NAVY, BLUE, LBLUE, ACCENT]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(range(len(labels)), values, color=colors,
                  width=0.55, zorder=3, edgecolor=WHITE, linewidth=0.8)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_billions))
    ax.set_ylabel("Tỷ đồng")
    ax.set_title("So sánh phương pháp định giá", fontweight="bold", color=NAVY, pad=10)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 1.012,
            f"{val:,.0f}",
            ha="center", va="bottom", fontsize=8, fontweight="bold", color=NAVY,
        )

    fig.tight_layout()
    return _fig_to_svg(fig)


# ── 5. Projection line chart ───────────────────────────────────────────────────
def projection_chart(base_case: list[dict]) -> str:
    """Line chart dự phóng doanh thu và FCF. Trả về SVG string."""
    if not base_case:
        return ""

    years   = [str(d["year"]) for d in base_case]
    revenue = [d.get("revenue", 0) for d in base_case]
    fcf     = [d.get("fcf",     0) for d in base_case]
    ebitda  = [d.get("ebitda",  0) for d in base_case]

    x = range(len(years))
    fig, ax = plt.subplots(figsize=(7, 3.8))

    ax.plot(x, revenue, marker="o", color=NAVY,   linewidth=2.2, label="Doanh thu", zorder=4)
    ax.plot(x, ebitda,  marker="s", color=BLUE,   linewidth=2.2, label="EBITDA",    zorder=4)
    ax.plot(x, fcf,     marker="^", color=ACCENT, linewidth=2.2, label="FCF",       zorder=4, linestyle="--")

    ax.set_xticks(list(x))
    ax.set_xticklabels(years)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_billions))
    ax.set_ylabel("Tỷ đồng")
    ax.set_title("Dự phóng tài chính (Base Case)", fontweight="bold", color=NAVY, pad=10)
    ax.legend(frameon=False, fontsize=8)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4, zorder=0)

    # Annotate last data point
    for series, color in [(revenue, NAVY), (ebitda, BLUE), (fcf, ACCENT)]:
        last_x = len(years) - 1
        ax.annotate(
            f"{series[-1]:,.0f}",
            xy=(last_x, series[-1]),
            xytext=(5, 4), textcoords="offset points",
            fontsize=7.5, color=color, fontweight="bold",
        )

    fig.tight_layout()
    return _fig_to_svg(fig)
