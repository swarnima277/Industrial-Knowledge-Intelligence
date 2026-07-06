import re
import json
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# ===========================================================================
# REGEX PATTERNS (Kept exactly as you wrote them)
# ===========================================================================
_RE_NAMED_EQUIPMENT = re.compile(
    r"\b((?:Discharge\s+Pump|Circulation\s+Pump|Centrifugal\s+Pump|Reciprocating\s+Pump"
    r"|Charge\s+Pump|Transfer\s+Pump|Dosing\s+Pump|Injection\s+Pump|Booster\s+Pump"
    r"|Vacuum\s+Pump|Screw\s+Pump|Gear\s+Pump"
    r"|Heat\s+Exchanger|Air\s+Cooler|Fin\s+Fan|Plate\s+Exchanger"
    r"|Safety\s+Valve|Relief\s+Valve|Control\s+Valve|Check\s+Valve"
    r"|Gate\s+Valve|Ball\s+Valve|Butterfly\s+Valve"
    r"|Rupture\s+Disc|Flame\s+Arrester"
    r"|Knock\s+Out\s+Drum|Surge\s+Drum|Reflux\s+Drum|Flash\s+Drum|Blow\s+Down\s+Drum"
    r"|Storage\s+Tank|Day\s+Tank|Slop\s+Tank|Feed\s+Tank|Product\s+Tank"
    r"|Overhead\s+Condenser"
    r"|Tank|Vessel|Drum|Column|Tower|Reactor|Separator|Exchanger|Condenser"
    r"|Evaporator|Cooler|Heater|Furnace|Boiler|Compressor|Turbine|Pump"
    r"|Blower|Fan|Filter|Strainer|Scrubber|Absorber|Stripper|Mixer|Agitator"
    r"|Reboiler|Crystalliser|Dryer|Silo|Hopper|Bin|Feeder|Conveyor|Ejector|Flare)"
    r"\s+\d{2,3}[A-Z]?)\b",
    re.IGNORECASE,
)

_RE_INSTRUMENT_TAG = re.compile(r'(?<!")\b([A-Z]{2,5}-\d{2,4}[A-Z]?)\b')
_RE_EQUIPMENT_TAG = re.compile(r'(?<!")\b([A-Z]-\d{3,4}[A-Z]?)\b')
_RE_PIPE_LINE = re.compile(r'\b(\d+(?:\.\d+)?"\s*-\s*[A-Z]{1,4}-\d{3,5}(?:-[A-Z0-9]{2,6})?)\b')

_RE_PERSON = re.compile(r'\b([A-Z][a-z]{1,20}(?:[^\S\n][A-Z][a-z]{1,20}){1,2})\b')
_PERSON_BLOCKLIST = {
    "Pipeline", "Line", "Header", "Nozzle", "Vent", "Drain", "Stack", "Chimney", 
    "Manifold", "Skid", "Package", "Hopper", "Silo", "Bin", "Crusher", "Mill",
    "Conveyor", "Elevator", "Feeder", "Dispenser", "Analyzer", "Sensor", "Switch", 
    "Gauge", "Detector", "Alarm", "Monitor", "Relay", "Actuator", "Positioner", 
    "Solenoid", "Thermocouple", "Flowmeter", "Rotameter", "Control Room", "Distributed", 
    "System", "Logic", "Interlock", "Shutdown", "Emergency", "Trip", "Override",
    "Setpoint", "Signal", "Output", "Input", "Operator", "Technician", "Supervisor",
    "Maintenance", "Inspection", "Calibration", "Commissioning", "Startup", "Overhaul", 
    "Testing", "Verification", "Description", "Remarks", "Comment", "Reference", 
    "Revision", "Document", "Drawing", "Project", "Department", "Section", "Category", 
    "Status", "Steam", "Water", "Nitrogen", "Hydrogen", "Oxygen", "Air", "Gas", "Liquid",
    "Fuel", "Chemical", "Product", "Feed", "Effluent", "Waste", "Condensate", "Equipment", 
    "Instrument", "Tag", "Standard", "Location", "Parameter", "Specification", "Asset",
    "Measured", "Value", "Unit", "Reading", "Sample", "Sampling", "Instrumentation",
    "Control", "Process", "Flow", "Meter", "Pressure", "Temperature", "Level", "Indicator", 
    "Pump", "Station", "Supply"
}
PERSON_STOPWORDS = {"Inspection Date", "Sample Point", "Instrument Air Supply"}

_RE_DATE = re.compile(
    r"""\b(\d{1,2}[\ \-/]\w{3,9}[\ \-/]\d{2,4}|\w{3,9}\ \d{1,2},?\ \d{4}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{2}[/\-]\d{2})\b""",
    re.VERBOSE | re.IGNORECASE,
)

_RE_PARAM = re.compile(
    r"(?<!\d)(\d+(?:\.\d+)?\s*(?:bar(?:a|g)?|psi(?:a|g)?|kPa|MPa|Pa\b|°C|°F|deg\s*C|deg\s*F|K\b|rpm|m/s|m3/h|m³/h|Nm3/h|kg/h|t/h|L/min|L/h|bbl/d|kW|MW|W\b|kJ|MJ|kcal|mm|cm|m\b|km|inch|ft|%|ppm|ppb|wt%|vol%))\b",
    re.IGNORECASE,
)

_RE_REGULATORY = re.compile(
    r"\b((?:ISO|API|ASME|IS\b|OSHA|EPA|IEC|NFPA|ATEX|ANSI|BSI|DIN|EN\b|PED|PESO)[\s\-]?[\d\w]{2,10}(?:[\-:]\d+)?)\b",
    re.IGNORECASE,
)


