/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",    // Build to web/frontend/out/ — served by FastAPI
  trailingSlash: true, // Generates index.html per route for clean paths
};

export default nextConfig;
