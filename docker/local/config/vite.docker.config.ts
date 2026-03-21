import { defineConfig, mergeConfig } from 'vite';
import baseConfig from './vite.config';

export default mergeConfig(baseConfig, defineConfig({
  server: {
    watch: {
      usePolling: true,
      interval: 1000,
    },
  },
}));
