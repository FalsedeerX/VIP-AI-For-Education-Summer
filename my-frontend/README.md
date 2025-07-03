# AI for EDU Internship — Front End

A React/Next.js front-end for the AI for EDU Internship platform. Provides a responsive dashboard UI with a collapsible sidebar, sheet dialogs, and custom UI components styled with Tailwind CSS.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Prerequisites](#prerequisites)
3. [Getting Started](#getting-started)
4. [Environment Variables](#environment-variables)
5. [Available Scripts](#available-scripts)
6. [Project Structure](#project-structure)
7. [Styling & Design](#styling-design)
8. [Important Pages and Components](#pages-components)
9. [Authors](#authors)

---

## Tech Stack

- **Framework:** Next.js 13 (App Router)
- **Language:** TypeScript, React 18
- **Styling:** Tailwind CSS
- **Component Library:** Radix UI, class-variance-authority (`cva`), lucide-react icons, shadcn-ui

---

## Prerequisites

- **Node.js** v16+
- **npm** v8+ or **yarn** v1.22+

---

## Getting Started

'''bash
npm install
'''

'''bash
npm run dev
'''

---

## Environment Variables

Create and .env.local file at the project route with '''NEXT_PUBLIC_API_BASE_URL=(Address where the server runs)'''

---

## Project Structure

'''python
├── public/ # Static assets (images, favicon, etc.)
├── src/
│ ├── app/ # Next.js App Router
│ │ ├── (protected)/ # Protected routes wrapper
│ │ ├── login/
│ │ │ └── page.tsx
│ │ ├── register/
│ │ │ └── page.tsx
│ │ ├── terms/
│ │ │ └── page.tsx
│ │ ├── admindashboard.tsx
│ │ ├── chatscreen.tsx
│ │ ├── favicon.ico
│ │ ├── globals.css
│ │ ├── layout.tsx
│ │ ├── mainscreen.tsx
│ │ └── page.tsx
│ │
│ ├── components/
│ │ ├── ui/ # Reusable UI primitives
│ │ │ ├── accordion.tsx
│ │ │ ├── button.tsx
│ │ │ ├── card.tsx
│ │ │ ├── checkbox.tsx
│ │ │ ├── dialog.tsx
│ │ │ ├── drawer.tsx
│ │ │ ├── input.tsx
│ │ │ ├── separator.tsx
│ │ │ └── sidebar-2.tsx
│ │ ├── footer.tsx
│ │ └── header.tsx
│ │
│ ├── context/
│ │ └── AuthContext.tsx # Authentication context/provider
│ │
│ ├── hooks/
│ │ └── use-mobile.ts # Mobile detection hook
│ │
│ └── lib/
│ ├── api.ts # API client wrappers
│ ├── config.ts # Runtime configuration
│ └── utils.ts # Helpers (e.g. cn)
│
├── .env.local # Environment variables
├── .gitignore
├── components.json
├── eslint.config.mjs
├── next-env.d.ts
├── next-config.ts # Next.js config
├── package-lock.json
├── package.json
├── postcss.config.mjs
├── README.md
└── tsconfig.json
'''

---

## Important Pages and Components

---

## Authors

Developed by Shrey Agarwal and Yu-Kuang Chen
