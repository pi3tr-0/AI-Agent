"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, DollarSign, Users, BarChart3, MessageSquare } from "lucide-react"
import { useEffect, useState } from "react"

// TypeScript interface for the data structure
interface InvestmentData {
  metadata: {
    analysis_timestamp: string
    analyst_name: string
    original_filename: string
    analysis_version: string
  }
  parsed_content: {
    financialMetrics: {
      ticker: string
      analyst_name: string
      year: number
      quarter: number
      totalrevenue: number
      revenuegrowth: number
      ebitda: number
      ebitdamargins: number
      netincome: number
      profitmargin: number
      operatingmargin: number
      basiceps: number
      sharesoutstanding: number
      dividendrate: number
      dividendyield: number
    }
    analyst: {
      summary: string
      priceTarget: string
      upside: string
      sentiment: string
      catalysts: string
      risks: string
    }
  }
  financial_analysis: {
    company_name: string
    analysis_period: string
    financial_health_score: {
      overall_score: number
      liquidity_score: number
      profitability_score: number
      efficiency_score: number
      growth_score: number
    }
    performance_summary: string
    investment_outlook: string
    risk_assessment: {
      key_risks: string[]
      risk_factors: string[]
    }
  }
  sentiment_analysis: {
    company_name: string
    overall_sentiment: string
    confidence_score: number
    analyst_sentiment: {
      sentiment: string
      confidence: number
    }
    market_sentiment: {
      sentiment: string
      confidence: number
      supporting_quotes: string[]
    }
    key_themes: string[]
  }
  leadership_analysis: {
    company_ticker: string
    company_name: string
    analysis_period: string
    key_trends: Array<{
      trend: string
      trend_direction: string
    }>
    stability_assessment: {
      stability_score: number
      key_risks: string[]
      succession_readiness: string
    }
    overall_impact: string
    investor_implications: string
  }
}

// Helper function to format large numbers to Billions
const formatToBillions = (num: number | null | undefined) => {
  if (num === null || num === undefined || typeof num !== "number") {
    return "N/A"
  }
  return `$${(num / 1000000000).toFixed(1)}B`
}

// Helper function to format percentage
const formatPercentage = (num: number | null | undefined) => {
  if (num === null || num === undefined || typeof num !== "number") {
    return "N/A"
  }
  return `${(num * 100).toFixed(1)}%`
}

// Helper function to format EPS values
const formatEPS = (num: number | null | undefined) => {
  if (num === null || num === undefined || typeof num !== "number") {
    return "N/A"
  }
  return `$${num.toFixed(2)}`
}

// Helper to get Badge variant based on sentiment string
const getSentimentBadgeVariant = (sentiment: string) => {
  switch (sentiment?.toLowerCase()) {
    case "positive":
    case "bullish":
    case "strong": // For succession readiness
      return { className: "bg-green-100 text-green-800" }
    case "negative":
    case "bearish":
      return { className: "bg-red-100 text-red-800" }
    case "neutral":
      return { variant: "secondary" as const }
    default:
      return { variant: "default" as const }
  }
}

interface InvestmentReportProps {
  filename?: string
}

