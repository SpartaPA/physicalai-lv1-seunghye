"""문제 6 — 좌표 변환 체인 모듈. (학생 작성용 템플릿)

base -> link -> camera 로 이어지는 동차변환 체인을 구성하고,
카메라 기준 좌표를 로봇 base 기준으로 바꾼다.
모듈 4(픽앤플레이스 미니 프로젝트)에서 그대로 import 해 쓰게 되므로,
공개 함수 이름과 반환 형식을 이 템플릿 그대로 유지한다.
"""

from __future__ import annotations

import numpy as np

from .rotation import axis_angle_from_matrix, rot_x, rot_y, rot_z
from .transform import inv_T, make_T, transform_points

__all__ = ["CoordinateChain", "default_chain", "camera_point_to_base", "base_point_to_camera"]


class CoordinateChain:
    """부모 -> 자식 동차변환을 이름으로 등록하고, 임의의 두 프레임 사이 변환을 만든다.

    TF2 의 축소판이라고 보면 된다.

    Examples
    --------
    >>> chain = CoordinateChain("base")
    >>> chain.add("base", "link", T_base_link)
    >>> chain.add("link", "camera", T_link_camera)
    >>> T = chain.T("base", "camera")     # camera 좌표 -> base 좌표
    """

    def __init__(self, root: str = "base"):
        self.root = root
        self._parent: dict[str, str] = {}                 # child -> parent
        self._T: dict[tuple[str, str], np.ndarray] = {}   # (parent, child) -> T

    def add(self, parent: str, child: str, T) -> "CoordinateChain":
        """parent 기준으로 표현된 child 프레임의 자세 T(parent<-child) 를 등록한다.

        체이닝이 되도록 self 를 돌려준다. 4x4 가 아니면 ValueError.
        """
        T = np.asarray(T, dtype=float)
        if T.shape != (4, 4):
            raise ValueError(f"4x4 동차변환이 필요합니다. 받은 shape={T.shape}")
        self._parent[child] = parent
        self._T[(parent, child)] = T
        return self

    def get(self, parent: str, child: str) -> np.ndarray:
        """등록해 둔 T(parent <- child) 를 그대로 돌려준다."""
        return self._T[(parent, child)]

    def frames(self) -> list[str]:
        """등록된 프레임 이름 목록 (root 포함)."""
        return [self.root] + list(self._parent.keys())

    # ------------------------------------------------------ 여기부터 구현

    def _path_to_root(self, frame: str) -> list[str]:
        """frame 에서 root 까지의 경로 [frame, ..., root] 를 만든다.

        root 에 연결되어 있지 않으면 KeyError.
        """
        """지정한 frame에서 root(base)까지 부모를 타고 올라가는 경로 리스트를 만듭니다.
            예시: 'camera' 입력 시 -> ['camera', 'link', 'base']
        """
        # TODO: 문제 6-1
        path = [frame]

        # 현재 프레임의 부모가 _parent 딕셔너리에 존재하는 동안 계속 부모를 찾아 올라갑니다.
        while path[-1] != self.root:
            if path[-1] not in self._parent:
                raise KeyError(f"프레임 '{path[-1]}'이(가) root('{self.root}')에 연결되어 있지 않습니다.")
            parent = self._parent[path[-1]] # 부모 이름으로 교체
            path.append(parent)             # 경로 리스트에 추가
        return path
        

    def T_from_root(self, frame: str) -> np.ndarray:
        """root(base) 기준으로 해당 frame 의 위치/자세를 나타내는 T(root <- frame)를 계산.

        경로를 따라가며 등록된 변환을 곱한다. 곱하는 **순서**에 주의할 것:
        윗첨자/아랫첨자가 이웃끼리 상쇄되도록 놓으면 틀리지 않는다.
            경로: ['camera', 'link', 'base'] 라면,
            계산: T(base<-camera) = T(base<-link) @ T(link<-camera)
            
        """
        # TODO: 문제 6-1
        path = self._path_to_root(frame)

        # 시작은 아무런 변화도 주지 않는 4x4 단위행렬(Identity Matrix)
        T = np.eye(4)

        # path의 맨 뒤(root)부터 앞으로 오면서 행렬을 순서대로 곱해줍니다.
        # 예: i가 len(path)-1 일 때 -> parent: base, child: link
        for i in range(len(path)-1 ,0 ,-1):
            parent = path[i]
            child = path[i-1]
            T = T @ self.get(parent, child)  # T(parent<-child)를 곱해줍니다.   
        return T    

    def T(self, target: str, source: str) -> np.ndarray:
        """source 좌표를 target 좌표로 바꾸는 변환 T(target <- source).

        힌트: T(target<-source) = inv(T(root<-target)) @ T(root<-source)
        """
        # TODO: 문제 6-1
        # 출발지와 목적지가 같으면 아무것도 바꾸지 않는 단위행렬 반환
        if target == source:
            return np.eye(4)

        T_root_target = self.T_from_root(target)
        T_root_source = self.T_from_root(source)
        T_target_source = inv_T(T_root_target) @ T_root_source
        return T_target_source  

    def transform(self, target: str, source: str, P, w: float = 1.0) -> np.ndarray:
        """source 프레임의 점(w=1) 또는 방향(w=0)을 target 프레임으로 변환한다.

        (3,) 와 (N,3) 을 모두 지원해야 하고, **반복문을 쓰지 않는다**.
        """
        # TODO: 문제 6-2
        T_target_source = self.T(target, source)
        return transform_points(T_target_source, P, w=w)
        #raise NotImplementedError("transform 을 구현하세요")

    def axis_angle(self, target: str, source: str):
        """T(target <- source) 의 회전 부분에서 회전축과 회전각을 복원한다."""
        # TODO: 문제 6-4
        T_target_source = self.T(target, source)
        R = T_target_source[:3, :3]
        return axis_angle_from_matrix(R)
        #raise NotImplementedError("axis_angle 을 구현하세요")

