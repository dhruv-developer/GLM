"use client"

import { ReactNode } from "react"
import { SidebarNav } from "@/components/sidebar-nav"
import { Header } from "@/components/header"
import { GradientBg } from "@/components/gradient-bg"

interface MainLayoutProps {
  children: ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <GradientBg />
      <SidebarNav />
      <div className="lg:pl-64">
        <Header />
        <main className="container py-8">
          {children}
        </main>
      </div>
    </div>
  )
}
