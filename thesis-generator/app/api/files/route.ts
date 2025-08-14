import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET() {
  try {
    const dataDir = path.join(process.cwd(), 'public', 'data')
    
    // Check if directory exists
    if (!fs.existsSync(dataDir)) {
      return NextResponse.json({ files: [] })
    }

    // Read all files in the data directory
    const files = fs.readdirSync(dataDir)
    
    // Filter for JSON files and extract metadata
    const jsonFiles = files
      .filter(file => file.endsWith('.json'))
      .map(filename => {
        // Extract company, period, and analyst info from filename
        // Expected format: COMPANY_Q#_YEAR_ANALYST_combined_analysis.json
        const match = filename.match(/^([A-Z]+)_Q(\d+)_(\d{4})_(.+)_combined_analysis\.json$/)
        
        if (match) {
          const [, ticker, quarter, year, analyst] = match
          const analystName = analyst.replace(/_/g, ' ')
          return {
            name: `${ticker} Q${quarter} ${year} - ${analystName}`,
            filename,
            ticker,
            quarter: `Q${quarter}`,
            year: parseInt(year),
            analyst: analystName,
            path: `/data/${filename}`
          }
        } else {
          // Try the old format without analyst name
          const oldMatch = filename.match(/^([A-Z]+)_Q(\d+)_(\d{4})_combined_analysis\.json$/)
          if (oldMatch) {
            const [, ticker, quarter, year] = oldMatch
            return {
              name: `${ticker} Q${quarter} ${year}`,
              filename,
              ticker,
              quarter: `Q${quarter}`,
              year: parseInt(year),
              analyst: 'Unknown',
              path: `/data/${filename}`
            }
          } else {
            // Fallback for files that don't match any expected pattern
            const name = filename.replace('.json', '').replace(/_/g, ' ')
            return {
              name,
              filename,
              ticker: 'N/A',
              quarter: 'N/A',
              year: null,
              analyst: 'Unknown',
              path: `/data/${filename}`
            }
          }
        }
      })
      .sort((a, b) => {
        // Sort by year (descending), then by quarter (descending), then by ticker
        if (a.year && b.year) {
          if (a.year !== b.year) return b.year - a.year
          if (a.quarter !== b.quarter) return b.quarter.localeCompare(a.quarter)
        }
        return a.ticker.localeCompare(b.ticker)
      })

    return NextResponse.json({ files: jsonFiles })
  } catch (error) {
    console.error('Error reading files:', error)
    return NextResponse.json(
      { error: 'Failed to read files' },
      { status: 500 }
    )
  }
} 