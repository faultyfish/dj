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
                  "chef", "cook", "catering", "café", "cafe", "deli counter"],  "score": 15, "field": "title"},

    # Security (comprehensive expansion - primary focus area)
    
    # Core security roles (highest priority)
    {"keywords": ["security guard", "security officer", "armed security", "unarmed security",
                  "door supervisor", "bouncer", "protective services", "protection officer",
                  "security operative"],  "score": 45, "field": "title"},
    
    # DUBLIN/IRELAND MAJOR SECURITY AGENCIES (Top Priority)
    # International companies
    {"keywords": ["g4s", "allied universal", "securitas", "brinks", "loomis",
                  # Irish companies and contractors
                  "horizon security", "eclipse security", "shield security", "guardian security",
                  "precision security", "professional security services", "cis security",
                  "sector security", "centurion security", "capital security", "armoured", "armored"],  "score": 45, "field": "title"},
    
    # IRISH SECURITY SERVICES & NATIONAL CONTRACTORS
    {"keywords": ["irish security services", "iss security", "dublin security", "ireland security",
                  "loomis ireland", "loomis", "cash in transit", "cash management", "secure transport",
                  "cash handling", "cash handler", "money handling", "bank security", "financial security",
                  "armoured vehicle driver", "armored vehicle driver"],  "score": 42, "field": "title"},
    
    # RETAIL & MAJOR RETAILERS SECURITY
    {"keywords": ["dunnes security", "tesco security", "supervalu security", "retail security",
                  "loss prevention", "asset protection", "stock protection", "shrinkage prevention",
                  "warehouse security", "store detective"],  "score": 40, "field": "title"},
    
    # TRANSPORTATION & LOGISTICS SECURITY
    {"keywords": ["airport security", "aviation security", "transport security", "cargo security",
                  "secure logistics", "armoured vehicle", "armored vehicle", "security driver"],  "score": 40, "field": "title"},
    
    # SPECIALIZED SECURITY ROLES
    {"keywords": ["event security", "venue security", "nightclub security", "bar security",
                  "concert security", "festival security", "vip security", "close protection",
                  "bodyguard", "executive protection", "personal security", "private security",
                  "corporate security", "building security", "site security", "museum security",
                  "gallery security"],  "score": 38, "field": "title"},
    
    # SECURITY OPERATIONS & MONITORING
    {"keywords": ["surveillance", "cctv", "cctv operator", "security monitoring", "control room",
                  "security patrol", "incident response", "alarm", "access control", "security checkpoint",
                  "security monitoring centre", "monitoring centre", "night watch"],  "score": 35, "field": "title"},
    
    # RISK & LOSS PREVENTION SPECIALISTS
    {"keywords": ["loss prevention officer", "risk assessment", "security risk", "theft prevention",
                  "fraud prevention", "compliance officer", "compliance security", "audit security"],  "score": 32, "field": "title"},
    
    # SHIFT-BASED & NIGHT WORK
    {"keywords": ["night security", "security night shift", "evening security", "graveyard security",
                  "24/7 security", "round the clock", "7 days a week"],  "score": 30, "field": "title"},
    
    # CERTIFICATIONS & QUALIFICATIONS (in description)
    {"keywords": ["security clearance", "security patrol", "armed response", "security training",
                  "sro certified", "security certification", "licensed security", "unarmed combat",
                  "health and safety", "first aid", "security industry authority"],  "score": 25, "field": "description"},
    
    # General security (catch-all with reasonable score)
    {"keywords": ["security", "protection", "protective"],           "score": 18, "field": "title"},

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
