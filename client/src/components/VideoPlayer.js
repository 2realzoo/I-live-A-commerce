import React, { useRef, useEffect } from 'react';
import Hls from 'hls.js';
import { useApp } from '../AppContext';

const VideoPlayer = ({ 
  autoPlay = true, 
  controls = true, 
  width = '100%', 
  height = 'auto', 
  style = {}, 
}) => {
  const videoRef = useRef(null);
  const { category_map, selectedCategory, selectedChannel } = useApp()

  const src=`http://localhost:1700/streaming/${category_map[selectedCategory]}_${selectedChannel}/${category_map[selectedCategory]}_${selectedChannel}_data/output.m3u8`
  
  useEffect(() => {
    const video = videoRef.current;

    if (!video) return;

    // Hls.js 지원 여부 확인
    if (Hls.isSupported()) {
      const hls = new Hls();

      // HLS 스트림 로드
      hls.loadSource(src);
      hls.attachMedia(video);

      // // 실시간 업데이트를 처리하기 위해 HLS 이벤트 설정
      // hls.on(Hls.Events.MANIFEST_PARSED, () => {
      //   console.log('HLS manifest loaded');
      // });

      hls.on(Hls.Events.ERROR, (event, data) => {
        if (data.fatal) {
          console.error('Fatal HLS error:', data);
          if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
            console.warn('Attempting to recover from network error...');
            hls.startLoad();
          } else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) {
            console.warn('Attempting to recover from media error...');
            hls.recoverMediaError();
          } else {
            console.error('Cannot recover from error, destroying HLS instance.');
            hls.destroy();
          }
        }
      });
      const interval = setInterval(() => {
        hls.startLoad(); // 주기적으로 스트림 로드
      }, 5000); // 5초마다

      return () => {
        // HLS 인스턴스 정리
        clearInterval(interval);
        hls.destroy();
      };
    } 
    // Safari 및 HLS 네이티브 지원
    else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = src;
    } 
    // HLS 미지원 브라우저
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
