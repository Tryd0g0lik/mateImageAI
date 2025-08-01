"""
__tests__/tests_person/test_task_user_is_authenticate.py
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
        ("", False),
        (None, False),
    ],
)
@pytest.mark.authenticate
async def test_person_tasks_task_user_is_authenticate_async_task_user_authenticate(
    user_id: int, expected: bool
) -> None:
    """
    path: person.tasks.task_user_is_authenticate.task_user_authenticate
    :param user_id:
    :return:
    """
    from person.tasks.task_user_is_authenticate import async_task_user_authenticate

    log.info(
        "%s: START TEST WHERE user_id: %s, expected: %s"
        % (
            test_person_tasks_task_user_is_authenticate_async_task_user_authenticate.__name__,
            user_id,
            expected,
        )
    )
    response = await async_task_user_authenticate(user_id)
    log.info(
        "%s: Response: %s"
        % (
            test_person_tasks_task_user_is_authenticate_async_task_user_authenticate.__name__,
            response,
        )
    )
    result_bool = False if isinstance(response, dict) else True
    log.info(
        "%s: result_bool: %s"
        % (
            test_person_tasks_task_user_is_authenticate_async_task_user_authenticate.__name__,
            result_bool,
        )
    )

    assert result_bool is expected
    log.info(
        "%s: COMPLETED TEST WHERE user_id: %s, expected: %s"
        % (
            test_person_tasks_task_user_is_authenticate_async_task_user_authenticate.__name__,
            user_id,
            expected,
        )
    )
