"""F1 feasibility: dump the pypdf lines the production Freedom24 importer walks on the
Transactions (page 6) and Commissions (page 7) pages, to show where each trade's own date sits."""
import sys
sys.path.insert(0, r"C:\projects\investments\portfolio\services\quant-engine")
from app.importers.freedom24 import _extract_text_by_page, _PAGE_TRANSACTIONS, _PAGE_COMMISSIONS

pages = _extract_text_by_page(r"C:\projects\investments\portfolio\docs\FF2026.pdf")
for label, idx in (("TRANSACTIONS", _PAGE_TRANSACTIONS), ("COMMISSIONS", _PAGE_COMMISSIONS)):
    print(f"===== {label} page {idx}")
    for n, line in enumerate(pages[idx].splitlines()):
        print(f"{n:3d} | {line}")
