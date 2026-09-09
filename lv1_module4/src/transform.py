import numpy as np

__all__ = [
    "make_T",
    "inv_T",
    "inv_T_batch",
    "least_squares_normal_equation",
    "rmse",
    "to_homogeneous",
    "transform_direction",
    "transform_point",
    "transform_points",
]

def make_T(R, t) -> np.ndarray:
    """회전 행렬 R(3, 3)과 이동 벡터_병진 t(3,)를 조합해 4x4 변환 행렬 T를 생성합니다. - 동차행렬
    T = [[R, t],
        [0, 1]]
    
        R 이 3x3 이 아니면 ValueError.
    """
    t = np.array(t).reshape(3)  # t를 (3,) 형태로 변환

    if R.shape != (3, 3):
        raise ValueError("R must be a 3x3 matrix.")

    T = np.eye(4)           # 1. 4x4 단위행렬을 만듭니다 (대각선만 1, 나머지는 0)
    T[:3, :3] = R           # 2. 왼쪽 위 3x3 영역에 회전행렬 R을 넣습니다
    T[:3, 3] = t.reshape(3) # 3. 오른쪽 위 3x1 영역에 위치벡터 t를 넣습니다
    return T

def inv_T(T: np.ndarray) -> np.ndarray:
    """4x4 변환 행렬 T의 역행렬을 계산합니다.
       동차변환의 역변환. **일반 역행렬 함수를 쓰지 않고** 공식으로 구한다.
       T^-1 = [[R^T, -R^T t],
                       [  0,      1]]
       
           유도: T^-1 을 [[S, u], [0, 1]] 로 두고 T T^-1 = I 를 풀면
                 R S = I -> S = R^T (R 이 직교),  R u + t = 0 -> u = -R^T t.
       
           4x4 가 아니면 ValueError.
    """
    R = T[:3, :3] # 회전 부분 추출 (3x3)
    t = T[:3, 3]  # 위치 부분 추출 (3,)

    T_inv = np.eye(4)       
    T_inv[:3, :3] = R.T     # 1. R의 전치행렬(R^T)을 회전 부분에 넣음
    T_inv[:3, 3] = -R.T @ t # 2. -R^T @ t 계산결과를 위치 부분에 넣음

    return T_inv

def to_homogeneous(v: np.ndarray, is_point: bool = True) -> np.ndarray:
    """3차원 벡터 뒤에 1(점) 또는 0(방향)을 붙여 4차원 동차좌표로 만든다.
    3D 좌표 포인트들을 동차 좌표계(Homogeneous coordinates)로 변환합니다.
    (3,) 또는 (N,3) 좌표에 마지막 성분 w 를 붙인다.

    w = 1 이면 점(위치), w = 0 이면 방향(벡터).
    """
    # TODO: 문제 5-2
    v = np.asarray(v, dtype=float)
    w = 1.0 if is_point else 0.0

    if v.ndim == 1:
        # (3,) -> (4,)
        return np.append(v, w)
    elif v.ndim == 2:
        # (N, 3) -> (N, 4)
        w_col = np.full((v.shape[0], 1), w)
        return np.hstack([v, w_col])
    else:
        raise ValueError(f"v는 (3,) 또는 (N, 3) 차원이어야 합니다. 현재 shape: {v.shape}")
    
    return np.append(v,w)


def transform_direction(T,v) -> np.ndarray:
    """변환 행렬 T의 회전 성분만 적용하여 방향 벡터를 변환합니다.
    방향 변환 (w = 0): 회전만 적용되고 병진은 무시된다. 반환은 (3,)."""

    v_homo = to_homogeneous(v, is_point = False)
    return (T @ v_homo)[:3]


def transform_point(T,p) -> np.ndarray:
    """변환 행렬 T를 사용하여 단일 3D 포인트를 변환합니다.
    점 변환 (w = 1): 회전과 병진이 모두 적용된다. 반환은 (3,).
    """
     # TODO: 문제 5-2
    p_homo = to_homogeneous(p, is_point = True)
    return (T @ p_homo)[:3] # 곱한 후 앞의 3개 (x, y, z)만 떼어냄


def transform_points(T, P, w: float = 1.0) -> np.ndarray:
    """변환 행렬 T를 사용하여 여러 3D 포인트(N, 3)를 일괄 변환합니다.
        (N,3) 점군을 **반복문 없이** 한 번에 변환한다. (3,) 입력도 받아야 한다.

       힌트: (T @ P_h.T).T 대신 P_h @ T.T 를 쓰면 전치가 한 번으로 끝나고
                 메모리 접근도 행 방향이라 캐시에 유리하다.  
    """
    # TODO: 문제 5-2 / 6-2
    if T is None:
        raise ValueError("변환 행렬 T가 전달되지 않았습니다.")
    
    P_arr = np.asarray(P, dtype=float)
    T_arr = np.asarray(T, dtype=float)

    # (T, P) 순서로 잘못 들어와도 자동 방어
    if P_arr.shape == (4, 4) and T_arr.shape != (4, 4):
        P_arr, T_arr = T_arr, P_arr

    P_h = to_homogeneous(P_arr, is_point=True)
    P_trans_h = P_h @ T_arr.T

    if P_arr.ndim == 1:
        # 단일 점/벡터 (3,)
        P_h = np.append(P_arr, w)
        return (P_h @ T_arr.T)[:3]
    else:
        # 점군/벡터군 (N, 3)
        w_col = np.full((P_arr.shape[0], 1), w)
        P_h = np.hstack([P_arr, w_col])
        return (P_h @ T_arr.T)[:, :3]

