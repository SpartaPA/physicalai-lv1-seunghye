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

def gram_schmidt() :
    return

def is_rotation() :
    return

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
    return norm(dot(E,E))#np.sqrt(np.sum(E * E))

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
    # TODO: 문제 6-4
    R = np.asarray(R, dtype=float)
    tr = np.trace(R)
    cos_theta = np.clip((tr - 1.0) / 2.0, -1.0, 1.0)
    angle = np.arccos(cos_theta)

    # 규약 1: 회전이 거의 없는 경우 (theta = 0)
    if np.isclose(angle, 0.0, atol=atol):
        return np.array([0.0, 0.0, 1.0], dtype=float), 0.0

    # 규약 2: 고유값 분해로 고유값 1에 대응하는 고유벡터(회전축) 찾기
    vals, vecs = np.linalg.eig(R)
    idx = np.argmin(np.abs(vals - 1.0))
    axis = np.real(vecs[:, idx])

    n_val = norm(axis)
    if n_val > 1e-12:
        axis = axis / n_val

    # 규약 3: 반대칭 성분을 이용해 축의 부호 정렬 (올바른 회전 방향 보장)
    skew = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]], dtype=float)
    if dot(skew, axis) < 0.0:
        axis = -axis

    return axis, float(angle)


def quaternion_from_axis_angle(axis, angle: float) -> np.ndarray:
    """축-각에서 단위 쿼터니언을 만든다.

        q = (k * sin(theta/2), cos(theta/2))

    반환 순서는 SciPy `Rotation.as_quat()` 와 같은 **(x, y, z, w)** 로 맞춘다
    (그래야 문제 6-5 에서 바로 비교할 수 있다).
    """
    # TODO: 문제 6-5
    axis = np.asarray(axis, dtype=float)
    if axis.shape != (3,):
        raise ValueError(f"회전축은 3차원 벡터여야 합니다. 받은 shape={axis.shape}")

    # 커스텀 norm 함수로 회전축 정규화
    n_val = norm(axis)
    if n_val > 1e-12:
        axis = axis / n_val
    else:
        axis = np.array([0.0, 0.0, 1.0], dtype=float)

    # angle은 이미 라디안 단위이므로 deg2rad를 쓰면 안 되고 2로만 나누어야 함
    half_angle = float(angle) / 2.0
    sin_half = np.sin(half_angle)
    cos_half = np.cos(half_angle)

    # 튜플이 아니라 명시적인 numpy 배열(x, y, z, w)로 반환
    q = np.array([
        axis[0] * sin_half,
        axis[1] * sin_half,
        axis[2] * sin_half,
        cos_half
    ], dtype=float)

    # 정규화된 쿼터니언 반환
    q_norm = norm(q)
    if q_norm > 1e-12:
        q = q / q_norm

    return q
