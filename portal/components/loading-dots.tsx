"use client";

import { motion } from "framer-motion";

export default function LoadingDots() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      transition={{ duration: 0.3 }}
      className="flex justify-start items-start ml-12 mt-2 mb-4"
    >
      <div className="flex items-center gap-2 bg-white py-2 px-4 rounded-full shadow-sm border border-gray-100">
        <div className="w-6 h-6 rounded-full bg-[#8f0e0e] flex items-center justify-center shadow-sm">
          <span className="text-white text-xs">K</span>
        </div>
        <div className="loading-dots flex space-x-1">
          <span />
          <span />
          <span />
        </div>
      </div>
    </motion.div>
  );
}
