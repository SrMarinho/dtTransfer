from entities.titulos_com_notas import TitulosComNotas
from entities.configuracoes_ol import ConfiguracoesOl
from entities.configuracoes_ol_excecoes import ConfiguracoesOlExcecoes
from entities.configuracoes_ol_excecoes_clientes import ConfiguracoesOlExcecoesClientes
from entities.configuracoes_ol_excecoes_descontos import ConfiguracoesOlExcecoesDescontos
from entities.configuracoes_ol_excecoes_marcas import ConfiguracoesOlExcecoesMarcas
from entities.configuracoes_ol_excecoes_ols import ConfiguracoesOlExcecoesOls
from entities.configuracoes_ol_excecoes_produtos import ConfiguracoesOlExcecoesProdutos
from entities.configuracoes_ol_excecoes_unidades import ConfiguracoesOlExcecoesUnidades
from entities.identificadores import Identificadores
from entities.grupos_clientes import GruposClientes
from entities.vans_projetos import VansProjetos
from entities.clientes_redes import ClientesRedes
from entities.tipos_acoes_descontos_ol import TiposAcoesDescontosOl
from entities.titulos_contas_receber import TitulosContasReceber
from entities.acopanhamento_solicitacoes_compras import AcompanhamentoSolicitacoesCompras
from entities.f_folha_visao_contabil import FfolhaVisaoContabil
from entities.estoque_usu_consumo import EstoqueUsuConsumo
from entities.titulos_sem_notas import TitulosSemNotas
from entities.f_titulos_com_notas_servicos import FtitulosComNotasServicos
from entities.f_titulos_com_notas_produtos import FTitulosComNotasProdutos
from entities.plano_contas_contabeis import PlanoContasContabeis
from entities.folha_controladoria import FolhaControladoria
from entities.d_filiais import Dfiliais
from entities.d_custos import Dcusto
from entities.d_historico_filial import DhistoricoFilial
from entities.d_eventos import DEventos


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
            'acopanhamento_solicitacoes_compras': AcompanhamentoSolicitacoesCompras,
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
            'd_eventos': DEventos
        }

        if queryName in entities_list:
            return entities_list[queryName](params)
        else:
            raise "Tabela não registrada!"
