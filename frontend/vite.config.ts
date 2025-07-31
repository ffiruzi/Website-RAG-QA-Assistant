import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Disable the HMR overlay to prevent the parsing error messages
    hmr: {
      overlay: false
    }
  },
});