#!/usr/bin/env python3
"""Fix non-admin test expectations (403 not 401)."""

FIXES = {
    "tests/test_admin_gallery.py": [
        ("test_get_gallery_post_non_admin", 253),
        ("test_update_gallery_post_unauthorized", 346),
        ("test_delete_gallery_post_unauthorized", 451),
    ],
    "tests/test_admin_vision.py": [
        ("test_get_vision_registrations_non_admin", 128),
        ("test_export_vision_registrations_unauthorized", 212),
    ],
}

def fix_file(filename, fixes):
    """Fix 401 -> 403 in specific non-admin test lines."""
    print(f"Fixing {filename}...")
    with open(filename, 'r') as f:
        lines = f.readlines()

    for test_name, line_num in fixes:
        idx = line_num - 1
        if idx < len(lines):
            original = lines[idx]
            # Replace 401 with 403 for non-admin tests
            lines[idx] = original.replace('status.HTTP_401_UNAUTHORIZED', 'status.HTTP_403_FORBIDDEN')
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

    print("\nDone! All non-admin test expectations updated.")

if __name__ == "__main__":
    main()
