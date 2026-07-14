/** Format angka dengan pemisah ribuan Indonesia (mis. 9212 → "9.212"). */
export function formatNumber(n: number): string {
  return n.toLocaleString("id-ID");
}

/** Format proporsi 0..1 → persen (mis. 0.738 → "73,8%"). */
export function formatPct(fraction: number, digits = 1): string {
  return `${(fraction * 100).toLocaleString("id-ID", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })}%`;
}

/** Format ringkas untuk sumbu chart (mis. 6800 → "6,8rb"). */
export function formatCompact(n: number): string {
  if (n >= 1000) {
    return `${(n / 1000).toLocaleString("id-ID", {
      maximumFractionDigits: 1,
    })}rb`;
  }
  return formatNumber(n);
}
