# config.py — All tuneable settings in one place

SCRAPER = {
    "locations": ["Dublin, Dublin 15, County Dublin"],
    "sources": ["indeed", "linkedin","jobs.ie"],
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

    # Target categories
    {"keywords": ["retail", "shop assistant", "sales assistant",
                  "store assistant", "cashier", "checkout"],   "score": 15, "field": "title"},
    {"keywords": ["warehouse", "picker", "packer", "forklift",
                  "logistics", "stock", "stores"],             "score": 15, "field": "title"},
    {"keywords": ["hospitality", "barista", "waiter", "waitress",
                  "bar staff", "hotel", "restaurant", "kitchen",
                  "chef", "cook", "catering", "café", "cafe","deli"], "score": 15, "field": "title"},
    {"keywords": ["security", "security guard", "door supervisor",
                  "concierge"],                                "score": 15, "field": "title"},
    {"keywords": ["cleaner", "cleaning", "housekeeper",
                  "janitorial"],                               "score": 12, "field": "title"},
    {"keywords": ["driver", "delivery driver", "courier"],     "score": 12, "field": "title"},
    {"keywords": ["carer", "care assistant", "healthcare assistant",
                  "support worker", "childcare","research assistant"],              "score": 12, "field": "title"},

    # Entry-level signals in description
    {"keywords": ["no experience required", "no experience necessary",
                  "entry level", "entry-level", "will train"],  "score": 8, "field": "description"},
]

# Keywords that PENALISE score (job is likely irrelevant)
BLOCK_RULES = [
    # Seniority
    {"keywords": ["senior", "lead ", "head of", "director",
                  "vp ", "vice president", "chief", "principal"],  "score": -25, "field": "title"},
    {"keywords": ["manager", "management"],                        "score": -20, "field": "title"},

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
