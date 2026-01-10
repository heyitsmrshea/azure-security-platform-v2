/** @type {import('next').NextConfig} */

// Determine build mode from environment
// DOCKER_BUILD=true -> standalone for Docker/Azure deployment
// GITHUB_ACTIONS=true without DOCKER_BUILD -> static export for GitHub Pages
const isDockerBuild = process.env.DOCKER_BUILD === 'true'
const isGitHubPages = process.env.GITHUB_ACTIONS && !isDockerBuild

const nextConfig = {
  reactStrictMode: true,
  
  // Skip lint during build for MVP - fix lint errors incrementally
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // Skip type checking during build for faster iteration
  typescript: {
    ignoreBuildErrors: false, // Keep type errors as blocking
  },
  
  // Output mode:
  // - 'standalone' for Docker/containerized deployment (smaller image)
  // - 'export' for static hosting (GitHub Pages)
  output: isDockerBuild ? 'standalone' : (isGitHubPages ? 'export' : undefined),
  
  // Base path only for GitHub Pages
  basePath: isGitHubPages ? '/azure-security-platform-v2' : '',
  assetPrefix: isGitHubPages ? '/azure-security-platform-v2/' : '',
  
  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },
  
  // Trailing slash for static export compatibility
  trailingSlash: isGitHubPages,
  
  // Environment variables available to client
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  },
  
  // Webpack configuration for production optimizations
  webpack: (config, { isServer }) => {
    // Add any custom webpack config here
    return config
  },
}

module.exports = nextConfig
