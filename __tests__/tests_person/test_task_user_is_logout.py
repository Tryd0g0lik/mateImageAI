import logging
import pytest
from logs import configure_logging

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@pytest.mark.parametrize(
    "user_id, expected",
    [
        (101, True),
        ("101", True),
        (6, False),
    ],
)
@pytest.mark.logout
async def test_person_redis_person_RedisOfPerson_async_basis_collection(
    user_id, expected
) -> None:
    """
    Test method for code of basis collection.
    path: person.redis_person.RedisOfPerson.async_basis_collection
    :return:
    """
    from person.redis_person import RedisOfPerson

    person = RedisOfPerson()
    response = await person.async_basis_collection(user_id)
    assert type(response) == dict
    if type(response) == dict:
        assert True if len(response.keys()) > 0 else False is expected


@pytest.mark.parametrize(
    "user_id, expected",
    [
        (6, False),
        (101, True),
        ("101", True),
    ],
)
@pytest.mark.logout
async def test_person_tasks_task_user_is_logout_async_task_user_logout(
    user_id, expected
) -> None:
    from person.tasks.task_user_is_logout import async_task_user_logout

    log.info(
        "%s: START TEST WHERE user_iD: %s, expecteD: %s" % (__name__, user_id, expected)
    )
    responses: dict | bool = await async_task_user_logout(user_id)
    log.info("%s: TEST ASSERT TYPE: %s" % (__name__, type(responses)))
    assert bool == type(responses)
    if bool == type(responses):
        assert responses == expected
    log.info(
        "%s: COMPLETED TEST WHERE user_iD: %s, expecteD: %s"
        % (__name__, user_id, expected)
    )
