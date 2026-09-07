#include "motor.hpp"
#include <iostream> 

//설계도(헤더), 구현체(cpp), 사용부(main) 3개 파일로 분리
//motor.cpp (소스 파일 — 실제 동작 코드)

//Motor::: "이 함수는 Motor 설계도 안에 명시했던 그 함수의 실제 알맹이 코드다"라고 소속을 밝히는 구문입니다.
Motor::Motor() : speed(0.0) {} // 생성자: 속도를 0으로 초기화

void Motor::setSpeed(double speed) {
    this->speed = speed; // 외부에서 입력받은 속도 값을 내부 속도 데이터에 저장
    std::cout << "[Motor] 속도 설정: " << speed << " RPM " << std::endl; // 속도 설정 시 콘솔에 출력
}

double Motor::getSpeed() const {
    return speed; // 내부 속도 데이터를 외부로 반환
}   