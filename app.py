import streamlit as st
import fitz  # PyMuPDF
from PIL import Image

# Configuração inicial da página (usando layout "wide" para caber a grade melhor)
st.set_page_config(page_title="PDF Merger Turbo", page_icon="🔗", layout="wide")

st.title("🔗 Mesclador de PDFs")
st.markdown("Faça o upload dos seus PDFs, organize a ordem de junção visualmente e baixe a prancha final de forma rápida e segura.")

# --- FUNÇÃO PARA GERAR MINIATURAS COM CACHE ---
# O cache evita que o PDF seja reprocessado toda vez que você clica em um botão
@st.cache_data(show_spinner=False)
def get_pdf_thumbnail(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page = doc.load_page(0) # Pega a primeira página
        # Reduz a resolução para gerar uma miniatura leve (zoom de 20%)
        pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2)) 
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return img
    except Exception:
        return None

# PASSO 1: Upload dos arquivos
uploaded_files = st.file_uploader("📥 PASSO 1: Faça o upload dos PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Inicializa o estado de sessão para manter a memória da ordem dos arquivos
    current_file_names = [f.name for f in uploaded_files]
    
    # Se a ordem ainda não existe ou se houve mudança no upload
    if "file_order" not in st.session_state or set(st.session_state.file_order) != set(current_file_names):
        # Remove arquivos que não estão mais no upload ou adiciona os novos no final
        st.session_state.file_order = [f for f in st.session_state.file_order if f in current_file_names] if "file_order" in st.session_state else []
        for name in current_file_names:
            if name not in st.session_state.file_order:
                st.session_state.file_order.append(name)

    # Dicionário para mapear os nomes na tela para os arquivos reais em memória
    file_dict = {f.name: f for f in uploaded_files}

    st.markdown("---")
    st.subheader("🛠️ PASSO 2: Organize a ordem (Visual)")
    st.markdown("Use as setas abaixo de cada miniatura para mover o arquivo para a esquerda ou direita. **Passe o mouse sobre o nome do arquivo para lê-lo por completo.**")
    
    # Define a quantidade de colunas da grade (ex: 5 por linha, similar ao Adobe)
    num_cols = 5
    cols = st.columns(num_cols)
    
    for i, name in enumerate(st.session_state.file_order):
        col_idx = i % num_cols
        
        with cols[col_idx]:
            # Cria um container visual para cada arquivo
            with st.container(border=True):
                # Obtém e exibe a miniatura
                file_obj = file_dict[name]
                thumb = get_pdf_thumbnail(file_obj.getvalue())
                
                if thumb:
                    st.image(thumb, use_container_width=True)
                else:
                    st.write("📄 Preview indisponível")
                
                # NOME COM TOOLTIP: Encurta o nome visualmente, mas mostra o completo ao passar o mouse
                nome_exibicao = f"**{i+1}º** - {name[:15]}..." if len(name) > 15 else f"**{i+1}º** - {name}"
                
                # O parâmetro 'help' cria o tooltip (balão de texto no hover)
                st.caption(nome_exibicao, help=f"Nome completo: {name}")
                
                # Botões de navegação
                b1, b2, b3 = st.columns([1, 1, 1])
                
                with b1:
                    if st.button("◀", key=f"left_{i}_{name}", use_container_width=True, disabled=(i == 0)):
                        # Troca com o anterior
                        st.session_state.file_order[i], st.session_state.file_order[i-1] = st.session_state.file_order[i-1], st.session_state.file_order[i]
                        st.rerun()
                with b2:
                    if st.button("❌", key=f"del_{i}_{name}", use_container_width=True, help=f"Remover {name} da lista"):
                        st.session_state.file_order.pop(i)
                        st.rerun()
                with b3:
                    if st.button("▶", key=f"right_{i}_{name}", use_container_width=True, disabled=(i == len(st.session_state.file_order) - 1)):
                        # Troca com o próximo
                        st.session_state.file_order[i], st.session_state.file_order[i+1] = st.session_state.file_order[i+1], st.session_state.file_order[i]
                        st.rerun()

    st.markdown("---")
    st.subheader("🔗 PASSO 3: Juntar e Baixar")
    
    # Botão de processamento principal
    if st.button("Gerar PDF Único", type="primary", use_container_width=True):
        if len(st.session_state.file_order) == 0:
            st.warning("⚠️ Adicione pelo menos um PDF para continuar.")
        else:
            with st.spinner("⏳ Processando e unindo pranchas pesadas, aguarde..."):
                try:
                    # Cria um PDF final vazio
                    doc_final = fitz.open()
                    
                    # Vai inserindo cada PDF na ordem selecionada
                    for name in st.session_state.file_order:
                        file_obj = file_dict[name]
                        file_obj.seek(0) # Reinicia o ponteiro de leitura do arquivo
                        
                        # Abre e mescla
                        doc_temp = fitz.open(stream=file_obj.read(), filetype="pdf")
                        doc_final.insert_pdf(doc_temp)
                        doc_temp.close()
                    
                    # Salva o documentaço na memória do Streamlit
                    pdf_bytes = doc_final.write()
                    doc_final.close()
                    
                    st.success("✨ Sucesso Absoluto! Seu PDF está pronto para download.")
                    
                    # Botão nativo de download do Streamlit
                    st.download_button(
                        label="📥 Baixar PDF Final",
                        data=pdf_bytes,
                        file_name="PDF_Final_Unido_Completo.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro ao unir os arquivos: {e}")

st.markdown("atualizado 07/10/2026         by redmargoth")
