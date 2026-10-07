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
                        st.session_state.file_order[i], st.session_state.file_order[i-1] = st.session_state.file_order[i-1], st.session_state.file_order[i]
                        st.rerun()
                with b2:
                    if st.button("❌", key=f"del_{i}_{name}", use_container_width=True, help=f"Remover {name} da lista"):
                        st.session_state.file_order.pop(i)
                        st.rerun()
                with b3:
                    if st.button("▶", key=f"right_{i}_{name}", use_container_width=True, disabled=(i == len(st.session_state.file_order) - 1)):
                        st.session_state.file_order[i], st.session_state.file_order[i+1] = st.session_state.file_order[i+1], st.session_state.file_order[i]
                        st.rerun()
