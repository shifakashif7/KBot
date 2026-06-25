"use client";

import Link from "next/link";
import Image from "next/image";
import TopBar from "./top-bar";
import { useEffect, useState } from "react";

import { motion } from "framer-motion";
import { ArrowRight, MessageCircle, ShieldCheck, Headset } from "lucide-react";

export default function WelcomeScreen() {
  const imageUrls = [
    { src: "image 1.png", height: 600, width: 600 },
    { src: "image 2.jpeg", height: 600, width: 600 },
    {
      src: "https://kinnaird.edu.pk/wp-content/uploads/2024/03/Pic-for-Website-7-scaled.jpg",
      height: 551,
      width: 825,
    },
    { src: "image 4.jpeg", height: 600, width: 600 },
    {
      src: "https://kinnaird.edu.pk/wp-content/uploads/2024/06/1Y5A2097-scaled.jpg",
      height: 600,
      width: 600,
    },
  ];
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % imageUrls.length);
    }, 3000); // Change slide every 3 seconds
    return () => clearInterval(interval); // Cleanup on component unmount
  }, [imageUrls.length]);

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <TopBar />

      <div className="w-full relative h-[80vh] overflow-hidden mt-14">
        <div className="absolute inset-0 bg-black/40 z-10" />
        <div
          className="slider w-full h-full flex transition-transform duration-1000 ease-in-out"
          style={{ transform: `translateX(-${currentIndex * 100}%)` }}
        >
          {imageUrls.map((src, index) => (
            <div key={index} className="slide w-full flex-shrink-0 h-full">
              <Image
                src={src}
                alt={`Slide ${index + 1}`}
                width={600}
                height={700}
                className="w-full h-full object-cover"
              />
            </div>
          ))}
        </div>

        {/* <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="absolute top-1/3 left-1/4 transform -translate-x-1/2 -translate-y-1/2 text-center text-white z-20 w-full max-w-xl px-4"
        >
          <h1 className="text-5xl font-bold mb-2 drop-shadow-lg">Welcome To KBot!</h1>
          <p className="mb-8 text-lg text-gray-100">
            Your intelligent assistant for quick and accurate information
          </p>
          <Link
            href="/chat"
            className="group inline-flex items-center gap-2 py-4 px-8 bg-[#8f0e0e] text-white text-xl font-medium rounded-full hover:bg-[#a51212] transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
          >
            Get Started
            <ArrowRight className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" />
          </Link>
        </motion.div> */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="flex flex-col items-center justify-center text-center text-white z-20 w-full max-w-2xl px-4 absolute inset-0"
        >
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 drop-shadow-lg">
            Welcome To KBot!
          </h1>
          <p className="mb-8 text-base sm:text-lg text-gray-100">
            Your intelligent assistant for quick and accurate information
          </p>
          <Link
            href="/chat"
            className="group inline-flex items-center gap-2 py-3 px-6 sm:py-4 sm:px-8 bg-[#8f0e0e] text-white text-lg sm:text-xl font-medium rounded-full hover:bg-[#a51212] transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
          >
            Get Started
            <ArrowRight className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" />
          </Link>
        </motion.div>
      </div>

      <div className="py-16 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <MessageCircle className="w-10 h-10 text-[#8f0e0e]" />,
                title: "Instant Answers",
                description: "Get immediate responses to your questions without waiting",
              },
              {
                icon: <ShieldCheck className="w-10 h-10 text-[#8f0e0e]" />,
                title: "Accurate Information",
                description: "Access verified information about admissions and courses",
              },
              {
                icon: <Headset className="w-10 h-10 text-[#8f0e0e]" />,
                title: "Available 24/7",
                description: "Get help anytime, day or night, whenever you need it",
              },
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow"
              >
                <div className="mb-4 flex justify-center">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2 text-center">{feature.title}</h3>
                <p className="text-gray-600 text-center">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-[#8f0e0e] py-16 px-6 text-white">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.7 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold mb-6">About KBot</h2>
            <p className="text-lg leading-relaxed mb-8">
              Hi I am KBot! I am an AI based application that answers user queries instantly. I
              focus specifically on Kinnaird College for Women University's data and all its areas
              of activity. I am responsible for providing relevant data to stakeholders which is up
              to date and authentic. To ease the difficulty faced by visitors and students, I
              provide a relevant platform to make different processes such as admission, enrollment
              or course registration easy for my users.
            </p>

            <div className="flex justify-center mt-8 space-x-6">
              <a
                href="https://www.linkedin.com/school/kcw-lahore/"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-white/10 p-3 rounded-full hover:bg-white/20 transition-colors"
              >
                <Image src="/linkedin.png" alt="LinkedIn" width={24} height={24} />
              </a>
              <a
                href="https://www.instagram.com/kinnairdcsdept"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-white/10 p-3 rounded-full hover:bg-white/20 transition-colors"
              >
                <Image src="/insta.png" alt="Instagram" width={24} height={24} />
              </a>
              <a
                href="https://www.facebook.com/kcwlhr/"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-white/10 p-3 rounded-full hover:bg-white/20 transition-colors"
              >
                <Image src="/fb.png" alt="Facebook" width={24} height={24} />
              </a>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