export function InvestmentReport({ filename = "AAPL_Q2_2025_combined_analysis.json" }: InvestmentReportProps) {
  // State for data and loading
  const [reportData, setReportData] = useState<InvestmentData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // useEffect to fetch data from JSON file
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await fetch(`/data/${filename}`)
        if (!response.ok) {
          throw new Error("Failed to fetch investment data")
        }
        const data = await response.json()
        setReportData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [filename])

  // Loading and error states
  if (loading) {
    return (
      <div className="max-w-[210mm] mx-auto p-8 bg-white text-black font-sans text-sm leading-tight">
        <div className="flex items-center justify-center h-64">
          <p className="text-lg text-gray-600">Loading investment report...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-[210mm] mx-auto p-8 bg-white text-black font-sans text-sm leading-tight">
        <div className="flex items-center justify-center h-64">
          <p className="text-lg text-red-600">Error: {error}</p>
        </div>
      </div>
    )
  }

  if (!reportData) {
    return (
      <div className="max-w-[210mm] mx-auto p-8 bg-white text-black font-sans text-sm leading-tight">
        <div className="flex items-center justify-center h-64">
          <p className="text-lg text-gray-600">No data available</p>
        </div>
      </div>
    )
  }

  const { parsed_content, financial_analysis, sentiment_analysis, leadership_analysis, metadata } = reportData

  const { financialMetrics, analyst } = parsed_content
  const { company_name, analysis_period } = financial_analysis

  // Extract Quarter and Year from analysis_period (e.g., "Q2 2025")
  const periodParts = analysis_period.split(" ")
  const quarter = periodParts[0]
  const year = periodParts[1]

  return (
    <div className="max-w-[210mm] mx-auto p-8 bg-white text-black font-sans text-sm leading-tight">
      {/* Header Section */}
      <div className="border-b-2 border-gray-900 pb-4 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{financialMetrics.ticker}</h1>
            <p className="text-lg text-gray-600">{company_name} Investment Thesis</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-600 space-y-1">
              <p>
                <span className="font-semibold">Analyst:</span> {metadata.analyst_name}
              </p>
              <p>
                <span className="font-semibold">Quarter:</span> {quarter}
              </p>
              <p>
                <span className="font-semibold">Year:</span> {year}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Report Summary */}
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <BarChart3 className="h-5 w-5" />
            Report Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{analyst.priceTarget}</p>
              <p className="text-xs text-gray-600">Price Target</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{analyst.upside}</p>
              <p className="text-xs text-gray-600">Upside</p>
            </div>
            <div className="text-center">
              <Badge {...getSentimentBadgeVariant(analyst.sentiment)}>{analyst.sentiment}</Badge>
              <p className="text-xs text-gray-600 mt-1">Sentiment</p>
            </div>
          </div>
          <p className="text-sm leading-relaxed">{analyst.summary}</p>
        </CardContent>
      </Card>

      {/* Financial Analysis */}
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <DollarSign className="h-5 w-5" />
            Financial Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-4 gap-3 text-center">
            <div>
              <p className="text-lg font-bold">{formatToBillions(financialMetrics.totalrevenue)}</p>
              <p className="text-xs text-gray-600">Revenue</p>
            </div>
            <div>
              <p className="text-lg font-bold">
                {financialMetrics.revenuegrowth !== null && financialMetrics.revenuegrowth !== undefined 
                  ? formatPercentage(financialMetrics.revenuegrowth)
                  : <span className="text-gray-400">N/A</span>
                }
              </p>
              <p className="text-xs text-gray-600">Growth</p>
            </div>
            <div>
              <p className="text-lg font-bold">{formatPercentage(financialMetrics.operatingmargin)}</p>
              <p className="text-xs text-gray-600">Op. Margin</p>
            </div>
            <div>
              <p className="text-lg font-bold">{formatEPS(financialMetrics.basiceps)}</p>
              <p className="text-xs text-gray-600">EPS</p>
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="font-semibold text-sm">Performance Summary:</h4>
            <p className="text-xs text-gray-700">{financial_analysis.performance_summary}</p>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-semibold">Financial Health Score:</span>
              <Badge variant="secondary">{financial_analysis.financial_health_score.overall_score}/6.0</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-semibold">Investment Outlook:</span>
              <Badge variant="outline">{financial_analysis.investment_outlook}</Badge>
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="font-semibold text-sm">Key Concerns:</h4>
            <ul className="text-xs space-y-1 text-gray-700">
              {financial_analysis.risk_assessment.key_risks.map((risk, index) => (
                <li key={index} className="flex items-center gap-2">
                  <TrendingDown className="h-3 w-3 text-red-500" />
                  {risk}
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Sentiment Analysis */}
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <MessageSquare className="h-5 w-5" />
            Sentiment Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-sm">Analyst Sentiment</span>
                <Badge {...getSentimentBadgeVariant(sentiment_analysis.analyst_sentiment.sentiment)}>
                  {sentiment_analysis.analyst_sentiment.sentiment}
                </Badge>
              </div>
              <p className="text-xs text-gray-600">
                Confidence: {formatPercentage(sentiment_analysis.analyst_sentiment.confidence)}
              </p>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-sm">Market Sentiment</span>
                <Badge {...getSentimentBadgeVariant(sentiment_analysis.market_sentiment.sentiment)}>
                  {sentiment_analysis.market_sentiment.sentiment}
                </Badge>
              </div>
              <p className="text-xs text-gray-600">
                Confidence: {formatPercentage(sentiment_analysis.market_sentiment.confidence)}
              </p>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-2">Key Themes:</h4>
            <div className="flex flex-wrap gap-1">
              {sentiment_analysis.key_themes.map((theme) => (
                <Badge key={theme} variant="outline" className="text-xs">
                  {theme}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-1">Market Reaction:</h4>
            <p className="text-xs text-gray-700">
              {sentiment_analysis.market_sentiment.supporting_quotes?.[0] || "No specific market reaction found."}
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-sm mb-1">Risk Factors:</h4>
            <ul className="text-xs space-y-1 text-gray-700">
              {financial_analysis.risk_assessment.risk_factors.map((risk, index) => (
                <li key={index} className="flex items-center gap-2">
                  <TrendingDown className="h-3 w-3 text-red-500" />
                  {risk}
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Leadership Analysis */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Users className="h-5 w-5" />
            Leadership Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-sm">Stability Score</span>
                <Badge className="bg-blue-100 text-blue-800">
                  {leadership_analysis.stability_assessment.stability_score}/10
                </Badge>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-sm">Succession Readiness</span>
                <Badge {...getSentimentBadgeVariant(leadership_analysis.stability_assessment.succession_readiness)}>
                  {leadership_analysis.stability_assessment.succession_readiness}
                </Badge>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <h4 className="font-semibold text-sm mb-2">Key Positive Trends:</h4>
              <ul className="text-xs space-y-1 text-gray-700">
                {leadership_analysis.key_trends
                  .filter((trend) => trend.trend_direction === "Positive")
                  .map((trend, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <TrendingUp className="h-3 w-3 text-green-500" />
                      {trend.trend}
                    </li>
                  ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-sm mb-2">Key Risks:</h4>
              <ul className="text-xs space-y-1 text-gray-700">
                {leadership_analysis.stability_assessment.key_risks.map((risk, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <TrendingDown className="h-3 w-3 text-red-500" />
                    {risk}
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-gray-50 p-3 rounded">
              <h4 className="font-semibold text-sm mb-1">Investor Implications:</h4>
              <p className="text-xs text-gray-700">{leadership_analysis.investor_implications}</p>
            </div>

            <div className="bg-gray-50 p-3 rounded">
              <h4 className="font-semibold text-sm mb-1">Overall Impact:</h4>
              <p className="text-xs text-gray-700">
                The overall impact of leadership decisions and stability is considered{" "}
                <span className="font-semibold">{leadership_analysis.overall_impact.toLowerCase()}</span>.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
