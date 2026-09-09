from __future__ import  annotations
from .vectors import dot ,norm
import numpy as np

#한글라벨이 깨지지 않도록 폰트 지정(Windows 기준, 없으면 기본폰트로 fallback)
# 파일 밖에서 공식적으로 공개할 함수의 목록을 작성된 것.
__all__= [
    "rodrigues","gram_schmidt", "is_rotation", "orthogonality_error", "rot_x", "rot_y", "rot_z",
    "axis_angle_from_matrix","quaternion_from_axis_angle" ,
]

# --- 로드리게스(Rodrigues) 임의 축 회전 행렬 생성 함수 ---
# [역할] 기울어진 임의의 화살표 축(k)을 중심으로 rad 각도만큼 회전하는 행렬을 조립합니다.
# [이유] 로봇 관절 축이 X, Y, Z축처럼 딱 맞지 않고 사선으로 기울어져 있을 때 회전을 제어하기 위해 사용합니다.
def rodrigues(axis, theta):
    """Rodrigues' rotation formula를 사용하여 주어진 축(axis)과 각도(theta)로 회전하는 3x3 회전 행렬을 반환합니다.
    axis: 회전축 (3차원 벡터)
    theta: 회전 각도 (라디안)
    """
    axis = np.asarray(axis, dtype=float)     # 축 벡터를 숫자 데이터로 변환
    if axis.shape != (3,):
        raise ValueError(f"회전축은 3차원 벡터여야 합니다. 받은 shape={axis.shape}")
    # np.linalg.norm: 벡터 화살표의 실제 '길이'를 구함
    # norm = np.linalg.norm(axis)             
    # 축 벡터의 길이를 1로 맞춤 (정규화: Normalization)
    axis = axis / norm(axis)  

    # np.eye(3): 변화가 없는 기준 상태인 3x3 '단위행렬' 생성
    I = np.eye(3)

    # Rodrigues' rotation formula 적용 skew-symmetric matrix K 생성
    # 축 벡터 axis를 스큐 행렬 상자로 변환
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])

    # 로드리게스 핵심 공식: I + sin(rad)*K + (1-cos(rad))*(K @ K)
    R = I + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)
    
    return R

def gram_schmidt(A) -> np.ndarray:
    """열벡터에 대해 Modified Gram-Schmidt 직교정규화를 수행한다.

    q1 = a1 / |a1|,  vj = aj - sum_{i<j} (qi.vj) qi  (빼자마자 갱신),  qj = vj / |vj|
    마지막에 det(Q) < 0 이면 마지막 열 부호를 뒤집어 det=+1 로 맞춘다.
    """
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError(f"정방행렬이 필요합니다. 받은 shape={A.shape}")
    n = A.shape[0]
    Q = np.zeros_like(A, dtype=float)
    for j in range(n):
        v = np.asarray(A[:, j], dtype=float).copy()
        for i in range(j):
            qi = Q[:, i]
            coeff = float(np.dot(qi, v))
            v = v - coeff * qi
        nrm = float(np.sqrt(float(np.dot(v, v))))
        if nrm < 1e-12:
            raise ValueError("앞선 열들에 종속인 열이 있어 정규화할 수 없습니다.")
        Q[:, j] = v / nrm
    # 반사(det=-1)가 섞였으면 마지막 열 부호를 뒤집어 회전행렬로 만든다.
    if float(np.linalg.det(Q)) < 0:
        Q[:, -1] *= -1
    return Q

def is_rotation(R, atol: float = 1e-8) -> bool:
    """회전행렬 판정: 직교(R^T R = I) 그리고 det(R) = +1 이면 True. 3x3이 아니면 False."""
    R = np.asarray(R, dtype=float)
    if R.shape != (3, 3):
        return False
    if orthogonality_error(R) > atol:
        return False
    if abs(float(np.linalg.det(R)) - 1.0) > atol:
        return False
    return True

def orthogonality_error(R) -> float:
    """ 행렬 R이 완벽한 회전행렬에서 얼마나 찌그러졌는지 오차를 측정합니다.
        직교성 이탈 지표: || R^T R - I ||_F (프로베니우스 노름).
    """
    # R과 크기가 똑같은 단위행렬 I(1,0,0 / 0,1,0 / 0,0,1)을 만든다.
    R = np.asarray(R, dtype= float)
    I = np.eye(R.shape[0])
    #R^T @ R이 I와 얼마나 다른지 차이를 구합니다.
    E = R.T @ R - I

    # 전체 차이의 크기(프로베니우스 노름)를 하나의 숫자로 반환합니다.- 노름 구하기.
    return float(np.sqrt(np.sum(E * E)))

##----------------------회전 행렬 생성 함수
# ---  X축 기준 회전 행렬 생성 함수 ---
# [역할] X축 좌표는 가만히 고정하고, Y축과 Z축을 라디안 각도(rad)만큼 회전시키는 3x3 행렬을 만듭니다.
# [이유] 로봇 팔 관절 중 X축을 중심으로 돌아가는 움직임을 표현할 때 사용합니다.
def rot_x(theta):
    """X축을 기준으로 theta(라디안)만큼 돌리는 3x3 회전 행렬"""
    c , s = np.cos(theta) , np. sin(theta)
    return np.array([
        [1,0,0],
        [0,c,-s],
        [0,s,c]
    ])

