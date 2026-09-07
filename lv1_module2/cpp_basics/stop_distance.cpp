#include <iostream>  //C++ 표준 입출력 도구상자
#include <cmath> 

//자동거리 계산 함수: d = v^2 / (2 * mu * g)
double calculateStoppingDistance(double speed, double friction) {
    const double g = 9.8; // 중력가속도(m.s^2) 값을 변경할 수 없는 '상수'로 지정하여 계산 중 중력가속도 값이 바뀌는 실수를 막습니다.
    return (speed * speed) / (2 * friction * g);    
}

int main() {
    double speed ,friction;
    std::cout << "속도(m/s) 입력: ";
    std::cin >> speed;
    std::cout << "마찰계수 입력: ";
    std::cin >> friction;

    double stop_dist = calculateStoppingDistance(speed, friction);

    std::cout << "속도: " << speed << " m/s" << std::endl;
    std::cout << "마찰계수: " << friction << std::endl;
    std::cout << "제동(정지) 거리: " << stop_dist << " m" << std::endl;
    return 0;
}