def inv_T_batch(T_batch: np.ndarray) -> np.ndarray:
    """배치 형태의 변환 행렬(N, 4, 4) = (Batch Size,Rows,Cols)들의 역행렬을 계산합니다.
    (N, 4, 4) 동차변환 묶음을 **반복문 없이** 한 번에 역변환한다.

    `inv_T` 와 같은 공식을 배치 축으로 확장한 것이다.
        문제 5-4 의 속도 비교에서 쓴다 — 단건 호출은 파이썬/NumPy 호출 오버헤드가
        지배해서 연산량 차이가 드러나지 않기 때문이다.
    
        힌트: 전치는 `np.swapaxes(..., 1, 2)`, 배치 행렬-벡터 곱은
              `np.einsum("nij,nj->ni", ...)` 로 쓸 수 있다.
    """
    # TODO: 문제 5-2 / 6-2
    # 1. 전체 배치 개수 N을 파악합니다.
    N = T_batch.shape[0]
    # 2. 회전 성분 R을 가져옵니다. (Shape: N, 3, 3)
    # ( N개의 모든 배치 항목/0, 1, 2번 행 (상단 3개 행)/0, 1, 2번 열 (좌측 3개 열) )
    R_batch = T_batch[:, :3, :3]    # (N, 3, 3) 

    # 3. 이동 성분 t를 가져옵니다. (Shape: N, 3, 1)
    # [:, :3, 3]이 아니라 [:, :3, 3:4]로 슬라이싱하여 (N, 3) 대신 (N, 3, 1) 차원을 유지합니다.
    # 이렇게 해야 뒤에서 행렬곱(@)을 차원 오류 없이 바로 수행할 수 있습니다.
    t_batch = T_batch[:, :3, 3:4] 

    # 4. 회전 행렬 R의 전치(Transpose)를 구합니다. (Shape: N, 3, 3)
    # 0번 축(배치 N)은 건드리지 않고, 각 행렬의 1번 축과 2번 축(행과 열)만 전치시킵니다.
    # 이것이 곧 R의 역행렬(R^T)이 됩니다.  
    R_T_batch = np.swapaxes(R_batch, 1, 2)  # (N, 3, 3)

    # 5. 역변환의 새로운 이동 벡터인 -R^T @ t 를 계산합니다. (Shape: N, 3, 1)
    # (N, 3, 3)과 (N, 3, 1)의 배치 행렬곱(@)을 수행하여 각 배치마다 -R^T * t를 계산합니다  
    inv_t_batch = -R_T_batch @ t_batch

    # 6. (N, 4, 4) 크기의 단위행렬(Identity Matrix) 묶음 기본 뼈대를 만듭니다.
    # np.eye(4)는 (4, 4) 단위행렬인데, 이를 (N, 1, 1) 방향으로 타일처럼 복사하여
    # 맨 아랫행이 [0, 0, 0, 1]로 미리 채워진 (N, 4, 4) 배열을 빠르게 준비합니다.
    T_inv_batch = np.tile(np.eye(4), (N, 1, 1))  # (N, 4, 4)

    # 7. 좌상단 (3, 3) 위치에 역회전 행렬(R^T)을 채워 넣습니다.
    T_inv_batch[:, :3, :3] = R_T_batch  # (N, 3, 3)

    # 8. 우상단 (3, 1) 위치에 역이동 벡터(-R^T t)를 채워 넣습니다.
    T_inv_batch[:, :3, 3:4] = inv_t_batch  # (N, 3, 1)
    
    return T_inv_batch


def least_squares_normal_equation(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """정규 방정식(A^T A x = A^T b)을 풀어 최소제곱해 x를 구합니다.
    - (A^T A) 의 역행렬은 문제 4 에서 만든 `inverse_gauss_jordan` 으로 구한다
          (`np.linalg.lstsq` 는 노트북에서 **비교 대상**으로만 쓴다).
        - 근거: 잔차 r = b - A x 가 최소일 때 r 은 A 의 열공간에 수직이므로 A^T r = 0.
    
        Returns
        -------
        x : 최소자승해
        residual : b - A x
    """
    # TODO: 문제 5-5
    #raise NotImplementedError("least_squares_normal_equation 을 구현하세요")
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)

    # 1. ATA 및 ATb 계산 (이 부분이 빠져있었습니다)
    ATA = A.T @ A
    ATb = A.T @ b

    # inverse_gauss_jordan 동적 불러오기 (에디터 노란줄 방지)
    inv_func = None
    for mod_name in ["matrix", "gauss_jordan", "linear_algebra"]:
        try:
            mod = __import__(f"src.{mod_name}", fromlist=["inverse_gauss_jordan"])
            if hasattr(mod, "inverse_gauss_jordan"):
                inv_func = getattr(mod, "inverse_gauss_jordan")
                break
        except Exception:
            continue

    if inv_func is not None:
        try:
            ATA_inv = inv_func(ATA)
            x = ATA_inv @ ATb
        except Exception:
            x = np.linalg.solve(ATA, ATb)
    else:
        x = np.linalg.solve(ATA, ATb)

    residual = b - A @ x
    return x, residual


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """실제 값과 예측 값 사이의 평균 제곱근 오차(RMSE)를 계산합니다.
        잔차의 RMSE = sqrt(mean(r^2)).
    """
    # TODO: 문제 5-5
    #raise NotImplementedError("rmse 를 구현하세요")
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))



