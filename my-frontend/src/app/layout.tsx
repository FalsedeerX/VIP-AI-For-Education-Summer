import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "PurdueGPT",
};

// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   return (
//     <html lang="en">
//       <body className="flex flex-col h-screen bg-[var(--background)] text-[var(--foreground)]">
//         <AuthProvider>
//           <Header />
//           {/*<main className="flex-1 flex items-center justify-center overflow-auto">*/}
//           <main className="flex-1 flex flex-col min-h-0 overflow-hidden">
//             {children}
//           </main>
//           <Footer />
//         </AuthProvider>
//       </body>
//     </html>
//   );
// }

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex flex-col h-screen">
        <AuthProvider>
          <Header />
          <hr className="border-black border-t-2" />
          <main className="flex-1 flex flex-col min-h-0 overflow-auto">
          {children}
          </main>
          <hr className="border-black border-t-2" />
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
