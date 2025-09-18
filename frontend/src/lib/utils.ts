import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export async function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export const STREAMING_INTERVAL = 110;

export function formatNumber(value: number) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 1,
    notation: value >= 1000 ? "compact" : "standard"
  }).format(value);
}

export function formatDuration(ms: number) {
  const seconds = Math.round(ms / 100) / 10;
  if (seconds < 1) {
    return `${Math.round(ms)} ms`;
  }

  return `${seconds.toFixed(seconds >= 10 ? 0 : 1)} s`;
}

export function formatRelativeTime(timestamp: number) {
  const diff = Date.now() - timestamp;
  if (diff < 45_000) {
    return "just now";
  }
  if (diff < 90_000) {
    return "1 min ago";
  }
  const minutes = Math.round(diff / 60_000);
  if (minutes < 60) {
    return `${minutes} min ago`;
  }
  const hours = Math.round(minutes / 60);
  if (hours < 24) {
    return `${hours} hr${hours > 1 ? "s" : ""} ago`;
  }
  const days = Math.round(hours / 24);
  return `${days} day${days > 1 ? "s" : ""} ago`;
}
