# Security Documentation

This document outlines the security measures implemented in the Glam by Lynn API.

## Security Features

### 1. CORS (Cross-Origin Resource Sharing)

**Configuration:** `app/main.py`

- **Allowed Origins:** Configured via `ALLOWED_ORIGINS` environment variable
- **Credentials:** Enabled for authenticated requests
- **Methods:** All HTTP methods allowed (GET, POST, PUT, DELETE, etc.)
- **Headers:** All headers allowed for flexibility

**Production Recommendations:**
- Set `ALLOWED_ORIGINS` to specific frontend domain only
- Never use wildcard (`*`) in production
- Always use HTTPS in production

### 2. Security Headers

**Middleware:** `app/core/middleware.py - SecurityHeadersMiddleware`

The following security headers are automatically added to all responses:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking attacks |
| `X-XSS-Protection` | `1; mode=block` | Enables XSS filter in older browsers |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Enforces HTTPS (production only) |
| `Content-Security-Policy` | Custom policy | Prevents XSS and injection attacks |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Controls referrer information |
| `Permissions-Policy` | Feature restrictions | Restricts browser features |

### 3. Rate Limiting

**Middleware:** `app/core/middleware.py`

#### General Rate Limiting
- **Limit:** 60 requests per minute per IP
- **Applies to:** All endpoints
- **Response:** 429 Too Many Requests with `Retry-After` header

#### Authentication Rate Limiting
- **Limit:** 5 requests per minute per IP
- **Hourly Limit:** 20 requests per hour per IP
- **Applies to:** `/api/auth/*` endpoints only
- **Purpose:** Prevent brute force attacks on authentication

**Headers Returned:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying (when limited)

**Production Recommendations:**
- Use Redis for distributed rate limiting across multiple servers
- Adjust limits based on your traffic patterns
- Consider IP whitelisting for known good actors

### 4. Input Validation

**Framework:** Pydantic

All API inputs are validated using Pydantic models:

- **Type Safety:** Automatic type checking and conversion
- **Field Validation:** Custom validators for complex rules
- **Error Messages:** Clear, actionable error messages (422 status)
- **SQL Injection Prevention:** Parameterized queries via SQLAlchemy ORM

**Best Practices:**
- Never trust user input
- Always use Pydantic schemas for request validation
- Use SQLAlchemy ORM for database queries (never raw SQL with user input)
- Sanitize outputs when necessary

### 5. SQL Injection Prevention

**ORM:** SQLAlchemy

- **Parameterized Queries:** All database queries use parameterized statements
- **No Raw SQL:** User input is never directly interpolated into SQL
- **Type Safety:** ORM ensures type safety in queries

**Example Safe Query:**
```python
# SAFE - Parameterized query
user = db.query(User).filter(User.email == user_email).first()

# UNSAFE - Never do this
# query = f"SELECT * FROM users WHERE email = '{user_email}'"
```

### 6. Environment Variable Validation

**Configuration:** `app/core/config.py`

Production environment variables are validated on startup:

#### Required in Production:
- `SECRET_KEY` (minimum 32 characters, not default value)
- `DATABASE_URL` (must be PostgreSQL, not SQLite)
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- `DEBUG=False` (debug mode must be disabled)

#### Format Validation:
- `ALLOWED_ORIGINS` must start with `http://` or `https://`
- `DATABASE_URL` must be valid connection string

**Sensitive Values Masked:**
The `get_safe_config()` method masks sensitive values for logging:
- `SECRET_KEY`
- `DATABASE_URL`
- `GOOGLE_CLIENT_SECRET`
- `AWS_SECRET_ACCESS_KEY`
- `RESEND_API_KEY`

### 7. Authentication & Authorization

**JWT Tokens:**
- **Algorithm:** HS256
- **Access Token:** 15 minutes expiry
- **Refresh Token:** 7 days expiry
- **Storage:** Never store tokens in localStorage (use httpOnly cookies in production)

**Role-Based Access Control (RBAC):**
- 5 admin roles: `super_admin`, `product_manager`, `booking_manager`, `content_editor`, `artist`
- Permission middleware enforces role requirements
- Admin whitelist via `ADMIN_EMAILS` environment variable

**Dependencies:**
- `get_current_user` - Requires valid JWT token
- `get_current_admin_user` - Requires admin status
- `get_current_super_admin` - Requires super admin role
- `get_product_manager` - Requires product management permissions
- `get_booking_manager` - Requires booking management permissions
- `get_content_editor` - Requires content editing permissions
- `get_artist` - Requires artist permissions

### 8. Secrets Management

**Never commit secrets to version control!**

**Development:**
- Use `.env` file (added to `.gitignore`)
- Set minimal required values for local development

**Production:**
- Use environment variables
- Use secrets management service (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate secrets regularly
- Use strong random values (minimum 32 characters for SECRET_KEY)

**Sensitive Values:**
- `SECRET_KEY` - JWT signing key
- `DATABASE_URL` - Database connection string with credentials
- `GOOGLE_CLIENT_SECRET` - OAuth client secret
- `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `RESEND_API_KEY` - Email service API key

## Security Checklist for Production

### Before Deployment:

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY` (min 32 chars)
- [ ] Configure production `DATABASE_URL` (PostgreSQL)
- [ ] Set specific `ALLOWED_ORIGINS` (no wildcards)
- [ ] Configure all required OAuth credentials
- [ ] Set up HTTPS/TLS certificates
- [ ] Configure admin whitelist (`ADMIN_EMAILS`)
- [ ] Review and adjust rate limits
- [ ] Enable database backups
- [ ] Set up monitoring and alerting
- [ ] Review security headers configuration
- [ ] Test authentication flows
- [ ] Verify CORS configuration
- [ ] Check rate limiting works correctly

### Ongoing:

- [ ] Rotate secrets regularly (every 90 days)
- [ ] Monitor rate limit violations
- [ ] Review admin access logs
- [ ] Keep dependencies updated
- [ ] Monitor security advisories
- [ ] Perform security audits
- [ ] Review and update CORS origins
- [ ] Check for SQL injection vulnerabilities
- [ ] Test authentication edge cases

## Reporting Security Issues

If you discover a security vulnerability, please email security@glambylynn.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Do not** create public GitHub issues for security vulnerabilities.

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/faq/security.html)
