from typing import List, Mapping, Sequence, cast

import pytest
from faker import Faker
from pytest_mock import MockFixture

from overhave.entities import FeatureTypeName
from overhave.stash import OverhaveStashProjectSettings, StashClient
from tests.objects import get_feature_extractor


@pytest.fixture()
def test_repository_name(faker: Faker) -> str:
    return cast(str, faker.word())


@pytest.fixture()
def test_project_key(faker: Faker) -> str:
    return cast(str, faker.word()).upper()


@pytest.fixture()
def test_target_branch(faker: Faker) -> str:
    return cast(str, faker.word())


@pytest.fixture()
def test_default_reviewers(faker: Faker) -> Sequence[str]:
    return cast(Sequence[str], faker.words(faker.random.randint(1, 10)))


@pytest.fixture()
def test_stash_project_settings_with_default_reviewers(
    test_repository_name: str, test_project_key: str, test_target_branch: str, test_default_reviewers: Sequence[str],
) -> OverhaveStashProjectSettings:
    return OverhaveStashProjectSettings(
        repository_name=test_repository_name,
        project_key=test_project_key,
        default_target_branch_name=test_target_branch,
        default_reviewers=test_default_reviewers,
    )


@pytest.fixture()
def test_reviewers_mapping(faker: Faker) -> Mapping[FeatureTypeName, List[str]]:
    return {
        feature_type: cast(List[str], faker.words(faker.random.randint(1, 10)))
        for feature_type in get_feature_extractor().feature_types
    }


@pytest.fixture()
def test_stash_project_settings_with_reviewers_mapping(
    test_repository_name: str,
    test_project_key: str,
    test_target_branch: str,
    test_reviewers_mapping: Mapping[FeatureTypeName, List[str]],
) -> OverhaveStashProjectSettings:
    return OverhaveStashProjectSettings(
        repository_name=test_repository_name,
        project_key=test_project_key,
        default_target_branch_name=test_target_branch,
        feature_type_to_reviewers_mapping=test_reviewers_mapping,
    )


@pytest.fixture()
def mocked_stash_client(mocker: MockFixture) -> StashClient:
    return cast(StashClient, mocker.create_autospec(StashClient))