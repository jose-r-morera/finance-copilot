---
name: frontend_dev
description: Best practices for Next.js, TypeScript, and Tailwind CSS development.
---

# Frontend Development Skill

This skill provides guidance on building modern, performant, and accessible frontends.

## Tech Stack
- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript (Strict Mode)
- **Styling**: Tailwind CSS
- **Components**: Functional components with Hooks

## Guidelines
- **Server Components**: Prefer Server Components by default; use `'use client'` only when necessary for interactivity.
- **State Management**: Use React state or specialized libraries (Zustand/Jotai) if complexity grows.
- **API Fetching**: Use standard `fetch` with Next.js caching/revalidation.
- **Accessibility (A11y)**: Use semantic HTML and ARIA labels.

## Commands
- Dev Server: `npm run dev`
- Build: `npm run build`
- Lint: `npm run lint`
- Type Check: `npx tsc --noEmit`
