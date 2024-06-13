import { useEffect, useRef, useState } from 'react';

function App() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [mensagem, setMensagem] = useState<string>('Acordado')
  const [image, setImage] = useState<string | undefined >()
  const [video, setVideo] = useState<string | undefined >()

  useEffect(() => {
    // Conecta ao WebSocket
    wsRef.current = new WebSocket('ws://localhost:8000/ws');

    wsRef.current.onopen = () => {
      console.log('Connected to server');
    };

    wsRef.current.onclose = () => {
      console.log('Disconnected from server');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.status){
        case "dormindo":
          setMensagem("Dormindo");
          console.log(data.status)  
          break;
        case "pescando":
          setMensagem("Pescando");
          console.log(data.status)  
          break;
        case "erro":
          setMensagem("Erro");
          console.log(data.status)  
          break;
        default:
          break;
      }
      if(data.processed_image){
        setImage(data.processed_image)
      }
      if(data.eyes_array){
        console.log(data.eyes_array)
      }
      if(data.frame){
        setVideo(data.frame)
      }
    };

    // Captura o feed de vídeo da câmera
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        const canvas = canvasRef.current;
        if (canvas) {
          const context = canvas.getContext('2d');

          setInterval(() => {
            if (videoRef.current && context) {
              context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
              const imageData = canvas.toDataURL('image/png');
              sendImage(imageData);
            }
          }, 1000);  // Envia uma imagem a cada segundo
        }
      })
      .catch((err) => {
        console.error('Error accessing the camera', err);
      });

    return () => {
      // Fechar o WebSocket quando o componente desmontar
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const sendImage = (imageData: string) => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ image: imageData }));
    }
  };

  return (
    <div>
      <h2>Exemplo do websocket</h2>
      <video ref={videoRef} width="320" height="240" autoPlay />
      <div style={{display: 'flex', flexDirection: 'row'}}>
        <canvas ref={canvasRef} width="320" height="240" style={{ display: 'none' }} />
        <img src={"data:image/jpeg;base64,"+video} alt="video processado"></img>
      </div>
      <h2>{mensagem}</h2>
      <img src={"data:image/jpeg;base64,"+image} alt="Olhos"></img>
    </div>
  );
}

export default App;
