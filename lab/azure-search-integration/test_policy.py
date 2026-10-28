from policy import ENGINEERING, FINANCE, allowed_ids, enforce_result_gate
import pytest


def test_known_fixture_acl():
    assert allowed_ids((FINANCE,)) == {"finance-001", "shared-001"}
    assert allowed_ids((ENGINEERING,)) == {"engineering-001", "shared-001"}
    assert allowed_ids(()) == set()


def test_injected_unauthorized_result_is_blocked():
    with pytest.raises(PermissionError, match="Unauthorized"):
        enforce_result_gate(
            [{"document_id": "engineering-001"}, {"document_id": "finance-001"}],
            (ENGINEERING,),
        )


def test_unknown_result_fails_closed():
    with pytest.raises(PermissionError):
        enforce_result_gate([{"document_id": "not-in-fixture"}], (FINANCE,))


def test_authorized_results_pass():
    result = [{"document_id": "shared-001"}]
    assert enforce_result_gate(result, (ENGINEERING,)) == result
