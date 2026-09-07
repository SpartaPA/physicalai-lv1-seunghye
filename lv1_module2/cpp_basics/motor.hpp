#pragma once //헤더 파일이 다른 파일에서 여러 번 불러와지더라도 컴파일러가 중복해서 해석하지 않도록 막는 방어 장치입니다.

//설계도(헤더), 구현체(cpp), 사용부(main) 3개 파일로 분리
//motor.hpp (헤더 파일 — 설계도)

class Motor {
private:
    double speed; // 속도(m/s) : 내부 속도 데이터(외부 접근 불가)

public:
    Motor();
    void setSpeed(double speed);
    double getSpeed() const;
};