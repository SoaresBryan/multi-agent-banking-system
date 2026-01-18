"""Interface de chat simples com Streamlit."""

import os
import sys
import warnings
from pathlib import Path

# Desabilitar telemetria do CrewAI (evita warnings de signal handler)
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

# Suprimir warnings desnecessarios
warnings.filterwarnings("ignore", category=UserWarning)

# Adicionar raiz do projeto ao path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

import asyncio

import pandas as pd
import streamlit as st

from app.agents import AgentOrchestrator
from app.agents.tools.context import reset_contexto, set_contexto
from app.services import ClienteService, SolicitacaoService

st.set_page_config(
    page_title="Banco Agil - Atendimento",
    page_icon="🏦",
    layout="wide",
)

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = AgentOrchestrator()
    st.session_state.orchestrator.registrar_todos_agentes()
    set_contexto(st.session_state.orchestrator.contexto)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "chat"


def reset_session():
    """Reseta a sessao e inicia novo atendimento."""
    st.session_state.orchestrator.resetar()
    st.session_state.orchestrator.registrar_todos_agentes()
    set_contexto(st.session_state.orchestrator.contexto)
    reset_contexto()
    st.session_state.messages = []


with st.sidebar:
    st.title("🏦 Banco Agil")
    st.caption("Sistema de Atendimento Inteligente")
    st.divider()

    st.subheader("Menu")

    if st.button("💬 Chat com Agente", width="stretch", type="primary" if st.session_state.pagina_atual == "chat" else "secondary"):
        st.session_state.pagina_atual = "chat"
        st.rerun()

    if st.button("➕ Adicionar Cliente", width="stretch", type="primary" if st.session_state.pagina_atual == "adicionar_cliente" else "secondary"):
        st.session_state.pagina_atual = "adicionar_cliente"
        st.rerun()

    if st.button("👥 Listar Clientes", width="stretch", type="primary" if st.session_state.pagina_atual == "listar_clientes" else "secondary"):
        st.session_state.pagina_atual = "listar_clientes"
        st.rerun()

    if st.button("📋 Solicitações de Limite", width="stretch", type="primary" if st.session_state.pagina_atual == "solicitacoes" else "secondary"):
        st.session_state.pagina_atual = "solicitacoes"
        st.rerun()

    st.divider()

    if st.session_state.pagina_atual == "chat":
        st.subheader("Informacoes do Chat")
        estado = st.session_state.orchestrator.get_estado()

        if estado["atendimento_encerrado"]:
            st.error("Atendimento encerrado")
        else:
            st.success("Atendimento em andamento")

        agente_nomes = {
            "triagem": "Agente de Triagem",
            "credito": "Agente de Credito",
            "entrevista": "Agente de Entrevista",
            "cambio": "Agente de Cambio",
        }
        st.info(f"Agente: {agente_nomes.get(estado['agente_atual'], estado['agente_atual'])}")

        if estado["cliente_autenticado"]:
            st.success(f"Cliente: {estado['nome_cliente']}")
        else:
            st.warning("Cliente nao autenticado")

        st.divider()

        if st.button("Novo Atendimento", width="stretch"):
            reset_session()
            st.rerun()


if st.session_state.pagina_atual == "chat":
    st.title("Chat com Agente")
    st.caption("Converse com nosso assistente inteligente")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Digite sua mensagem..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(
                        st.session_state.orchestrator.processar_mensagem(prompt)
                    )
                finally:
                    loop.close()

                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


