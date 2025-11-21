# Known Issues and Bugs

This document tracks all known issues, bugs, and areas for improvement in the Glam by Lynn application.

## Status Legend
- 🔴 **Critical**: Must fix before launch
- 🟠 **High**: Should fix before launch
- 🟡 **Medium**: Fix soon after launch
- 🟢 **Low**: Enhancement/Future improvement
- ✅ **Fixed**: Issue resolved
- 🔄 **In Progress**: Currently being worked on

---

## Critical Issues 🔴

None currently identified.

---

## High Priority Issues 🟠

### Pre-existing Type Errors

**ID:** BUG-001
**Status:** 🔄 In Progress
**Severity:** High
**Component:** Frontend - Multiple files

**Description:**
TypeScript compilation shows several type errors across the application:
- `src/app/admin/bookings/page.tsx`: Property 'accessToken' does not exist
- `src/app/bookings/[id]/confirmation/page.tsx`: Property 'locationName' vs 'location_name'
- `src/app/products/[id]/page.tsx`: 'product.images' is possibly 'undefined'
- `src/components/Header.tsx`: Cannot find module '@/components/ui/sheet'
- `src/lib/services.ts`: Multiple snake_case vs camelCase property mismatches

**Impact:**
- Type safety compromised
- Potential runtime errors
- Developer experience degraded

**Steps to Reproduce:**
```bash
npm run type-check
```

**Recommended Fix:**
1. Install missing sheet component: `npx shadcn@latest add sheet`
2. Fix property name mismatches (use snake_case consistently)
3. Add proper null checks for optional properties
4. Remove accessToken references or add to type definitions

**Priority:** Should fix before launch to ensure type safety

---

## Medium Priority Issues 🟡

### Product Images Possibly Undefined

**ID:** BUG-002
**Status:** Open
**Severity:** Medium
**Component:** Frontend - Product Detail Page
**File:** `src/app/products/[id]/page.tsx`

**Description:**
Product detail page doesn't handle cases where `product.images` is undefined properly.

**Lines Affected:** 354, 376, 378, 390, 392

**Recommended Fix:**
```typescript
// Add proper checks
const hasImages = product?.images && product.images.length > 0
const currentImage = hasImages && product.images ? product.images[selectedImageIndex] : null
```

---

### Auth Token Management

**ID:** BUG-003
**Status:** Open
**Severity:** Medium
**Component:** Backend/Frontend - Authentication

**Description:**
Some admin pages reference `user.accessToken` which doesn't exist in the session type. The app uses cookie-based authentication but some code expects JWT tokens.

**Files Affected:**
- `src/app/admin/bookings/page.tsx`
- `src/app/admin/calendar/page.tsx`
- `src/app/bookings/new/page.tsx`

**Recommended Fix:**
Use `credentials: "include"` consistently instead of Authorization headers, or properly implement JWT token management.

---

### Snake Case vs Camel Case Inconsistency

**ID:** BUG-004
**Status:** Open
**Severity:** Medium
**Component:** Frontend - Type Definitions

**Description:**
Backend returns snake_case properties but frontend TypeScript types expect camelCase in multiple places.

**Files Affected:**
- `src/lib/services.ts` (package_type vs packageType, base_bride_price vs baseBridePrice, etc.)
- `src/app/services/page.tsx`
- `src/app/bookings/[id]/confirmation/page.tsx`

**Recommended Fix:**
1. Choose one convention (snake_case recommended for API consistency)
2. Update all type definitions
3. Or implement camelCase transformation in API client

---

## Low Priority Issues 🟢

### Missing Sheet Component Import

**ID:** BUG-005
**Status:** Open
**Severity:** Low
**Component:** Frontend - Header Component

**Description:**
Header.tsx imports `@/components/ui/sheet` but component may not be installed.

**Recommended Fix:**
```bash
npx shadcn@latest add sheet
```

---

### Placeholder Images Missing

**ID:** ENHANCEMENT-001
**Status:** Open
**Severity:** Low
**Component:** Frontend - Various Pages

**Description:**
Several pages reference placeholder images that don't exist:
- `/placeholder-salon.jpg`
- `/placeholder-barber.jpg`
- `/placeholder-spa.jpg`
- `/placeholder-van.jpg`
- `/placeholder-image.jpg`

**Recommended Fix:**
1. Create or obtain appropriate placeholder images
2. Add to `public` folder
3. Or use a service like unsplash.com for temporary placeholders

---

### Google OAuth Credentials

**ID:** CONFIG-001
**Status:** Open
**Severity:** Low
**Component:** Configuration

**Description:**
Google OAuth client ID and secret need to be configured properly for both frontend and backend.

**Recommended Fix:**
1. Set up Google OAuth application
2. Add credentials to both `.env` files
3. Ensure redirect URLs match

---

## Fixed Issues ✅

None yet - this is a new tracking document.

---

## Enhancement Requests

### PDF Receipt Download

**ID:** ENH-001
**Priority:** Future
**Component:** Frontend - Orders

**Description:**
Add ability to download order receipts as PDF.

**Proposed Solution:**
- Use `react-pdf` or similar library
- Generate PDF server-side and provide download link

---

### Email Notifications

**ID:** ENH-002
**Priority:** Future
**Component:** Backend

**Description:**
Send email notifications for:
- Order confirmations
- Booking confirmations
- Order status updates
- Payment confirmations

**Proposed Solution:**
- Integrate email service (SendGrid, AWS SES, etc.)
- Create email templates
- Implement background job queue

---

### Advanced Search

**ID:** ENH-003
**Priority:** Future
**Component:** Frontend - Products

**Description:**
Enhance product search with:
- Advanced filters
- Search suggestions
- Recently viewed
- Search history

---

### Real-time Booking Availability

**ID:** ENH-004
**Priority:** Future
**Component:** Backend - Bookings

**Description:**
Implement real-time availability checking to prevent double bookings.

**Proposed Solution:**
- WebSocket connection for real-time updates
- Database-level locking
- Optimistic UI updates

---

## Testing Notes

### Browser Compatibility Issues

None identified yet. Will update after cross-browser testing.

### Performance Issues

None identified yet. Will update after Lighthouse audits.

### Mobile Issues

None identified yet. Will update after mobile device testing.

---

## How to Report a Bug

1. Check if bug already exists in this document
2. If new, add to appropriate section above
3. Include:
   - Clear title
   - Severity level
   - Component/file affected
   - Steps to reproduce
   - Expected vs actual behavior
   - Recommended fix (if known)
4. Assign bug ID (BUG-XXX, ENH-XXX, CONFIG-XXX)
5. Update status as work progresses

---

## Fix Priority Matrix

| Severity | Before Launch | After Launch |
|----------|--------------|--------------|
| Critical 🔴 | Must fix | N/A |
| High 🟠 | Should fix | Must fix soon |
| Medium 🟡 | Nice to fix | Fix in next sprint |
| Low 🟢 | Optional | Backlog |

---

## Last Updated

2025-01-21 - Initial document creation

## Contributors

- Claude Code (AI Assistant)
- [Add team members as they contribute]
