from typing import Callable, Dict, List, Optional
from unittest import mock

import click
import pytest
from flask import Flask

from demo.demo import _run_demo_admin
from overhave import set_config_to_context
from overhave.base_settings import DataBaseSettings
from overhave.factory import ProxyFactory


@pytest.fixture(scope="module")
def envs_for_mock(db_settings: DataBaseSettings) -> Dict[str, Optional[str]]:
    return {
        "OVERHAVE_DB_URL": str(db_settings.db_url),
    }


@pytest.fixture(scope="module")
def mock_default_value() -> str:
    return ""


@pytest.fixture()
def flask_run_mock(mock_envs: None, database: None) -> mock.MagicMock:
    with mock.patch.object(Flask, "run", return_value=mock.MagicMock()) as flask_run_handler:
        yield flask_run_handler


@pytest.fixture()
def click_ctx_mock() -> click.Context:
    return mock.create_autospec(click.Context)


@pytest.fixture()
def set_config_to_ctx(db_settings: DataBaseSettings, database: None, click_ctx_mock: click.Context) -> None:
    set_config_to_context(context=click_ctx_mock, settings=db_settings)


@pytest.fixture(scope="module")
def test_feature_types() -> List[str]:
    return ["feature_type_1", "feature_type_2", "feature_type_3"]


@pytest.fixture()
def test_proxy_factory(clean_proxy_factory: Callable[[], ProxyFactory]) -> ProxyFactory:
    return clean_proxy_factory()


@pytest.fixture()
def test_resolved_factory(flask_run_mock: mock.MagicMock, test_proxy_factory: ProxyFactory) -> ProxyFactory:
    _run_demo_admin()
    return test_proxy_factory
