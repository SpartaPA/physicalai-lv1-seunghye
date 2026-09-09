from __future__ import  annotations
import numpy as np

#from .vectors import det, normalize,skew
#import sys,os
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


#pivot_cols : list[int]

# 파일 밖에서 공식적으로 공개할 함수의 목록을 작성된 것.
__all__ = [
    "angle_between",
    "cross",
    "det",
    "dot",
    "gauss_eliminate",
    "inverse_gauss_jordan",
    "norm",
    "normalize",
    "plane_normal", 
    "project", 
    "rank",
    "reject",
    "row_echelon",
    "skew"
]

#-----------연습
#--------------------기본연산
#numpy Array
def as_vector(v) -> np.ndarray:
    """입력을 1차원 float배열로 변환한다."""
    arr = np.asarray(v, dtype=float)
    #ndim 차원을 계산함
    if arr.ndim != 1:
        raise ValueError(f"1차원 벡터가 필요합니다. 받은 shape={arr.shape}")
    return arr

#함수명 = dot
#입력 파라미터 a,b
#반환을 실수로 하겠다고 선언
def dot(a,b) -> float:
    """내적 .sum(a_i * b_i)를 직접 계산한다."""
    a,b = as_vector(a), as_vector(b)

    if a.shape != b.shape:
        raise ValueError(f"차원이 다릅니다 : {a.shape} vs {b.shape}")
    return float(np.sum(a*b))

def norm(v) -> float:
    """유클리드 노름. sqrt(v.v)"""
    return float(np.sqrt(dot(v,v)))

#degrees:bool =True-> 기본값은 True
def angle_between(a,b,degrees: bool = True) -> float:
    """두 벡터 사이각"""
    # 1. 분모 전체를 괄호로 감싸기
    cos_theta = dot(a, b) / (norm(a) * norm(b))

    # 2. 부동소수점 오차로 인한 np.arccos(-1~1 범위 초과) 에러 방지
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    angle = np.arccos(cos_theta)
   
    # 3. degrees 플래그에 따라 '각도 값'을 반환
    if degrees:
        return np.degrees(angle)  # 90.0 (float) 반환
    else:
        return angle # 라디안 (float) 반환

#1-2정규화 함수를 만들고 영벡터를 넣으면 어떻게 되는지 직접 실행해 기록한 뒤 처리 방식을 정해 구현
def normalize(v, eps:float = 1e-10):
    """입력벡터 v를 단위 벡터로 정규화 합니다.
        Parameters:
            v(array-like):정규화 할 입력 벡터
            eps(float): 영벡터 판단 기준 허용 오차 (기본값: 1e-10)
        Returns:
            np.ndarray: 길이가 1인 단위 벡터(영벡터 입력 시 영벡터 반환)
    """
    v = as_vector(v)
    #v = np.array(v, dtype=float)

    # 벡터 크기 구하기
    norm_val = norm(v)

    #검산용 np.linalg.norm 결과와 일치하는지 확인 가능
    #norm_check = np.linalg.norm(v) # [검산용]

    if norm_val < eps:
        return np.zeros_like(v)
    
    return v/norm_val

#1-3 정사영을 구현하고 1 남는 성분이 수직인지 2 두 성분의 합이 원해 벡터인지 검증
def project(a,b)-> float:
    v1 = dot(a,b)/dot(b,b)
    pjt = v1*b
    
    return pjt

def reject(a,b)-> float:
    rjt = a - project(a,b) 
    return rjt

def rank(matrix):
    #구현한 가우스 소거법 함수를 호출하여 행 사다리꼴(ref)을 얻습니다.
    ref, pivots, _ = row_echelon(matrix)

    # np.abs(ref): 절대값을 취함
    # .sum(axis=1):각 행(가로줄)별로 원소들을 다 더함(axis=1은 가로 방향 합)
    # 1e-9: 합이 0이 아닌 (살아있는) 행을 True로 판별
    # np.sum(...): True의 개수를 세어서 살아있는 행의 개수(Rank)를 구함.
    non_zero_rows = np.sum(np.abs(ref).sum(axis=1) > 1e-9)

    return int(non_zero_rows)

#1-4 외적을 반대칭행렬 곱으로 구현하고 np.cross와 비교, 반대칭성 검증
# --- [1] 스큐 행렬(Skew-symmetric Matrix) 생성 함수 ---
# [역할] 3D 벡터 v = [x, y, z]를 대각선이 0인 3x3 형태의 특수 행렬로 바꿉니다.
# [이유] 로드리게스 회전 공식에서 벡터 간의 '외적(Cross Product)' 계산을 파이썬 행렬 곱셈(@)으로 쉽게 처리하기 위해 사용합니다.
def skew(a):
    """ 3차원 벡터 a를 반대칭행렬(skew-symmetric matrix)로 변환합니다.
        skew(a) @ b == np.cross(a,b)관계가 성립합니다.
    """
    # 입력 벡터를 float 타입 numpy배열로 변환
    a= np.asarray(a, dtype=float)

    #각성분 추출(a1,a2,a3)
    a1,a2,a3 = a[0],a[1],a[2]

    #3x3 반대칭 행렬 생성 및 반환
    return np.array([
        [0, -a3, a2],
        [a3, 0, -a1],
        [-a2,a1, 0]
    ])

