import datetime
from typing import Optional

import pytest
from faker import Faker

from overhave import db
from overhave.entities import DraftModel
from overhave.storage.draft_storage import DraftStorage, NullableDraftsError, UniqueDraftCreationError


@pytest.mark.usefixtures("database")
class TestDraftStorage:
    """ Integration tests for :class:`DraftStorage`. """

    def test_get_none_if_not_existing_id(self, test_draft_storage: DraftStorage, faker: Faker) -> None:
        assert test_draft_storage.get_draft(faker.random_int()) is None

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_get_draft(self, test_draft_storage: DraftStorage, test_draft: DraftModel) -> None:
        draft_model: Optional[DraftModel] = test_draft_storage.get_draft(test_draft.id)
        assert draft_model is not None
        assert draft_model.id == test_draft.id
        assert draft_model.published_by == test_draft.published_by
        assert draft_model.pr_url == test_draft.pr_url
        assert draft_model.feature_id == test_draft.feature_id
        assert draft_model.test_run_id == test_draft.test_run_id

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_save_draft(self, test_draft_storage: DraftStorage, test_draft: DraftModel, faker: Faker) -> None:
        with pytest.raises(UniqueDraftCreationError):
            test_draft_storage.save_draft(faker.random_int(), test_draft.published_by)

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_save_response(self, test_draft_storage: DraftStorage, test_draft: DraftModel, faker: Faker) -> None:
        pr_url: str = faker.word()
        published_at: datetime.datetime = datetime.datetime.now()
        test_draft_storage.save_response(draft_id=test_draft.id, pr_url=pr_url, published_at=published_at, opened=False)
        new_test_draft: Optional[DraftModel] = test_draft_storage.get_draft(test_draft.id)
        assert new_test_draft is not None
        assert new_test_draft.pr_url == pr_url

    @pytest.mark.parametrize("test_user_role", [db.Role.admin], indirect=True)
    def test_get_previous_feature_draft_with_error(
        self, test_draft_storage: DraftStorage, test_draft: DraftModel
    ) -> None:
        with pytest.raises(NullableDraftsError):
            test_draft_storage.get_previous_feature_draft(test_draft.feature_id)
