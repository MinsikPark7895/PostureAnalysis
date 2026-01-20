import { useEffect, useState } from 'react'
import { analysisApi, type AnalysisStatus, type AnalysisResult } from '../services/api'
import './PostureAnalysis.css'

interface PostureAnalysisProps {
  analysisId: string | null
}

const PostureAnalysis = ({ analysisId }: PostureAnalysisProps) => {
  const [status, setStatus] = useState<AnalysisStatus | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [currentFrame, setCurrentFrame] = useState<number>(0)

  useEffect(() => {
    if (!analysisId) {
      setStatus(null)
      setResult(null)
      return
    }

    // 폴링으로 분석 진행 상황 확인
    const checkStatus = async () => {
      try {
        const statusData = await analysisApi.getAnalysisStatus(analysisId)
        setStatus(statusData)

        // 완료된 경우 결과 조회
        if (statusData.status === 'completed' && !result) {
          try {
            const resultData = await analysisApi.getAnalysisResult(analysisId)
            setResult(resultData)
          } catch (err) {
            console.error('Failed to fetch result:', err)
          }
        }

        // 에러 또는 완료된 경우 폴링 중지
        if (statusData.status === 'error' || statusData.status === 'completed') {
          return false
        }
        return true
      } catch (error) {
        console.error('Analysis status check failed:', error)
        return false
      }
    }

    // 즉시 한 번 확인
    checkStatus()

    // 2초마다 상태 확인 (진행 중일 때만)
    const interval = setInterval(async () => {
      const shouldContinue = await checkStatus()
      if (!shouldContinue) {
        clearInterval(interval)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [analysisId, result])

  const handleFrameChange = (frameNumber: number) => {
    if (result && frameNumber >= 0 && frameNumber < result.frames.length) {
      setCurrentFrame(frameNumber)
    }
  }

  return (
    <div className="posture-analysis">
      <h2>자세 분석 결과</h2>
      
      {!analysisId && (
        <div className="status-message">
          <p>분석을 시작하려면 YouTube URL을 입력하세요</p>
        </div>
      )}

      {status && status.status === 'pending' && (
        <div className="status-message">
          <p>분석 대기 중...</p>
        </div>
      )}

      {status && status.status === 'processing' && (
        <div className="status-message">
          <p>분석 중... {status.progress}%</p>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${status.progress}%` }} 
            />
          </div>
        </div>
      )}

      {status && status.status === 'error' && (
        <div className="status-message error">
          <p>분석 중 오류가 발생했습니다</p>
          {status.error && <p className="error-detail">{status.error}</p>}
        </div>
      )}

      {result && result.status === 'completed' && (
        <div className="analysis-result">
          <div className="score-display">
            <h3>자세 점수</h3>
            <div className="score-value">
              {result.summary.average_score.toFixed(1)}/100
            </div>
            <div className="score-details">
              <div>최고: {result.summary.max_score.toFixed(1)}</div>
              <div>최저: {result.summary.min_score.toFixed(1)}</div>
            </div>
          </div>

          {result.frames.length > 0 && (
            <div className="frame-navigation">
              <h3>프레임 탐색</h3>
              <div className="frame-controls">
                <button
                  onClick={() => handleFrameChange(currentFrame - 1)}
                  disabled={currentFrame === 0}
                >
                  이전
                </button>
                <span>
                  {currentFrame + 1} / {result.frames.length}
                </span>
                <button
                  onClick={() => handleFrameChange(currentFrame + 1)}
                  disabled={currentFrame === result.frames.length - 1}
                >
                  다음
                </button>
              </div>
              <div className="current-frame-score">
                프레임 {currentFrame + 1} 점수: {result.frames[currentFrame].score.toFixed(1)}
              </div>
            </div>
          )}

          <div className="skeleton-display">
            <h3>스켈리톤 데이터</h3>
            <div className="skeleton-info">
              <p>총 {result.summary.total_frames}개 프레임 분석 완료</p>
              <p>관절 데이터는 API를 통해 조회 가능합니다</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PostureAnalysis
