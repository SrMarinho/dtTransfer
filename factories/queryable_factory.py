from entities import *

class QueryableFactory:
    def __init__(self):
        ...

    @staticmethod
    def getInstance(queryName, params):
        entities_list = {
            'titulos_com_notas': TitulosComNotas,
            'configuracoes_ol': ConfiguracoesOl,
            'configuracoes_ol_excecoes': ConfiguracoesOlExcecoes,
            'configuracoes_ol_excecoes_clientes': ConfiguracoesOlExcecoesClientes,
            'configuracoes_ol_excecoes_descontos': ConfiguracoesOlExcecoesDescontos,
            'configuracoes_ol_excecoes_marcas': ConfiguracoesOlExcecoesMarcas,
            'configuracoes_ol_excecoes_ols': ConfiguracoesOlExcecoesOls,
            'configuracoes_ol_excecoes_produtos': ConfiguracoesOlExcecoesProdutos,
            'configuracoes_ol_excecoes_unidades': ConfiguracoesOlExcecoesUnidades,
            'identificadores': Identificadores,
            'grupos_clientes': GruposClientes,
            'vans_projetos': VansProjetos,
            'clientes_redes': ClientesRedes,
            'tipos_acoes_descontos_ol': TiposAcoesDescontosOl,
            'titulos_contas_receber': TitulosContasReceber,
            'acompanhamento_solicitacoes_compras': AcompanhamentoSolicitacoesCompras,
            'f_folha_visao_contabil': FfolhaVisaoContabil,
            'estoque_usu_consumo': EstoqueUsuConsumo,
            'titulos_sem_notas': TitulosSemNotas,
            'f_titulos_com_notas_servicos': FtitulosComNotasServicos,
            'f_titulos_com_notas_produtos': FTitulosComNotasProdutos,
            'plano_contas_contabeis': PlanoContasContabeis,
            'folha_controladoria': FolhaControladoria,
            'd_filiais': Dfiliais,
            'd_custos': Dcusto,
            'd_historico_filial': DhistoricoFilial,
            'd_eventos': DEventos,
            'f_mapear_contas_lanc_contabil': FMapearContasLancContabil,
            'rescisoes': Rescisoes
        }

        if queryName in entities_list:
            return entities_list[queryName](params)
        else:
            raise "Tabela não registrada!"
