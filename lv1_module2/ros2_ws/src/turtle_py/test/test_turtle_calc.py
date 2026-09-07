import math
import pytest
from turtle_py.calc_utils import calculate_distance, calculate_angle, is_waypoint_reached

# 1. 거리 계산 테스트 (정상값, 경계값)
def test_calculate_distance():
    assert calculate_distance(0, 0, 3, 4) == pytest.approx(5.0)
    assert calculate_distance(1.1, 1.1, 1.1, 1.1) == pytest.approx(0.0)
    assert calculate_distance(-1, -1, -4, -5) == pytest.approx(5.0)

# 2. 각도 정규화 테스트 (정상, 경계 -pi ~ pi)
def test_calculate_angle():
    assert calculate_angle(0, 0, 1, 0) == pytest.approx(0.0)
    assert calculate_angle(0, 0, 0, 1) == pytest.approx(math.pi / 2.0)
    assert calculate_angle(0, 0, -1, 0) == pytest.approx(math.pi)

# 3. 경유점 도달 판정 테스트 (허용 오차, 예외 처리)
def test_is_waypoint_reached():
    assert is_waypoint_reached(1.0, 1.0, 1.05, 1.0, tolerance=0.1) is True
    assert is_waypoint_reached(1.0, 1.0, 1.2, 1.0, tolerance=0.1) is False

    # 예외 상황 테스트 (tolerance <= 0)
    with pytest.raises(ValueError):
        is_waypoint_reached(1.0, 1.0, 1.0, 1.0, tolerance=-0.1)