def cross(a,b):
    return skew(a) @ as_vector(b)

#1-5 세 점이 만드는 편면의 단위 법선
def plane_normal(P1,P2,P3):
    """세 점 P1,P2,P3가 만드는 평면의 단위 법선 벡터를 반환합니다."""
    P1 = as_vector(P1)
    P2 = as_vector(P2)
    P3 = as_vector(P3)
    u = P2 - P1
    v = P3 - P1

    return normalize(np.cross(u, v))

#1-6 (1,0,1),(1,1,2)의 rank를 구하고 왜 3이 아닌지 설명, 행렬식과 일관성 확인
def row_echelon(matrix, tol: float = 1e-9):
    """가우스 소거법을 통해 행 사다리꼴(REF)과 피벗 열 인덱스를 반환합니다.

    Parameters
    ----------
    matrix : array-like, shape (rows, cols)
    tol : 피벗 판정 임계값

    Returns
    -------
    A : np.ndarray — 행 사다리꼴 (REF)
    pivots : list[int] — 피벗 열 인덱스
    n_swaps : int — 행 교환 횟수
    """
    # matrix.copy(): 원본 행렬 M이 수정되지 않도록 데이터 복사본을 만듭니다.
    #.astype(float): 정수가 섞여 있을 수 있으므로 나눗셈 연산을 위해 소수점(실수) 타입으로 변환합니다.
    A = np.asarray(matrix, dtype=float).copy()

    #A.shape: 행렬의 크기를(행 개수, 열 개수) 형태의 튜플로 가져옵니다. (3,3)
    rows, cols = A.shape
    pivots = []
    n_swaps = 0
    r = 0 # 현재 처리중인 행(줄) 번호

    #열(c)을 왼쪽에서 오른쪽으로 하나씩 순회합니다.
    for c in range(cols):
        if r >= rows:
            break
        # ----[피벗(대장숫자) 찾기 과정] ---
        # A[r: , c] : r번째 줄부터 맨 아래 줄까지, c번째 열에 있는 숫자들만 잘라냅니다.
        # np.abs(...): 부호(-/+)에 상관없이 크기만 비교하기 위해 절댓값을 취합니다.
        # np.argmax(...): 절대값이 가장 큰 숫자가 있는 "잘라낸 조각 내 위치(0,1,2...)"를 찾습니다.
        # + r : 잘라낸 조각의 위치 번호를 전체 행렬의 기준의 '진짜 행 번호'로 변환하기 위해 r을 더합니다.
        max_row = np.argmax(np.abs(A[r: , c]))+ r

        #가장 큰 절대값이 0에 가깝다면 (0.000000001보다 작다면) 0이면 continue
        #이 열에는 대장으로 쓸 수 있는 숫자가 없으므로 다음 열로 넘어갑니다.
        if np.abs(A[max_row , c]) < tol: 
            continue

        # --- [행 교환 (Row Swapping)] ---
        # A[[r, max_row]] = A [[max_row, r]] : r번째 행과 가장 큰 숫자가 있던 max_row번째 행의 위치를 서로 바꿉니다.
        if max_row != r:
            A[[r, max_row]] = A [[max_row, r]]
            n_swaps += 1
        pivots.append(c) #피벗이 존재하는 열 번호를 기록합니다.

        # --- [아래쪽 행 소거 (0으로 만들기)] ---
        # r번째 행 아래에 있는 행들(i)을 하나씩 처리합니다.
        for i in range(r+1, rows):
            #factor: 피벗 아래 숫자를 0으로 만들기 위해 곱해야 하는 비율을 계산합니다.
            factor = A[i,c]/A[r,c]

            #A[i, c:]: i번째 행의 c번째 칸부터 끝까지의 숫자들에서
            #(r번째 행의 c번째 칸부터 끝까지의 숫자들 * factor)를 빼서 0으로 만듭니다.
            A[i, c:] -= factor * A[r,c:]
        r += 1 # 다음 줄(행)로 이동

    # --- [부동소수점 오차 정리] ---
    # np.abs(A) < 1e-9: 행렬 원소 중 0.000000001보다 작은 원소들을 True, 나머지를 False로 판별하는 마스크를 만듭니다.
    # A[...] = 0.0: True인 위치의 숫자를 깔끔하게 완전한 0.0으로 바꿔줍니다.(-0.0 제거).
    A[np.abs(A) < tol] = 0.0

    return A, pivots, n_swaps