# ===========================================================================
# CLASS IMPLEMENTATION
# ===========================================================================
class EntityExtractor:
    """
    P&ID-aware hybrid entity extractor (Regex + LLM).
    """

    def __init__(self, llm_model=None):
        """
        Optional llm_model parameter allows Member 3 to inject their Llama3/OpenAI 
        instance cleanly into your extraction pipeline.
        """
        self.llm_model = llm_model

    def _regex_extract(self, text: str) -> Dict[str, Any]:
        # 1. OCR Normalization
        text = re.sub(r'([A-Za-z]{2,5})\s*\n\s*(\d{1,4}[A-Za-z]?)', r'\1-\2', text)
        for prefix in ['FV-', 'FT-', 'LT-', 'PT-', 'TT-']:
            text = re.sub(r'\b' + prefix.lower() + r'-', prefix, text)
        text = re.sub(r'[ \t]+', ' ', text)

        # 2. Extract lists
        named_eq = sorted(set(m.strip().title() for m in _RE_NAMED_EQUIPMENT.findall(text)))
        
        instrument_tags = sorted(set(m.strip().upper() for m in _RE_INSTRUMENT_TAG.findall(text)))
        multi_stage_tags = re.findall(r'\b([A-Z]{2,5}-\d+-\d+[A-Z]?)\b', text, flags=re.IGNORECASE)
        instrument_tags.extend(tag.upper() for tag in multi_stage_tags) 
        instrument_tags = sorted(set(instrument_tags))

        equipment_tags = sorted(set(m.strip().upper() for m in _RE_EQUIPMENT_TAG.findall(text)))
        pipe_lines = sorted(set(_RE_PIPE_LINE.findall(text)))

        personnel = []
        for p in _RE_PERSON.findall(text):
            words = p.split()
            if len(words) >= 2 and p not in PERSON_STOPWORDS and not any(w in _PERSON_BLOCKLIST for w in words):
                personnel.append(p)
        personnel = sorted(set([p for p in personnel if p not in named_eq]))

        dates = sorted(set(m.strip() for m in _RE_DATE.findall(text)))
        params = sorted(set(m.strip() for m in _RE_PARAM.findall(text)))
        regulatory = sorted(set(m.strip() for m in _RE_REGULATORY.findall(text)))

        # 3. Dynamic Local Context Mapping for Member 2
        relationships = []
        lines = text.split('\n')
        for line in lines:
            line_tags = [t.upper() for t in _RE_INSTRUMENT_TAG.findall(line)]
            line_params = _RE_PARAM.findall(line)
            if line_tags and line_params:
                for tag in line_tags:
                    for param in line_params:
                        relationships.append({
                            "source_tag": tag,
                            "relationship_type": "HAS_PARAMETER",
                            "target_parameter": param.strip()
                        })

        return {
            "named_equipment": named_eq,
            "instrument_tags": instrument_tags,
            "equipment_tags": equipment_tags,
            "pipe_lines": pipe_lines,
            "personnel_names": personnel,
            "dates": dates,
            "process_parameters": params,
            "regulatory_references": regulatory,
            "relationships": relationships
        }

    def _llm_extract(self, text: str) -> Dict[str, Any]:
        """
        Uses LangChain and a JSON parser to run advanced structural relationship extraction.
        """
        if not self.llm_model:
            print("  [!] LLM instance not provided to extractor. Falling back to Regex.")
            return self._regex_extract(text)

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an industrial expert parsing P&ID text documentation.\n"
                "Extract all entities and return them strictly in the following JSON format:\n\n"
                "{{\n"
                '  "named_equipment": [],\n'
                '  "instrument_tags": [],\n'
                '  "equipment_tags": [],\n'
                '  "pipe_lines": [],\n'
                '  "personnel_names": [],\n'
                '  "dates": [],\n'
                '  "process_parameters": [],\n'
                '  "regulatory_references": [],\n'
                '  "relationships": [\n'
                '     {{"source_tag": "TAG-ID", "relationship_type": "HAS_PARAMETER", "target_parameter": "VALUE"}}\n'
                "  ]\n"
                "}}\n"
                "Do not include conversational filler. Return raw JSON text only."
            )),
            ("human", "Extract from this text:\n\n{text}")
        ])

        try:
            # Chain definition: Prompt -> Model -> Strict JSON structural output
            chain = prompt | self.llm_model | JsonOutputParser()
            result = chain.invoke({"text": text})
            return result
        except Exception as e:
            print(f"  [!] LLM processing failed: {e}. Falling back to Regex extraction.")
            return self._regex_extract(text)

    def extract(self, text: str, use_llm: bool = False) -> Dict[str, Any]:
        """
        Extract all P&ID entities from text using either rule-based or LLM logic.
        """
        entities = self._llm_extract(text) if use_llm else self._regex_extract(text)
        self._print_results(entities)
        return entities

    def _print_results(self, entities: Dict[str, Any]):
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
                continue
            print(f"\n  {label}:")
            for item in items:
                print(f"    - {item}")

        relationships = entities.get("relationships", [])
        if relationships:
            print(f"\n  Identified Local Relationships:")
            for rel in relationships[:10]:
                print(f"    - ({rel.get('source_tag')}) -[{rel.get('relationship_type')}]-> ({rel.get('target_parameter')})")
            if len(relationships) > 10:
                print("    - ...")

        print(f"\n{'='*50}")
