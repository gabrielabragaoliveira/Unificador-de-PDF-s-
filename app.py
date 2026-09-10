import streamlit as st
import fitz  # PyMuPDF
import io

# Configuração inicial da página
st.set_page_config(page_title="PDF Merger Turbo", page_icon="🔗", layout="centered")

st.title("🔗 Mesclador de PDFs Turbo")
st.markdown("Faça o upload dos seus PDFs, organize a ordem de junção e baixe a prancha final de forma rápida e segura.")

# PASSO 1: Upload dos arquivos
uploaded_files = st.file_uploader("📥 PASSO 1: Faça o upload dos PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Inicializa o estado de sessão para manter a memória da ordem dos arquivos
    current_file_names = [f.name for f in uploaded_files]
    
    # Se novos arquivos foram adicionados ou a ordem ainda não foi criada, atualizamos
    if "file_order" not in st.session_state or set(st.session_state.file_order) != set(current_file_names):
        st.session_state.file_order = current_file_names

    # Dicionário para mapear os nomes na tela para os arquivos reais em memória
    file_dict = {f.name: f for f in uploaded_files}

    st.markdown("---")
    st.subheader("🛠️ PASSO 2: Organize a ordem")
    
    # Colunas para a interface de reordenação
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_file = st.selectbox("Selecione um arquivo na lista para mover:", st.session_state.file_order)
        
    with col2:
        st.write("") # Espaçamento para alinhar com a caixa de texto
        st.write("")
        c_up, c_down = st.columns(2)
        
        # Lógica para subir na lista
        if c_up.button("⬆️ Subir", use_container_width=True):
            idx = st.session_state.file_order.index(selected_file)
            if idx > 0:
                st.session_state.file_order[idx], st.session_state.file_order[idx-1] = st.session_state.file_order[idx-1], st.session_state.file_order[idx]
                st.rerun() # Atualiza a tela imediatamente
                
        # Lógica para descer na lista
        if c_down.button("⬇️ Descer", use_container_width=True):
            idx = st.session_state.file_order.index(selected_file)
            if idx < len(st.session_state.file_order) - 1:
                st.session_state.file_order[idx], st.session_state.file_order[idx+1] = st.session_state.file_order[idx+1], st.session_state.file_order[idx]
                st.rerun() # Atualiza a tela imediatamente

    st.markdown("**Ordem que será gerada no PDF Final:**")
    for i, name in enumerate(st.session_state.file_order):
        st.info(f"{i+1}º - {name}")

    st.markdown("---")
    st.subheader("🔗 PASSO 3: Juntar e Baixar")
    
    # Botão de processamento principal
    if st.button("Gerar PDF Único", type="primary", use_container_width=True):
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
