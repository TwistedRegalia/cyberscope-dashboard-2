import type { ReactNode } from "react";
import { NavBar } from "./NavBar";

/**
 * Cangkang aplikasi: top-bar + kontainer konten fluid (selebar viewport − padding).
 * Menyediakan SATU <main> untuk semua halaman — halaman mengembalikan konten saja.
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-full flex-col">
      <NavBar />
      <main className="w-full flex-1 px-6 py-8 md:py-10 lg:px-8">
        {children}
      </main>
    </div>
  );
}
