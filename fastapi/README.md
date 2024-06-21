# Como testar localmente (windows):

> Testado em Python 3.12.4, talvez não funcione em outras versões

### Criar ambiente virtual

* No terminal, dentro da pasta raiz do projeto:
```
python -m venv venv
```
> Se tiver mais de uma versão do python baixada e quiser usar uma específica, talvez seja necessário especificar o caminho dela:

```
caminho\para\python.exe -m venv venv
```

### Ativar ambiente virtual

```
venv\Scripts\activate
```

### Verificar a versão do Python

```
python --version
```

### Instalar as dependências

```
pip install -r requirements.txt
```
> Se a vida for muito injusta e dar erro vai ter que instalar as dependências pelo nome delas:
```
pip install fastapi==0.111.0 numpy==1.26.4 opencv-python==4.10.0.84 pillow==10.3.0 torch==2.3.1 torchvision==0.18.1 uvicorn==0.30.1
```

### Instalando o Dlib separadamente

* Abra *fastapi\Dlib_Windows_Python3.x-main.zip* e extraia o arquivo *.whl* correspondente a sua versão do python para pasta raiz do projeto (o arquivo contendo o número 312 para python 3.12, 311 para python 3.11, etc.)
* Execute o pip install com o caminho do arquivo, ex:
```
pip install dlib-19.24.99-cp312-cp312-win_amd64.whl
```

### Desativando o ambiente no terminal

```
deactivate
```

### Iniciando a API

* Você pode simplesmente abrir o *main.py* no VSCode e clicar em run, mas antes de rodar confira se no canto inferior direito, ao lado de Python, está a sua venv, se não estiver, clique no interpretador atual e insira o caminho para *venv\Scripts\python.exe*

* Também é possível iniciar pelo terminal, executando (substitua o caminho):
```
& caminho/para/pasta-raiz/Deep-Lerning-With-Mobile/venv/Scripts/python.exe caminho/para/pasta-raiz/Deep-Lerning-With-Mobile/fastapi/main.py
```


## Mensagens do WebSocket:

> face não detectada
```json
{
    "status": "indisponivel"
}
```

> olhos abertos
```json
{
    "status": "Awake"
}
```

> face não detectada
```json
{
    "status": "Sleepy"
}
```


