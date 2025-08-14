"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, ChevronDown, RefreshCw } from "lucide-react"

interface FileInfo {
  name: string
  filename: string
  ticker: string
  quarter: string
  year: number | null
  analyst: string
  path: string
}

interface FileSelectorProps {
  onFileSelect: (filename: string) => void
  selectedFile: string
}

export function FileSelector({ onFileSelect, selectedFile }: FileSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [availableFiles, setAvailableFiles] = useState<FileInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchFiles = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/files')
      if (!response.ok) {
        throw new Error('Failed to fetch files')
      }
      const data = await response.json()
      setAvailableFiles(data.files || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFiles()
  }, [])

  const selectedFileData = availableFiles.find(file => file.filename === selectedFile) || availableFiles[0]

  if (loading) {
    return (
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <FileText className="h-5 w-5" />
            Select Report File
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <RefreshCw className="h-6 w-6 animate-spin text-gray-500" />
            <span className="ml-2 text-gray-600">Loading available files...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <FileText className="h-5 w-5" />
            Select Report File
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center p-4">
            <p className="text-red-600 mb-2">{error}</p>
            <button
              onClick={fetchFiles}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Retry
            </button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (availableFiles.length === 0) {
    return (
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <FileText className="h-5 w-5" />
            Select Report File
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center p-4">
            <p className="text-gray-600 mb-2">No JSON files found in the data directory.</p>
            <p className="text-sm text-gray-500">Please add JSON files to the public/data folder.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="mb-6">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <FileText className="h-5 w-5" />
          Select Report File
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="w-full flex items-center justify-between p-3 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Badge variant="outline">{selectedFileData?.ticker || 'N/A'}</Badge>
              <span className="font-medium">{selectedFileData?.name || 'Select a file'}</span>
            </div>
            <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>
          
          {isOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
              {availableFiles.map((file) => (
                <button
                  key={file.filename}
                  onClick={() => {
                    onFileSelect(file.filename)
                    setIsOpen(false)
                  }}
                  className={`w-full flex items-center gap-3 p-3 hover:bg-gray-50 transition-colors ${
                    file.filename === selectedFile ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                  }`}
                >
                  <Badge variant="outline">{file.ticker}</Badge>
                  <div className="text-left">
                    <div className="font-medium">{file.name}</div>
                    <div className="text-xs text-gray-500">
                      {file.quarter} {file.year} • {file.analyst}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <p className="text-sm text-gray-600">
            {availableFiles.length} file{availableFiles.length !== 1 ? 's' : ''} available
          </p>
          <button
            onClick={fetchFiles}
            className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
          >
            Refresh
          </button>
        </div>
      </CardContent>
    </Card>
  )
} 