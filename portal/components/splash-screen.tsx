"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { motion } from "framer-motion"

export default function SplashScreen() {
  const [isVisible, setIsVisible] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(() => {
        router.push("/welcome")
      }, 600)
    }, 3000)

    return () => clearTimeout(timer)
  }, [router])

  return (
    <div
      className={`fixed top-0 left-0 w-full h-full bg-[#8f0e0e] flex flex-col items-center justify-center transition-all duration-600 ${
        isVisible ? "opacity-100" : "opacity-0"
      }`}
      onClick={() => {
        setIsVisible(false)
        setTimeout(() => {
          router.push("/welcome")
        }, 600)
      }}
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="overflow-hidden rounded-xl shadow-2xl"
      >
        <Image
          src="/logo-name.png"
          alt="KBot Logo"
          width={320}
          height={120}
          className="bg-[#8f0e0e] object-contain p-4"
        />
      </motion.div>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5 }}
        className="text-white mt-6 text-lg font-light"
      >
        Your AI Assistant
      </motion.p>
    </div>
  )
}
