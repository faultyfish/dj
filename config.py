# config.py — All tuneable settings in one place

# --- LOCATION ---
DUBLIN_KEYWORDS = [
    "dublin", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9",
    "d10", "d11", "d12", "d13", "d14", "d15", "d16", "d17", "d18",
    "d20", "d24"
]

SCRAPER = {
    "locations": [
    "dublin",
    "dublin 1",
    "dublin 2",
    "dublin 3",
    "dublin 4",
    "dublin 5",
    "dublin 6",
    "dublin 7",
    "dublin 8",
    "dublin 9",
    "dublin 10",
    "dublin 11",
    "dublin 12",
    "dublin 13",
    "dublin 14",
    "dublin 15",
    "dublin 16",
    "dublin 17",
    "dublin 18",
    "dublin 19",
    "dublin 20",
    "dublin 21",
    "dublin 22",
    "dublin 23",
    "dublin 24",           
    "county dublin",],
    "sources": ["indeed", "linkedin"],
    "results_per_source": 50,
    "hours_old": 12,          # Only jobs posted in the last N hours
    "country": "Ireland",
}

# --- FILTER SCORING ---
# A job needs a combined score >= PASS_THRESHOLD to be kept.
# Each rule below adds or subtracts from the score.
PASS_THRESHOLD = 10

# Job title / description keywords that BOOST score (job is likely relevant)
ALLOW_RULES = [
    # Employment type signals
    {"keywords": ["part-time", "part time", "parttime"],        "score": 20, "field": "any"},

    # Admin/Office roles
    {"keywords": ["receptionist", "secretary", "admin", "administrative",
                  "office assistant", "office manager", "data entry"],  "score": 14, "field": "title"},

    # Academic/Research roles
    {"keywords": ["research assistant", "tutor", "lecturer", "professor"],  "score": 14, "field": "title"},

    # Customer Support/Care roles
    {"keywords": ["customer service", "call centre", "call center",
                  "support worker", "carer", "care assistant", "healthcare assistant",
                  "childcare"],                                 "score": 12, "field": "title"},

    # Retail
    {"keywords": ["retail", "shop assistant", "sales assistant",
                  "store assistant", "cashier", "checkout"],   "score": 15, "field": "title"},

    # Warehouse/Logistics/Driver roles
    {"keywords": ["warehouse", "picker", "packer", "forklift",
                  "logistics", "stock", "stores"],             "score": 15, "field": "title"},
    {"keywords": ["driver", "delivery driver", "courier"],     "score": 12, "field": "title"},

    # Hospitality
    {"keywords": ["hospitality", "barista", "waiter", "waitress",
                  "bar staff", "hotel", "restaurant", "kitchen",
                  "chef", "cook", "catering", "café", "cafe", "deli"],  "score": 15, "field": "title"},

    # Security (specific, higher priority)
    {"keywords": ["security guard", "door supervisor", "concierge"],  "score": 35, "field": "title"},
    {"keywords": ["security"],                                  "score": 15, "field": "title"},

    # Cleaning
    {"keywords": ["cleaner", "cleaning", "housekeeper",
                  "janitorial"],                               "score": 12, "field": "title"},

    # Entry-level signals in description
    {"keywords": ["no experience required", "no experience necessary",
                  "entry level", "entry-level", "will train"],  "score": 8, "field": "description"},
]

# Keywords that PENALISE score (job is likely irrelevant)
BLOCK_RULES = [
    # Seniority (more specific terms first to avoid keyword overlap)
    {"keywords": ["head of", "director", "vp ", "vice president", "chief", "principal"],  "score": -25, "field": "title"},
    {"keywords": ["senior ", "lead role"],                      "score": -20, "field": "title"},
    {"keywords": ["manager", "management"],                      "score": -20, "field": "title"},

    # Tech / corporate
    {"keywords": ["software", "developer", "engineer", "devops",
                  "data scientist", "machine learning", "ai ",
                  "cloud", "backend", "frontend", "full stack",
                  "fullstack", "python developer", "java ",
                  "react ", "node.js"],                            "score": -25, "field": "title"},
    {"keywords": ["consultant", "consulting", "analyst",
                  "architect", "sap", "erp", "crm"],              "score": -20, "field": "title"},
    {"keywords": ["accountant", "finance", "financial",
                  "legal", "solicitor", "barrister", "compliance",
                  "audit"],                                        "score": -20, "field": "title"},
    {"keywords": ["marketing manager", "brand manager",
                  "product manager", "project manager"],           "score": -20, "field": "title"},

    # Suspicious / MLM / commission-only
    {"keywords": ["commission only", "self-employed", "own car required",
                  "must have own vehicle", "franchise"],           "score": -15, "field": "description"},
]


# --- VALIDATION ---
def validate_config():
    """
    Validate configuration for conflicts and inconsistencies.
    Raises ValueError if validation fails.
    """
    # Check PASS_THRESHOLD is reasonable
    if not isinstance(PASS_THRESHOLD, int) or PASS_THRESHOLD < 0:
        raise ValueError(f"PASS_THRESHOLD must be non-negative integer, got {PASS_THRESHOLD}")
    
    # Check that Dublin keywords are lowercase
    for kw in DUBLIN_KEYWORDS:
        if kw != kw.lower():
            raise ValueError(f"DUBLIN_KEYWORDS must be lowercase, found: {kw}")
    
    # Validate rule structure
    for rules, rule_type in [(ALLOW_RULES, "ALLOW_RULES"), (BLOCK_RULES, "BLOCK_RULES")]:
        for i, rule in enumerate(rules):
            if not isinstance(rule, dict):
                raise ValueError(f"{rule_type}[{i}] must be dict")
            if "keywords" not in rule or "score" not in rule or "field" not in rule:
                raise ValueError(f"{rule_type}[{i}] missing required keys: keywords, score, field")
            if not isinstance(rule["keywords"], list):
                raise ValueError(f"{rule_type}[{i}]['keywords'] must be list")
            if not isinstance(rule["score"], int):
                raise ValueError(f"{rule_type}[{i}]['score'] must be int")
            if rule["field"] not in ["title", "description", "any"]:
                raise ValueError(f"{rule_type}[{i}]['field'] must be one of: title, description, any")
    
    return True
