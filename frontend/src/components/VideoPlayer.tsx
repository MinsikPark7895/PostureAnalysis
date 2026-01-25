import { useEffect, useRef } from 'react'

interface VideoPlayerProps {
  videoUrl: string
}

const VideoPlayer = ({ videoUrl }: VideoPlayerProps) => {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!videoUrl || !containerRef.current) return

    // YouTube URL에서 video ID 추출
    const videoId = extractVideoId(videoUrl)
    if (!videoId) return

    // YouTube IFrame API로 영상 임베드
    const iframe = document.createElement('iframe')
    iframe.src = `https://www.youtube.com/embed/${videoId}`
    iframe.setAttribute('width', '100%')
    iframe.setAttribute('height', '100%')
    iframe.frameBorder = '0'
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture'
    iframe.allowFullscreen = true
    iframe.style.border = 'none'

    containerRef.current.innerHTML = ''
    containerRef.current.appendChild(iframe)
  }, [videoUrl])

  const extractVideoId = (url: string): string | null => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/
    const match = url.match(regExp)
    return match && match[2].length === 11 ? match[2] : null
  }

  return (
    <div className="video-player">
      <div ref={containerRef} className="video-container" />
      {!videoUrl && (
        <div className="placeholder">
          <p>YouTube URL을 입력하고 분석을 시작하세요</p>
        </div>
      )}
    </div>
  )
}

export default VideoPlayer
