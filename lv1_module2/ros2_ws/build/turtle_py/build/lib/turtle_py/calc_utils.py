import math

#두 좌표간 피타고라스 유클리드 거리가 정확히 계산되는지 (음수, 동일점 경계값 포함) 검증.
def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """두 점 사이의 거리를 계산"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

#연산 후 결과각이 -pi ~ pi 범위로 정상 정규화(Normalization)되는지 검증.
def calculate_angle(x1: float, y1: float, x2: float, y2: float) -> float:
    """목표를 향한 각도를 계산하고 -pi ~ pi 로 정규화"""
    angle = math.atan2(y2 - y1, x2 - x1)
    # -pi ~ pi 정규화
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle

#지정된 오차 범위(tolerance) 이내 진입 시 True 반환 여부 및 잘못된 tolerance(<=0) 입력 시 ValueError 예외 발생 검증.
def is_waypoint_reached(current_x: float, current_y: float, target_x: float, target_y: float, tolerance: float = 0.1) -> bool:
    """허용 오차(tolerance) 이내 도달 여부 판정"""
    if tolerance <= 0:
        raise ValueError("Tolerance must be positive")
    dist = calculate_distance(current_x, current_y, target_x, target_y)
    return dist <= tolerance