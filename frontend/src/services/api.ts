import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface AnalysisRequest {
  youtube_url: string
}

export interface AnalysisResponse {
  analysis_id: string
  status: string
  message: string
}

export interface AnalysisStatus {
  analysis_id: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  progress: number
  youtube_url: string
  created_at: string
  average_score?: number
  min_score?: number
  max_score?: number
  error?: string
}

export interface AnalysisResult {
  analysis_id: string
  status: string
  youtube_url: string
  created_at: string
  completed_at: string
  frames: FrameData[]
  summary: {
    average_score: number
    min_score: number
    max_score: number
    total_frames: number
  }
}

export interface FrameData {
  frame_number: number
  timestamp: number
  score: number
  landmarks: Record<string, {
    x: number
    y: number
    z: number
    visibility: number
  }>
}

export const analysisApi = {
  // 분석 시작
  startAnalysis: async (youtubeUrl: string): Promise<AnalysisResponse> => {
    const response = await apiClient.post<AnalysisResponse>('/api/analyze', {
      youtube_url: youtubeUrl,
    })
    return response.data
  },

  // 분석 상태 조회
  getAnalysisStatus: async (analysisId: string): Promise<AnalysisStatus> => {
    const response = await apiClient.get<AnalysisStatus>(
      `/api/analysis/${analysisId}`
    )
    return response.data
  },

  // 분석 결과 조회
  getAnalysisResult: async (analysisId: string): Promise<AnalysisResult> => {
    const response = await apiClient.get<AnalysisResult>(
      `/api/analysis/${analysisId}/result`
    )
    return response.data
  },

  // 특정 프레임 결과 조회
  getFrameResult: async (
    analysisId: string,
    frameNumber: number
  ): Promise<FrameData> => {
    const response = await apiClient.get<FrameData>(
      `/api/analysis/${analysisId}/frames/${frameNumber}`
    )
    return response.data
  },

  // 모든 분석 목록 조회
  listAnalyses: async (): Promise<AnalysisStatus[]> => {
    const response = await apiClient.get<AnalysisStatus[]>('/api/analyses')
    return response.data
  },

  // 분석 삭제
  deleteAnalysis: async (analysisId: string): Promise<void> => {
    await apiClient.delete(`/api/analysis/${analysisId}`)
  },
}
