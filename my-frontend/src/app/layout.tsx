import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";

export const metadata = {
  title: "PurdueGPT",
};

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
