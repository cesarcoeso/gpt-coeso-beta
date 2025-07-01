# main.py - Assistente de Excel para Construção Civil
import streamlit as st
from openai import OpenAI
import time
import re
from config_prompt import SYSTEM_PROMPT
import os

# Configuração para evitar problemas com protobuf
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

# === CONFIGURAÇÃO DA PÁGINA ===
st.set_page_config(
    page_title="Assistente BETA Excel - Coeso Cursos",
    page_icon="https://coesocursos.com.br/wp-content/uploads/2025/05/cropped-favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS EXTERNO E AJUSTES DE LAYOUT ===
with open("custom_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Adicione isto logo após carregar o CSS
st.markdown("""
<style>
    /* Garante que o container principal tenha espaço para o chat */
    .main .block-container {
        padding-bottom: 150px !important;
    }
    
    /* Ajuste extra para o chat input */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 20px !important;
        left: calc(20px + var(--sidebar-width, 336px)) !important;
        right: 20px !important;
        z-index: 9999 !important;
    }
    
    @media (max-width: 1200px) {
        [data-testid="stChatInput"] {
            left: 20px !important;
        }
    }
</style>

<script>
// Garante que o chat input fique visível
function ensureChatInputVisible() {
    const chatInput = document.querySelector('[data-testid="stChatInput"]');
    if (chatInput) {
        chatInput.style.position = 'fixed';
        chatInput.style.bottom = '20px';
        chatInput.style.zIndex = '9999';
    }
}
// Verifica a cada segundo
setInterval(ensureChatInputVisible, 1000);
</script>
""", unsafe_allow_html=True)

# Garante espaço para o chat_input
st.markdown("""
<style>
    .main .block-container {
        padding-bottom: 120px;
    }
</style>
""", unsafe_allow_html=True)

# === INTERFACE PRINCIPAL ===
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Barra lateral com instruções
with st.sidebar:
    # Logo com link clicável
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <a href="https://coesocursos.com.br" target="_blank">
                <img src="https://coesocursos.com.br/wp-content/uploads/2025/05/logo-e1738083192299.png" 
                     width="250" style="display: block; margin: 0 auto;">
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Instruções de uso
    st.markdown("""
    ### ℹ️ Como usar:
    - Pergunte sobre fórmulas, cálculos e planilhas
    - Exemplos:
      - <span class="sidebar-example">Como calcular área de laje?</span>
      - <span class="sidebar-example">Fórmula para previsão de materiais</span>
      - <span class="sidebar-example">Como usar PROCV em orçamentos?</span>
    
    🛠️ **Dicas técnicas:**
    - Todas as fórmulas em português
    - Exemplos práticos incluídos

    📌 **Como usar as fórmulas:**
    - As fórmulas do item **3** da resposta podem ser copiadas direto para o Excel
    - Cole na célula **B4**
    - Preencha os dados em **B2** (diâmetro em metros) e **C2** (altura em metros)
    """, unsafe_allow_html=True)
    
    # Botão de limpar conversa
    st.markdown("""
    <style>
        div.stButton > button {
            background-color: #f2295b;
            color: white;
            border: none;
            width: 100%;
            margin: 1.5rem 0;
            transition: background-color 0.3s;
            border-radius: 8px;
            padding: 0.5rem;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #d11c4a;
        }
    </style>
    <div style="text-align: center;">
    """, unsafe_allow_html=True)
    
    if st.button("🪟 Limpar Conversa"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Área principal do chat
st.title("🏗️ Assistente de Excel para Construção Civil")
st.caption("Obtenha fórmulas prontas para usar em suas planilhas de obra")

# Verificação da API Key
if 'openai' not in st.secrets:
    st.error("API Key não configurada. Verifique o arquivo secrets.toml")
    st.stop()

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Dicionário para formatação das respostas
titles = {
    '1': 'Explicação técnica breve',
    '2': 'Fórmula matemática clara',
    '3': 'Fórmula Excel aplicável',
    '4': 'Exemplo numérico completo'
}

def format_response(text):
    """Formata a resposta do assistente"""
    text = re.sub(r'\{.*?\}', '', text)
    text = re.sub(r'\\[a-z]+', '', text)

    for num, title in titles.items():
        pattern = rf"(?i)\b{num}\s*{title}\b[:：]?\s*|\b{title}\b[:：]?\s*"
        text = re.sub(pattern, '', text)

    sections = re.split(r'(\d+\.)', text)
    formatted_text = ""

    for i in range(1, len(sections), 2):
        section_num = sections[i].replace('.', '')
        section_content = sections[i + 1].strip()

        if section_num in titles:
            formatted_text += f"**{section_num}. {titles[section_num]}**\n\n{section_content}\n\n"

    return formatted_text.strip()

def limit_history(messages, max=10):
    """Limita o histórico de mensagens"""
    return [messages[0]] + messages[-max:] if len(messages) > max + 1 else messages

# Exibe o histórico de mensagens
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

# Processa a entrada do usuário
if prompt := st.chat_input("Digite sua dúvida sobre Excel para construção civil..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages = limit_history(st.session_state.messages)

    with st.chat_message("assistant"):
        try:
            with st.spinner('Processando sua pergunta...'):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.messages,
                    temperature=0.7,
                    max_tokens=600
                )
                content = response.choices[0].message.content
                formatted = format_response(content)
                
                # Exibe com efeito de digitação
                msg_box = st.empty()
                full_resp = ""
                for para in formatted.split('\n\n'):
                    if para.strip():
                        full_resp += para + "\n\n"
                        msg_box.markdown(full_resp + "▌", unsafe_allow_html=True)
                        time.sleep(0.15)
                msg_box.markdown(full_resp, unsafe_allow_html=True)
            
            st.session_state.messages.append({"role": "assistant", "content": formatted})
        except Exception as e:
            err = "⚠️ Ocorreu um erro ao processar sua pergunta. Por favor, tente novamente."
            st.error(err)
            st.session_state.messages.append({"role": "assistant", "content": err})

# Script JavaScript para garantir visibilidade do chat_input
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    function ensureChatInputVisible() {
        const chatInput = document.querySelector('[data-testid="stChatInput"]');
        if (chatInput) {
            chatInput.style.position = 'fixed';
            chatInput.style.bottom = '20px';
            chatInput.style.zIndex = '999';
        }
    }
    ensureChatInputVisible();
    setInterval(ensureChatInputVisible, 1000);
});
</script>
""", unsafe_allow_html=True)