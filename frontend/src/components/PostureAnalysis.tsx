import { useEffect, useState, useMemo } from 'react'
import { analysisApi, type AnalysisStatus, type AnalysisResult } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts'
import './PostureAnalysis.css'

interface PostureAnalysisProps {
  analysisId: string | null
  showOnlyScore?: boolean
  showOnlySkeleton?: boolean
  showOnlyPlayback?: boolean
  // 공유 상태 props
  currentFrame?: number
  setCurrentFrame?: (frame: number) => void
  isPlaying?: boolean
  setIsPlaying?: (playing: boolean) => void
  playSpeed?: number
  setPlaySpeed?: (speed: number) => void
}

const PostureAnalysis = ({ 
  analysisId, 
  showOnlyScore = false, 
  showOnlySkeleton = false, 
  showOnlyPlayback = false,
  currentFrame: externalCurrentFrame,
  setCurrentFrame: externalSetCurrentFrame,
  isPlaying: externalIsPlaying,
  setIsPlaying: externalSetIsPlaying,
  playSpeed: externalPlaySpeed,
  setPlaySpeed: externalSetPlaySpeed
}: PostureAnalysisProps) => {
  const [status, setStatus] = useState<AnalysisStatus | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  
  // 외부에서 상태를 제공하면 사용하고, 아니면 내부 상태 사용
  const [internalCurrentFrame, setInternalCurrentFrame] = useState<number>(0)
  const [internalIsPlaying, setInternalIsPlaying] = useState<boolean>(false)
  const [internalPlaySpeed, setInternalPlaySpeed] = useState<number>(1.0)
  
  const currentFrame = externalCurrentFrame !== undefined ? externalCurrentFrame : internalCurrentFrame
  const setCurrentFrame = externalSetCurrentFrame || setInternalCurrentFrame
  const isPlaying = externalIsPlaying !== undefined ? externalIsPlaying : internalIsPlaying
  const setIsPlaying = externalSetIsPlaying || setInternalIsPlaying
  const playSpeed = externalPlaySpeed !== undefined ? externalPlaySpeed : internalPlaySpeed
  const setPlaySpeed = externalSetPlaySpeed || setInternalPlaySpeed

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

  // 그래프 데이터 생성
  const chartData = useMemo(() => {
    if (!result || result.frames.length === 0) return []
    return result.frames.map(frame => ({
      time: frame.timestamp,
      score: frame.score,
      frameNumber: frame.frame_number
    }))
  }, [result])

  // 자동 재생 로직 (재생 컨트롤 섹션에서만 실행)
  useEffect(() => {
    // 재생 컨트롤 섹션이 아니면 실행하지 않음
    if (!showOnlyPlayback) return
    if (!isPlaying || !result || result.frames.length === 0) return

    const interval = setInterval(() => {
      setCurrentFrame(prev => {
        if (prev >= result.frames.length - 1) {
          setIsPlaying(false) // 마지막 프레임에 도달하면 정지
          return prev
        }
        return prev + 1
      })
    }, 1000 / playSpeed) // playSpeed에 따라 간격 조절 (1fps = 1000ms, 2fps = 500ms)

    return () => clearInterval(interval)
  }, [isPlaying, result, playSpeed, showOnlyPlayback, setCurrentFrame, setIsPlaying])

  // 결과가 로드되면 currentFrame 초기화 (재생 컨트롤 섹션에서만 실행)
  useEffect(() => {
    if (result && result.frames.length > 0 && showOnlyPlayback) {
      setCurrentFrame(0)
      setIsPlaying(false)
    }
  }, [result, showOnlyPlayback, setCurrentFrame, setIsPlaying])

  // 그래프 클릭 핸들러
  const handleChartClick = (data: any) => {
    if (!data || !result) return
    const clickedTime = data.activeLabel || data.time
    // 가장 가까운 프레임 찾기
    const closestFrame = result.frames.reduce((closest, frame, index) => {
      const currentDiff = Math.abs(frame.timestamp - clickedTime)
      const closestDiff = Math.abs(result.frames[closest].timestamp - clickedTime)
      return currentDiff < closestDiff ? index : closest
    }, 0)
    setCurrentFrame(closestFrame)
  }

  const togglePlay = () => {
    if (!result || result.frames.length === 0) return
    if (currentFrame >= result.frames.length - 1) {
      // 마지막 프레임이면 처음으로
      setCurrentFrame(0)
    }
    setIsPlaying(!isPlaying)
  }

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFrame = parseInt(e.target.value)
    handleFrameChange(newFrame)
  }

  // 상태 메시지 렌더링 (모든 섹션에서 공통)
  const renderStatusMessage = () => {
    if (!analysisId) {
      return (
        <div className="status-message">
          <p>분석을 시작하려면 YouTube URL을 입력하세요</p>
        </div>
      )
    }

    if (status && status.status === 'pending') {
      return (
        <div className="status-message">
          <p>분석 대기 중...</p>
        </div>
      )
    }

    if (status && status.status === 'processing') {
      return (
        <div className="status-message">
          <p>분석 중... {status.progress}%</p>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${status.progress}%` }} 
            />
          </div>
        </div>
      )
    }

    if (status && status.status === 'error') {
      return (
        <div className="status-message error">
          <p>분석 중 오류가 발생했습니다</p>
          {status.error && <p className="error-detail">{status.error}</p>}
        </div>
      )
    }

    return null
  }

  // 점수 섹션만 렌더링
  if (showOnlyScore) {
    return (
      <div className="posture-analysis">
        {renderStatusMessage()}
        {result && result.status === 'completed' && (
          <>
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
              <div className="score-chart-container">
                <h3>시간에 따른 자세 점수</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart
                    data={chartData}
                    onClick={handleChartClick}
                    style={{ cursor: 'pointer' }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                    <XAxis 
                      dataKey="time" 
                      label={{ value: '시간 (초)', position: 'insideBottom', offset: -5 }}
                      stroke="#aaa"
                    />
                    <YAxis 
                      label={{ value: '점수', angle: -90, position: 'insideLeft' }}
                      domain={[0, 100]}
                      stroke="#aaa"
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#2a2a2a', border: '1px solid #444' }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="score" 
                      stroke="#646cff" 
                      strokeWidth={2}
                      dot={{ r: 3, fill: '#646cff' }}
                      activeDot={{ r: 6 }}
                    />
                    <ReferenceLine 
                      x={result.frames[currentFrame]?.timestamp} 
                      stroke="#ff6b6b" 
                      strokeWidth={2}
                      strokeDasharray="5 5"
                    />
                  </LineChart>
                </ResponsiveContainer>
                <p className="chart-hint">그래프를 클릭하면 해당 시점으로 이동합니다</p>
              </div>
            )}
          </>
        )}
      </div>
    )
  }

  // 스켈리톤 섹션만 렌더링
  if (showOnlySkeleton) {
    return (
      <div className="posture-analysis">
        {renderStatusMessage()}
        {result && result.status === 'completed' && result.frames.length > 0 && (
          <div className="skeleton-display">
            <h3>스켈리톤 프레임</h3>
            <div className="skeleton-frame-viewer">
              {result.frames[currentFrame]?.image ? (
                <img
                  src={result.frames[currentFrame].image}
                  alt={`Frame ${currentFrame + 1} skeleton`}
                  className="skeleton-image"
                />
              ) : (
                <p>이 프레임에는 스켈리톤 이미지가 없습니다.</p>
              )}
            </div>
            <div className="skeleton-info">
              <p>총 {result.summary.total_frames}개 프레임 분석 완료</p>
            </div>
          </div>
        )}
      </div>
    )
  }

  // 재생 컨트롤 섹션만 렌더링
  if (showOnlyPlayback) {
    return (
      <div className="posture-analysis">
        {renderStatusMessage()}
        {result && result.status === 'completed' && result.frames.length > 0 && (
          <div className="playback-controls">
            <h3>프레임 재생</h3>
            <div className="playback-buttons">
              <button
                onClick={() => handleFrameChange(0)}
                disabled={currentFrame === 0}
                className="control-button"
              >
                ⏮ 처음
              </button>
              <button
                onClick={() => handleFrameChange(currentFrame - 1)}
                disabled={currentFrame === 0}
                className="control-button"
              >
                ⏪ 이전
              </button>
              <button
                onClick={togglePlay}
                className="control-button play-button"
              >
                {isPlaying ? '⏸ 일시정지' : '▶ 재생'}
              </button>
              <button
                onClick={() => handleFrameChange(currentFrame + 1)}
                disabled={currentFrame === result.frames.length - 1}
                className="control-button"
              >
                다음 ⏩
              </button>
              <button
                onClick={() => handleFrameChange(result.frames.length - 1)}
                disabled={currentFrame === result.frames.length - 1}
                className="control-button"
              >
                끝 ⏭
              </button>
            </div>
            <div className="playback-speed">
              <label>재생 속도:</label>
              <select
                value={playSpeed}
                onChange={(e) => setPlaySpeed(parseFloat(e.target.value))}
                disabled={isPlaying}
              >
                <option value={0.5}>0.5x</option>
                <option value={1.0}>1x</option>
                <option value={2.0}>2x</option>
                <option value={4.0}>4x</option>
              </select>
            </div>
            <div className="frame-slider-container">
              <input
                type="range"
                min="0"
                max={result.frames.length - 1}
                value={currentFrame}
                onChange={handleSliderChange}
                className="frame-slider"
              />
              <div className="slider-labels">
                <span>0초</span>
                <span>{result.frames[result.frames.length - 1]?.timestamp || 0}초</span>
              </div>
            </div>
            <div className="current-frame-info">
              <span>프레임 {currentFrame + 1} / {result.frames.length}</span>
              <span>시간: {result.frames[currentFrame]?.timestamp || 0}초</span>
              <span>점수: {result.frames[currentFrame]?.score.toFixed(1) || 0}</span>
            </div>
          </div>
        )}
      </div>
    )
  }

  // 기본 렌더링 (모든 섹션)
  return (
    <div className="posture-analysis">
      <h2>자세 분석 결과</h2>
      {renderStatusMessage()}
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
            <>
              {/* 점수 그래프 */}
              <div className="score-chart-container">
                <h3>시간에 따른 자세 점수</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart
                    data={chartData}
                    onClick={handleChartClick}
                    style={{ cursor: 'pointer' }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                    <XAxis 
                      dataKey="time" 
                      label={{ value: '시간 (초)', position: 'insideBottom', offset: -5 }}
                      stroke="#aaa"
                    />
                    <YAxis 
                      label={{ value: '점수', angle: -90, position: 'insideLeft' }}
                      domain={[0, 100]}
                      stroke="#aaa"
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#2a2a2a', border: '1px solid #444' }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="score" 
                      stroke="#646cff" 
                      strokeWidth={2}
                      dot={{ r: 3, fill: '#646cff' }}
                      activeDot={{ r: 6 }}
                    />
                    <ReferenceLine 
                      x={result.frames[currentFrame]?.timestamp} 
                      stroke="#ff6b6b" 
                      strokeWidth={2}
                      strokeDasharray="5 5"
                    />
                  </LineChart>
                </ResponsiveContainer>
                <p className="chart-hint">그래프를 클릭하면 해당 시점으로 이동합니다</p>
              </div>

              {/* 재생 컨트롤 */}
              <div className="playback-controls">
                <h3>프레임 재생</h3>
                <div className="playback-buttons">
                  <button
                    onClick={() => handleFrameChange(0)}
                    disabled={currentFrame === 0}
                    className="control-button"
                  >
                    ⏮ 처음
                  </button>
                  <button
                    onClick={() => handleFrameChange(currentFrame - 1)}
                    disabled={currentFrame === 0}
                    className="control-button"
                  >
                    ⏪ 이전
                  </button>
                  <button
                    onClick={togglePlay}
                    className="control-button play-button"
                  >
                    {isPlaying ? '⏸ 일시정지' : '▶ 재생'}
                  </button>
                  <button
                    onClick={() => handleFrameChange(currentFrame + 1)}
                    disabled={currentFrame === result.frames.length - 1}
                    className="control-button"
                  >
                    다음 ⏩
                  </button>
                  <button
                    onClick={() => handleFrameChange(result.frames.length - 1)}
                    disabled={currentFrame === result.frames.length - 1}
                    className="control-button"
                  >
                    끝 ⏭
                  </button>
                </div>
                <div className="playback-speed">
                  <label>재생 속도:</label>
                  <select
                    value={playSpeed}
                    onChange={(e) => setPlaySpeed(parseFloat(e.target.value))}
                    disabled={isPlaying}
                  >
                    <option value={0.5}>0.5x</option>
                    <option value={1.0}>1x</option>
                    <option value={2.0}>2x</option>
                    <option value={4.0}>4x</option>
                  </select>
                </div>
                <div className="frame-slider-container">
                  <input
                    type="range"
                    min="0"
                    max={result.frames.length - 1}
                    value={currentFrame}
                    onChange={handleSliderChange}
                    className="frame-slider"
                  />
                  <div className="slider-labels">
                    <span>0초</span>
                    <span>{result.frames[result.frames.length - 1]?.timestamp || 0}초</span>
                  </div>
                </div>
                <div className="current-frame-info">
                  <span>프레임 {currentFrame + 1} / {result.frames.length}</span>
                  <span>시간: {result.frames[currentFrame]?.timestamp || 0}초</span>
                  <span>점수: {result.frames[currentFrame]?.score.toFixed(1) || 0}</span>
                </div>
              </div>

              {/* 스켈리톤 프레임 표시 */}
              <div className="skeleton-display">
                <h3>스켈리톤 프레임</h3>
                <div className="skeleton-frame-viewer">
                  {result.frames[currentFrame]?.image ? (
                    <img
                      src={result.frames[currentFrame].image}
                      alt={`Frame ${currentFrame + 1} skeleton`}
                      className="skeleton-image"
                    />
                  ) : (
                    <p>이 프레임에는 스켈리톤 이미지가 없습니다.</p>
                  )}
                </div>
                <div className="skeleton-info">
                  <p>총 {result.summary.total_frames}개 프레임 분석 완료</p>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default PostureAnalysis
