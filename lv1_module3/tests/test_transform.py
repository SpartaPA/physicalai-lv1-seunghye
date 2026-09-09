"""문제 5 — 동차변환 inv_T 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 것은 `inv_T` 검증이지만,
점/방향 구분과 벡터화, 최소자승까지 함께 검증해 두면 이후 문제에서 안전하다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import rot_x, rot_y, rot_z
from src.transform import (
    inv_T,
    least_squares_normal_equation,
    make_T,
    rmse,
    to_homogeneous,
    transform_direction,
    transform_point,
    transform_points,
)


@pytest.fixture
def T():
    """테스트에 쓸 대표 동차변환 하나."""
    R = rot_z(0.9) @ rot_y(-0.35) @ rot_x(1.3)
    return make_T(R, [0.35, -0.15, 0.55])


def test_inv_T_gives_identity(T):
    Ti = inv_T(T)
    assert np.allclose(Ti @ T, np.eye(4))
    assert np.allclose(T @ Ti, np.eye(4))


def test_inv_T_matches_generic_inverse(T):
    assert np.allclose(inv_T(T), np.linalg.inv(T))  # 검산용
    # 전치 공식 확인
    R = T[:3, :3]
    t = T[:3, 3]
    Ti = inv_T(T)
    assert np.allclose(Ti[:3, :3], R.T)
    assert np.allclose(Ti[:3, 3], -R.T @ t)
    assert np.allclose(Ti[3], [0, 0, 0, 1])


def test_point_and_direction_differ(T):
    v = np.array([1.0, -2.0, 0.5])
    p_out = transform_point(T, v)
    d_out = transform_direction(T, v)
    assert not np.allclose(p_out, d_out)
    assert np.allclose(p_out - d_out, T[:3, 3])
    assert np.isclose(np.linalg.norm(d_out), np.linalg.norm(v))
    assert np.allclose(d_out, T[:3, :3] @ v)
    assert np.allclose(p_out, T[:3, :3] @ v + T[:3, 3])


def test_transform_points_is_vectorized(T):
    rng = np.random.default_rng(0)
    P = rng.standard_normal((10, 3))
    Pb = transform_points(T, P)
    ref = np.stack([transform_point(T, q) for q in P])
    assert Pb.shape == (10, 3)
    assert np.allclose(Pb, ref)


def test_roundtrip_through_inverse(T):
    rng = np.random.default_rng(1)
    P = rng.standard_normal((15, 3))
    Pb = transform_points(T, P)
    Pback = transform_points(inv_T(T), Pb)
    assert np.allclose(Pback, P)


def test_least_squares_matches_lstsq():
    rng = np.random.default_rng(42)
    T_true = make_T(rot_z(0.5) @ rot_x(-0.3), [0.18, -0.42, 0.61])
    P_cam = rng.uniform(-0.5, 0.5, size=(40, 3))
    P_base = transform_points(T_true, P_cam) + 2e-3 * rng.standard_normal((40, 3))
    Ph = to_homogeneous(P_cam, 1.0)
    A = np.vstack([np.kron(np.eye(3), row.reshape(1, 4)) for row in Ph])
    b = P_base.reshape(-1)
    assert A.shape == (120, 12)
    x_hat, residual = least_squares_normal_equation(A, b)
    x_ref = np.linalg.lstsq(A, b, rcond=None)[0]  # 비교 대상
    assert np.allclose(x_hat, x_ref)
    assert np.allclose(residual, b - A @ x_hat)
    assert np.allclose(A.T @ residual, 0.0, atol=1e-9)
    assert 0.2 * 2e-3 < rmse(residual) < 2.0 * 2e-3
