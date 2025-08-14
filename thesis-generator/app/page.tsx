"use client"

import { useState } from "react"
import { InvestmentReport } from "@/components/investment-report"
import { FileSelector } from "@/components/file-selector"

export default function Home() {
  const [selectedFile, setSelectedFile] = useState("AAPL_Q2_2025_combined_analysis.json")

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-[210mm] mx-auto p-8">
        <FileSelector 
          onFileSelect={setSelectedFile} 
          selectedFile={selectedFile} 
        />
        <InvestmentReport filename={selectedFile} />
      </div>
    </main>
  )
}
