# Email Service Setup

The Glam by Lynn application includes a flexible email service that supports multiple providers.

## Configuration

Add the following environment variables to your `.env` file:

### Basic Configuration

```env
# Email Provider (console, resend, sendgrid, smtp)
EMAIL_PROVIDER=console

# From Email Address
EMAIL_FROM=noreply@glambylynn.com
EMAIL_FROM_NAME=Glam by Lynn
```

### Provider-Specific Configuration

#### Option 1: Console (Development)

No additional configuration needed. Emails will be printed to the console.

```env
EMAIL_PROVIDER=console
```

#### Option 2: Resend (Recommended for Production)

1. Sign up at [resend.com](https://resend.com)
2. Create an API key
3. Install the package: `pip install resend`
4. Configure:

```env
EMAIL_PROVIDER=resend
RESEND_API_KEY=your_resend_api_key_here
```

#### Option 3: SendGrid

1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Create an API key
3. Install the package: `pip install sendgrid`
4. Configure:

```env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your_sendgrid_api_key_here
```

## Email Templates

The service includes responsive HTML templates for:

### 1. Order Confirmation Email
- Sent when customer places an order
- Includes order details, items, totals, delivery address
- Brand colors: Black background with pink accents

### 2. Booking Confirmation Email
- Sent when customer books a service
- Includes booking reference, service details, date/time, location
- Reminder to arrive 10 minutes early

### 3. Vision Registration Confirmation Email
- Sent when someone registers interest in 2026 expansion
- Thanks them for their interest
- Lists selected areas of interest

## Email Service Usage

### In Code

```python
from app.services.email_service import email_service

# Send order confirmation
email_service.send_order_confirmation(
    to_email="customer@example.com",
    order_number="ORD-12345",
    customer_name="Jane Doe",
    order_items=[...],
    subtotal=Decimal("1000.00"),
    discount=Decimal("100.00"),
    delivery_fee=Decimal("200.00"),
    total=Decimal("1100.00"),
    delivery_address={...},
)

# Send booking confirmation
email_service.send_booking_confirmation(
    to_email="customer@example.com",
    booking_reference="BKG-12345",
    customer_name="Jane Doe",
    service_name="Bridal Makeup Package",
    booking_date=datetime(2026, 1, 15),
    booking_time="10:00 AM",
    location="Nairobi Studio",
    total_price=Decimal("5000.00"),
)

# Send vision registration confirmation
email_service.send_vision_registration_confirmation(
    to_email="customer@example.com",
    full_name="Jane Doe",
    interests=["Full-service Salon", "Spa Treatments"],
)
```

## Testing

### Development Mode (Console)

In development, use `EMAIL_PROVIDER=console` to print emails to the console instead of sending them.

### Testing with Real Email Providers

1. **Resend**: Use their test mode to send to verified email addresses
2. **SendGrid**: Use sandbox mode for testing

## Email Design

All email templates feature:
- Responsive HTML design
- Plain text fallback
- Glam by Lynn branding (black/pink color scheme)
- Mobile-friendly layout
- Clear call-to-actions
- Professional footer with company info

## Future Email Templates

Templates to be added:
- Review request email (post-purchase)
- Newsletter confirmation
- Password reset
- Account verification
- Shipping confirmation with tracking
- Appointment reminders

## Troubleshooting

### Emails not sending

1. Check `EMAIL_PROVIDER` is set correctly
2. Verify API keys are correct
3. Check console/logs for error messages
4. Ensure required packages are installed (`resend` or `sendgrid`)

### Emails going to spam

1. Configure SPF, DKIM, and DMARC records for your domain
2. Use a verified domain with your email provider
3. Avoid spam trigger words in subject lines
4. Include unsubscribe link for marketing emails

## Production Checklist

- [ ] Choose email provider (Resend or SendGrid recommended)
- [ ] Set up domain verification
- [ ] Configure DNS records (SPF, DKIM, DMARC)
- [ ] Test all email templates
- [ ] Set up email monitoring/alerts
- [ ] Configure rate limiting if needed
- [ ] Add unsubscribe functionality for marketing emails
