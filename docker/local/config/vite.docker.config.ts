import { defineConfig, mergeConfig } from 'vite';
import baseConfig from './vite.config';

export default mergeConfig(baseConfig, defineConfig({
  server: {
    watch: {
      usePolling: true,
      interval: 1000,
    },
  },
  define: {
    'import.meta.env.VITE_APP_TITLE': JSON.stringify(process.env.VITE_APP_TITLE || 'unified-ui'),
    'import.meta.env.VITE_THEME_PRESET': JSON.stringify(process.env.VITE_THEME_PRESET || 'default'),
    'import.meta.env.VITE_BRANDING_SLUG': JSON.stringify(process.env.VITE_BRANDING_SLUG || 'default'),
  },
}));
