"""
EntityExtractor: P&ID-aware entity extraction using regex / rule-based logic.

Extracts:
  - named_equipment      : Tank 01, Discharge Pump 03, Heat Exchanger 02
  - instrument_tags      : ISA function-code tags  (FCV-04, LT-02, TT-205A, PSV-301)
  - equipment_tags       : Short asset tags         (E-101, V-201A, C-301)
  - pipe_lines           : Pipe spec line tags      (6"-P-1001-A1A)
  - personnel_names      : Firstname Lastname
  - dates                : Multiple date formats
  - process_parameters   : Numeric values with engineering units
  - regulatory_references: ISO, API, ASME, IEC, etc.

Architecture note:
  _regex_extract() is the current backend.
  To switch to an LLM, implement _llm_extract() and pass use_llm=True to extract().
  Public interface and return schema are identical either way.
"""

import re
from typing import Dict, List


# ---------------------------------------------------------------------------
# Pattern: Named equipment
# The number suffix (e.g. "01") is INSIDE the capture group so the full label
# is returned: "Discharge Pump 01", not just "Discharge Pump".
# Multi-word types are listed before single-word types so the longer match wins.
# ---------------------------------------------------------------------------
_RE_NAMED_EQUIPMENT = re.compile(
    r"\b("
    # ---- multi-word types (must precede single-word) ----
    r"(?:Discharge\s+Pump|Circulation\s+Pump|Centrifugal\s+Pump|Reciprocating\s+Pump"
    r"|Charge\s+Pump|Transfer\s+Pump|Dosing\s+Pump|Injection\s+Pump|Booster\s+Pump"
    r"|Vacuum\s+Pump|Screw\s+Pump|Gear\s+Pump"
    r"|Heat\s+Exchanger|Air\s+Cooler|Fin\s+Fan|Plate\s+Exchanger"
    r"|Safety\s+Valve|Relief\s+Valve|Control\s+Valve|Check\s+Valve"
    r"|Gate\s+Valve|Ball\s+Valve|Butterfly\s+Valve"
    r"|Rupture\s+Disc|Flame\s+Arrester"
    r"|Knock\s+Out\s+Drum|Surge\s+Drum|Reflux\s+Drum|Flash\s+Drum|Blow\s+Down\s+Drum"
    r"|Storage\s+Tank|Day\s+Tank|Slop\s+Tank|Feed\s+Tank|Product\s+Tank"
    r"|Overhead\s+Condenser"
    # ---- single-word types ----
    r"|Tank|Vessel|Drum|Column|Tower|Reactor|Separator|Exchanger|Condenser"
    r"|Evaporator|Cooler|Heater|Furnace|Boiler|Compressor|Turbine|Pump"
    r"|Blower|Fan|Filter|Strainer|Scrubber|Absorber|Stripper|Mixer|Agitator"
    r"|Reboiler|Crystalliser|Dryer|Silo|Hopper|Bin|Feeder|Conveyor|Ejector|Flare)"
    r"\s+\d{2,3}[A-Z]?"          # number + optional letter suffix INSIDE the group
    r")\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Pattern: ISA instrument / valve tags  — FCV-04, LT-02, TT-205A, PSV-301B
# 2–5 uppercase letters (ISA function code) + dash + 2–4 digits + optional suffix.
# Negative lookbehind for " prevents matching pipe spec fragments.
# ---------------------------------------------------------------------------
_RE_INSTRUMENT_TAG = re.compile(
    r'(?<!")\b([A-Z]{2,5}-\d{2,4}[A-Z]?)\b'
)


# ---------------------------------------------------------------------------
# Pattern: Short asset / equipment tags  — E-101, V-201A, C-301
# Single letter + dash + 3–4 digits.
# ---------------------------------------------------------------------------
_RE_EQUIPMENT_TAG = re.compile(
    r'(?<!")\b([A-Z]-\d{3,4}[A-Z]?)\b'
)


# ---------------------------------------------------------------------------
# Pattern: Pipe / line tags  — 6"-P-1001-A1A, 4"-FW-2002-B2B
# ---------------------------------------------------------------------------
_RE_PIPE_LINE = re.compile(
    r'\b(\d+(?:\.\d+)?"\s*-\s*[A-Z]{1,4}-\d{3,5}(?:-[A-Z0-9]{2,6})?)\b'
)


# ---------------------------------------------------------------------------
# Pattern: Personnel names
# Blocklist prevents equipment labels and instrument descriptions from matching.
# ---------------------------------------------------------------------------
_RE_PERSON = re.compile(
    r'\b([A-Z][a-z]{1,20}(?:[^\S\n][A-Z][a-z]{1,20}){1,2})\b'
)

_PERSON_BLOCKLIST = {
    "Tank", "Vessel", "Drum", "Column", "Tower", "Reactor", "Separator",
    "Exchanger", "Condenser", "Evaporator", "Cooler", "Heater", "Furnace",
    "Boiler", "Compressor", "Turbine", "Pump", "Blower", "Fan", "Filter",
    "Strainer", "Scrubber", "Absorber", "Stripper", "Mixer", "Agitator",
    "Valve", "Reboiler", "Ejector", "Flare", "Feeder", "Conveyor", "Dryer",
    # descriptor words common in P&ID labels
    "Controller", "Transmitter", "Indicator", "Recorder", "List",
    "Control", "Storage", "Feed", "Flow", "Level", "Pressure", "Temperature",
    "Safety", "Relief", "Check", "Gate", "Ball", "Butterfly",
    "Charge", "Transfer", "Indicating", "Checked", "Processing", "Firewater",
    "Discharge", "Circulation", "Centrifugal", "Reciprocating", "Instrument",
    "Supply", "Sample", "Point", "Air", "Flow", "Meter", "Date", "Inspection"
}

PERSON_STOPWORDS = {
    "Inspection Date",
    "Sample Point",
    "Instrument Air Supply",
}


# ---------------------------------------------------------------------------
# Pattern: Dates
# ---------------------------------------------------------------------------
_RE_DATE = re.compile(
    r"""
    \b(
        \d{1,2}[\ \-/]\w{3,9}[\ \-/]\d{2,4}    # 15 March 2025 / 15-Mar-2025
      | \w{3,9}\ \d{1,2},?\ \d{4}               # March 15, 2025
      | \d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}         # 15/03/2025  03-15-2025
      | \d{4}[/\-]\d{2}[/\-]\d{2}               # 2025-03-15
    )\b
    """,
    re.VERBOSE | re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Pattern: Process parameters
# Excludes bare alphanumeric codes (e.g. "205A") by requiring a recognised unit.
# ---------------------------------------------------------------------------
_RE_PARAM = re.compile(
    r"(?<!\d)(\d+(?:\.\d+)?\s*"
    r"(?:bar(?:a|g)?|psi(?:a|g)?|kPa|MPa|Pa\b"
    r"|°C|°F|deg\s*C|deg\s*F|K\b"
    r"|rpm|m/s|m3/h|m³/h|Nm3/h|kg/h|t/h|L/min|L/h|bbl/d"
    r"|kW|MW|W\b|kJ|MJ|kcal"
    r"|mm|cm|m\b|km|inch|ft"
    r"|%|ppm|ppb|wt%|vol%))\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Pattern: Regulatory / standards references
# ---------------------------------------------------------------------------
_RE_REGULATORY = re.compile(
    r"\b((?:ISO|API|ASME|IS\b|OSHA|EPA|IEC|NFPA|ATEX|ANSI|BSI|DIN|EN\b|PED|PESO)"
    r"[\s\-]?[\d\w]{2,10}(?:[\-:]\d+)?)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class EntityExtractor:
    """
    P&ID-aware rule-based entity extractor.

    Usage:
        extractor = EntityExtractor()
        entities  = extractor.extract(raw_text)
    """

    def _regex_extract(self, text: str) -> Dict[str, List[str]]:
    # ==========================================================
    # OCR NORMALIZATION
    # ==========================================================

    # FT\n10 -> FT-10
    # LT\n02 -> LT-02
    # PT\n101 -> PT-101
        text = re.sub(
            r'([A-Za-z]{2,5})\s*\n\s*(\d{1,4}[A-Za-z]?)',
            r'\1-\2',
            text
        )

    # Normalize common OCR capitalization
        text = re.sub(r'\bFv-', 'FV-', text)
        text = re.sub(r'\bFt-', 'FT-', text)
        text = re.sub(r'\bLt-', 'LT-', text)
        text = re.sub(r'\bPt-', 'PT-', text)
        text = re.sub(r'\bTt-', 'TT-', text)

    # Collapse excessive whitespace
        text = re.sub(r'[ \t]+', ' ', text)

    # ==========================================================
    # NAMED EQUIPMENT
    # ==========================================================

        named_eq = sorted(set(
            m.strip().title()
            for m in _RE_NAMED_EQUIPMENT.findall(text)
        ))

    # ==========================================================
    # INSTRUMENT TAGS
    # ==========================================================

        instrument_tags = sorted(set(
            m.strip().upper()
            for m in _RE_INSTRUMENT_TAG.findall(text)
        ))

    # Catch tags like FV-3-3040 and FV-3-3041
        multi_stage_tags = re.findall(
            r'\b([A-Z]{2,5}-\d+-\d+[A-Z]?)\b',
            text,
            flags=re.IGNORECASE
        )

        instrument_tags.extend(
            tag.upper()
            for tag in multi_stage_tags
        ) 

        instrument_tags = sorted(set(instrument_tags))

    # ==========================================================
    # EQUIPMENT TAGS
    # ==========================================================

        equipment_tags = sorted(set(
            m.strip().upper()
            for m in _RE_EQUIPMENT_TAG.findall(text)
        ))

    # ==========================================================
    # PIPE LINES
    # ==========================================================

        pipe_lines = sorted(set(
            _RE_PIPE_LINE.findall(text)
        ))

    # ==========================================================
    # PERSONNEL
    # ==========================================================

        personnel = []

        for p in _RE_PERSON.findall(text):
            words = p.split()

            if len(words) < 2:
                continue

    # Remove known non-person phrases
            if p in PERSON_STOPWORDS:
                continue

    # Remove phrases containing blocked words
            if any(word in _PERSON_BLOCKLIST for word in words):
                continue

            personnel.append(p)

        personnel = sorted(set(personnel))


    # ==========================================================
    # OTHER ENTITIES
    # ==========================================================

        dates = sorted(set(
            m.strip()
            for m in _RE_DATE.findall(text)
        ))

        params = sorted(set(
            _RE_PARAM.findall(text)
        ))

        regulatory = sorted(set(
            _RE_REGULATORY.findall(text)
        ))

    # ==========================================================
    # REMOVE DUPLICATES
    # ==========================================================

        personnel = [
            p for p in personnel
            if p not in named_eq
        ]

        return {
        "named_equipment": named_eq,
        "instrument_tags": instrument_tags,
        "equipment_tags": equipment_tags,
        "pipe_lines": pipe_lines,
        "personnel_names": personnel,
        "dates": dates,
        "process_parameters": params,
        "regulatory_references": regulatory,
    }

    def _llm_extract(self, text: str) -> Dict[str, List[str]]:
        """
        Placeholder for LLM-based extraction.
        Implement: call LLM with structured JSON prompt, parse response,
        return dict matching the schema above.
        """
        raise NotImplementedError("LLM extraction not yet configured.")

    def extract(self, text: str, use_llm: bool = False) -> Dict[str, List[str]]:
        """
        Extract all P&ID entities from text.

        Args:
            text    : Raw extracted document text.
            use_llm : Set True to use LLM extraction backend.

        Returns:
            Dict with keys: named_equipment, instrument_tags, equipment_tags,
            pipe_lines, personnel_names, dates, process_parameters,
            regulatory_references.
        """
        entities = self._llm_extract(text) if use_llm else self._regex_extract(text)
        self._print_results(entities)
        return entities

    def _print_results(self, entities: Dict[str, List[str]]):
        """Print a clean, categorised extraction report to the terminal."""
        labels = {
            "named_equipment":       "Named Equipment",
            "instrument_tags":       "Instrument & Valve Tags",
            "equipment_tags":        "Equipment Tags",
            "pipe_lines":            "Pipe / Line Tags",
            "personnel_names":       "Personnel",
            "dates":                 "Dates",
            "process_parameters":    "Process Parameters",
            "regulatory_references": "Regulatory References",
        }

        print(f"\n{'='*50}")
        print("ENTITY EXTRACTION COMPLETE\n")
        print("Extracted Entities:")

        for key, label in labels.items():
            items = entities.get(key, [])
            if not items:
                continue          # skip empty categories — keeps output clean
            print(f"\n  {label}:")
            for item in items:
                print(f"    - {item}")

        print(f"\n{'='*50}")