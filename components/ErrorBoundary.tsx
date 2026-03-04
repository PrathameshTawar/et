'use client'

import React, { Component, ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({ error, errorInfo })
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen bg-deep-black flex items-center justify-center p-6 font-mono overflow-hidden relative">
          <div className="absolute inset-0 opacity-10 bg-[linear-gradient(rgba(239,68,68,0.2)_1px,transparent_1px),linear-gradient(90deg,rgba(239,68,68,0.2)_1px,transparent_1px)] bg-[size:20px_20px]" />

          <div className="bg-deep-black/80 backdrop-blur-2xl border border-red-500/20 rounded-xl p-10 max-w-lg w-full text-center relative z-10 shadow-[0_0_50px_rgba(239,68,68,0.05)]">
            <div className="relative inline-block mb-8">
              <AlertTriangle className="h-16 w-16 text-red-500 mx-auto" />
              <div className="absolute inset-0 bg-red-500/20 blur-xl rounded-full animate-pulse" />
            </div>

            <h2 className="text-2xl font-black text-white mb-4 uppercase tracking-[0.2em]">KERNEL_PANIC: EXCEPTION</h2>
            <p className="text-white/40 text-[11px] mb-8 uppercase tracking-widest leading-relaxed">
              Orchestration pipeline encountered a non-recoverable state. System integrity maintained.
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="bg-red-500/5 border border-red-500/10 rounded-lg p-5 mb-8 text-left group">
                <summary className="text-red-500 cursor-pointer mb-3 text-[10px] font-black uppercase tracking-widest group-open:mb-4">DUMP_STACK_TRACE</summary>
                <pre className="text-[9px] text-white/30 overflow-auto max-h-48 custom-scrollbar">
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            <button
              onClick={this.handleReset}
              className="w-full bg-neon-lime text-black px-8 py-4 rounded font-black uppercase tracking-widest text-[10px] transition-all duration-300 flex items-center justify-center space-x-3 shadow-[0_0_30px_rgba(193,255,0,0.2)] hover:shadow-[0_0_50px_rgba(193,255,0,0.4)] hover:scale-[1.02]"
            >
              <RefreshCw className="h-3 w-3" />
              <span>REBOOT_INSTANCE</span>
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook version for functional components
export function useErrorHandler() {
  return (error: Error, errorInfo?: React.ErrorInfo) => {
    console.error('Error caught by useErrorHandler:', error, errorInfo)
    // You could send this to an error reporting service
  }
}