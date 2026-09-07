#include "motor.hpp"
#include <iostream>

//설계도(헤더), 구현체(cpp), 사용부(main) 3개 파일로 분리
//main.cpp (실행 파일 — 모터 조작부)

int main() {
    Motor motor; // Motor 객체 생성

    double speed;
    std::cout << "모터 속도(RPM) 입력: ";
    std::cin >> speed;

    motor.setSpeed(speed); // 모터 속도 설정
    std::cout << "현재 모터 속도: " << motor.getSpeed() << " RPM" << std::endl; // 현재 모터 속도 출력

    return 0;
}