def default_chain() -> CoordinateChain:
    """과제에서 쓸 기본 체인(base -> link -> camera)을 만든다.

    지시문은 '임의의 회전·병진'을 쓰라고 하지만, 채점 수치를 맞추기 위해
    아래 값을 그대로 쓰기를 권장한다. (바꾸려면 노트북에도 그 값을 명시할 것)

    base -> link   : z축 30도 회전 후 (0.30, 0.00, 0.40) m 이동
    link -> camera : y축 -20도, x축 90도 회전(y 먼저 곱함) 후 (0.10, 0.05, 0.15) m 이동
    """
    # TODO: 문제 6-1
    #   T_base_link   = make_T(rot_z(...), [...])
    #   T_link_camera = make_T(rot_y(...) @ rot_x(...), [...])
    #   return CoordinateChain("base").add(...).add(...)
    chain = CoordinateChain("base")

    # 1. base -> link : z축 30도 회전 후 (0.30, 0.00, 0.40) m 이동
    T_base_link = make_T(rot_z(np.deg2rad(30)) , [0.30, 0.00, 0.40])
    chain.add(parent="base", child="link", T=T_base_link)

    # 2. link -> camera : y축 -20도, x축 90도 회전 후 (0.10, 0.05, 0.15) m 이동
    T_link_camera = make_T(rot_y(np.deg2rad(-20)) @ rot_x(np.deg2rad(90)), [0.10, 0.05, 0.15])
    chain.add(parent="link", child="camera", T=T_link_camera)

    return chain


def camera_point_to_base(p_cam, chain: CoordinateChain | None = None) -> np.ndarray:
    """카메라 기준 좌표 -> base 기준 좌표. (3,) 와 (N,3) 모두 지원.

    chain 이 None 이면 default_chain() 을 쓴다.
    """
    # TODO: 문제 6-1
    if chain is None:
        chain = default_chain()

    return chain.transform("base", "camera", p_cam)
    #raise NotImplementedError("camera_point_to_base 를 구현하세요")

def base_point_to_camera(p_base, chain: CoordinateChain | None = None) -> np.ndarray:
    """base 기준 좌표 -> 카메라 기준 좌표. 왕복 검증(문제 6-2)에 쓴다."""
    # TODO: 문제 6-2
    if chain is None:
        chain = default_chain()
    return chain.transform("camera", "base", p_base)
    #raise NotImplementedError("base_point_to_camera 를 구현하세요")
