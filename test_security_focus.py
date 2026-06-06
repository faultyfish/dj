#!/usr/bin/env python3
"""Test security job focus enhancements - comprehensive security keyword detection."""

def categorise(title: str) -> str:
    t = title.lower()
    
    # Check security FIRST (highest priority - overrides other categories)
    # Specific security types first
    if any(k in t for k in ["security guard", "security officer", "armed security", "unarmed security",
                             "door supervisor", "bouncer", "protective services", "protection officer",
                             "event security", "retail security", "loss prevention", "asset protection",
                             "corporate security", "building security", "site security", "warehouse security",
                             "surveillance", "cctv", "control room", "access control",
                             "nightclub security", "bar security", "venue security", "airport security",
                             "aviation security", "vip security", "executive protection", "close protection",
                             "bodyguard", "personal security", "private security", "night security",
                             "armed response", "cash in transit", "g4s", "allied universal", "securitas"]):
        return "security"
    # Then broader security terms
    if any(k in t for k in ["security patrol", "loss prevention officer", "risk assessment",
                             "concierge", "patrol", "guarding", "protective", "protection"]):
        return "security"
    # Finally generic "security"
    if "security" in t:
        return "security"
    
    # Academic/Research roles
    if any(k in t for k in ["research assistant", "tutor", "lecturer", "professor", "academic"]):
        return "academic"
    
    # Admin/Office roles
    if any(k in t for k in ["receptionist", "secretary", "admin", "administrative", "office assistant", "office manager", "data entry"]):
        return "admin"
    
    # Customer support/care roles
    if any(k in t for k in ["customer service", "call centre", "call center", "support", "helpdesk", "help desk", 
                             "carer", "care assistant", "healthcare assistant", "childcare"]):
        return "support"
    
    # Retail roles
    if any(k in t for k in ["retail", "shop assistant", "cashier", "sales assistant", "store", "checkout"]):
        return "retail"
    
    # Hospitality roles
    if any(k in t for k in ["barista", "bar ", "waiter", "waitress", "chef", "cook",
                             "hotel", "restaurant", "hospitality", "cafe", "café", "deli counter", "kitchen"]):
        return "hospitality"
    
    # Warehouse/Logistics/Driver roles
    if any(k in t for k in ["warehouse", "picker", "packer", "forklift", "logistics", "stock", 
                             "delivery driver", "courier", "driver"]):
        return "warehouse"
    
    # Cleaning roles
    if any(k in t for k in ["cleaner", "cleaning", "housekeeper", "janitorial"]):
        return "other"
    
    return "other"

test_titles = [
    # Core security roles
    'Security Guard - Part Time',
    'Security Officer',
    'Armed Security',
    'Unarmed Security Officer',
    'Door Supervisor',
    'Bouncer',
    'Protective Services Officer',
    
    # Specialized security
    'Event Security',
    'Retail Security Officer',
    'Loss Prevention Officer',
    'Asset Protection Specialist',
    'Corporate Security',
    'Building Security',
    'Site Security',
    'Warehouse Security',
    
    # Operations/Monitoring
    'Surveillance Officer',
    'CCTV Operator',
    'Control Room Security',
    'Access Control Officer',
    'Security Monitoring',
    
    # VIP/Specialized
    'Airport Security',
    'VIP Security',
    'Executive Protection',
    'Close Protection Officer',
    'Bodyguard',
    'Private Security',
    
    # Shift-based
    'Night Security',
    'Evening Security Officer',
    'Night Shift Security Guard',
    
    # Agencies
    'G4S Security Officer',
    'Allied Universal Security',
    'Securitas Guard',
    'Cash in Transit Security',
    'Armoured Truck Security',
    
    # Non-security for comparison
    'Customer Service',
    'Barista',
    'Warehouse Picker',
]

print('Comprehensive Security Job Categorization:')
print('=' * 60)
sec_count = 0
other_count = 0
for title in test_titles:
    cat = categorise(title)
    if cat == 'security':
        sec_count += 1
        status = '✓ SEC'
    else:
        other_count += 1
        status = f'  {cat.upper()}'
    print(f'{status:8} {title:40} → {cat}')
print('=' * 60)
print(f'Security jobs detected: {sec_count}/{len(test_titles)}')
