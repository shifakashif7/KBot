"use client"

import Image from "next/image"
import Link from "next/link"
import { motion } from "framer-motion"

export default function TopBar() {
  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="fixed top-0 left-0 right-0 flex items-center justify-between bg-white shadow-md w-full z-50 h-14 px-4 md:px-8"
    >
      <div className="flex items-center gap-2">
        <div className="flex items-center justify-center bg-[#8f0e0e] rounded-full w-10 h-10 overflow-hidden">
          <Image src="/logo.png" alt="KBot Logo" width={30} height={30} className="object-contain" />
        </div>
        <h1 className="text-[#8f0e0e] text-xl font-semibold">
          <Link href="/" className="no-underline hover:text-[#a51212] transition-colors">
            KBot 1.0
          </Link>
        </h1>
      </div>

      <div className="hidden md:flex items-center gap-6">
        <Link href="/welcome" className="text-gray-600 hover:text-[#8f0e0e] transition-colors text-sm font-medium">
          Home
        </Link>
        <Link href="/chat" className="text-gray-600 hover:text-[#8f0e0e] transition-colors text-sm font-medium">
          Chat
        </Link>
      </div>
    </motion.nav>
  )
}
