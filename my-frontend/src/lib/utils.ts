// src/lib/utils.ts

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge and dedupe TailwindCSS classes.
 * Usage: cn("p-4", isActive && "bg-purdue-gold", customClass)
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
