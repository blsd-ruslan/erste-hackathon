import type { NextConfig } from "next";

module.exports = {
    typescript: {
        // !! WARN !!
        // Dangerously allow production builds to successfully complete even if
        // your project has type errors.
        // !! WARN !!
        ignoreBuildErrors: true,
    },
    distDir: 'build',
}

const nextConfig: NextConfig = {

};

export default nextConfig;
