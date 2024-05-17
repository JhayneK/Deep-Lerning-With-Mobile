let detectEyes = false; 

// Função do botão
function switchDetection() {
    detectEyes = !detectEyes; 
}

// Função do opencv 
function openCvReady() {
    cv['onRuntimeInitialized'] = () => {
        // Pegando elemento da câmera
        let video = document.getElementById("cam"); 
        
        // Ativando a webcam (substituir pela câmera do dispositivo)
        navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
        })
        .catch(function(err) {
            console.log("An error occurred! " + err);
        });

        // Objeto pra guardar o video de origem e o video de saída
        let src = new cv.Mat(video.height, video.width, cv.CV_8UC4);
        let frame = new cv.Mat(video.height, video.width, cv.CV_8UC1);

        // Objeto para guardar o vídeo em escala de cinza 
        let gray = new cv.Mat();

        // Captura de vídeo usando o elemento da câmera
        let cap = new cv.VideoCapture(cam);

        // Vetor dos olhos
        let eyes = new cv.RectVector();
        let face = new cv.RectVector();

        // Objetos de classificação
        let eyeClassifier = new cv.CascadeClassifier();
        let faceClassifier = new cv.CascadeClassifier();

        // Função para conseguir rodar o haarcascade no javascript
        const createFileFromUrl = (path, url, callback) => {
            let request = new XMLHttpRequest();
            request.open('GET', url, true);
            request.responseType = 'arraybuffer';
            request.onload = () => {
                if (request.readyState === 4) {
                    if (request.status === 200) {
                        let data = new Uint8Array(request.response);
                        cv.FS_createDataFile('/', path, data, true, false, false);
                        callback();
                    } else {
                        console.log('Erro ao carregar ' + url + ' status: ' + request.status);
                    }
                }
            };
            request.send();
        };

        // Path dos arquivos haar cascade
        let eyeCascadeFile = 'haarcascade_eye_tree_eyeglasses.xml'; 
        let faceCascadeFile = 'haarcascade_frontalface_alt2.xml'; 
        
        // Dando load dos arquivos nos objetos de classificação
        createFileFromUrl(eyeCascadeFile, eyeCascadeFile, () => {
            eyeClassifier.load(eyeCascadeFile);
        });
        createFileFromUrl(faceCascadeFile, faceCascadeFile, () => {
            faceClassifier.load(faceCascadeFile);
        });

        // Frames por segundo do processamento video
        const FPS = 15;

        // Array para guardar a posição dos olhos para detecção de quando abaixa a cabeça
        let y_array = new Array(42).fill(0);

        // Variável para salvar quando está pescando
        let pescando = false;

        // Contagem de verificação de quantos valores foram inseridos na array de posição
        let count = 0;

        // Inicializando o tamanho do rosto para salvar em eventuais falhas na detecção
        let face_height

        // Função de processamento do vídeo
        function processVideo() {
            let begin = Date.now();
            cap.read(src);
            src.copyTo(frame);
            cv.cvtColor(frame, gray, cv.COLOR_RGBA2GRAY, 0);

            // Verifica se foi iniciado
            if (detectEyes){
                try {
                    // Tamanho mínimo da face e detecção
                    let minsize_face = new cv.Size(30, 30);
                    faceClassifier.detectMultiScale(gray, face, 1.1, 6, 0, minsize_face);
                    
                    // Salvando tamanho da face
                    try{
                        let face_ = face.get(0);
                        face_height = face_.height;
                    }catch{}
                    
                    // Tamanho mínimo e máximo dos olhos com base no da face para evitar falsos positivos e falsos negativos em piscadas
                    let minsize_eyes = new cv.Size(face_height/5, face_height/5);
                    let maxsize_eyes = new cv.Size(face_height/3.5, face_height/3.5);
                    // Detecção dos olhos
                    eyeClassifier.detectMultiScale(gray, eyes, 1.1, 6, 0, minsize_eyes, maxsize_eyes);

                    // Dando display de retângulo ao redor dos olhos
                    for (let i = 0; i < Math.min(2, eyes.size()); ++i) {
                        let eye = eyes.get(i);
                        let edge1 = new cv.Point(eye.x, eye.y);
                        let edge2 = new cv.Point(eye.x + eye.width, eye.y + eye.height);
                        cv.rectangle(frame, edge1, edge2, [0, 255, 0, 255]);

                        // Atualizando array de posições
                        if(count === y_array.length && !pescando){
                            y_array = [...y_array.slice(1), y_array[0]];
                            y_array[y_array.length -1] = eye.y;
                        }else{
                            y_array[count] = eye.y;
                            count++;
                        }
                    }
                    // Última posição
                    console.log(y_array[y_array.length -1])
                    // Detectando se está pescando e dando display de texto
                    if (y_array[y_array.length - 1] - (face_height * 0.5) > y_array[0]){
                        console.log('ta pescando')
                        pescando = true
                        cv.putText(
                            frame, 
                            "ta pescando", 
                            {x:100,y:100}, 
                            cv.FONT_HERSHEY_PLAIN, 
                            2.3, 
                            [0, 255, 0, 255], 
                            2, 
                            cv.LINE_AA)
                    }
                
                } catch (err) {
                    console.log(err);
                }
            }
            
            // Passar pro canvas
            cv.imshow("canvas_output", frame);

            // Agendar próxima execução.
            let delay = 1000 / FPS - (Date.now() - begin);
            setTimeout(processVideo, delay);
        }


        // Executar.
        setTimeout(processVideo, 0);
    };
}
