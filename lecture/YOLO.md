[모델] YOLO(you only look once)
==
> 이 글에서는 YOLO 모델의 사용법을 위주로 설명한다.
> 특히 탐지 부분에서만 설명되어 있다.
---
# 1. 모델 다운로드
yolo 모델은 현재 파이썬의 `ultralytics`에서 제공 중이다.
따라서 일단 라이브러리를 `import`해야한다.

```python
from ultralytics import YOLO
```

이후 모델은 아래 형식으로 작성하여 다운로드 할 수 있다
```python
model = YOLO("<다운로드할 모델의 버전>")
```

## 1.1. 모델의 종류
버전은 작성일(2025.07.10.) 기준 yolo v11까지 나와있는 상태이다.
각 버전을 알고 싶다면 [여기서](https://docs.ultralytics.com/ko/models/#featured-models) 알아볼 수 있다.

![YOLO 모델 버전 차이](./images/yolo_model_version.png)
> n, s, m, l, x 순으로 갈수록 모델의 매개변수 수가 증가한다.
> 즉 x는 속도는 느리지만 정교하고, n는 빠르지만 정확도가 떨어진다

---
# 2. 데이터셋 구조
