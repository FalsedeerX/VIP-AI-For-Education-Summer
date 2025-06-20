// src/app/(protected)/layout.tsx
/** 
"use client";

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Sidebar } from "@/components/Sidebar";
import { Drawer, DrawerContent, DrawerTrigger } from "@/ui/drawer";
import { LucideMenu } from "lucide-react"; // you can install lucide-react for icons

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-screen">
      <Header />

      <div className="flex flex-1 overflow-hidden">
       // {/* Desktop: persistently visible }
        <aside className="hidden lg:block w-72 border-r border-gray-200 bg-white">
          <Sidebar />
        </aside>

        {/* Mobile: toggle drawer }
        <div className="lg:hidden">
          <Drawer>
            <DrawerTrigger asChild>
              <button className="p-4">
                <LucideMenu className="h-6 w-6 text-purdue-black" />
              </button>
            </DrawerTrigger>
            <DrawerContent className="w-64 p-4 bg-white">
              <Sidebar />
            </DrawerContent>
          </Drawer>
        </div>

     //   { Main chat area }
        <main className="flex-1 bg-gray-50 overflow-auto p-4">{children}</main>
      </div>

      <Footer />
    </div>
  );
}
**/
