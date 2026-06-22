# Como instalar e rodar o app

## 1. Instale o Python
Baixe em: https://www.python.org/downloads/
- Marque a opção **"Add Python to PATH"** antes de instalar

## 2. Instale as dependências
Abra o PowerShell nesta pasta e rode:
```
pip install -r requirements.txt
```

## 3. Rode o app
```
streamlit run app.py
```
O navegador abre automaticamente em http://localhost:8501

---

## Para hospedar online (grátis no Streamlit Cloud)

1. Crie uma conta em https://github.com e suba esta pasta como repositório
2. Acesse https://share.streamlit.io
3. Conecte o repositório e clique em Deploy
4. O app fica disponível em uma URL pública (ex: brauna-carteiras.streamlit.app)
