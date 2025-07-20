import React, { useRef, useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const playerRef = useRef(null);
  const [matchedName, setMatchedName] = useState(null);
  const [videoPlayed, setVideoPlayed] = useState(false);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
      videoRef.current.srcObject = stream;
      videoRef.current.play();
    });
  }, []);

  useEffect(() => {
    if (matchedName && matchedName !== "Unknown") {
      const videoEl = playerRef.current;
      const tryPlay = () => {
        if (videoEl) {
          videoEl.load();
          videoEl.play().catch(err => {
            console.warn("Auto-play blocked or failed:", err);
          });
        }
      };
      setTimeout(tryPlay, 500);
    }
  }, [matchedName]);

  const captureAndSend = async () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL("image/jpeg");

    const res = await axios.post("http://localhost:5000/recognize", { image: imageData });

    if (res.data.status === "success" && !videoPlayed) {
      setMatchedName(res.data.name);
      setVideoPlayed(true);
    } else {
      setMatchedName("Unknown");
    }
  };

  return (
    <div style={{ textAlign: "center", padding: "2rem" }}>
      <h2>Face Recognition App</h2>
      <video ref={videoRef} style={{ width: "400px" }}></video>
      <canvas ref={canvasRef} width="640" height="480" style={{ display: "none" }}></canvas>
      <br />
      <button onClick={captureAndSend}>Scan Face</button>

      {matchedName && (
        <>
          <h3>Matched: {matchedName}</h3>
          {matchedName !== "Unknown" && (
            <video ref={playerRef} width="400" controls>
              <source src={`/videos/${matchedName}_video.mp4`} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          )}
        </>
      )}
    </div>
  );
}

export default App;