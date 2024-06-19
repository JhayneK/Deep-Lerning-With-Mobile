import { useEffect, useRef, useState } from 'react';

function App() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [mensagem, setMensagem] = useState<string>('Acordado')

  useEffect(() => {
    // Conecta ao WebSocket
    wsRef.current = new WebSocket('ws://localhost:8000/ws');

    wsRef.current.onopen = () => {
      console.log('Connected to server');
    };

    wsRef.current.onclose = () => {
      console.log('Disconnected from server');
    };
    // Recebe mensagens do WebSocket
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.status){
        case "Awake":
          setMensagem("acordado");
          console.log(data.status)  
          break;
        case "Sleepy":
          setMensagem("dormindo");
          console.log(data.status)  
          break;
        default:
          break;
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
  // Função para enviar imagem ao servidor
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
      </div>
      <h2>{mensagem}</h2>
    </div>
  );
}

export default App;
