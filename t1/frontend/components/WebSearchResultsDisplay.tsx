"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ExternalLink, Globe, Calendar, User, Search, TrendingUp } from "lucide-react"
import { motion } from "framer-motion"
import { WebSearchResult, SearchResultItem } from "@/types"

interface WebSearchResultsDisplayProps {
  searchResults: WebSearchResult[]
}

export default function WebSearchResultsDisplay({ searchResults }: WebSearchResultsDisplayProps) {
  if (!searchResults || searchResults.length === 0) {
    return null
  }

  return (
    <div className="space-y-6">
      {searchResults.map((searchResult, sIdx) => (
        <Card key={sIdx} className="overflow-hidden">
          <CardContent className="p-6">
            {/* Search Header */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between mb-6 pb-4 border-b"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/10">
                  <Search className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">"{searchResult.query}"</h3>
                  <p className="text-sm text-muted-foreground">
                    {searchResult.total_results || searchResult.results.length} results found
                  </p>
                </div>
              </div>
              {searchResult.search_type && (
                <Badge variant="secondary" className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  {searchResult.search_type}
                </Badge>
              )}
            </motion.div>

            {/* Search Results Grid */}
            <div className="grid gap-4">
              {searchResult.results.map((result, rIdx) => (
                <motion.div
                  key={rIdx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: rIdx * 0.05 }}
                  className="group"
                >
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block"
                  >
                    <Card className="transition-all duration-200 hover:shadow-lg hover:scale-[1.02] border-2 hover:border-primary/20 overflow-hidden">
                      <CardContent className="p-0">
                        {/* Thumbnail Section */}
                        {result.thumbnail && (
                          <div className="relative h-48 overflow-hidden bg-muted">
                            <img
                              src={result.thumbnail}
                              alt={result.title}
                              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                            <div className="absolute bottom-3 left-3 right-3">
                              <div className="flex items-center gap-2 text-white text-sm">
                                <ExternalLink className="w-4 h-4" />
                                <span className="truncate">{new URL(result.url).hostname}</span>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Content Section */}
                        <div className="p-4">
                          <h4 className="font-semibold text-lg mb-2 text-blue-600 dark:text-blue-400 group-hover:underline line-clamp-2">
                            {result.title}
                          </h4>

                          {/* Meta Information */}
                          <div className="flex flex-wrap items-center gap-3 mb-3 text-xs text-muted-foreground">
                            {result.site_name && (
                              <span className="flex items-center gap-1">
                                <Globe className="w-3 h-3" />
                                {result.site_name}
                              </span>
                            )}
                            {result.published_date && (
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(result.published_date).toLocaleDateString()}
                              </span>
                            )}
                            {result.author && (
                              <span className="flex items-center gap-1">
                                <User className="w-3 h-3" />
                                {result.author}
                              </span>
                            )}
                          </div>

                          {/* Snippet */}
                          <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed">
                            {result.snippet}
                          </p>

                          {/* URL Preview */}
                          <div className="mt-3 pt-3 border-t">
                            <div className="text-xs text-muted-foreground truncate">
                              {result.url}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </a>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
