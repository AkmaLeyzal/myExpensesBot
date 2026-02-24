import os
import re
import tempfile
from datetime import datetime
from fpdf import FPDF

from parser import format_rupiah

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U0000FE00-\U0000FE0F"
    "\U0000200D"
    "\U00002B50"
    "]+",
    flags=re.UNICODE,
)


def _strip_emoji(text: str) -> str:
    return _EMOJI_PATTERN.sub("", text).strip()


class ExpenseReport(FPDF):

    def __init__(self, period_label: str):
        super().__init__()
        self.period_label = period_label

    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(33, 37, 41)
        self.cell(0, 12, "Laporan Pengeluaran", new_x="LMARGIN", new_y="NEXT", align="C")

        self.set_font("Helvetica", "", 11)
        self.set_text_color(108, 117, 125)
        self.cell(0, 8, self.period_label, new_x="LMARGIN", new_y="NEXT", align="C")

        self.set_font("Helvetica", "I", 8)
        self.cell(
            0, 6,
            f"Dibuat: {datetime.now().strftime('%d %B %Y, %H:%M')}",
            new_x="LMARGIN", new_y="NEXT", align="C",
        )

        self.set_draw_color(52, 152, 219)
        self.set_line_width(0.8)
        self.line(10, self.get_y() + 3, 200, self.get_y() + 3)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Halaman {self.page_no()}/{{nb}}", align="C")


def generate_report(expenses: list[dict], period_label: str) -> str:
    pdf = ExpenseReport(period_label)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    if not expenses:
        pdf.set_font("Helvetica", "I", 12)
        pdf.cell(0, 20, "Tidak ada data pengeluaran untuk periode ini.", align="C")
    else:
        _add_summary_section(pdf, expenses)
        _add_category_breakdown(pdf, expenses)
        _add_expense_table(pdf, expenses)

    filepath = os.path.join(tempfile.gettempdir(), f"expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(filepath)
    return filepath


def _add_summary_section(pdf: FPDF, expenses: list[dict]):
    total = sum(e["price"] for e in expenses)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 10, "Ringkasan", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)

    pdf.cell(60, 8, "Total Transaksi:")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"{len(expenses)} transaksi", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(60, 8, "Total Pengeluaran:")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(231, 76, 60)
    pdf.cell(0, 8, format_rupiah(total), new_x="LMARGIN", new_y="NEXT")

    avg = total // len(expenses) if expenses else 0
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(60, 8, "Rata-rata per Transaksi:")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, format_rupiah(avg), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)


def _add_category_breakdown(pdf: FPDF, expenses: list[dict]):
    categories = {}
    for e in expenses:
        cat = e.get("category", "Lainnya")
        categories[cat] = categories.get(cat, 0) + e["price"]

    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 10, "Per Kategori", new_x="LMARGIN", new_y="NEXT")

    total = sum(e["price"] for e in expenses)

    for cat_name, cat_total in sorted_cats:
        pct = (cat_total / total * 100) if total > 0 else 0

        safe_cat = _strip_emoji(cat_name)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(33, 37, 41)
        pdf.cell(70, 7, f"  {safe_cat}")
        pdf.cell(40, 7, format_rupiah(cat_total))
        pdf.set_text_color(108, 117, 125)
        pdf.cell(0, 7, f"({pct:.1f}%)", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)


def _add_expense_table(pdf: FPDF, expenses: list[dict]):
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 10, "Detail Transaksi", new_x="LMARGIN", new_y="NEXT")

    col_widths = [10, 35, 50, 50, 30]
    headers = ["No", "Tanggal", "Item", "Kategori", "Harga"]

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(52, 152, 219)
    pdf.set_text_color(255, 255, 255)

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(33, 37, 41)

    for idx, expense in enumerate(expenses, 1):
        if idx % 2 == 0:
            pdf.set_fill_color(241, 245, 249)
        else:
            pdf.set_fill_color(255, 255, 255)

        fill = True

        item_text = expense["item"]
        if expense.get("description"):
            item_text += f" ({expense['description']})"
        if len(item_text) > 30:
            item_text = item_text[:27] + "..."

        cat_text = _strip_emoji(expense.get("category", ""))
        if len(cat_text) > 28:
            cat_text = cat_text[:25] + "..."

        try:
            dt = datetime.strptime(expense["timestamp"], "%Y-%m-%d %H:%M:%S")
            date_str = dt.strftime("%d/%m/%y %H:%M")
        except (ValueError, KeyError):
            date_str = expense.get("timestamp", "")[:16]

        pdf.cell(col_widths[0], 7, str(idx), border=1, fill=fill, align="C")
        pdf.cell(col_widths[1], 7, date_str, border=1, fill=fill, align="C")
        pdf.cell(col_widths[2], 7, item_text, border=1, fill=fill)
        pdf.cell(col_widths[3], 7, cat_text, border=1, fill=fill)
        pdf.cell(col_widths[4], 7, format_rupiah(expense["price"]), border=1, fill=fill, align="R")
        pdf.ln()

    total = sum(e["price"] for e in expenses)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    total_label_width = sum(col_widths[:4])
    pdf.cell(total_label_width, 8, "TOTAL", border=1, fill=True, align="R")
    pdf.cell(col_widths[4], 8, format_rupiah(total), border=1, fill=True, align="R")
    pdf.ln()
