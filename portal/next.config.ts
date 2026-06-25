import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: "/chat",
        headers: [
          {
            key: "Content-Security-Policy",
            value: "frame-ancestors 'self' https://kinnaird.edu.pk https://www.kinnaird.edu.pk",
          },
          {
            key: "X-Frame-Options",
            value: "ALLOW-FROM https://kinnaird.edu.pk",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
