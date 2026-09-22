import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.blrmap.app',
  appName: 'BLRMap',
  webDir: 'out',
  server: {
    androidScheme: 'http',
    cleartext: true,
  },
};

export default config;
