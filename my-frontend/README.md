# AI for EDU Internship — Front End

A React/Next.js front-end for the AI for EDU Internship platform. Provides a responsive dashboard UI with a collapsible sidebar, sheet dialogs, and custom UI components styled with Tailwind CSS.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Prerequisites](#prerequisites)
3. [Getting Started](#getting-started)
4. [Environment Variables](#environment-variables)
5. [Project Structure](#project-structure)
6. [Important Pages and Components](#pages-components)
7. [Testing](#testing)
8. [Authors](#authors)

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

```bash
npm install
```

```bash
npm run dev
```

---

## Environment Variables

Create and .env.local file at the project route with:

- NEXT_PUBLIC_BACKEND_WS=(ws:// websocket)
- NEXT_PUBLIC_API_BASE_URL=(Address where the server runs)

---

## Project Structure

```txt
├── public/                                 # Static assets (images, favicon, etc.)
├── src/
│ ├── app/                                  # Next.js App Router
│ │ ├── (protected)/                        # Protected routes wrapper
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
│ │ ├── ui/                                  # Reusable UI primitives
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
│ │ └── AuthContext.tsx                     # Authentication context/provider
│ │
│ ├── hooks/
│ │ └── use-mobile.ts                       # Mobile detection hook
│ │
│ └── lib/
│ ├── api.ts                                # API client wrappers
│ ├── config.ts                             # Runtime configuration
│ └── utils.ts                              # Helpers (e.g. cn)
│
├── .env.local                              # Environment variables
├── .gitignore
├── components.json
├── eslint.config.mjs
├── next-env.d.ts
├── next-config.ts                          # Next.js config
├── package-lock.json
├── package.json
├── postcss.config.mjs
├── README.md
└── tsconfig.json
```

---

## Important Pages and Components

- **login**
  Under the login folder, the page.tsx handles the code for login page

- **register**
  Under the register folder, the page.tsx handles the code for register page

- **terms**
  Under the terms folder, the page.tsx handles the code for terms page

- **Stlyling and Design**
  Color and Font choices can be found in globals.css, most component designs were imported from from shadcn UI library

- **Main Page**
  The main page.tsx directly under the app folder handles the code for main dashboard
  every user sees when they login. For admins it renders the Admin Dashboard, for normal users it renders a combination of the sidebar component and the messaging screen.

- **Admin Dashboard**
  This page is more in the style of a component that is then rendered by the main page.tsx. It features a way for teachers to create courses, add folder, add files and delete them as well.

- **Sidebar**
  This component is rendered to display the courses that a user has joined, and under all the folders is the chats a user has created and the the option to start a new one. Collapsible from the side.

- **Chat Screen**
  Thic screen displays the message conversation between the user and the AI, it feature autmatic scrolling, dynamic sizing and onerror can restart the websocket connection. Rendered under ChatPage, and accessed it's HTTP adress includes the UUID chat_id.


---

## Testing

Three Functional Testing files coded using Jest and React Testing Library, that test if the ChatPage, LoginPage and RegisterPage render correctly and work with user interaction.  
  
To run  
```
npm test
```

