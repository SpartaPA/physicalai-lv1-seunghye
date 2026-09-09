"""문제 2 — PosePipeline 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 "2개 이상" 을 아래 두 테스트로 채운다.

  1. camera_to_base 가 모듈 ③ 체인(행렬 곱)과 같은 결과를 주는가  -> test_camera_to_base_matches_chain
  2. base 로 갔다가 camera 로 되돌리면 원래 점군이 나오는가       -> test_roundtrip_restores_points

작성 요령
--------
- 비교는 `np.allclose` (기본 허용오차) 로 한다.
- 난수는 반드시 시드를 고정한다 (fixture `rng`).
- 관절 각도 0 에서 파이프라인이 default_chain 과 같은지, 각도를 바꾸면 결과가 달라지는지 등
  테스트를 더 붙이면 좋다 (아래 권장 예시).

실행: 프로젝트 루트에서  pytest tests/test_pose_pipeline.py -v
"""
import sys
from pathlib import Path
# 프로젝트 루트 경로를 sys.path에 강제로 추가 (src 모듈 인식 불가 해결)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest

from src.coordinate_chain import default_chain
from src.pose_pipeline import PosePipeline
from src.transform import make_T, transform_points
from src.rotation import rot_x, rot_y, rot_z


@pytest.fixture
def rng():
    """난수는 반드시 시드를 고정한다."""
    return np.random.default_rng(42)


@pytest.fixture
def pipeline():
    """모듈 ③ default_chain 과 같은 값으로 만든 파이프라인."""
    chain = default_chain()
    return PosePipeline(chain.get("base", "link"), chain.get("link", "camera"))


# --- 1. camera_to_base == 체인/행렬 곱 --------------------------------------

def test_camera_to_base_matches_chain(pipeline, rng):
    # TODO: (N,3) 점군을 만들어 pipeline.camera_to_base 결과가
    #       default_chain().transform("base", "camera", P) 및
    #       transform_points(T_base_link @ T_link_camera, P) 와 같은지 검사
    #raise NotImplementedError("test_camera_to_base_matches_chain 을 작성하세요")
    
    # 1. 시드가 고정된 난수로 (N,3) 점군 생성
    P_cam = rng.normal(0.0, 1.0, (100, 3))

    # 2. PosePipeline 변환
    P_base_pipe = pipeline.camera_to_base(P_cam)

    # 3. CoordinateChain 변환
    P_base_chain = default_chain().transform("base", "camera", P_cam)

    # 4. T_base_link @ T_link_camera 직접 행렬 곱 변환 (인자 순서: T, P)
    T_base_cam = pipeline.T_base_link @ pipeline.T_link_camera
    P_base_matmul = transform_points(T_base_cam, P_cam)

    # 5. 세 결과 일치 검증
    assert np.allclose(P_base_pipe, P_base_chain)
    assert np.allclose(P_base_pipe, P_base_matmul)

# --- 2. 왕복 검증 -------------------------------------------------------------

def test_roundtrip_restores_points(pipeline, rng):
    # TODO: P_cam -> camera_to_base -> base_to_camera 가 P_cam 과 같은지 (allclose) 검사
    #       (3,) 단일 점과 (N,3) 점군 둘 다 확인
    #raise NotImplementedError("test_roundtrip_restores_points 를 작성하세요")

    # 1. (N,3) 점군 왕복 검증
    P_cam_pts = rng.normal(0.0, 1.0, (100, 3))
    P_base_pts = pipeline.camera_to_base(P_cam_pts)
    P_restored_pts = pipeline.base_to_camera(P_base_pts)
    assert np.allclose(P_restored_pts, P_cam_pts)

    # 2. (3,) 단일 점 왕복 검증
    p_cam_single = rng.normal(0.0, 1.0, 3)
    p_base_single = pipeline.camera_to_base(p_cam_single)
    p_restored_single = pipeline.base_to_camera(p_base_single)
    assert np.allclose(p_restored_single, p_cam_single)

# --- 여기부터는 추가 테스트 (권장) -------------------------------------------
#
# 예) def test_joint_angle_zero_is_nominal(pipeline):
#         """set_joint_angle(0) 이면 T_base_link 가 생성자에 준 값 그대로."""
def test_joint_angle_zero_is_nominal(pipeline):
    chain = default_chain()
    T_nominal = chain.T("base", "link") if hasattr(chain, "T") else chain.get("base", "link")

    pipeline.set_joint_angle(0.0)
    assert np.allclose(pipeline.T_base_link, T_nominal)

#
# 예) def test_joint_angle_changes_result(pipeline, rng):
#         """관절 각도를 바꾸면 같은 관측이 base 에서 다른 위치로 간다."""
def test_joint_angle_changes_result(pipeline, rng):
    P_cam = rng.normal(0.0, 1.0, (50, 3))

    pipeline.set_joint_angle(0.0)
    P_base_0 = pipeline.camera_to_base(P_cam)

    pipeline.set_joint_angle(np.deg2rad(30.0))
    P_base_30 = pipeline.camera_to_base(P_cam)

    # 관절 각도가 바뀌었으므로 결과 좌표가 달라져야 함
    assert not np.allclose(P_base_0, P_base_30)

#
# 예) def test_distance_is_preserved(pipeline, rng):
#         """강체 변환은 두 점 사이 거리를 보존한다."""
def test_distance_is_preserved(pipeline, rng):
    P_cam = rng.normal(0.0, 1.0, (20, 3))
    P_base = pipeline.camera_to_base(P_cam)

    d_cam = np.linalg.norm(P_cam[1:] - P_cam[:-1], axis=1)
    d_base = np.linalg.norm(P_base[1:] - P_base[:-1], axis=1)

    assert np.allclose(d_cam, d_base)
#
# 예) def test_rejects_wrong_shape():
#         """(3,3) 을 넣으면 ValueError."""
def test_rejects_wrong_shape():
    wrong_T = np.eye(3)
    valid_T = np.eye(4)

    with pytest.raises(ValueError):
        PosePipeline(wrong_T, valid_T)

    with pytest.raises(ValueError):
        PosePipeline(valid_T, wrong_T)