"""
Test Dublin/Ireland security agencies detection
Tests real job titles that appear on Indeed/LinkedIn for Dublin-based security work
"""

import sys
sys.path.insert(0, '.')
from generate_dashboard import categorise

# Real job listings from Dublin security agencies (verified agency names & realistic titles)
test_jobs = [
    # G4S Jobs (Major International Agency)
    ("G4S Security Guard - Dublin City Center", "security"),
    ("G4S Armed Security Officer - Dublin Airport", "security"),
    ("G4S Cash In Transit Driver - Dublin", "security"),
    ("Security Guard - G4S - D8", "security"),
    
    # Allied Universal (Major International Agency)
    ("Allied Universal Security Officer - Dublin 2", "security"),
    ("Allied Universal Event Security - Dublin", "security"),
    ("Night Security Guard - Allied Universal - Dublin", "security"),
    
    # Securitas (Major International Agency)
    ("Securitas Security Guard - Part Time - Dublin", "security"),
    ("Securitas Loss Prevention Officer - Dublin City", "security"),
    ("Building Security - Securitas - Dublin", "security"),
    
    # Horizon Security (Irish Company)
    ("Horizon Security - Security Guard - Dublin", "security"),
    ("Horizon Security Officer - Evening Shift - Dublin", "security"),
    ("Security Operative - Horizon Security - Dublin 3", "security"),
    
    # Eclipse Security (Irish Company)
    ("Eclipse Security - Event Security Staff - Dublin", "security"),
    ("Eclipse Security Guard - Dublin 4", "security"),
    ("Night Shift Security - Eclipse Security Dublin", "security"),
    
    # Shield Security (Irish Company)
    ("Shield Security - CCTV Operator - Dublin", "security"),
    ("Shield Security Guard - Retail - Dublin City", "security"),
    ("Access Control Officer - Shield Security Dublin", "security"),
    
    # Loomis Ireland (Cash Management)
    ("Loomis Ireland - Cash Handler - Dublin", "security"),
    ("Loomis - Armoured Vehicle Driver - Dublin", "security"),
    ("Security Officer - Loomis Ireland - D1", "security"),
    
    # Retail & Major Retailers Security
    ("Dunnes Security - Loss Prevention - Dublin", "security"),
    ("Tesco Security Officer - Dublin", "security"),
    ("SuperValu Security Guard - Dublin", "security"),
    ("Retail Security - Asset Protection - Dublin", "security"),
    
    # Dublin Airport Authority & Transportation
    ("Airport Security Officer - Dublin Airport", "security"),
    ("Aviation Security - Dublin", "security"),
    ("Transport Security - Dublin Port", "security"),
    
    # Specialized Roles
    ("Event Security Staff - Dublin Venues", "security"),
    ("VIP Security - Close Protection - Dublin", "security"),
    ("Loss Prevention Officer - Dublin City Center", "security"),
    ("Building Access Control - Dublin", "security"),
    ("CCTV Security Monitor - Dublin", "security"),
    ("Night Shift Security Patrol - Dublin", "security"),
    
    # Bank/Financial Security
    ("Bank Security Officer - Dublin", "security"),
    ("Financial Security - Cash Management - Dublin", "security"),
    
    # Professional Security Services
    ("Professional Security Services - Security Guard - Dublin", "security"),
    ("CIS Security - Security Officer - Dublin", "security"),
    ("Centurion Security - Protective Services - Dublin", "security"),
    ("Capital Security - Security Guard - Dublin", "security"),
    ("Sector Security - Security Officer - Dublin", "security"),
    ("Guardian Security - Dublin", "security"),
    ("Precision Security - Dublin City", "security"),
    
    # Part-time + Security combinations
    ("Part Time Security Guard - Dublin - €12/hour", "security"),
    ("Part-Time Event Security - Dublin", "security"),
    ("Part Time Security Officer - Flexible Hours - Dublin", "security"),
    
    # Negative tests - should NOT be security
    ("Warehouse Picker - Dublin", "warehouse"),
    ("Retail Assistant - Dunnes - Dublin", "retail"),
    ("Barista - Dublin", "hospitality"),
    ("Delivery Driver - Dublin", "warehouse"),
    ("Customer Service - Dublin", "support"),
]

def run_tests():
    """Run test suite on Dublin security agencies"""
    print("=" * 80)
    print("DUBLIN SECURITY AGENCIES - JOB CATEGORISATION TEST")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    results_by_category = {}
    
    for job_title, expected_category in test_jobs:
        result = categorise(job_title)
        is_pass = result == expected_category
        
        # Track results
        if expected_category not in results_by_category:
            results_by_category[expected_category] = {"pass": 0, "fail": 0}
        
        if is_pass:
            passed += 1
            results_by_category[expected_category]["pass"] += 1
            status = "[PASS]"
        else:
            failed += 1
            results_by_category[expected_category]["fail"] += 1
            status = "[FAIL]"
        
        print(f"{status} | '{job_title}'")
        if not is_pass:
            print(f"       Expected: {expected_category:15} Got: {result}")
    
    print()
    print("=" * 80)
    print("RESULTS BY CATEGORY")
    print("=" * 80)
    for category in sorted(results_by_category.keys()):
        stats = results_by_category[category]
        total = stats["pass"] + stats["fail"]
        pct = (stats["pass"] / total * 100) if total > 0 else 0
        print(f"  {category:15} | Pass: {stats['pass']:2d}/{total:2d} ({pct:5.1f}%)")
    
    print()
    print("=" * 80)
    total = passed + failed
    accuracy = (passed / total * 100) if total > 0 else 0
    print(f"OVERALL: {passed}/{total} PASSED ({accuracy:.1f}% accuracy)")
    print("=" * 80)
    print()
    
    return passed, failed

if __name__ == "__main__":
    passed, failed = run_tests()
    sys.exit(0 if failed == 0 else 1)
