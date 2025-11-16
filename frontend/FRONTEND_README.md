# Glam by Lynn - Frontend

Next.js 16 frontend application for the Glam by Lynn platform.

## Tech Stack

- **Framework**: Next.js 16.0.3 with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui compatible
- **State Management**: TanStack React Query
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Axios
- **Authentication**: NextAuth.js with Google OAuth

## Prerequisites

- Node.js 20+
- npm or yarn
- Backend API running on http://localhost:8000

## Getting Started

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Update .env.local with your values
```

### Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Create production build
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components
│   ├── config/          # Configuration files
│   │   └── api.ts       # API endpoints configuration
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utility functions
│   │   └── utils.ts     # Common utilities (cn, etc.)
│   └── types/           # TypeScript type definitions
│       └── index.ts     # Shared types
├── public/              # Static assets
├── .env.local.example   # Environment variables template
├── next.config.ts       # Next.js configuration
├── tailwind.config.ts   # Tailwind CSS configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies and scripts
```

## Available Scripts

### Development
- `npm run dev` - Start development server
- `npm run build` - Create production build
- `npm start` - Start production server

### Code Quality
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run type-check` - Run TypeScript compiler check

## Environment Variables

Required environment variables (see `.env.local.example`):

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth.js
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## TypeScript Configuration

TypeScript is configured with **strict mode** enabled for maximum type safety:

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "jsx": "react-jsx"
  }
}
```

## API Integration

API endpoints are configured in `src/config/api.ts`:

```typescript
import { API_ENDPOINTS } from "@/config/api";

// Example usage
const productsUrl = API_ENDPOINTS.PRODUCTS.LIST;
const productDetailUrl = API_ENDPOINTS.PRODUCTS.DETAIL("product-id");
```

## Type Definitions

All TypeScript types are defined in `src/types/index.ts`:

```typescript
import type { User, Product, Order, Booking } from "@/types";
```

Available types:
- User, Brand, Category, Product, ProductImage, ProductVariant
- ServicePackage, TransportLocation
- Booking
- Order, OrderItem, CartItem, PromoCode
- Review, Testimonial
- ApiResponse, PaginatedResponse

## Styling

### Tailwind CSS

Tailwind CSS 4 is configured with custom utilities:

```tsx
import { cn } from "@/lib/utils";

<div className={cn("base-class", condition && "conditional-class")} />
```

### Prettier

Code formatting is handled by Prettier with Tailwind plugin:

```bash
# Format all files
npm run format

# Check formatting
npm run format:check
```

## Best Practices

1. **Type Safety**: Always use TypeScript types, avoid `any`
2. **Component Structure**: Use functional components with TypeScript
3. **API Calls**: Use React Query for data fetching
4. **Forms**: Use React Hook Form with Zod validation
5. **Styling**: Use Tailwind utility classes
6. **Code Formatting**: Run Prettier before committing
7. **Linting**: Fix ESLint errors before committing

## shadcn/ui Integration

The project is configured for shadcn/ui components. To add components:

```bash
npx shadcn@latest add button
npx shadcn@latest add form
npx shadcn@latest add dialog
```

Components will be added to `src/components/ui/`.

## Development Workflow

1. Create feature branch
2. Develop feature with TypeScript strict mode
3. Write/update types in `src/types/`
4. Format code: `npm run format`
5. Check types: `npm run type-check`
6. Run linter: `npm run lint`
7. Test locally: `npm run dev`
8. Build: `npm run build`
9. Commit and create PR

## Deployment

### Vercel (Recommended)

1. Connect repository to Vercel
2. Configure environment variables
3. Deploy automatically on push

### Manual Build

```bash
npm run build
npm start
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

### Type Errors

```bash
# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build
```

### ESLint Errors

```bash
# Auto-fix
npm run lint:fix
```

## Contributing

1. Follow TypeScript strict mode
2. Use Prettier for formatting
3. Write descriptive commit messages
4. Ensure all checks pass before PR
5. Update types when adding new features

## Links

- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [React Query](https://tanstack.com/query/latest)

---

**Version**: 0.1.0
**Node**: 20+
**Next.js**: 16.0.3
