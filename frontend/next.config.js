// frontend/next.config.js

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next 13.5+ 默认启用 App Router，无需再设置 experimental.appDir
  images: {
    unoptimized: true,
  },
  webpack(config) {
    // 1️⃣ 关闭符号链接解析，避免 Windows 下 EISDIR 错误
    config.resolve.symlinks = false;

    // 2️⃣ 原有的 fallback 配置，避免 supports-color 在浏览器端报错
    config.resolve.fallback = {
      ...(config.resolve.fallback || {}),
      'supports-color': false,
    };

    return config;
  },
};

module.exports = nextConfig;
