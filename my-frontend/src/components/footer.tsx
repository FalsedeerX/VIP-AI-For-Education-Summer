// src/components/Footer.tsx
export function Footer() {
  return (
    <footer className="w-full bg-[var(--color-purdue-brown)] text-[var(--color-purdue-black)] p-2 text-center text-sm">
      © {new Date().getFullYear()} PurdueGPT
    </footer>
  );
}
