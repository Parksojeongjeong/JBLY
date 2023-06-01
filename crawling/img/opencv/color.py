import cv2
import os

# 분홍색 티셔츠 이미지 파일 경로
query_image_path = "D:\\Jblytop\\6a8e1e1a1e677e20a0dd49001ae7b4e6.jpg"

# 이미지들이 저장되어 있는 폴더 경로
image_folder_path = "D:\\Jblytop"

# 분류된 이미지를 저장할 폴더 경로
output_folder_path = "D:\\top_pink"

# 분홍색 티셔츠 이미지 읽기
query_image = cv2.imread(query_image_path)

# 분홍색 티셔츠 이미지의 히스토그램 계산
query_hist = cv2.calcHist([query_image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

# 이미지 폴더 내의 모든 파일에 대해 반복
for filename in os.listdir(image_folder_path):
    # 파일 경로 생성
    file_path = os.path.join(image_folder_path, filename)
    # 파일 읽기
    image = cv2.imread(file_path)
    # 이미지 히스토그램 계산
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    # 히스토그램 비교
    correlation = cv2.compareHist(query_hist, hist, cv2.HISTCMP_CORREL)
    # correlation 값이 0.5 이상이면 분홍색에 가까운 이미지로 분류
    if correlation > 0.5:
        # 이미지 저장
        output_path = os.path.join(output_folder_path, filename)
        cv2.imwrite(output_path, image)
