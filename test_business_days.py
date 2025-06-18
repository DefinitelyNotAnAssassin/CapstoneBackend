#!/usr/bin/env python3
"""
Quick test script to verify business days calculation
"""
import os
import sys
import django
from datetime import datetime, date

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from leave_management.views import calculate_business_days

def test_business_days():
    """Test various scenarios for business days calculation"""
    
    print("Testing business days calculation (Monday to Saturday, excluding Sunday)")
    print("=" * 60)
    
    # Test cases: (start_date, end_date, expected_days, description)
    test_cases = [
        # Basic week tests
        (date(2024, 6, 10), date(2024, 6, 10), 1, "Same day (Monday)"),
        (date(2024, 6, 10), date(2024, 6, 11), 2, "Monday to Tuesday"),
        (date(2024, 6, 10), date(2024, 6, 15), 6, "Monday to Saturday"),
        
        # Tests with Sunday
        (date(2024, 6, 10), date(2024, 6, 16), 6, "Monday to Sunday (exclude Sunday)"),
        (date(2024, 6, 16), date(2024, 6, 16), 0, "Sunday only (should be 0)"),
        (date(2024, 6, 15), date(2024, 6, 17), 2, "Saturday to Monday (skip Sunday)"),
        
        # Multi-week tests
        (date(2024, 6, 10), date(2024, 6, 22), 12, "Two weeks (exclude 2 Sundays)"),
    ]
    
    for start_date, end_date, expected, description in test_cases:
        actual = calculate_business_days(start_date, end_date)
        status = "✓" if actual == expected else "✗"
        print(f"{status} {description}")
        print(f"   {start_date} to {end_date}")
        print(f"   Expected: {expected}, Got: {actual}")
        if actual != expected:
            print(f"   ERROR: Calculation mismatch!")
        print()

if __name__ == "__main__":
    test_business_days()
