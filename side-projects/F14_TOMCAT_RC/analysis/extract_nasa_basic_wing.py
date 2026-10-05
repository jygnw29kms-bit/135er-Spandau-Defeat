"""Extract only the original Grumman basic wing from NASA CR-3992 Appendix 2.

Usage: python extract_nasa_basic_wing.py NASA_CR_3992.pdf output.json
The few OCR repairs below were inspected against enlarged native PDF table images.
Gloved experimental wings are deliberately excluded.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import pymupdf


def extract(pdf_path):
    document = pymupdf.open(pdf_path)
    text = "\n".join(page.get_text() for page in document)
    basic = text.split("GRUMMAN DEFINITION OF THE BASIC F-14 WING (20-DEG SWEEP)", 1)[1]
    basic = basic.split("MACH 0.8 NLF GLOVE DEFINITION", 1)[0]
    repairs = {
        ".... 011850": "-.011850",
        "-~030520": "-.030520",
        "~045650": ".045650",
        "~.021680": "-.021680",
        "~.027680": "-.027680",
        ",..037840": "-.037840",
        "311 .15283": "311.15283",
        '.00491"0': ".004910",
    }
    for before, after in repairs.items():
        if basic.count(before) != 1:
            raise ValueError(f"Unexpected OCR token count: {before!r}")
        basic = basic.replace(before, after)
    sections = []
    for block in re.split(r"\bWBL\b", basic)[1:]:
        header, rows = block.split("Y/C(LOWER)", 1)
        metadata = [float(v) for v in re.findall(r"[-+]?\d+\.\d+", header)]
        if len(metadata) != 4:
            raise ValueError("Incomplete station metadata")
        # Integer printed page numbers are excluded by the decimal-number pattern.
        values = [float(v) for v in re.findall(r"[-+]?(?:\d*\.\d+)", rows)]
        if len(values) != 200:
            raise ValueError(f"Expected 50 four-column rows at WBL {metadata[0]}")
        ordinates = []
        for i in range(0, len(values), 4):
            xu, upper, xl, lower = values[i:i + 4]
            if xu != xl or not (0 <= xu <= 1) or upper < lower:
                raise ValueError(f"Invalid paired ordinate at WBL {metadata[0]}, row {i // 4}")
            ordinates.append([xu, upper, lower])
        if ordinates[0][0] != 0 or ordinates[-1][0] != 1:
            raise ValueError("Incomplete chord range")
        if any(a[0] >= b[0] for a, b in zip(ordinates, ordinates[1:])):
            raise ValueError("Non-monotonic chord samples")
        sections.append({
            "wbl_in": metadata[0],
            "leading_edge_fs_in": metadata[1],
            "trailing_edge_fs_in": metadata[2],
            "reference_vertical_wl_in": metadata[3],
            "ordinates_xc_upper_lower": ordinates,
        })
    if len(sections) != 8 or any(a['wbl_in'] >= b['wbl_in'] for a, b in zip(sections, sections[1:])):
        raise ValueError("Expected eight ordered basic-wing defining sections")
    return {
        "status": "SOURCE_TABLE_EXTRACTED_WITH_CHECKED_OCR_REPAIRS",
        "source_url": "https://ntrs.nasa.gov/api/citations/19880019510/downloads/19880019510.pdf",
        "source_sha256": hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest(),
        "source": "NASA CR-3992 Appendix 2, Grumman basic F-14 wing, 20 degree sweep",
        "units": "Aircraft FS/WBL/WL in inches; section ordinates dimensionless",
        "mapping": "FS=LE_FS+xc*(TE_FS-LE_FS); WBL=station; WL=reference_WL+yc*(TE_FS-LE_FS)",
        "incidence": "Already incorporated in ordinates; do not add a second incidence rotation",
        "aircraft_nose_fs_datum_verified": False,
        "experimental_gloves_included": False,
        "ocr_repairs_visually_checked": repairs,
        "sections": sections,
    }


if __name__ == "__main__":
    result = extract(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Validated {len(result['sections'])} sections, 50 paired ordinates each.")
