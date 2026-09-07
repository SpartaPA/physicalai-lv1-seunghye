#include <iostream>  //C++ 표준 입출력 도구상자
#include <vector>    //C++ 표준 벡터 컨테이너
#include <memory>    //C++ 표준 스마트 포인터
#include <unordered_map> //C++ 표준 해시맵 컨테이너
#include <algorithm> //C++ 표준 알고리즘 라이브러리
#include <string>    //C++ 표준 문자열 라이브러리

//1. 값 범위 자르기 함수 템플릿 (double,int 모두 적용 가능)
template <typename T>
T clamp(T value, T min, T max) {
    if (value < min) return min;
    if (value > max) return max;
    return value;
}
//===============================================
//2. 부모 추상 클래스 Sensor 정의
//로봇에 장착되는 센서들의 공통 기능을 정의하는 추상 클래스
//===============================================
class Sensor {
    protected: // 본인과 상속받을 자식들만 접근 가능.
        std::string name; // 센서 이름
    public: // 생성자 및 소멸자
        // 생성자: 객체가 만들어질 때 가장 먼저 실행되어 이름을 초기화
        // name(name) 부분은 '멤버 초기화 리스트'로 변수에 값을 넣어줌.
        Sensor(const std::string& name) : name(name) {} 
        
        //[가상 소멸자] virtual 키워드가 붙은 소멸자
        // 자식 객체가 메모리에서 사라질 때 자식의 소멸자까지 안전하게 불러주어
        // 메모리가 남아있는 버그(메모리누수)를 방지합니다.
         virtual ~Sensor() {
            std::cout << "[Sensor] 부모 소멸자 실행: " << name << "메모리 해제됨" <<  std::endl;
        }

        // [순수 가상 함수]
        // 함수 끝에 '=0'을 붙임. 알맹이(몸통)가 없는 함수.
        // 이 문장 하나로 Sensor 클래스는 추상 클래스가 되며, 자식 클래스에서 반드시 구현해야 하는 강제성을 부여합니다.
        // "자식 클래스들아, 너희가 알아서 read() 함수를 구현해라!"하고 강제한 규칙.
        virtual double read() = 0; 
        
        std::string getName() const { return name; } // 센서 이름 반환
};        
//===============================================
//3. 자식클래스 Lidar 정의
// public sensor: 부모 클래스 Sensor의 public 멤버를 자식 클래스 Lidar에서도 public으로 사용 가능하게 함.
//===============================================
class Lidar : public Sensor {
    private:
        double distance; // 라이다 센서가 측정한 거리 데이터
        double* raw_buffer; //힙 메모리를 가리킬 변수
    public:
        //부모클래스의 생성자 Sensor(name)을 호출하여 name을 초기화하고, distance를 0.0으로 초기화
        Lidar(const std::string& name) : Sensor(name), distance(0.0) {
            raw_buffer = new double[100]; //생성 시 800바이트 힙 메모리 할당
        } // 생성자: 부모 생성자 호출 및 거리 초기화

        //자식 소멸자: Lidar 객체가 메모리에서 사라질 때 호출되는 소멸자
        ~Lidar() {
            delete[] raw_buffer; // 생성자에서 new double[100]로 할당한 힙 메모리 해제
            std::cout << "[Lidar] 자식 소멸자 실행: " << name << std::endl;
        }

        //override 키워드: "부모가 정해준 규칙 read()를 내가 직접 만든다!" 라고 컴파일러에 알립니다.
        double read() override { 
            distance = 0.25; 
            return distance; 
        }
};
//===============================================
//4. 자식클래스 Imu 정의
//===============================================
class Imu : public Sensor {
    private:
        double acceleration; // IMU 센서가 측정한 가속도 데이터
    public:
        Imu(const std::string& name) : Sensor(name), acceleration(0.0) {} // 생성자: 부모 생성자 호출 및 가속도 초기화
        ~Imu() {
            std::cout << "[Imu] 자식 소멸자 실행: " << name  << std::endl;
        }

        //override 키워드: "부모가 정해준 규칙 read()를 내가 직접 만든다!" 라고 컴파일러에 알립니다.
        double read() override { 
            acceleration = 0.80; 
            return acceleration;
        }
};
//===============================================
//5. 메모리 생성 및 수명 관찰 함수
//스택(Stack)과 힙(Heap) 메모리의 차이를 직접 눈으로 확인하는 함수
//===============================================
void observeMemory() {
    std::cout << "===[관찰 1] 스택 객체 vs 힙 객체 소멸 시점===" << std::endl;
    { //중괄호 {}로 영역(Scope)을 만들어 수명을 제한합니다.
        
        //1)스택 생성: 일반적인 방식으로 변수를 만듭니다.
        Lidar stacklidarSensor("스택_라이다"); // 스택 생성: 중괄호 {}를 벗어나면 자동소멸

        //2)힙 생성 + 스마트 포인터(std:unique_ptr)
        //std::make_unique:힙 메모리에 Lidar를 안전하게 할당하여 만듭니다.
        // 스마트 포인터 변수인 heap_lidar가 이 힙 메모리의 주인이 됩니다.
        std::unique_ptr<Sensor> heapLidarSensor = std::make_unique<Lidar>("힙_스마트포인터_라이다"); // 힙 생성: 중괄호 {}를 벗어나도 소멸되지 않음, 스마트 포인터 사용
        std::cout<< "---중괄호 범위 종료 전 ---" << std::endl;
    }
    
    std::cout << "--- 중괄호 범위 종료 후 ---\n"  << std::endl;
}

