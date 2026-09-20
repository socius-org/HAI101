import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Relative base so the build works both at socius-org.github.io/HAI101/ and on a custom domain.
export default defineConfig({
  plugins: [react()],
  base: './',
});
