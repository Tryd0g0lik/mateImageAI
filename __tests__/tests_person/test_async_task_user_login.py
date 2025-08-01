"""
__tests__/tests_person/test_async_task_user_login.py
"""

import pytest
import logging
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
@pytest.mark.login
async def test_person_tasks_task_user_is_login_async_task_user_login(
    user_id, expected
) -> None:
    """
    path: person.tasks.task_user_is_login.async_task_user_login
    :return:
    """
    from person.tasks.task_user_is_login import async_task_user_login

    log.info(
        "%s: START TEST WHERE user_iD: %s, expecteD: %s"
        % (
            test_person_tasks_task_user_is_login_async_task_user_login.__name__,
            user_id,
            expected,
        )
    )
    responses: dict | bool = await async_task_user_login(user_id)
    log.info(
        "%s: TEST ASSERT TYPE: %s"
        % (
            test_person_tasks_task_user_is_login_async_task_user_login.__name__,
            (responses),
        )
    )
    result__bool = False if type(responses) == dict else True

    log.info("TEST RESULT: %s" % (result__bool))
    assert (result__bool) is expected

    log.info(
        "%s: COMPLETED TEST WHERE user_iD: %s, expecteD: %s"
        % (
            test_person_tasks_task_user_is_login_async_task_user_login.__name__,
            user_id,
            expected,
        )
    )
