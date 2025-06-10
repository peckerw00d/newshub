import pytest
from sqlalchemy import select


@pytest.mark.asyncio
async def test_repository_create(base_repo, test_user, mock_async_session):
    result = await base_repo.create(test_user)

    mock_async_session.add.assert_called_once_with(test_user)
    mock_async_session.commit.assert_awaited_once()

    assert result is test_user


@pytest.mark.asyncio
async def test_repository_get_by_id(
    base_repo, test_user, test_model, mock_async_session
):
    mock_async_session.execute.return_value.scalars.return_value.first.return_value = (
        test_user
    )

    result = await base_repo.get_by_id(1)

    actual_query = str(mock_async_session.execute.await_args[0][0])
    expected_query = str(select(test_model).where(test_model.id == "123"))

    assert actual_query == expected_query
    assert result == test_user


@pytest.mark.asyncio
async def test_repository_get_by_id_not_found(base_repo, mock_async_session):
    mock_async_session.execute.return_value.scalars.return_value.first.return_value = (
        None
    )

    result = await base_repo.get_by_id(1)
    assert result is None
    mock_async_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_repository_delete(base_repo, test_user, mock_async_session):
    mock_async_session.execute.return_value.scalars.return_value.first.side_effect = [
        test_user,
        None,
    ]

    await base_repo.delete(1)

    mock_async_session.delete.assert_awaited_once_with(test_user)
    mock_async_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_repository_delete_not_found(base_repo, mock_async_session):
    mock_async_session.execute.return_value.scalars.return_value.first.return_value = (
        None
    )

    await base_repo.delete(1)

    mock_async_session.delete.assert_not_called()
    mock_async_session.commit.assert_not_called()