# --- [2] 행렬식(Determinant) 계산 함수 ---
# [역할] n x n 행렬이 공간을 얼마나 팽창/축소시키는지 나타내는 '부피 변화율' 수치를 구합니다.
# 행 사다리꼴의 대각성분 곱 x (-1)^(행 교환 횟수) 로 구합니다.
def det(matrix):
    """행렬식을 row_echelon 기반으로 구한다 (임의의 n x n 지원).

    det = (-1)^n_swaps * prod(diag(U)).
    특이행렬이면 대각에 0이 나타나 0을 반환한다.
    """
    A = np.asarray(matrix, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError(f"정방행렬이 필요합니다. 받은 shape={A.shape}")
    n = A.shape[0]
    if n == 0:
        return 1.0
    if n == 1:
        return float(A[0, 0])
    # det 전용 소거: row_echelon 의 1e-9 zeroing 이 작은 det 를 삼키지 않도록
    # 별도 루프에서 부분 피벗팅 + 임계값 없이 계산한다.
    M = A.copy()
    n_swaps = 0
    for k in range(n):
        piv = int(np.argmax(np.abs(M[k:, k])) + k)
        if M[piv, k] == 0.0:
            return 0.0
        if piv != k:
            M[[k, piv]] = M[[piv, k]]
            n_swaps += 1
        for i in range(k + 1, n):
            factor = M[i, k] / M[k, k]
            M[i, k:] -= factor * M[k, k:]
    return float(((-1) ** n_swaps) * np.prod(np.diag(M)))


def gauss_eliminate(A, b, pivoting: bool = True, verbose: bool = False, tol: float = 1e-12):
    """가우스 소거법(전진 소거 + 후진 대입)으로 Ax = b 를 푼다.

    Parameters
    ----------
    A : (n, n) 계수행렬
    b : (n,) 우변 벡터
    pivoting : True 면 부분 피벗팅(각 열에서 절댓값 최대 행을 위로),
               False 면 행 교환 없이 현재 행을 피벗으로 사용
    verbose : True 면 초기 첨가행렬과 각 단계(행 교환 / 소거)의 첨가행렬을 모두 출력
    tol : 특이 판정 임계값

    Returns
    -------
    x : (n,) 해 벡터
    steps : list of (n, n+1) 첨가행렬 — steps[0] 은 초기 [A|b],
            이후 행 교환 직후와 각 열 소거 직후의 복사본을 순서대로 담는다.
    """
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float).reshape(-1)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError(f"정방행렬이 필요합니다. 받은 shape={A.shape}")
    n = A.shape[0]
    if b.shape != (n,):
        raise ValueError(f"b 의 shape 이 맞지 않습니다: {b.shape} vs ({n},)")
    M = np.hstack([A.copy(), b.reshape(-1, 1)])
    steps = [M.copy()]
    if verbose:
        print("[초기 첨가행렬 [A|b]]")
        print(M)

    for k in range(n):
        if pivoting:
            piv = int(np.argmax(np.abs(M[k:, k])) + k)
            if abs(M[piv, k]) < tol:
                raise ValueError("행렬이 특이행렬에 가깝습니다 (피벗 ~0).")
            if piv != k:
                M[[k, piv]] = M[[piv, k]]
                steps.append(M.copy())
                if verbose:
                    print(f"[행 교환: {k}행 <-> {piv}행 (부분 피벗팅)]")
                    print(M)
        else:
            if M[k, k] == 0.0:
                raise ValueError("피벗이 0 입니다 (pivoting=False 에서는 교환하지 않음).")
        # k열 아래쪽 소거
        for i in range(k + 1, n):
            factor = M[i, k] / M[k, k]
            M[i, k:] -= factor * M[k, k:]
        steps.append(M.copy())
        if verbose:
            print(f"[소거 단계 k={k} — {k}열 아래를 0으로]")
            print(M)

    # 후진 대입
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        if M[i, i] == 0.0:
            raise ValueError("후진 대입 중 0 피벗을 만났습니다 (특이행렬).")
        x[i] = (M[i, -1] - float(M[i, i + 1:n] @ x[i + 1:])) / M[i, i]
    return x, steps


def inverse_gauss_jordan(A, verbose: bool = False, tol: float = 1e-12):
    """가우스-조던 소거 [A|I] -> [I|A^-1] 로 역행렬을 구한다."""
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError(f"정방행렬이 필요합니다. 받은 shape={A.shape}")
    n = A.shape[0]
    M = np.hstack([A.copy(), np.eye(n)])
    if verbose:
        print("[초기 [A|I]]")
        print(M)
    for k in range(n):
        piv = int(np.argmax(np.abs(M[k:, k])) + k)
        if abs(M[piv, k]) < tol:
            raise ValueError("행렬이 특이행렬에 가깝습니다 (역행렬 없음).")
        if piv != k:
            M[[k, piv]] = M[[piv, k]]
            if verbose:
                print(f"[행 교환: {k}행 <-> {piv}행]")
                print(M)
        # 피벗 행 정규화
        M[k, :] /= M[k, k]
        if verbose:
            print(f"[피벗 행 {k} 정규화]")
            print(M)
        # 다른 모든 행 소거
        for i in range(n):
            if i == k:
                continue
            factor = M[i, k]
            if factor != 0.0:
                M[i, :] -= factor * M[k, :]
        if verbose:
            print(f"[조던 소거 k={k} — {k}열의 다른 행을 0으로]")
            print(M)
    return M[:, n:].copy()
