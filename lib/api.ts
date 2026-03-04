/**
 * API client with error handling and retry logic
 * Centralized HTTP client for SatyaSetu frontend
 */

interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

interface VoiceProcessResponse {
  success: boolean
  transcribed_text?: string
  intent?: string
  response: string
  audio_url?: string
  verdict?: string
  risk_level?: string
  risk_flags?: string[]
  sources?: any[]
  confidence_score?: number
  processing_time: number
  error?: string
}

interface SystemStats {
  uptime: string
  total_requests: number
  active_connections: number
  recent_events: any[]
  ai_pipeline_stats: any
}

class ApiClient {
  private baseUrl: string
  private wsUrl: string
  
  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    this.wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
  }

  private async fetchWithRetry(
    url: string, 
    options: RequestInit = {}, 
    retries: number = 3
  ): Promise<Response> {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        })
        
        if (response.ok) {
          return response
        }
        
        // Don't retry on client errors (4xx)
        if (response.status >= 400 && response.status < 500) {
          throw new Error(`Client error: ${response.status} ${response.statusText}`)
        }
        
        // Retry on server errors (5xx) or network issues
        if (i === retries - 1) {
          throw new Error(`Server error: ${response.status} ${response.statusText}`)
        }
        
        // Wait before retry (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000))
        
      } catch (error) {
        if (i === retries - 1) {
          throw error
        }
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000))
      }
    }
    
    throw new Error('Max retries exceeded')
  }

  async processText(text: string, userId: string = 'anonymous', language: string = 'hi'): Promise<VoiceProcessResponse> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/voice/process-text`, {
        method: 'POST',
        body: JSON.stringify({
          text: text.trim(),
          user_id: userId,
          language: language
        })
      })
      
      return await response.json()
    } catch (error) {
      console.error('Text processing error:', error)
      return {
        success: false,
        response: '',
        processing_time: 0,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  }

  async processAudio(audioFile: File, userId: string = 'anonymous'): Promise<VoiceProcessResponse> {
    try {
      const formData = new FormData()
      formData.append('audio', audioFile)
      formData.append('user_id', userId)
      
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/voice/process-audio`, {
        method: 'POST',
        headers: {
          // Don't set Content-Type for FormData
        },
        body: formData
      })
      
      return await response.json()
    } catch (error) {
      console.error('Audio processing error:', error)
      return {
        success: false,
        response: '',
        processing_time: 0,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  }

  async processImage(imageFile: File, userId: string = 'anonymous'): Promise<VoiceProcessResponse> {
    try {
      const formData = new FormData()
      formData.append('image', imageFile)
      formData.append('user_id', userId)
      
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/voice/process-image`, {
        method: 'POST',
        headers: {
          // Don't set Content-Type for FormData
        },
        body: formData
      })
      
      return await response.json()
    } catch (error) {
      console.error('Image processing error:', error)
      return {
        success: false,
        response: '',
        processing_time: 0,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  }

  async getSystemStats(): Promise<SystemStats | null> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/admin/stats`)
      return await response.json()
    } catch (error) {
      console.error('Failed to fetch system stats:', error)
      return null
    }
  }

  async getPipelineStatus(): Promise<any> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/admin/pipeline-status`)
      return await response.json()
    } catch (error) {
      console.error('Failed to fetch pipeline status:', error)
      return null
    }
  }

  async triggerTestEvent(): Promise<boolean> {
    try {
      await this.fetchWithRetry(`${this.baseUrl}/api/admin/trigger-test-event`, {
        method: 'POST'
      })
      return true
    } catch (error) {
      console.error('Failed to trigger test event:', error)
      return false
    }
  }

  createWebSocket(path: string = '/ws/telemetry'): WebSocket {
    return new WebSocket(`${this.wsUrl}${path}`)
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/`, { 
        method: 'GET',
        signal: AbortSignal.timeout(5000) // 5 second timeout
      })
      return response.ok
    } catch (error) {
      console.error('Health check failed:', error)
      return false
    }
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
export type { VoiceProcessResponse, SystemStats }