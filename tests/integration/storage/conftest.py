import datetime
import socket
from typing import cast
from unittest import mock
from uuid import uuid1

import pytest
from _pytest.fixtures import FixtureRequest
from faker import Faker

from overhave import db
from overhave.entities.converters import (
    DraftModel,
    EmulationModel,
    FeatureModel,
    FeatureTypeModel,
    ScenarioModel,
    SystemUserModel,
    TestUserModel,
)
from overhave.entities.settings import OverhaveEmulationSettings
from overhave.storage import DraftStorage, FeatureTypeStorage, TestRunStorage
from overhave.storage.emulation_storage import EmulationStorage


@pytest.fixture(scope="module")
def socket_mock() -> mock.MagicMock:
    with mock.patch("socket.socket", return_value=mock.create_autospec(socket.socket)) as mocked_socket:
        yield mocked_socket


@pytest.fixture(scope="class")
def test_emulation_settings() -> OverhaveEmulationSettings:
    return OverhaveEmulationSettings()


@pytest.fixture(scope="class")
def test_emulation_storage(
    socket_mock: mock.MagicMock, test_emulation_settings: OverhaveEmulationSettings
) -> EmulationStorage:
    return EmulationStorage(test_emulation_settings)


@pytest.fixture()
def test_feature_type(database: None, faker: Faker) -> db.FeatureType:
    with db.create_session() as session:
        feature_type = db.FeatureType(name=cast(str, faker.word()))
        session.add(feature_type)
        session.flush()
        return cast(FeatureTypeModel, FeatureTypeModel.from_orm(feature_type))


@pytest.fixture()
def test_user_role(request: FixtureRequest) -> db.Role:
    if hasattr(request, "param"):
        return request.param
    raise NotImplementedError


@pytest.fixture()
def test_system_user(database: None, faker: Faker, test_user_role: db.Role) -> SystemUserModel:
    with db.create_session() as session:
        app_user = db.UserRole(login=faker.word(), password=faker.word(), role=test_user_role)
        session.add(app_user)
        session.flush()
        return cast(SystemUserModel, SystemUserModel.from_orm(app_user))


@pytest.fixture()
def test_user(test_system_user: SystemUserModel, faker: Faker, test_feature_type) -> TestUserModel:
    with db.create_session() as session:
        test_user = db.TestUser(
            feature_type_id=test_feature_type.id, name=cast(str, faker.word()), created_by=test_system_user.login
        )
        session.add(test_user)
        session.flush()
        return cast(TestUserModel, TestUserModel.from_orm(test_user))


@pytest.fixture()
def test_emulation(test_system_user: SystemUserModel, test_user: TestUserModel, faker: Faker) -> EmulationModel:
    with db.create_session() as session:
        emulation = db.Emulation(
            name=cast(str, faker.word()),
            command=cast(str, faker.word()),
            test_user_id=test_user.id,
            created_by=test_system_user.login,
        )
        session.add(emulation)
        session.flush()
        return cast(EmulationModel, EmulationModel.from_orm(emulation))


@pytest.fixture(scope="class")
def test_test_run_storage() -> TestRunStorage:
    return TestRunStorage()


@pytest.fixture(scope="class")
def test_feature_type_storage() -> FeatureTypeStorage:
    return FeatureTypeStorage()


@pytest.fixture()
def test_feature(faker: Faker, test_system_user: SystemUserModel, test_feature_type: FeatureTypeModel) -> FeatureModel:
    with db.create_session() as session:
        feature = db.Feature(
            name=faker.word(),
            author=test_system_user.login,
            type_id=test_feature_type.id,
            task=[faker.word()[:11]],
            last_edited_by=test_system_user.login,
            file_path="my_folder/my_feature",
        )
        session.add(feature)
        session.flush()
        return cast(FeatureModel, FeatureModel.from_orm(feature))


@pytest.fixture()
def test_scenario(test_feature: FeatureModel, faker: Faker) -> ScenarioModel:
    with db.create_session() as session:
        db_scenario = db.Scenario(feature_id=test_feature.id, text=faker.word())
        session.add(db_scenario)
        session.flush()
        return cast(ScenarioModel, ScenarioModel.from_orm(db_scenario))


@pytest.fixture(scope="class")
def test_report() -> str:
    return uuid1().hex


@pytest.fixture()
def test_created_test_run_id(
    test_test_run_storage: TestRunStorage, test_scenario: ScenarioModel, test_feature: FeatureModel
) -> int:
    return test_test_run_storage.create_test_run(test_scenario.id, test_feature.author)


@pytest.fixture(scope="class")
def test_draft_storage() -> DraftStorage:
    return DraftStorage()


@pytest.fixture()
def test_draft(
    faker: Faker, test_feature: FeatureModel, test_created_test_run_id: int, test_system_user: SystemUserModel
) -> DraftModel:
    with db.create_session() as session:
        draft: db.Draft = db.Draft(
            feature_id=test_feature.id,
            test_run_id=test_created_test_run_id,
            text=faker.word(),
            pr_url=faker.word(),
            published_by=test_system_user.login,
            published_at=datetime.datetime.now(),
        )
        session.add(draft)
        session.flush()
        return cast(DraftModel, DraftModel.from_orm(draft))
