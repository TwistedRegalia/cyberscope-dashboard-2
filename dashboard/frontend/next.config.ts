import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // Optimalkan barrel import recharts (transform ke impor langsung).
    optimizePackageImports: ["recharts"],
  },
};

export default nextConfig;
