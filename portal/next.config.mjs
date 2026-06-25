/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async headers() {
    return [
      {
        source: "/chat",
        headers: [
          {
            key: "Content-Security-Policy",
            value: "frame-ancestors 'self' https://kinnaird.edu.pk https://*.kinnaird.edu.pk",
          },
          {
            key: "X-Frame-Options",
            value: "ALLOWALL",
          },
        ],
      },
    ]
  },
}

export default nextConfig
