# Testing Guide - Glam by Lynn

This comprehensive guide covers all testing procedures for the Glam by Lynn application including user journeys, checkout flows, booking flows, admin operations, cross-browser testing, and performance testing.

## Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [User Journey Tests](#user-journey-tests)
3. [Checkout Flow Tests](#checkout-flow-tests)
4. [Booking Flow Tests](#booking-flow-tests)
5. [Admin Operations Tests](#admin-operations-tests)
6. [Cross-Browser Testing](#cross-browser-testing)
7. [Performance Testing](#performance-testing)
8. [Load Testing](#load-testing)
9. [Bug Reporting](#bug-reporting)

---

## Test Environment Setup

### Prerequisites

**Backend:**
```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Database:**
- PostgreSQL running with test data
- Ensure migrations are up to date: `alembic upgrade head`

**Test Accounts:**
- Regular User: test@example.com
- Admin User: admin@example.com (with admin privileges)
- Guest User: No account (test guest checkout)

### Environment Variables

Verify all required environment variables are set:
- `NEXT_PUBLIC_API_URL` pointing to backend
- `DATABASE_URL` configured
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` set
- `NEXTAUTH_URL` and `NEXTAUTH_SECRET` configured

---

## User Journey Tests

### Journey 1: New Visitor to First Purchase

**Goal:** Complete user flow from landing to checkout

**Steps:**
1. [ ] Load homepage at `http://localhost:3000`
2. [ ] Verify hero section displays correctly
3. [ ] Browse featured products section
4. [ ] Click "Browse Products" or navigate to Products page
5. [ ] Apply filters (category, price range, etc.)
6. [ ] Click on a product card
7. [ ] View product details page
8. [ ] Select variant (if applicable)
9. [ ] Click "Add to Cart"
10. [ ] Verify success message appears
11. [ ] Click cart icon (should show count)
12. [ ] Navigate to cart page
13. [ ] Verify items displayed correctly
14. [ ] Update quantity (increase/decrease)
15. [ ] Verify total updates
16. [ ] Click "Proceed to Checkout"
17. [ ] Sign in or continue as guest
18. [ ] Fill out checkout form
19. [ ] Accept terms and conditions
20. [ ] Submit order
21. [ ] Verify redirect to order confirmation
22. [ ] Verify order details displayed
23. [ ] Check email for order confirmation (if implemented)

**Expected Results:**
- All pages load without errors
- Navigation smooth and intuitive
- Cart updates correctly
- Checkout completes successfully
- Order confirmation displays accurate information

**Test Data:**
- Product: Any available product
- Quantity: 2
- Promo Code: WELCOME10 (if exists)
- Delivery: Nairobi, Westlands

---

### Journey 2: Service Booking Flow

**Goal:** Book a makeup service appointment

**Steps:**
1. [ ] Navigate to Services page
2. [ ] Browse available services
3. [ ] Click on a service (e.g., Bridal Makeup)
4. [ ] View service details and packages
5. [ ] Click "Book Now"
6. [ ] Sign in (required for bookings)
7. [ ] Select service package
8. [ ] Choose date from calendar
9. [ ] Select time slot
10. [ ] Fill in booking details:
    - Number of people
    - Location preferences
    - Special requests
11. [ ] Review booking summary
12. [ ] Accept terms
13. [ ] Submit booking
14. [ ] Verify booking confirmation page
15. [ ] Navigate to "My Bookings"
16. [ ] Verify booking appears in list

**Expected Results:**
- Service details clear and accurate
- Calendar shows available dates
- Time slots display correctly
- Booking form validates properly
- Confirmation shows all booking details
- Booking appears in user's bookings list

**Test Data:**
- Service: Bridal Makeup - Premium Package
- Date: 2 weeks from today
- Time: 10:00 AM
- People: Bride + 3 bridesmaids
- Location: Nairobi

---

### Journey 3: Returning User - Reorder

**Goal:** Logged-in user reorders previous purchase

**Steps:**
1. [ ] Sign in to account
2. [ ] Navigate to "My Orders"
3. [ ] View order history
4. [ ] Click on a previous order
5. [ ] Click "Reorder" button
6. [ ] Verify items added to cart
7. [ ] View cart
8. [ ] Proceed to checkout
9. [ ] Verify saved address pre-selected
10. [ ] Complete checkout
11. [ ] Verify new order created

**Expected Results:**
- Order history displays correctly
- Reorder adds all items to cart
- Saved addresses available
- Checkout faster with saved info

---

### Journey 4: Wishlist Management

**Goal:** Use wishlist feature

**Steps:**
1. [ ] Sign in to account
2. [ ] Browse products
3. [ ] Click heart icon on multiple products
4. [ ] Verify success message
5. [ ] Navigate to Wishlist page
6. [ ] Verify all items displayed
7. [ ] Click "Add to Cart" on an item
8. [ ] Verify item removed from wishlist
9. [ ] Verify item added to cart
10. [ ] Remove an item from wishlist
11. [ ] Verify item removed

**Expected Results:**
- Heart icon toggles correctly
- Wishlist shows all saved items
- Move to cart works properly
- Remove function works

---

## Checkout Flow Tests

### Test 1: Guest Checkout

**Scenario:** User checks out without account

**Steps:**
1. [ ] Add items to cart (no sign-in)
2. [ ] Navigate to checkout
3. [ ] See guest checkout notice
4. [ ] Fill out contact information:
    - Full Name
    - Email
    - Phone
5. [ ] Fill out delivery address:
    - County
    - Town
    - Street Address
6. [ ] Apply promo code (optional)
7. [ ] Accept terms and conditions
8. [ ] Submit order
9. [ ] Verify order confirmation

**Validation Checks:**
- [ ] Required fields enforce validation
- [ ] Email format validated
- [ ] Phone format validated
- [ ] Terms checkbox required
- [ ] Total calculation correct
- [ ] Guest checkout notice visible

**Test Data:**
```
Name: Test Guest User
Email: guest@test.com
Phone: +254712345678
County: Nairobi
Town: Westlands
Address: Test Street, Building 123
Promo: SAVE20
```

---

### Test 2: Authenticated Checkout with Saved Address

**Scenario:** Logged-in user with previous orders

**Steps:**
1. [ ] Sign in
2. [ ] Add items to cart
3. [ ] Navigate to checkout
4. [ ] Verify contact info pre-filled
5. [ ] See "Use saved address" option
6. [ ] Select a saved address
7. [ ] Apply promo code
8. [ ] Submit order
9. [ ] Verify confirmation

**Validation Checks:**
- [ ] User info auto-populated
- [ ] Saved addresses displayed
- [ ] Radio buttons work correctly
- [ ] Can switch between saved/new address
- [ ] Promo code applies correctly

---

### Test 3: Authenticated Checkout with New Address

**Scenario:** Logged-in user with new delivery address

**Steps:**
1. [ ] Sign in
2. [ ] Add items to cart
3. [ ] Navigate to checkout
4. [ ] Select "Add new address"
5. [ ] Fill out new address
6. [ ] Submit order
7. [ ] Verify order uses new address
8. [ ] Verify address saved for future

**Validation Checks:**
- [ ] New address form displays
- [ ] All fields required
- [ ] Address saves to user profile

---

### Test 4: Empty Cart Prevention

**Scenario:** Attempt checkout with empty cart

**Steps:**
1. [ ] Clear cart completely
2. [ ] Attempt to access checkout page
3. [ ] Verify appropriate handling

**Expected Results:**
- Redirect to products page OR
- Show "Cart is empty" message

---

### Test 5: Promo Code Validation

**Scenario:** Test valid and invalid promo codes

**Steps:**
1. [ ] Add items to cart
2. [ ] Go to checkout
3. [ ] Test valid promo code
4. [ ] Verify discount applied
5. [ ] Test invalid promo code
6. [ ] Verify error message
7. [ ] Test expired promo code (if available)
8. [ ] Verify appropriate error

**Test Cases:**
```
Valid Code: WELCOME10 (10% off)
Invalid Code: INVALID123
Expired Code: EXPIRED2024
```

**Validation Checks:**
- [ ] Discount calculates correctly
- [ ] Error messages clear
- [ ] Discount displayed in summary
- [ ] Total updates accordingly

---

### Test 6: Payment Instruction Display

**Scenario:** Verify payment instructions shown

**Steps:**
1. [ ] Complete checkout
2. [ ] View order confirmation
3. [ ] Verify payment instructions displayed
4. [ ] Check M-Pesa details shown
5. [ ] Verify bank transfer info shown

**Expected Results:**
- Payment methods clearly listed
- M-Pesa number displayed
- Bank account details shown
- Instructions clear and complete

---

## Booking Flow Tests

### Test 1: New Service Booking

**Scenario:** Book a makeup service

**Steps:**
1. [ ] Sign in (required)
2. [ ] Navigate to Services
3. [ ] Select a service
4. [ ] Choose package type
5. [ ] Select date (calendar)
6. [ ] Choose time slot
7. [ ] Fill booking form:
    - Service type
    - Number of people
    - Location
    - Special requests
8. [ ] Review summary
9. [ ] Accept terms
10. [ ] Submit booking
11. [ ] Verify confirmation

**Validation Checks:**
- [ ] Calendar shows available dates only
- [ ] Time slots filtered correctly
- [ ] Required fields validated
- [ ] Price calculation correct
- [ ] Confirmation shows all details

**Test Data:**
```
Service: Bridal Makeup
Package: Premium
Date: [Select available date]
Time: 09:00 AM
Bride: 1
Bridesmaids: 3
Mothers: 2
Location: Nairobi, Westlands
Special Requests: Outdoor wedding, natural look preferred
```

---

### Test 2: Booking Calendar Availability

**Scenario:** Test date/time selection

**Steps:**
1. [ ] Start booking process
2. [ ] Open calendar
3. [ ] Verify past dates disabled
4. [ ] Select a date
5. [ ] Verify time slots appear
6. [ ] Select booked time (if exists)
7. [ ] Verify appropriate handling
8. [ ] Select available time
9. [ ] Proceed with booking

**Validation Checks:**
- [ ] Past dates not selectable
- [ ] Booked slots marked/disabled
- [ ] Available slots clearly indicated
- [ ] Time zone correct

---

### Test 3: View Booking History

**Scenario:** Access My Bookings page

**Steps:**
1. [ ] Sign in
2. [ ] Navigate to "My Bookings"
3. [ ] Verify bookings list displayed
4. [ ] Check booking details:
    - Service name
    - Date and time
    - Status
    - Location
5. [ ] Click on a booking
6. [ ] View full booking details
7. [ ] Verify all information correct

**Validation Checks:**
- [ ] All bookings displayed
- [ ] Status indicators correct
- [ ] Dates formatted properly
- [ ] Details page loads

---

### Test 4: Booking Confirmation Page

**Scenario:** Verify confirmation details

**Steps:**
1. [ ] Complete a booking
2. [ ] On confirmation page, verify:
    - Booking reference number
    - Service details
    - Date and time
    - Pricing breakdown
    - Payment instructions
    - Contact information
3. [ ] Verify email notification (if implemented)

**Expected Results:**
- All booking details accurate
- Reference number generated
- Payment instructions clear
- Confirmation email sent

---

## Admin Operations Tests

### Test 1: Admin Dashboard Access

**Scenario:** Access admin panel

**Steps:**
1. [ ] Sign in as admin user
2. [ ] Verify "Admin" link in navigation
3. [ ] Click Admin link
4. [ ] Verify dashboard loads
5. [ ] Check all sections accessible:
    - Bookings
    - Orders
    - Products
    - Users (if applicable)

**Validation Checks:**
- [ ] Only admin users see Admin link
- [ ] Non-admin users redirected
- [ ] All admin sections load
- [ ] No console errors

---

### Test 2: Booking Management

**Scenario:** Manage service bookings

**Steps:**
1. [ ] Access Admin > Bookings
2. [ ] View bookings list
3. [ ] Verify all bookings shown
4. [ ] Apply status filter
5. [ ] Change booking status
6. [ ] Verify status updated
7. [ ] Add notes to booking
8. [ ] Search for specific booking
9. [ ] Export bookings (if available)

**Validation Checks:**
- [ ] Bookings list complete
- [ ] Filters work correctly
- [ ] Status changes save
- [ ] Search functional
- [ ] Pagination works

---

### Test 3: Admin Calendar View

**Scenario:** View bookings calendar

**Steps:**
1. [ ] Access Admin > Calendar
2. [ ] Verify calendar displays
3. [ ] Check current month shown
4. [ ] Navigate to different months
5. [ ] Click on a date with booking
6. [ ] Verify booking details popup
7. [ ] Test week/day views (if available)

**Validation Checks:**
- [ ] Calendar renders correctly
- [ ] Bookings appear on correct dates
- [ ] Navigation works
- [ ] Different views functional

---

### Test 4: Order Management (Future)

**Scenario:** Manage product orders

**Steps:**
1. [ ] Access Admin > Orders (if implemented)
2. [ ] View orders list
3. [ ] Update order status
4. [ ] Add tracking number
5. [ ] Mark as payment confirmed
6. [ ] Filter by status
7. [ ] Search orders

**Validation Checks:**
- [ ] Orders displayed correctly
- [ ] Status updates save
- [ ] Tracking numbers save
- [ ] Filters work

---

## Cross-Browser Testing

### Browsers to Test

**Desktop:**
- [ ] Google Chrome (latest)
- [ ] Mozilla Firefox (latest)
- [ ] Safari (latest - macOS)
- [ ] Microsoft Edge (latest)

**Mobile:**
- [ ] Safari iOS (iPhone)
- [ ] Chrome Android
- [ ] Samsung Internet

### Test Checklist Per Browser

**Visual Tests:**
- [ ] Layout renders correctly
- [ ] Fonts load properly
- [ ] Images display
- [ ] Colors accurate
- [ ] Spacing consistent

**Functionality Tests:**
- [ ] Navigation works
- [ ] Forms submit
- [ ] Buttons clickable
- [ ] Dropdowns function
- [ ] Modals open/close
- [ ] Animations smooth

**Mobile-Specific:**
- [ ] Touch targets adequate (44x44px)
- [ ] No horizontal scroll
- [ ] Keyboard doesn't cover inputs
- [ ] Hamburger menu works
- [ ] Swipe gestures work

### Browser-Specific Issues Log

| Browser | Issue | Severity | Status |
|---------|-------|----------|--------|
| Example | Button misaligned | Low | Fixed |

---

## Performance Testing

### Lighthouse Audit

**Target Scores (Mobile & Desktop):**
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90

**How to Run:**
```bash
# Production build
npm run build
npm start

# Run Lighthouse
npx lighthouse http://localhost:3000 --view

# Or use Chrome DevTools > Lighthouse
```

**Pages to Test:**
- [ ] Homepage
- [ ] Products page
- [ ] Product detail page
- [ ] Services page
- [ ] Checkout page
- [ ] Order confirmation
- [ ] My Orders
- [ ] My Bookings

### Core Web Vitals

**Targets:**
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

**Measurement:**
```javascript
// Add to page for real user monitoring
new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    console.log('LCP:', entry.renderTime || entry.loadTime);
  }
}).observe({entryTypes: ['largest-contentful-paint']});
```

### Page Load Time Testing

**Test on Different Connection Speeds:**
- [ ] Fast 3G
- [ ] Slow 3G
- [ ] 4G
- [ ] Fiber/Broadband

**Chrome DevTools:**
1. Open DevTools
2. Network tab
3. Throttling dropdown
4. Select connection speed
5. Reload page
6. Verify acceptable load time

**Targets:**
- 3G: < 3 seconds
- 4G: < 2 seconds
- Broadband: < 1 second

### Bundle Size Analysis

```bash
# Analyze bundle
npm run build
npx @next/bundle-analyzer
```

**Check for:**
- [ ] Largest bundles identified
- [ ] Unnecessary dependencies
- [ ] Code splitting effective
- [ ] Tree shaking working

---

## Load Testing

### Basic Load Testing with Apache Bench

**Simple Load Test:**
```bash
# Test homepage with 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:3000/

# Test API endpoint
ab -n 100 -c 10 http://localhost:8000/api/products
```

**Targets:**
- Average response time: < 200ms
- 95th percentile: < 500ms
- 99th percentile: < 1000ms
- 0 failed requests

### Load Test Scenarios

**Scenario 1: Homepage Load**
```bash
ab -n 500 -c 25 http://localhost:3000/
```

**Scenario 2: Product API**
```bash
ab -n 1000 -c 50 http://localhost:8000/api/products/list?limit=20
```

**Scenario 3: Checkout Simulation**
```bash
# Multiple users checking out
ab -n 100 -c 10 -p checkout-data.json -T application/json \
  http://localhost:8000/api/orders/create
```

### Database Performance

**Check Query Performance:**
```sql
-- Enable query logging (PostgreSQL)
SET log_statement = 'all';
SET log_duration = on;

-- Monitor slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Targets:**
- Most queries: < 50ms
- Complex queries: < 200ms
- No N+1 query issues

---

## Bug Reporting

### Bug Report Template

```markdown
**Bug Title:** Brief description

**Severity:** Critical / High / Medium / Low

**Environment:**
- Browser: Chrome 120
- OS: macOS 14
- Screen Size: 1920x1080
- Device: Desktop / Mobile

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Screenshots/Videos:**
[Attach if applicable]

**Console Errors:**
```
Error message here
```

**Additional Context:**
Any other relevant information
```

### Bug Tracking

Create file: `BUGS.md`

| ID | Title | Severity | Status | Assigned | Fixed In |
|----|-------|----------|--------|----------|----------|
| 1  | Example bug | High | Open | - | - |

### Critical Bug Criteria

**Must Fix Before Launch:**
- Data loss or corruption
- Security vulnerabilities
- Payment processing failures
- Complete feature breakage
- Accessibility blockers
- SEO critical issues

**Can Fix After Launch:**
- Minor UI inconsistencies
- Non-critical animations
- Edge case bugs
- Enhancement requests

---

## Testing Sign-Off Checklist

Before marking testing complete:

**User Journeys:**
- [ ] All 4 primary journeys tested
- [ ] No blocking issues found
- [ ] Edge cases documented

**Checkout Flow:**
- [ ] Guest checkout works
- [ ] Authenticated checkout works
- [ ] Promo codes validated
- [ ] Payment instructions clear

**Booking Flow:**
- [ ] New booking works
- [ ] Calendar functional
- [ ] Confirmation accurate
- [ ] My Bookings displays

**Admin Operations:**
- [ ] Dashboard accessible
- [ ] Booking management works
- [ ] Calendar view functional
- [ ] Permissions enforced

**Cross-Browser:**
- [ ] Chrome tested
- [ ] Firefox tested
- [ ] Safari tested (if available)
- [ ] Mobile browsers tested

**Performance:**
- [ ] Lighthouse scores > 90
- [ ] Core Web Vitals pass
- [ ] Load times acceptable
- [ ] Bundle size optimized

**Load Testing:**
- [ ] Basic load test passed
- [ ] No server crashes
- [ ] Response times acceptable
- [ ] Database performs well

**Documentation:**
- [ ] All bugs logged
- [ ] Known issues documented
- [ ] Workarounds noted
- [ ] Future enhancements listed

---

## Continuous Testing

### Automated Testing (Future)

**Unit Tests:**
```bash
# Backend
pytest tests/

# Frontend
npm test
```

**Integration Tests:**
```bash
# API endpoint tests
pytest tests/integration/
```

**E2E Tests:**
```bash
# Playwright/Cypress
npm run test:e2e
```

### Regression Testing

After every major update:
1. Run smoke tests (core user journeys)
2. Test affected features
3. Check for new console errors
4. Verify performance hasn't degraded
5. Update test documentation

---

## Resources

- [Lighthouse Documentation](https://developers.google.com/web/tools/lighthouse)
- [Core Web Vitals](https://web.dev/vitals/)
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)
- [Apache Bench Guide](https://httpd.apache.org/docs/2.4/programs/ab.html)
- [Next.js Testing](https://nextjs.org/docs/testing)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
