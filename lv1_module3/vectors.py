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
    ref , pivots = row_echelon(matrix)

    # np.abs(ref): 절대값을 취함
    # .sum(axis=1):각 행(가로줄)별로 원소들을 다 더함(axis=1은 가로 방향 합)
    # 1e-9: 합이 0이 아닌 (살아있는) 행을 True로 판별
    # np.sum(...): True의 개수를 세어서 살아있는 행의 개수(Rank)를 구함.
    non_zero_rows = np.sum(np.abs(ref).sum(axis=1) > 1e-9)

    return non_zero_rows

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
    return np.cross(a,b)

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
def row_echelon(matrix):
    """가우스 소거법을 통해 행 사다리꼴(REF)과 피벗 열 인덱스를 반환합니다."""
    # matrix.copy(): 원본 행렬 M이 수정되지 않도록 데이터 복사본을 만듭니다.
    #.astype(float): 정수가 섞여 있을 수 있으므로 나눗셈 연산을 위해 소수점(실수) 타입으로 변환합니다.
    A = matrix.copy().astype(float)

    #A.shape: 행렬의 크기를(행 개수, 열 개수) 형태의 튜플로 가져옵니다. (3,3)
    rows, cols = A.shape
    print("rows:: ", rows,"  cols:: ",cols)
    pivots = []
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
        if np.abs(A[max_row , c]) <1e-9: 
            continue

        # --- [행 교환 (Row Swapping)] ---
        # A[[r, max_row]] = A [[max_row, r]] : r번째 행과 가장 큰 숫자가 있던 max_row번째 행의 위치를 서로 바꿉니다.
        A[[r, max_row]] = A [[max_row, r]]
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
    A[np.abs(A) < 1e-9] = 0.0

    return A , pivots

# --- [2] 행렬식(Determinant) 계산 함수 ---
# [역할] 3x3 행렬 M이 공간을 얼마나 팽창/축소시키는지 나타내는 '부피 변화율' 수치를 구합니다.
def det(matrix):
    #3x3 행렬의 각 위치 원소를 변수에 나누어 담습니다.
    a,b,c = matrix[0]
    d,e,f = matrix[1]
    g,h,i = matrix[2]
    #샤루스 공식을 그대로 대입하여 3D 부피(행렬식)를 구합니다. 
    return a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)
    #return float(np.linalg.det(matrix))  # np.linalg.det: NumPy 내부의 행렬식 계산 함수를 실행하여 소수점(float)으로 반환