//==============================================
//6. 메인 함수(프로그램의 시작점)
//===============================================  
int main() {
    //1) 메모리 수명 관찰 함수 실행
    observeMemory();

    //2) 다형성 루프 및 smart pointer 사용 예제
    //std::vector<std::unique_ptr<Sensor>> Sensor 부모 클래스 타입을 가리키는
    //   스마트 포인터들을 여러 개 담을 수 있는 가변 배열(바구니)을 만듭니다.
    std::cout << "===[관찰 2] 다형성 루프 실행 ===" << std::endl;
    std::vector<std::unique_ptr<Sensor>> sensors; 

    // push_back :배열에 새 항목을 추가합니다.
    // Lidar와 Imu는 서로 다른 클래스이지만, 모두 'Sensor'의 자식들이므로
    // 부모 타입 배열인 sensors 바구니 하나에 다 함께 담길 수 있습니다!
    sensors.push_back(std::make_unique<Lidar>("LidarSensor")); // Lidar 객체를 힙에 생성하고 스마트 포인터로 관리
    sensors.push_back(std::make_unique<Imu>("ImuSensor")); // Imu 객체를 힙에 생성하고 스마트 포인터로 관리


    // 범위 기반 for 문 (Range-based for loop):
    // sensors 바구니에 있는 항목을 하나씩 꺼내어 sensor 변수에 넣고 반복합니다.
    for (const auto& sensor : sensors) { 
        // sensor->read(): 똑같은 read() 함수를 호출하지만!
        // sensor가 Lidar일 때는 0.25가 나오고, Imu일 때는 0.80이 나옵니다.
        // 이것이 바로 "하나의 코드로 여러 형태를 다루는" 다형성입니다.
        std::cout << "[Main] " << sensor->getName() << " 측정값: " << sensor->read() << std::endl;
    }

    // 3) STL unordered_map 및 vector + count_if 사용 예제
    std::cout << "===[관찰 3] STL 컨테이너 및 count_if 사용 예제 ===" << std::endl;

    //unordered_map<키, 값>: 사전(Dictionary) 구조
    //"Front_Lidar"라는 이름(key)으로 0.25라는 값을 찾을 수 있게 저장합니다.
    std::unordered_map<std::string, double> sensorDataMap; // 센서 이름과 측정값을 저장하는 해시맵 생성

    for (const auto& sensor : sensors) { 
        sensorDataMap[sensor->getName()] = sensor->read(); // 센서 이름과 측정값을 해시맵에 저장
    }

    //측정 데이터 기록 목록 (vector)
    std::vector<double> logs = {0.12, 0.45, 0.30, 0.88, 0.22, 0.35, 0.50}; // 센서 측정값을 저장하는 벡터 생성

    // std::count_if(시작위치, 끝위치, 조건식)
    // [](double distance) { return distance <= 0.35; } 부분은 '람다(Lambda) 함수'로,
    // 데이터 값이 0.35 이하일 때만 참(true)을 반환하는 이름 없는 즉석 함수입니다.
    int count = std::count_if(logs.begin(), logs.end(), [](double distance) {
         return distance <= 0.35; 
        }); // 람다 함수 사용
    
    std::cout << "0.35 m 이내인 기록 개수(장애물 감지 횟수): " << count << "개(회)" << std::endl;

    //4) clamp 함수 템플릿 적용
    std::cout << "===[관찰 4] clamp 함수 템플릿 함수 적용 ===" << std::endl;
    double speed = 12.5; // 속도가 허용 한도를 초과함
    // template 덕분에 double 형 데이터를 넣으면 알아서 double용 clamp가 작동합니다.
    double clampedSpeed = clamp(speed, 0.0, 10.0); // speed 값을 0.0과 10.0 사이로 제한

    int pixel = 300;// 픽셀값이 255를 초과함
    int clampedPixel = clamp(pixel, 0, 255); // pixel 값을 0과 255 사이로 제한

    std::cout << "[Main] 속도 제한(12.5->0~10): " << clampedSpeed << "m/s"  << std::endl;
    std::cout << "[Main] 픽셀 값 제한(300->0~255): " << clampedPixel << "px" << std::endl;

    return 0;// 프로그램 정상 종료
};