# ---  Y축 기준 회전 행렬 생성 함수 ---
# [역할] Y축 좌표는 가만히 고정하고, Z축과 X축을 라디안 각도(rad)만큼 회전시키는 3x3 행렬을 만듭니다.
# [이유] 오른손 규칙 순환 구조(X->Y->Z->X) 특성상 마이너스(-s) 부호의 위치가 3행 1열로 바뀝니다.
def rot_y(theta):
    """y축을 기준으로 theta(라디안)만큼 돌리는 3x3 회전 행렬"""
    c, s = np.cos(theta) , np.sin(theta)
    return np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c]
    ])

# ---  Z축 기준 회전 행렬 생성 함수 ---
# [역할] Z축 좌표는 가만히 고정하고, X축과 Y축을 평면상에서 라디안 각도(rad)만큼 회전시킵니다.
# [이유] 로봇이 바닥 평면(XY 평면) 위에서 제자리 회전할 때 기본으로 쓰입니다.
def rot_z(theta):
    """z축을 기준으로 theta(라디안)만큼 돌리는 3x3 회전 행렬"""
    c, s = np.cos(theta) , np.sin(theta)
    return np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ])

# --------------------------------------------------- 회전축·회전각·쿼터니언

def axis_angle_from_matrix(R, atol: float = 1e-8):
    """고유값 분해로 회전축을, 대각합으로 회전각을 복원한다.

    - 회전축은 고유값 1 에 대응하는 실수 고유벡터다 (R k = k).
      -> 여기서는 `np.linalg.eig` 를 써도 된다 (검산이 아니라 축 복원이 목적).
    - 회전각은 trace(R) = 1 + 2 cos(theta) 에서 구한다.
    - arccos 의 치역이 [0, pi] 라 '어느 쪽으로 도는지'는 알 수 없고,
      고유벡터도 부호가 정해지지 않는다. 반대칭 성분
      R - R^T = 2 sin(theta) [k]_x 를 이용해 부호를 맞춘다.
    - theta = 0 (회전 없음) 과 theta = pi (sin = 0) 는 따로 처리해야 한다.
      두 경우에 어떤 규약을 쓸지 정하고 주석으로 남긴다.

    Returns
    -------
    axis : 단위 회전축 (3,)
    angle : 회전각 [rad], 0 <= angle <= pi
    """
    R = np.asarray(R, dtype=float)
    if R.shape != (3, 3):
        raise ValueError(f"3x3 회전행렬이 필요합니다. 받은 shape={R.shape}")
    # 대각합에서 회전각 복원: tr(R) = 1 + 2 cos(theta)
    cos_theta = float(np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0))
    angle = float(np.arccos(cos_theta))
    # 규약 1) theta ~ 0: 회전 없음. 축은 임의로 +z, 각은 0
    if np.isclose(angle, 0.0, atol=atol):
        return np.array([0.0, 0.0, 1.0]), 0.0
    # 규약 2) 고유값 1에 대응하는 고유벡터가 회전축 (R k = k)
    vals, vecs = np.linalg.eig(R)
    idx = int(np.argmin(np.abs(vals - 1.0)))
    axis = np.real(vecs[:, idx]).astype(float)
    n = float(np.linalg.norm(axis))
    if n < 1e-12:
        axis = np.array([0.0, 0.0, 1.0])
    else:
        axis = axis / n
    # 규약 3) theta ~ pi (sin~0): 부호 판별 불가, 고유벡터 그대로 사용
    # 그 외: R - R^T = 2 sin(theta) [k]x 관계로 부호 정렬
    if abs(float(np.sin(angle))) > 1e-8:
        v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
        if float(np.dot(v, axis)) < 0.0:
            axis = -axis
    return axis, angle


def quaternion_from_axis_angle(axis, angle: float) -> np.ndarray:
    """축-각에서 단위 쿼터니언을 만든다.

        q = (k * sin(theta/2), cos(theta/2))

    반환 순서는 SciPy `Rotation.as_quat()` 와 같은 **(x, y, z, w)** 로 맞춘다
    (그래야 문제 6-5 에서 바로 비교할 수 있다).
    """
    ax = np.asarray(axis, dtype=float)
    if ax.shape != (3,):
        raise ValueError(f"회전축은 3차원 벡터여야 합니다. 받은 shape={ax.shape}")
    n = float(np.linalg.norm(ax))
    if n < 1e-12:
        # 영벡터 입력 시 기본 축 +z 사용
        k = np.array([0.0, 0.0, 1.0])
    else:
        k = ax / n
    # angle 은 라디안 입력이므로 2로만 나눈다 (deg 변환 금지)
    half = float(angle) / 2.0
    s, c = float(np.sin(half)), float(np.cos(half))
    q = np.array([k[0] * s, k[1] * s, k[2] * s, c], dtype=float)
    qn = float(np.linalg.norm(q))
    if qn > 1e-12:
        q = q / qn
    return q
