import React, { useRef, useEffect } from 'react';
import Hls from 'hls.js'


const VideoPlayer = ({ 
    src,
    autoPlay = true,
    controls = true,
    width = '100%',
    height = 'auto',
    style = {},
 }) => {
    const videoRef = useRef(null);
    
    useEffect(() => {
        const video = videoRef.current;
    
        if (!video) return;
    
        // 1) hls.js를 지원하는 브라우저(Chrome, Firefox, Edge 등)
        if (Hls.isSupported()) {
          const hls = new Hls();
    
          hls.loadSource(src);
          hls.attachMedia(video);
    
          // 오류 핸들링 예시
          hls.on(Hls.Events.ERROR, function (event, data) {
            console.error('HLS error', data);
          });
    
          return () => {
            // 언마운트 시 hls 인스턴스 정리
            hls.destroy();
          };
        } 
        // 2) Safari (iOS) 등 HLS 네이티브 지원
        else if (video.canPlayType('application/vnd.apple.mpegurl')) {
          video.src = src;
        } 
        // 3) HLS 미지원 브라우저(아주 구형 등)
        else {
          console.warn('HLS is not supported in this browser.');
        }
      }, [src]);
    
      return (
        <video
          ref={videoRef}
          autoPlay={autoPlay}
          controls={controls}
          style={{ width, height, backgroundColor: '#000', ...style }}
        />
      );
    };

export default VideoPlayer;
