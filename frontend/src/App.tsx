import { useState } from 'react'
import VideoPlayer from './components/VideoPlayer'
import PostureAnalysis from './components/PostureAnalysis'
import { analysisApi } from './services/api'
import './App.css'

function App() {
  const [videoUrl, setVideoUrl] = useState<string>('')
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // 공유 상태: 모든 섹션에서 동일한 프레임 상태 사용
  const [sharedCurrentFrame, setSharedCurrentFrame] = useState<number>(0)
  const [sharedIsPlaying, setSharedIsPlaying] = useState<boolean>(false)
  const [sharedPlaySpeed, setSharedPlaySpeed] = useState<number>(1.0)

  const handleAnalyze = async (url: string) => {
    if (!url.trim()) {
      setError('YouTube URL을 입력해주세요')
      return
    }

    try {
      setIsAnalyzing(true)
      setError(null)
      setVideoUrl(url)
      
      const response = await analysisApi.startAnalysis(url)
      setAnalysisId(response.analysis_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || '분석 시작에 실패했습니다')
      console.error('Analysis error:', err)
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>자세 분석 시스템</h1>
        <div className="url-input-container">
          <input
            type="text"
            placeholder="YouTube URL을 입력하세요 (예: https://www.youtube.com/watch?v=VIDEO_ID)"
            value={videoUrl}
            onChange={(e) => {
              setVideoUrl(e.target.value)
              setError(null)
            }}
            className="url-input"
            disabled={isAnalyzing}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isAnalyzing) {
                handleAnalyze(videoUrl)
              }
            }}
          />
          <button 
            onClick={() => handleAnalyze(videoUrl)} 
            className="analyze-button"
            disabled={isAnalyzing || !videoUrl.trim()}
          >
            {isAnalyzing ? '분석 중...' : '분석 시작'}
          </button>
        </div>
        {error && <div className="error-message">{error}</div>}
      </header>
      <main className="main-content">
        {/* 왼쪽 위: 유튜브 영상 */}
        <div className="video-section">
          <VideoPlayer videoUrl={videoUrl} />
        </div>
        {/* 왼쪽 아래: 자세 분석 점수 및 그래프 */}
        <div className="score-section">
          <PostureAnalysis 
            analysisId={analysisId} 
            showOnlyScore={true}
            currentFrame={sharedCurrentFrame}
            setCurrentFrame={setSharedCurrentFrame}
            isPlaying={sharedIsPlaying}
            setIsPlaying={setSharedIsPlaying}
            playSpeed={sharedPlaySpeed}
            setPlaySpeed={setSharedPlaySpeed}
          />
        </div>
        {/* 오른쪽 위: 스켈리톤 프레임 */}
        <div className="skeleton-section">
          <PostureAnalysis 
            analysisId={analysisId} 
            showOnlySkeleton={true}
            currentFrame={sharedCurrentFrame}
            setCurrentFrame={setSharedCurrentFrame}
            isPlaying={sharedIsPlaying}
            setIsPlaying={setSharedIsPlaying}
            playSpeed={sharedPlaySpeed}
            setPlaySpeed={setSharedPlaySpeed}
          />
        </div>
        {/* 오른쪽 아래: 프레임 재생 */}
        <div className="playback-section">
          <PostureAnalysis 
            analysisId={analysisId} 
            showOnlyPlayback={true}
            currentFrame={sharedCurrentFrame}
            setCurrentFrame={setSharedCurrentFrame}
            isPlaying={sharedIsPlaying}
            setIsPlaying={setSharedIsPlaying}
            playSpeed={sharedPlaySpeed}
            setPlaySpeed={setSharedPlaySpeed}
          />
        </div>
      </main>
    </div>
  )
}

export default App
