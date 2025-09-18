"use client";

import { motion } from "framer-motion";

const blobs = [
  { x: "-10%", y: "-10%", size: 280, color: "from-accent/40 via-accent/10 to-transparent" },
  { x: "80%", y: "0%", size: 340, color: "from-secondary/40 via-secondary/10 to-transparent" },
  { x: "40%", y: "60%", size: 260, color: "from-primary/30 via-primary/10 to-transparent" }
];

export function MotionBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {blobs.map((blob, index) => (
        <motion.span
          key={`${blob.x}-${index}`}
          className={`absolute rounded-full bg-gradient-to-br ${blob.color}`}
          style={{
            left: blob.x,
            top: blob.y,
            width: blob.size,
            height: blob.size,
            filter: "blur(60px)"
          }}
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.35, 0.55, 0.35]
          }}
          transition={{ duration: 12 + index * 3, repeat: Infinity, ease: "easeInOut" }}
        />
      ))}
    </div>
  );
}
