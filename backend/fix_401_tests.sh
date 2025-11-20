#!/bin/bash

# Fix test files - replace HTTP_403_FORBIDDEN with HTTP_401_UNAUTHORIZED in unauthorized tests

# Admin tests
sed -i 's/\(test_.*unauthorized.*\)/\1/; /test_.*unauthorized/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_admin_activity_logs.py
sed -i 's/\(test_.*no_auth.*\)/\1/; /test_.*no_auth/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_admin_analytics.py
sed -i 's/\(test_.*without_auth.*\)/\1/; /test_.*without_auth/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_admin_bookings.py
sed -i 's/\(test_.*without_auth.*\)/\1/; /test_.*without_auth/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_admin_calendar.py
sed -i 's/\(test_.*unauthorized.*\)/\1/; /test_.*unauthorized/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_admin_gallery.py
sed -i 's/\(test_.*without_auth.*\)/\1/; /test_.*without_auth/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_admin_locations.py
sed -i 's/\(test_.*unauthorized.*\)/\1/; /test_.*unauthorized/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_admin_vision.py

# Cart and wishlist
sed -i 's/\(test_.*unauthorized.*\)/\1/; /test_.*unauthorized/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_cart.py
sed -i 's/\(test_.*unauthorized.*\)/\1/; /test_.*unauthorized/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_wishlist.py

# Booking tests
sed -i 's/\(test_.*no_auth.*\)/\1/; /test_.*no_auth/,/def test_/ { s/403/401/g; }' tests/test_booking_cancellation.py
sed -i 's/\(test_.*no_auth.*\)/\1/; /test_.*no_auth/,/def test_/ { s/403/401/g; }' tests/test_booking_history.py

# Order tracking
sed -i 's/\(test_.*unauthorized.*\)/\1/; /test_.*unauthorized/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_order_tracking.py

# Product reviews
sed -i 's/\(test_.*unauthenticated.*\)/\1/; /test_.*unauthenticated/,/def test_/ { s/status\.HTTP_403_FORBIDDEN/status.HTTP_401_UNAUTHORIZED/g; }' tests/test_product_reviews.py

echo "Fixed all 401 vs 403 test expectations"
