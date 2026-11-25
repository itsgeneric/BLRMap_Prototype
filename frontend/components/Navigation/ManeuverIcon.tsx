'use client';

import React from 'react';
import { ManeuverType } from '@/lib/types';

interface ManeuverIconProps {
  type: ManeuverType;
  size?: number;
  color?: string;
  /** Dimmed colour for the branch NOT taken (forks) */
  mutedColor?: string;
  exit?: number | null;
  className?: string;
}

const STROKE = 3.2;

/** Arrowhead triangle at (x, y) pointing along `deg` (0 = up, clockwise). */
function head(x: number, y: number, deg: number, s = 4.2) {
  const r = (deg * Math.PI) / 180;
  const dx = Math.sin(r);
  const dy = -Math.cos(r);
  const tip = [x + dx * s, y + dy * s];
  const l = [x - dy * s * 0.85, y + dx * s * 0.85];
  const rr = [x + dy * s * 0.85, y - dx * s * 0.85];
  return `${tip[0]},${tip[1]} ${l[0]},${l[1]} ${rr[0]},${rr[1]}`;
}

/** Stem up from the bottom, then a bend of `deg` degrees. */
function bentArrow(deg: number, color: string, len = 7.5) {
  const r = (deg * Math.PI) / 180;
  const ex = 12 + Math.sin(r) * len;
  const ey = 11 - Math.cos(r) * len;
  return (
    <>
      <path
        d={`M12 22 L12 11 L${ex} ${ey}`}
        fill="none"
        stroke={color}
        strokeWidth={STROKE}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polygon points={head(ex, ey, deg)} fill={color} />
    </>
  );
}

export const ManeuverIcon: React.FC<ManeuverIconProps> = ({
  type,
  size = 40,
  color = '#ffffff',
  mutedColor = 'rgba(255,255,255,0.35)',
  exit,
  className,
}) => {
  let body: React.ReactNode;

  switch (type) {
    case 'turn_left':
      body = bentArrow(-90, color);
      break;
    case 'turn_right':
      body = bentArrow(90, color);
      break;
    case 'slight_left':
      body = bentArrow(-45, color);
      break;
    case 'slight_right':
      body = bentArrow(45, color);
      break;
    case 'sharp_left':
      body = bentArrow(-135, color, 6.5);
      break;
    case 'sharp_right':
      body = bentArrow(135, color, 6.5);
      break;
    case 'keep_left':
    case 'keep_right': {
      const left = type === 'keep_left';
      const take = left ? -30 : 30;
      const other = left ? 30 : -30;
      const at = (deg: number) => {
        const r = (deg * Math.PI) / 180;
        return [12 + Math.sin(r) * 8, 12 - Math.cos(r) * 8];
      };
      const [ox, oy] = at(other);
      const [tx, ty] = at(take);
      body = (
        <>
          <path d={`M12 22 L12 13 L${ox} ${oy}`} fill="none" stroke={mutedColor} strokeWidth={STROKE} strokeLinecap="round" strokeLinejoin="round" />
          <path d={`M12 22 L12 13 L${tx} ${ty}`} fill="none" stroke={color} strokeWidth={STROKE} strokeLinecap="round" strokeLinejoin="round" />
          <polygon points={head(tx, ty, take)} fill={color} />
        </>
      );
      break;
    }
    case 'u_turn':
      body = (
        <>
          <path d="M15 22 V10 a4.5 4.5 0 0 0 -9 0 V15" fill="none" stroke={color} strokeWidth={STROKE} strokeLinecap="round" strokeLinejoin="round" />
          <polygon points={head(6, 15.5, 180)} fill={color} />
        </>
      );
      break;
    case 'roundabout': {
      // Ring, entry from the bottom. India drives on the left, so traffic circulates
      // clockwise: 1st exit ≈ left, 2nd ≈ straight on, 3rd ≈ right, 4th ≈ back.
      const n = Math.max(1, exit ?? 2);
      const deg = -90 + (Math.min(n, 4) - 1) * 90;
      const r = (deg * Math.PI) / 180;
      const sx = 12 + Math.sin(r) * 5;
      const sy = 10 - Math.cos(r) * 5;
      const ex = 12 + Math.sin(r) * 10;
      const ey = 10 - Math.cos(r) * 10;
      body = (
        <>
          <circle cx="12" cy="10" r="5" fill="none" stroke={mutedColor} strokeWidth={STROKE - 0.6} />
          <path d={`M12 22 L12 15`} fill="none" stroke={color} strokeWidth={STROKE} strokeLinecap="round" />
          <path d={`M${sx} ${sy} L${ex} ${ey}`} fill="none" stroke={color} strokeWidth={STROKE} strokeLinecap="round" />
          <polygon points={head(ex, ey, deg, 3.8)} fill={color} />
          <text x="12" y="12.4" textAnchor="middle" fontSize="6.5" fontWeight="700" fill={color}>
            {n}
          </text>
        </>
      );
      break;
    }
    case 'arrive':
      body = (
        <>
          <path d="M12 22 s-6-6.2-6-11 a6 6 0 0 1 12 0 c0 4.8-6 11-6 11z" fill={color} />
          <circle cx="12" cy="11" r="2.3" fill="#137333" />
        </>
      );
      break;
    case 'depart':
    case 'straight':
    case 'continue':
    default:
      body = (
        <>
          <path d="M12 22 V6" fill="none" stroke={color} strokeWidth={STROKE} strokeLinecap="round" />
          <polygon points={head(12, 5, 0)} fill={color} />
        </>
      );
  }

  return (
    <svg width={size} height={size} viewBox="0 0 24 24" className={className} aria-hidden="true">
      {body}
    </svg>
  );
};

export default ManeuverIcon;
