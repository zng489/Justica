from unittest import mock

from health.backends import (
    CabecalhoProcessualBackend,
    DatabaseBackend,
    DeclaracaoRendaDetalheBackend,
    DeclaracaoRendaListaBackend,
    GraphDatabaseBackend,
    NotConfiguredService,
    SisbajudContasBackend,
    SisbajudOrdensBackend,
)
from health.core import get_backends, run_checks


class TestCore:
    def setup_method(self):
        self.p_get_backends = mock.patch("health.core.get_backends")
        self.m_get_backends = self.p_get_backends.start()

    def teardown_method(self):
        self.p_get_backends.stop()

    def test_get_backends(self):
        backends = get_backends()
        expected = {
            "cabecalho-processual": CabecalhoProcessualBackend,
            "graphdb": GraphDatabaseBackend,
            "db": DatabaseBackend,
            "infojud-lista": DeclaracaoRendaListaBackend,
            "infojud-detalhe": DeclaracaoRendaDetalheBackend,
            "sisbajud-contas": SisbajudContasBackend,
            "sisbajud-ordens": SisbajudOrdensBackend,
        }

        assert backends == expected

    @mock.patch("health.backends.DatabaseBackend")
    def test_run_db_check(self, m_DatabaseBackend):
        name = "db"
        m_db_backend = mock.Mock(errors=[])
        m_DatabaseBackend.return_value = m_db_backend
        self.m_get_backends.return_value = {name: m_DatabaseBackend}

        report = run_checks(name)
        expected = {name: {"status": "ok"}}

        m_DatabaseBackend.assert_called_once_with()
        m_db_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.DatabaseBackend")
    def test_run_db_check_unhealthy(self, m_DatabaseBackend):
        name = "db"
        m_db_backend = mock.Mock(errors=["error"])
        m_DatabaseBackend.return_value = m_db_backend
        self.m_get_backends.return_value = {name: m_DatabaseBackend}

        report = run_checks(name)
        expected = {name: {"status": "nok"}}

        m_DatabaseBackend.assert_called_once_with()
        m_db_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.GraphDatabaseBackend")
    def test_run_graphdb_check(self, m_GraphDatabaseBackend):
        name = "graphdb"
        m_graphdb_backend = mock.Mock(errors=[])
        m_GraphDatabaseBackend.return_value = m_graphdb_backend
        self.m_get_backends.return_value = {name: m_GraphDatabaseBackend}

        report = run_checks(name)
        expected = {name: {"status": "ok"}}

        m_GraphDatabaseBackend.assert_called_once_with()
        m_graphdb_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.GraphDatabaseBackend")
    def test_run_graphdb_check_unhealthy(self, m_GraphDatabaseBackend):
        name = "graphdb"
        m_graphdb_backend = mock.Mock(errors=["error"])
        m_GraphDatabaseBackend.return_value = m_graphdb_backend
        self.m_get_backends.return_value = {name: m_GraphDatabaseBackend}

        report = run_checks(name)
        expected = {name: {"status": "nok"}}

        m_GraphDatabaseBackend.assert_called_once_with()
        m_graphdb_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.CabecalhoProcessualBackend")
    def test_run_cabecalho_processual_check(self, m_CabecalhoProcessualBackend):
        name = "cabecalho-processual"
        m_cabecalho_backend = mock.Mock(errors=[])
        m_CabecalhoProcessualBackend.return_value = m_cabecalho_backend
        self.m_get_backends.return_value = {name: m_CabecalhoProcessualBackend}

        report = run_checks(name)
        expected = {name: {"status": "ok"}}

        m_CabecalhoProcessualBackend.assert_called_once_with()
        m_cabecalho_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.CabecalhoProcessualBackend")
    def test_run_cabecalho_processual_unhealthy(self, m_CabecalhoProcessualBackend):
        name = "cabecalho-processual"
        m_cabecalho_backend = mock.Mock(errors=["error"])
        m_CabecalhoProcessualBackend.return_value = m_cabecalho_backend
        self.m_get_backends.return_value = {name: m_CabecalhoProcessualBackend}

        report = run_checks(name)
        expected = {name: {"status": "nok"}}

        m_CabecalhoProcessualBackend.assert_called_once_with()
        m_cabecalho_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.CabecalhoProcessualBackend")
    def test_run_cabecalho_processual_not_configured(self, m_CabecalhoProcessualBackend, settings):
        del settings.CABECALHO_PROCESSUAL_HEALTH_USER
        del settings.CABECALHO_PROCESSUAL_HEALTH_DOCUMENT
        name = "cabecalho-processual"
        m_cabecalho_backend = mock.Mock(errors=[])
        m_cabecalho_backend.run_check.side_effect = NotConfiguredService
        m_CabecalhoProcessualBackend.return_value = m_cabecalho_backend
        self.m_get_backends.return_value = {name: m_CabecalhoProcessualBackend}

        report = run_checks(name)
        expected = {name: {"status": "not-configured"}}

        m_CabecalhoProcessualBackend.assert_called_once_with()
        m_cabecalho_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.CabecalhoProcessualBackend")
    def test_run_cabecalho_processual_empty(self, m_CabecalhoProcessualBackend, settings):
        settings.CABECALHO_PROCESSUAL_HEALTH_USER = ""
        settings.CABECALHO_PROCESSUAL_HEALTH_DOCUMENT = ""
        name = "cabecalho-processual"
        m_cabecalho_backend = mock.Mock(errors=[])
        m_cabecalho_backend.run_check.side_effect = NotConfiguredService
        m_CabecalhoProcessualBackend.return_value = m_cabecalho_backend
        self.m_get_backends.return_value = {name: m_CabecalhoProcessualBackend}

        report = run_checks(name)
        expected = {name: {"status": "not-configured"}}

        m_CabecalhoProcessualBackend.assert_called_once_with()
        m_cabecalho_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.SisbajudContasBackend")
    def test_run_sisbajud_contas_check(self, m_Backend):
        name = "sisbajud-contas"
        m_backend = mock.Mock(errors=[])
        m_Backend.return_value = m_backend
        self.m_get_backends.return_value = {name: m_Backend}

        report = run_checks(name)
        expected = {name: {"status": "ok"}}

        m_Backend.assert_called_once_with()
        m_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.SisbajudContasBackend")
    def test_run_sisbajud_contas_unhealthy(self, m_Backend):
        name = "sisbajud-contas"
        m_backend = mock.Mock(errors=["error"])
        m_Backend.return_value = m_backend
        self.m_get_backends.return_value = {name: m_Backend}

        report = run_checks(name)
        expected = {name: {"status": "nok"}}

        m_Backend.assert_called_once_with()
        m_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.SisbajudContasBackend")
    def test_run_sisbajud_contas_not_configured(self, m_Backend, settings):
        del settings.SISBAJUD_CONTAS_HEALTH_CPF_SOLICITANTE
        del settings.SISBAJUD_CONTAS_HEALTH_DOCUMENT_ENTIDADE
        del settings.SISBAJUD_CONTAS_HEALTH_TOKEN
        name = "sisbajud-contas"
        m_backend = mock.Mock(errors=[])
        m_backend.run_check.side_effect = NotConfiguredService
        m_Backend.return_value = m_backend
        self.m_get_backends.return_value = {name: m_Backend}

        report = run_checks(name)
        expected = {name: {"status": "not-configured"}}

        m_Backend.assert_called_once_with()
        m_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.SisbajudContasBackend")
    def test_run_sisbajud_contas_empty(self, m_Backend, settings):
        settings.SISBAJUD_CONTAS_HEALTH_CPF_SOLICITANTE = ""
        settings.SISBAJUD_CONTAS_HEALTH_DOCUMENT_ENTIDADE = ""
        settings.SISBAJUD_CONTAS_HEALTH_TOKEN = ""
        name = "sisbajud-contas"
        m_backend = mock.Mock(errors=[])
        m_backend.run_check.side_effect = NotConfiguredService
        m_Backend.return_value = m_backend
        self.m_get_backends.return_value = {name: m_Backend}

        report = run_checks(name)
        expected = {name: {"status": "not-configured"}}

        m_Backend.assert_called_once_with()
        m_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.SisbajudOrdensBackend")
    def test_run_sisbajud_ordens_check(self, m_Backend):
        name = "sisbajud-ordens"
        m_backend = mock.Mock(errors=[])
        m_Backend.return_value = m_backend
        self.m_get_backends.return_value = {name: m_Backend}

        report = run_checks(name)
        expected = {name: {"status": "ok"}}

        m_Backend.assert_called_once_with()
        m_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.SisbajudOrdensBackend")
    def test_run_sisbajud_ordens_unhealthy(self, m_Backend):
        name = "sisbajud-ordens"
        m_backend = mock.Mock(errors=["error"])
        m_Backend.return_value = m_backend
        self.m_get_backends.return_value = {name: m_Backend}

        report = run_checks(name)
        expected = {name: {"status": "nok"}}

        m_Backend.assert_called_once_with()
        m_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.SisbajudOrdensBackend")
    def test_run_sisbajud_ordens_not_configured(self, m_Backend, settings):
        del settings.SISBAJUD_ORDENS_HEALTH_CPF
        del settings.SISBAJUD_ORDENS_HEALTH_TRIBUNAL
        name = "sisbajud-ordens"
        m_backend = mock.Mock(errors=[])
        m_backend.run_check.side_effect = NotConfiguredService
        m_Backend.return_value = m_backend
        self.m_get_backends.return_value = {name: m_Backend}

        report = run_checks(name)
        expected = {name: {"status": "not-configured"}}

        m_Backend.assert_called_once_with()
        m_backend.run_check.assert_called_once_with()
        assert report == expected

    @mock.patch("health.backends.SisbajudOrdensBackend")
    def test_run_sisbajud_ordens_empty(self, m_Backend, settings):
        settings.SISBAJUD_ORDENS_HEALTH_CPF = ""
        settings.SISBAJUD_ORDENS_HEALTH_TRIBUNAL = ""
        name = "sisbajud-ordens"
        m_backend = mock.Mock(errors=[])
        m_backend.run_check.side_effect = NotConfiguredService
        m_Backend.return_value = m_backend
        self.m_get_backends.return_value = {name: m_Backend}

        report = run_checks(name)
        expected = {name: {"status": "not-configured"}}

        m_Backend.assert_called_once_with()
        m_backend.run_check.assert_called_once_with()
        assert report == expected

    def test_run_all(self):
        m_service_0 = mock.Mock(errors=[])
        m_service_1 = mock.Mock(errors=[])
        m_services = {
            "service_0": mock.Mock(return_value=m_service_0),
            "service_1": mock.Mock(return_value=m_service_1),
        }
        self.m_get_backends.return_value = m_services

        report = run_checks()
        expected = {"service_0": {"status": "ok"}, "service_1": {"status": "ok"}}

        assert report == expected

    def test_run_all_unhealthy(self):
        m_service_0 = mock.Mock(errors=["error"])
        m_service_1 = mock.Mock(errors=["error"])
        m_services = {
            "service_0": mock.Mock(return_value=m_service_0),
            "service_1": mock.Mock(return_value=m_service_1),
        }
        self.m_get_backends.return_value = m_services

        report = run_checks()
        expected = {"service_0": {"status": "nok"}, "service_1": {"status": "nok"}}

        assert report == expected
