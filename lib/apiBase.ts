/**
 * The ONE place the backend address lives (the app and the journey tracker both import it).
 *
 * Set NEXT_PUBLIC_API_BASE in .env BEFORE `npm run build`: Next.js inlines it at build time, so a different value needs a
 * rebuild (and `npx cap sync android` for the APK).
 *   - Phone testing against your PC:  NEXT_PUBLIC_API_BASE=http://192.168.x.x:8000   (PC's Wi-Fi address; phone on the same Wi-Fi)
 *   - Local browser testing:          NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
 * 127.0.0.1 only works in a desktop browser: on a phone it means the phone itself.
 * If unset, the Azure VM below is used (it must run the current backend code to get the routing fixes).
 */
const FALLBACK_API_BASE = 'http://4.193.145.212:8000';

export const API_BASE: string = (process.env.NEXT_PUBLIC_API_BASE || FALLBACK_API_BASE).trim().replace(/\/+$/, '');
