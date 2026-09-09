"""문제 3 — 회전 행렬의 수학적 성질 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 4가지를 각각 테스트 함수로 작성한다.

  1. 회전행렬의 열이 서로 직교하는 단위벡터인가   -> test_columns_are_orthonormal
  2. 행렬식이 1인가                               -> test_determinant_is_one
  3. 역행렬이 전치와 같은가                       -> test_inverse_equals_transpose
  4. 재직교화 결과가 직교행렬인가                 -> test_gram_schmidt_restores_orthogonality

작성 요령
--------
- `@pytest.mark.parametrize` 로 여러 축 x 여러 각도를 한 함수에서 검사하면
  테스트 하나가 여러 케이스를 담당한다 (아래 ANGLES / MAKERS 참고).
- 비교는 반드시 `np.isclose` / `np.allclose` 로 한다 (부동소수점).
- `np.linalg` 는 검산용으로만 쓰고, 쓸 때는 주석으로 검산임을 밝힌다.
- assert 에 실패 메시지를 붙이면 어디가 깨졌는지 바로 보인다.
- 4개는 **최소 개수**다. 반사 행렬 반례, 로드리게스 일치, 축·각 왕복 같은
  테스트를 더 붙이면 좋다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import (
    axis_angle_from_matrix,
    gram_schmidt,
    is_rotation,
    orthogonality_error,
    rodrigues,
    rot_x,
    rot_y,
    rot_z,
)
from src.vectors import det

ANGLES = [0.0, np.deg2rad(22.5), np.pi / 6, np.pi / 4, np.pi / 2, 2.0, np.pi, -1.234]
MAKERS = [rot_x, rot_y, rot_z]


@pytest.fixture
def rng():
    """난수는 반드시 시드를 고정한다."""
    return np.random.default_rng(42)


# --- 1. 열이 서로 직교하는 단위벡터인가 -------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_columns_are_orthonormal(maker, theta):
    R = maker(theta)
    # 각 열의 길이가 1인지 (내적==1)
    for i in range(3):
        col = R[:, i]
        assert np.isclose(float(col @ col), 1.0, atol=1e-12), \
            f"{maker.__name__}({theta}): {i}열 길이 제곱이 1이 아님: {float(col @ col)}"
    # 서로 다른 두 열의 내적이 0인지
    for i in range(3):
        for j in range(i + 1, 3):
            assert np.isclose(float(R[:, i] @ R[:, j]), 0.0, atol=1e-12), \
                f"{maker.__name__}({theta}): {i},{j}열 직교 실패: {float(R[:, i] @ R[:, j])}"
    # 검산용: R^T R == I (np.linalg는 검산용이 아니라 직접 곱이므로 별도 검산 불필요)
    # 추가 검산용: 열 노름을 np.linalg.norm으로 확인
    assert np.allclose(np.linalg.norm(R, axis=0), np.ones(3), atol=1e-12), "검산용 np.linalg.norm 열길이 확인 실패"  # 검산용


# --- 2. 행렬식이 1인가 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_determinant_is_one(maker, theta):
    R = maker(theta)
    assert np.isclose(det(R), 1.0, atol=1e-12), \
        f"{maker.__name__}({theta}): det={det(R)} != 1"
    # 검산용 np.linalg.det 로 교차 확인
    assert np.isclose(float(np.linalg.det(R)), 1.0, atol=1e-12), "검산용 np.linalg.det 확인 실패"  # 검산용


# --- 3. 역행렬 == 전치 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_inverse_equals_transpose(maker, theta):
    R = maker(theta)
    assert np.allclose(R.T @ R, np.eye(3), atol=1e-12), \
        f"{maker.__name__}({theta}): R^T R != I"
    assert np.allclose(R @ R.T, np.eye(3), atol=1e-12), \
        f"{maker.__name__}({theta}): R R^T != I"
    # 검산용: np.linalg.inv 로 구한 역행렬이 전치와 같은지
    assert np.allclose(np.linalg.inv(R), R.T, atol=1e-12), "검산용 np.linalg.inv 확인 실패"  # 검산용


# --- 4. 재직교화 결과가 직교행렬인가 -----------------------------------------

def test_gram_schmidt_restores_orthogonality(rng):
    R0 = rot_z(0.7) @ rot_y(-0.4) @ rot_x(0.5)
    noisy = R0 + 1e-3 * rng.standard_normal((3, 3))
    # 깨졌는지 먼저 확인
    assert orthogonality_error(noisy) > 1e-6, \
        f"노이즈가 직교성을 깨뜨리지 못함: {orthogonality_error(noisy)}"
    Q = gram_schmidt(noisy)
    assert orthogonality_error(Q) < 1e-14, \
        f"복구 후 오차가 큼: {orthogonality_error(Q)}"
    assert np.isclose(float(np.linalg.det(Q)), 1.0, atol=1e-8), "검산용 np.linalg.det 확인 실패"  # 검산용
    assert np.isclose(det(Q), 1.0, atol=1e-8), f"det(Q)={det(Q)} != 1"
    assert is_rotation(Q), "gram_schmidt 결과가 회전행렬이 아님"
    # 단일 축 노이즈 케이스도 확인
    for maker, th in [(rot_x, 0.3), (rot_y, -0.8), (rot_z, 1.1)]:
        n2 = maker(th) + 1e-3 * rng.standard_normal((3, 3))
        q2 = gram_schmidt(n2)
        assert is_rotation(q2), f"{maker.__name__} 노이즈 복구 실패"
        assert orthogonality_error(q2) < 1e-14, f"{maker.__name__} 복구 오차 큼"


# --- 여기부터는 추가 테스트 (권장) -------------------------------------------

def test_reflection_is_not_a_rotation():
    """det = -1 인 반사 행렬은 직교여도 회전이 아니다."""
    Refl = np.diag([1.0, 1.0, -1.0])
    # 직교성은 만족 (R^T R == I)
    assert np.allclose(Refl.T @ Refl, np.eye(3)), "반사행렬 직교성 자체가 깨짐"
    assert np.isclose(det(Refl), -1.0), f"det={det(Refl)} != -1"
    assert not is_rotation(Refl), "반사행렬을 회전으로 판정하면 안 됨"


@pytest.mark.parametrize("theta", ANGLES)
def test_rodrigues_matches_rot_z(theta):
    """로드리게스 z축 회전이 rot_z와 일치한다."""
    Rr = rodrigues([0, 0, 1], theta)
    Rz = rot_z(theta)
    assert np.allclose(Rr, Rz, atol=1e-12), f"rodrigues z축 불일치 theta={theta}"
    # 정규화되지 않은 축을 넣어도 같은 결과가 나와야 한다
    Rr2 = rodrigues([0, 0, 5.0], theta)
    assert np.allclose(Rr2, Rz, atol=1e-12), "축 정규화 실패"


def test_orthogonality_error_zero_for_exact():
    """완벽한 회전행렬의 오차는 0에 가깝고, 깨진 행렬은 크다."""
    assert orthogonality_error(np.eye(3)) < 1e-15, "단위행렬 오차가 0이 아님"
    assert orthogonality_error(rot_x(0.7)) < 1e-15, "rot_x 오차가 0이 아님"
    broken = rot_z(0.2) + 1e-2 * np.ones((3, 3))
    assert orthogonality_error(broken) > 1e-4, "깨진 행렬 오차가 너무 작음"
