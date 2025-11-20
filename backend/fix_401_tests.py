#!/usr/bin/env python3
"""Fix 401 vs 403 test expectations for unauthorized tests."""

import re

# Map of file -> (test_function_name, line_number_to_fix)
FIXES = {
    "tests/test_admin_activity_logs.py": [
        ("test_get_activity_logs_unauthorized", 130),
    ],
    "tests/test_admin_analytics.py": [
        ("test_get_overview_analytics_no_auth", 252),
    ],
    "tests/test_admin_bookings.py": [
        ("test_list_bookings_without_auth", 269),
    ],
    "tests/test_admin_calendar.py": [
        ("test_get_calendar_without_auth", 150),
    ],
    "tests/test_admin_gallery.py": [
        ("test_list_gallery_posts_unauthorized", 197),
        ("test_get_gallery_post_unauthorized", 204),
        ("test_create_gallery_post_unauthorized", 247),
        ("test_update_gallery_post_unauthorized", 255),
        ("test_delete_gallery_post_unauthorized", 336),
    ],
    "tests/test_admin_locations.py": [
        ("test_list_locations_without_auth", 130),
    ],
    "tests/test_admin_vision.py": [
        ("test_get_vision_registrations_unauthorized", 121),
        ("test_get_vision_analytics_unauthorized", 130),
        ("test_export_vision_registrations_unauthorized", 204),
    ],
    "tests/test_booking_cancellation.py": [
        ("test_cancel_booking_no_auth", 103),
    ],
    "tests/test_booking_history.py": [
        ("test_list_bookings_no_auth", 76),
        ("test_get_booking_details_no_auth", 397),
    ],
    "tests/test_cart.py": [
        ("test_get_cart_unauthorized", 195),
        ("test_add_item_unauthorized", 324),
        ("test_clear_cart_unauthorized", 547),
    ],
    "tests/test_order_tracking.py": [
        ("test_get_user_orders_unauthorized", 176),
    ],
    "tests/test_product_reviews.py": [
        ("test_create_review_unauthenticated", 218),
    ],
    "tests/test_wishlist.py": [
        ("test_get_wishlist_unauthorized", 152),
        ("test_add_to_wishlist_unauthorized", 271),
        ("test_remove_from_wishlist_unauthorized", 319),
        ("test_check_wishlist_unauthorized", 358),
    ],
}

def fix_file(filename, fixes):
    """Fix 403 -> 401 in specific lines of a file."""
    print(f"Fixing {filename}...")
    with open(filename, 'r') as f:
        lines = f.readlines()

    for test_name, line_num in fixes:
        # Line numbers are 1-indexed, list is 0-indexed
        idx = line_num - 1
        if idx < len(lines):
            original = lines[idx]
            # Replace 403 with 401
            lines[idx] = original.replace('status.HTTP_403_FORBIDDEN', 'status.HTTP_401_UNAUTHORIZED')
            lines[idx] = lines[idx].replace('== 403', '== 401')
            if lines[idx] != original:
                print(f"  Line {line_num}: Fixed {test_name}")

    with open(filename, 'w') as f:
        f.writelines(lines)

def main():
    for filename, fixes in FIXES.items():
        try:
            fix_file(filename, fixes)
        except Exception as e:
            print(f"Error fixing {filename}: {e}")

    print("\nDone! All test expectations updated.")

if __name__ == "__main__":
    main()
