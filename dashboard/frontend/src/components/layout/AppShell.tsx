import type { ReactNode } from "react";
import { NavBar } from "./NavBar";

/**
 * Cangkang aplikasi: top-bar + kontainer konten ter-center (max-w 1200px).
 * Menyediakan SATU <main> untuk semua halaman — halaman mengembalikan konten saja.
 */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-full flex-col">
      <NavBar />
      <main className="mx-auto w-full max-w-[1200px] flex-1 px-6 py-8 md:py-10">
        {children}
      </main>
    </div>
  );
}
