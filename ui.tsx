"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Paperclip, Send, FileText, X } from "lucide-react"

export default function Component() {
  const [jobDescription, setJobDescription] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [bubbles, setBubbles] = useState<{ id: number; x: number; y: number; size: number }[]>([])

  useEffect(() => {
    const createBubble = () => {
      const newBubble = {
        id: Date.now(),
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 50 + 10,
      }
      setBubbles(prev => [...prev, newBubble])
      setTimeout(() => {
        setBubbles(prev => prev.filter(b => b.id !== newBubble.id))
      }, 8000)
    }

    const interval = setInterval(createBubble, 2000)
    return () => clearInterval(interval)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    console.log("Job Description:", jobDescription)
    console.log("File:", file)
    setIsSubmitting(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-400 to-purple-500 p-6 flex flex-col justify-center relative overflow-hidden">
      {bubbles.map(bubble => (
        <div
          key={bubble.id}
          className="absolute rounded-full bg-white opacity-20"
          style={{
            left: `${bubble.x}%`,
            top: `${bubble.y}%`,
            width: `${bubble.size}px`,
            height: `${bubble.size}px`,
            animation: `float 8s ease-in-out infinite`,
          }}
        />
      ))}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl mx-auto w-full bg-white bg-opacity-90 backdrop-blur-md rounded-xl shadow-lg overflow-hidden z-10"
      >
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">HiredEasy Custom Resume</h1>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700 mb-2">
                Job Description
              </label>
              <motion.div
                initial={false}
                animate={{ height: jobDescription ? "auto" : "56px" }}
                transition={{ duration: 0.3 }}
              >
                <textarea
                  id="jobDescription"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 ease-in-out hover:shadow-md"
                  rows={jobDescription ? 4 : 1}
                  placeholder="Enter job description here..."
                />
              </motion.div>
            </div>
            <div>
              <label htmlFor="resumeUpload" className="block text-sm font-medium text-gray-700 mb-2">
                Upload LaTeX Resume (.tex)
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md transition-all duration-300 ease-in-out hover:border-blue-500 hover:shadow-md">
                <div className="space-y-1 text-center">
                  <AnimatePresence>
                    {!file && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                      >
                        <Paperclip className="mx-auto h-12 w-12 text-gray-400" />
                        <p className="text-xs text-gray-500">
                          Drag and drop your file here, or click to select
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                  <AnimatePresence>
                    {file && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        className="flex items-center justify-center space-x-2"
                      >
                        <FileText className="h-8 w-8 text-blue-500" />
                        <span className="text-sm text-gray-700">{file.name}</span>
                        <button
                          type="button"
                          onClick={() => setFile(null)}
                          className="text-red-500 hover:text-red-700 transition-colors duration-200"
                        >
                          <X className="h-5 w-5" />
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                  <input
                    id="resumeUpload"
                    name="resumeUpload"
                    type="file"
                    accept=".tex"
                    className="sr-only"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <motion.button
                type="submit"
                disabled={isSubmitting}
                className={`px-4 py-2 rounded-md text-white font-medium ${
                  isSubmitting ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'
                } transition-all duration-300 ease-in-out flex items-center space-x-2 hover:shadow-lg`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span>{isSubmitting ? 'Submitting...' : 'Submit'}</span>
                <Send className="h-5 w-5" />
              </motion.button>
            </div>
          </form>
        </div>
      </motion.div>
      <style jsx global>{`
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-20px); }
        }
      `}</style>
    </div>
  )
}