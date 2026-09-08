# classmethod vs. staticmethod

일반 메서드, `@classmethod`, `@staticmethod`는 첫 번째 인자로 무엇을 받느냐와 객체나 클래스의 상태에 접근할 수 있는지에 따라 명확하게 구분됩니다.

파이썬 공식 문서([Python Official Documentation](https://docs.python.org/3/library/functions.html))에 따르면 각 메서드는 호출될 때 전달되는 암묵적 인자와 활용 방식이 다릅니다. 세 가지 메서드 타입의 차이점을 아래 표와 설명으로 비교해 드립니다.

------------------------------
## 메서드 타입별 비교

| 구분 | 첫 번째 인자 | 인스턴스(self) 접근 | 클래스(cls) 접근 | 주요 용도 |
|---|---|---|---|---|
| 일반 메서드 | self (인스턴스) | 가능 | 가능 | 인스턴스 속성 변경 및 조회 |
| `@classmethod` | cls (클래스) | 불가능 | 가능 | 대체 생성자(팩토리 메서드), 클래스 상태 관리 |
| @staticmethod | 없음 (자유) | 불가능 | 불가능 | 클래스 네임스페이스에 속한 독립적인 유틸리티 함수 |

------------------------------
## 1. 일반 메서드 (Instance Method)

* 특징: 첫 번째 인자로 인스턴스 자신인 self를 자동으로 받습니다.
* 용도: 특정 객체(인스턴스)의 데이터를 읽거나 수정할 때 사용합니다.
* 예시: `def instance_method(self):`

## 2. 클래스 메서드 (@classmethod)

* 특징: 첫 번째 인자로 클래스 자체인 cls를 자동으로 받습니다.
* 용도: 객체 생성 없이 클래스 변수를 다루거나, 다양한 형태의 입력값으로 객체를 만드는 대체 생성자(팩토리 패턴)로 주로 사용합니다.
* 메서드 내부에서 인스턴스 변수(self.name 등)를 쓰지 않고, 오직 클래스 레벨의 동작이나 변수만 다룬다면 `@classmethod` 사용
* 예시: 
    ```python
    @classmethod
    def class_method(cls):
    ```

    ```python
    class Person:
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

        # 하이픈(-)으로 연결된 문자열을 받아 객체를 생성하는 클래스 메서드
        @classmethod
        def from_string(cls, string_data: str):
            # 1. 데이터를 파싱
            name, age_str = string_data.split("-")
            # 2. cls(생성자)를 이용해 객체를 생성하여 반환 (Person(name, int(age_str))과 동일)
            return cls(name, int(age_str))

        def introduce(self):
            print(f"안녕하세요, 제 이름은 {self.name}이고, 나이는 {self.age}살입니다.")


    # 1. 일반적인 방식으로 객체 생성
    p1 = Person("홍길동", 25)
    p1.introduce()

    # 2. @classmethod를 이용해 문자열 데이터로 바로 객체 생성
    p2 = Person.from_string("이순신-40")
    p2.introduce()
    ```

    ```python
    class User:
        # 모든 유저가 공유하는 클래스 변수 (총 유저 수 카운트)
        total_users = 0

        def __init__(self, nickname: str):
            self.nickname = nickname
            # 객체가 생성될 때마다 클래스 변수 카운트 증가
            User.total_users += 1

        # 클래스 변수를 다루는 클래스 메서드
        @classmethod
        def get_total_users(cls):
            # cls를 통해 클래스 변수에 안전하게 접근
            return f"현재 서비스에 가입된 총 유저 수: {cls.total_users}명"


    # 유저 객체 생성
    user1 = User("파이썬 초보")
    user2 = User("데코레이터 장인")

    # 인스턴스 없이 클래스에서 직접 호출 가능
    print(User.get_total_users())  # 출력: 현재 서비스에 가입된 총 유저 수: 2명
    ```

## 3. 정적 메서드 (@staticmethod)

* 특징: self나 cls를 전혀 받지 않는 일반 함수 형태입니다. 다만 논리적으로 해당 클래스 내부에 포함되어야 할 때 사용합니다.
* 용도: 클래스나 인스턴스의 상태와 무관하게 동작하며, 외부에서 전달받은 인자만 가지고 단순 계산이나 검증을 수행하는 유틸리티 함수를 만들 때 씁니다.
* 예시:

```python
class MathUtils:
    @staticmethod
    def add(a, b):
        # self나 cls를 쓰지 않고 전달받은 값만 연산
        return a + b
# 객체 생성 없이 바로 호출 가능
print(MathUtils.add(3, 4))  # 7
```