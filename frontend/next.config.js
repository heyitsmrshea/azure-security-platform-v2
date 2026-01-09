/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  basePath: process.env.NODE_ENV === 'production' || process.env.GITHUB_ACTIONS ? '/azure-security-platform-v2' : '',
  assetPrefix: process.env.NODE_ENV === 'production' || process.env.GITHUB_ACTIONS ? '/azure-security-platform-v2/' : '',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
}

module.exports = nextConfig
