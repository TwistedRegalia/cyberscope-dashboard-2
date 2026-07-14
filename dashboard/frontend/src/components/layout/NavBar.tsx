"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/cn";
import { BrandMark } from "./BrandMark";

const NAV = [
  { href: "/", label: "Monitoring" },
  { href: "/klasifikasi", label: "Klasifikasi" },
] as const;

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(href + "/");
}

/**
 * Top-bar Dub: logo kiri + navigasi. Minimal, hairline border bawah, tanpa shadow.
 * Active state pakai fill lembut + teks charcoal (bukan warna sebagai satu-satunya
 * pembawa makna — aria-current juga di-set).
 */
export function NavBar() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-ash bg-canvas-white">
      <div className="mx-auto flex h-14 w-full max-w-[1200px] items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2" aria-label="Beranda monitoring">
          <BrandMark className="size-6 text-electric-blue" />
          <span className="font-display text-[15px] text-charcoal">
            CyberScope
          </span>
        </Link>

        <nav className="flex items-center gap-1" aria-label="Navigasi utama">
          {NAV.map((item) => {
            const active = isActive(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "rounded-full px-3 py-1.5 text-[14px] font-medium transition-colors",
                  active
                    ? "bg-paper-mist text-charcoal"
                    : "text-fog hover:bg-paper-mist hover:text-charcoal",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