elif st.session_state.pagina_atual == "adicionar_cliente":
    st.title("Adicionar Novo Cliente")
    st.caption("Cadastre um novo cliente no sistema")

    with st.form("form_adicionar_cliente"):
        col1, col2 = st.columns(2)

        with col1:
            cpf = st.text_input("CPF", placeholder="00000000000", help="Apenas numeros")
            nome = st.text_input("Nome Completo", placeholder="João Silva")

        with col2:
            data_nascimento = st.text_input(
                "Data de Nascimento",
                placeholder="DD/MM/AAAA ou AAAA-MM-DD",
                help="Formatos aceitos: DD/MM/AAAA ou AAAA-MM-DD"
            )
            score = st.number_input("Score", min_value=0, max_value=1000, value=500, step=1)

        st.divider()

        cliente_service = ClienteService()
        limite_calculado = cliente_service.calcular_limite_por_score(score)
        st.info(f"Limite calculado baseado no score {score}: R$ {limite_calculado:,.2f}")

        submitted = st.form_submit_button("Adicionar Cliente", width="stretch")

        if submitted:
            if not cpf or not nome or not data_nascimento:
                st.error("Por favor, preencha todos os campos obrigatórios.")
            else:
                cpf_limpo = cpf.replace(".", "").replace("-", "").strip()
                if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
                    st.error("CPF inválido. O CPF deve conter exatamente 11 dígitos numéricos.")
                else:
                    from datetime import datetime
                    data_valida = False
                    try:
                        data_obj = datetime.strptime(data_nascimento.strip(), "%d/%m/%Y")
                        data_valida = True
                    except ValueError:
                        try:
                            data_obj = datetime.strptime(data_nascimento.strip(), "%Y-%m-%d")
                            data_valida = True
                        except ValueError:
                            st.error("Formato de data inválido. Use DD/MM/AAAA ou AAAA-MM-DD")

                    if data_valida:
                        if data_obj.year > 2026:
                            st.error("A data de nascimento não pode ser superior ao ano de 2026.")
                        else:
                            data_nascimento_str = data_obj.strftime("%Y-%m-%d")
                            sucesso = cliente_service.adicionar_cliente(cpf, nome, data_nascimento_str, score)

                            if sucesso:
                                st.success(f"Cliente {nome} adicionado com sucesso!")
                                st.balloons()
                            else:
                                st.error("Erro ao adicionar cliente. Verifique se o CPF já não está cadastrado.")


elif st.session_state.pagina_atual == "listar_clientes":
    st.title("Clientes Cadastrados")
    st.caption("Visualize todos os clientes do sistema")

    cliente_service = ClienteService()
    clientes = cliente_service.listar_todos()

    if not clientes:
        st.warning("Nenhum cliente cadastrado no sistema.")
    else:
        st.success(f"Total de clientes: {len(clientes)}")

        df_clientes = pd.DataFrame([
            {
                "CPF": cliente.cpf,
                "Nome": cliente.nome,
                "Data Nascimento": cliente.data_nascimento.strftime("%d/%m/%Y"),
                "Score": cliente.score,
                "Limite Atual": f"R$ {cliente.limite_atual:,.2f}",
            }
            for cliente in clientes
        ])

        st.dataframe(df_clientes, width="stretch", hide_index=True)


elif st.session_state.pagina_atual == "solicitacoes":
    st.title("Solicitações de Aumento de Limite")
    st.caption("Visualize todas as solicitações de aumento de limite")

    solicitacao_service = SolicitacaoService()
    solicitacoes = solicitacao_service.listar_todas()

    if not solicitacoes:
        st.warning("Nenhuma solicitação encontrada.")
    else:
        st.success(f"Total de solicitações: {len(solicitacoes)}")

        col1, col2 = st.columns(2)
        with col1:
            filtro_status = st.multiselect(
                "Filtrar por Status",
                options=["aprovado", "rejeitado", "pendente"],
                default=["aprovado", "rejeitado", "pendente"]
            )
        with col2:
            filtro_cpf = st.text_input("Filtrar por CPF", placeholder="Digite o CPF")

        solicitacoes_filtradas = [
            s for s in solicitacoes
            if s.status_pedido.value in filtro_status
            and (not filtro_cpf or filtro_cpf in s.cpf_cliente)
        ]

        df_solicitacoes = pd.DataFrame([
            {
                "CPF Cliente": sol.cpf_cliente,
                "Data/Hora": sol.data_hora_solicitacao.strftime("%d/%m/%Y %H:%M:%S"),
                "Limite Atual": f"R$ {sol.limite_atual:,.2f}",
                "Novo Limite": f"R$ {sol.novo_limite_solicitado:,.2f}",
                "Status": sol.status_pedido.value.upper(),
            }
            for sol in solicitacoes_filtradas
        ])

        st.dataframe(
            df_solicitacoes,
            width="stretch",
            hide_index=True
        )
