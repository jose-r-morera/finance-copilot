---
name: frontend_standards
description: Enforcing high-quality React and Next.js code.
---

# Frontend Standards Rule

## Code Quality
- **Components**: One component per file unless logically grouped.
- **Naming**: PascalCase for components, camelCase for variables/functions.
- **TS**: Avoid `any` type at all costs.
- **Clean Code**: Keep components small and focused.

## Next.js Specifics
- **File Structure**: Follow the App Router structure within `src/app`.
- **Optimization**: Use `next/image` for all images and `next/font` for web fonts.
- **Routing**: Use `Link` from `next/link` for internal navigation.
